from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from uuid import uuid4

import pytest

import api
import collector_adapter
from agents import agent2_context_collection
from orchestrators import processual_chat_orchestrator
from services import process_repository
from test_api_processual_chat import asgi_request
from test_p3_collector_integration import FORMATTED_NUMBER, NUMBER, collected_tree


PUBLIC_FIELDS = {
    "tipo", "intent", "resposta", "processo_ativo", "collection_status",
    "failed_stage", "rag_status", "fontes",
}


@pytest.fixture
def integrated_flow(monkeypatch):
    database = Path(__file__).parent / f".p6-{uuid4().hex}.sqlite3"
    monkeypatch.setattr(process_repository, "database_path", lambda: database)
    monkeypatch.setattr(process_repository, "SAMPLE_DATA_FILE", database.with_suffix(".missing.json"))
    monkeypatch.setattr(
        processual_chat_orchestrator,
        "interpret_user_message",
        lambda message, **kwargs: {
            "intent": "process_lookup" if FORMATTED_NUMBER in message else "process_question",
            "process_number": FORMATTED_NUMBER if FORMATTED_NUMBER in message else None,
            "confidence": 1.0,
        },
    )
    monkeypatch.setattr(
        agent2_context_collection,
        "retrieve_rag_context",
        lambda **kwargs: {"status": "not_needed", "chunks": [], "sources": []},
    )
    api._SESSIONS.clear()
    yield database
    api._SESSIONS.clear()
    database.unlink(missing_ok=True)


def _post(message: str, session_id: str | None = None):
    payload = {"mensagem": message}
    if session_id is not None:
        payload["session_id"] = session_id
    response = asgi_request("POST", "/api/processos/chat", payload)
    assert response.status_code == 200
    assert set(response.json()["resultado"]) == PUBLIC_FIELDS
    public = response.content.decode("utf-8").lower()
    for forbidden in ("traceback", "playwright", "captcha", "respostas_api", ".sqlite"):
        assert forbidden not in public
    return response


def test_api_local_hit_uses_real_repository_without_collector(integrated_flow, monkeypatch):
    process_repository.ingest_processes([collected_tree()], source_name="p6-local")
    monkeypatch.setattr(collector_adapter, "collect_process", lambda number: pytest.fail("local hit recollected"))

    result = _post(f"Consulte {FORMATTED_NUMBER}").json()["resultado"]

    assert result["collection_status"] == "success"
    assert result["processo_ativo"] == FORMATTED_NUMBER


def test_api_success_persists_reloads_and_survives_session_and_restart(integrated_flow, monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(collector_adapter, "collect_process", lambda number: calls.append(number) or collected_tree())

    first = _post(f"Consulte {FORMATTED_NUMBER}")
    session_id = first.json()["session_id"]
    persisted = process_repository.find_process_by_number(NUMBER)
    assert first.json()["resultado"]["collection_status"] == "collected"
    assert api._SESSIONS[session_id]["active_process"] == persisted
    assert calls == [NUMBER]

    second = _post("Qual o valor da causa?", session_id)
    assert second.json()["resultado"]["processo_ativo"] == FORMATTED_NUMBER
    assert calls == [NUMBER]

    new_session = _post(f"Consulte {FORMATTED_NUMBER}")
    assert new_session.json()["resultado"]["collection_status"] == "success"
    assert calls == [NUMBER]

    api._SESSIONS.clear()
    restarted = _post(f"Consulte {FORMATTED_NUMBER}", "restart-logico")
    assert restarted.json()["resultado"]["collection_status"] == "success"
    assert calls == [NUMBER]


@pytest.mark.parametrize(
    ("producer_status", "public_status"),
    [("NAO_ENCONTRADO", "not_found"), ("PARCIAL", "partial"), ("BLOQUEADO", "blocked"), ("FALHA", "failed")],
)
def test_api_preserves_external_failure_semantics_without_persistence(
    integrated_flow, monkeypatch, producer_status, public_status
):
    tree = collected_tree()
    tree["coleta"]["status_coleta"] = producer_status
    if producer_status == "NAO_ENCONTRADO":
        tree = {"processo": {}, "partes_interessadas": [], "movimentacoes": [], "documentos": [], "pendencias": [], "coleta": {"status_coleta": producer_status}}
    monkeypatch.setattr(collector_adapter, "collect_process", lambda number: tree)

    result = _post(f"Consulte {FORMATTED_NUMBER}").json()["resultado"]

    assert result["collection_status"] == public_status
    assert result["processo_ativo"] is None
    assert process_repository.find_process_by_number(NUMBER) is None
    if public_status != "not_found":
        assert "não foi encontrado" not in result["resposta"].lower()


def test_api_contains_external_exception_without_leaking_or_persisting(integrated_flow, monkeypatch):
    def fail(number):
        raise RuntimeError("PRIVATE traceback CAPTCHA browser payload")

    monkeypatch.setattr(collector_adapter, "collect_process", fail)
    result = _post(f"Consulte {FORMATTED_NUMBER}").json()["resultado"]
    assert result["collection_status"] == "failed"
    assert result["processo_ativo"] is None
    assert process_repository.find_process_by_number(NUMBER) is None


def test_api_ingestion_failure_rolls_back_and_preserves_existing_data(integrated_flow, monkeypatch):
    previous = collected_tree()
    previous["processo"]["numero_normalizado"] = "00000010220265180001"
    previous["processo"]["numero"] = "0000001-02.2026.5.18.0001"
    process_repository.ingest_processes([previous], source_name="p6-existing")
    before = deepcopy(process_repository.find_process_by_number("00000010220265180001"))
    monkeypatch.setattr(collector_adapter, "collect_process", lambda number: collected_tree())
    monkeypatch.setattr(
        process_repository,
        "build_process_chunks",
        lambda process: (_ for _ in ()).throw(RuntimeError("controlled ingestion failure")),
    )

    result = _post(f"Consulte {FORMATTED_NUMBER}").json()["resultado"]

    assert result["collection_status"] == "failed"
    assert result["processo_ativo"] is None
    assert process_repository.find_process_by_number(NUMBER) is None
    assert process_repository.find_process_by_number("00000010220265180001") == before
