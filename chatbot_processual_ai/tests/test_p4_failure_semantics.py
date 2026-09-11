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
from test_p3_collector_integration import (
    FORMATTED_NUMBER,
    NUMBER,
    collected_tree,
)


PUBLIC_EXPECTATIONS = {
    collector_adapter.AdapterStatus.INVALID_NUMBER: "não é um processo válido",
    collector_adapter.AdapterStatus.NOT_FOUND: "não foi encontrado na consulta ao TRT18",
    collector_adapter.AdapterStatus.PARTIAL: "obter dados suficientes",
    collector_adapter.AdapterStatus.BLOCKED: "fonte externa está temporariamente indisponível",
    collector_adapter.AdapterStatus.FAILED: "falha técnica",
}


@pytest.fixture
def isolated_database(monkeypatch):
    database = Path(__file__).parent / f".p4-{uuid4().hex}.sqlite3"
    monkeypatch.setattr(process_repository, "database_path", lambda: database)
    monkeypatch.setattr(
        process_repository,
        "SAMPLE_DATA_FILE",
        database.with_suffix(".missing.json"),
    )
    yield database
    database.unlink(missing_ok=True)


def _producer_tree(status: collector_adapter.AdapterStatus) -> dict:
    producer_status = {
        collector_adapter.AdapterStatus.NOT_FOUND: "NAO_ENCONTRADO",
        collector_adapter.AdapterStatus.PARTIAL: "PARCIAL",
        collector_adapter.AdapterStatus.BLOCKED: "BLOQUEADO",
        collector_adapter.AdapterStatus.FAILED: "FALHA",
    }[status]
    if status is collector_adapter.AdapterStatus.NOT_FOUND:
        return {
            "processo": {},
            "partes_interessadas": [],
            "movimentacoes": [],
            "documentos": [],
            "pendencias": [],
            "coleta": {"status_coleta": producer_status},
        }
    tree = collected_tree()
    tree["coleta"]["status_coleta"] = producer_status
    return tree


def _adapter_for_status(status, calls):
    def validator(value):
        calls["validator"] += 1
        if status is collector_adapter.AdapterStatus.INVALID_NUMBER:
            raise ValueError("detalhe interno da validação")
        return NUMBER

    def collector(value):
        calls["collector"] += 1
        return _producer_tree(status)

    return collector_adapter.CollectorAdapter(
        validator=validator,
        lookup=lambda value: calls.__setitem__("lookup", calls["lookup"] + 1),
        collector=collector,
        persist=lambda value: calls.__setitem__("persist", calls["persist"] + 1),
        reload=lambda value: None,
    )


def _install_offline_flow(monkeypatch, status, calls):
    adapter = _adapter_for_status(status, calls)
    monkeypatch.setattr(
        agent2_context_collection,
        "create_collector_adapter",
        lambda: adapter,
    )
    monkeypatch.setattr(
        agent2_context_collection,
        "retrieve_rag_context",
        lambda **kwargs: {"status": "not_needed", "chunks": [], "sources": []},
    )
    monkeypatch.setattr(
        processual_chat_orchestrator,
        "interpret_user_message",
        lambda message, **kwargs: {
            "intent": "process_lookup",
            "process_number": FORMATTED_NUMBER,
            "confidence": 1.0,
        },
    )


@pytest.mark.parametrize("status", list(PUBLIC_EXPECTATIONS))
def test_agent2_preserves_failure_status_without_activation_or_persistence(
    monkeypatch, status
):
    calls = {"validator": 0, "lookup": 0, "collector": 0, "persist": 0}
    _install_offline_flow(monkeypatch, status, calls)
    state = {"conversation": [], "active_process": None, "last_intent": None}
    events = []

    context = agent2_context_collection.build_context_and_collect(
        f"Consulte {FORMATTED_NUMBER}",
        {"intent": "process_lookup", "process_number": FORMATTED_NUMBER},
        state,
        progress_reporter=events.append,
    )

    assert context["collection_status"] == status.value.lower()
    assert state["active_process"] is None
    assert calls["persist"] == 0
    assert calls["collector"] == (0 if status is collector_adapter.AdapterStatus.INVALID_NUMBER else 1)
    event_text = " ".join(event.message for event in events).lower()
    assert "processo nao encontrado" not in event_text or status is collector_adapter.AdapterStatus.NOT_FOUND
    assert "automatic" not in event_text


@pytest.mark.parametrize("status", list(PUBLIC_EXPECTATIONS))
def test_orchestrator_returns_safe_distinct_public_semantics(monkeypatch, status):
    calls = {"validator": 0, "lookup": 0, "collector": 0, "persist": 0}
    _install_offline_flow(monkeypatch, status, calls)

    result = processual_chat_orchestrator.run_processual_chat_step(
        f"Consulte {FORMATTED_NUMBER}",
        {"conversation": [], "active_process": None, "last_intent": None},
    )

    response = result.response
    assert response.collection_status == status.value.lower()
    assert response.processo_ativo is None
    assert response.failed_stage is None
    assert PUBLIC_EXPECTATIONS[status].lower() in response.resposta.lower()
    public_text = response.resposta.lower()
    for forbidden in ("traceback", "playwright", "captcha", "cookie", "token", ".sqlite"):
        assert forbidden not in public_text
    if status is not collector_adapter.AdapterStatus.NOT_FOUND:
        assert "não foi encontrado" not in public_text


@pytest.mark.parametrize("status", list(PUBLIC_EXPECTATIONS))
def test_api_keeps_http_contract_for_each_failure_state(monkeypatch, status):
    api._SESSIONS.clear()
    calls = {"validator": 0, "lookup": 0, "collector": 0, "persist": 0}
    _install_offline_flow(monkeypatch, status, calls)

    response = asgi_request(
        "POST",
        "/api/processos/chat",
        {"mensagem": f"Consulte {FORMATTED_NUMBER}"},
    )

    assert response.status_code == 200
    payload = response.json()
    result = payload["resultado"]
    assert result["collection_status"] == status.value.lower()
    assert result["processo_ativo"] is None
    assert set(result) == {
        "tipo", "intent", "resposta", "processo_ativo", "collection_status",
        "failed_stage", "rag_status", "fontes",
    }
    assert PUBLIC_EXPECTATIONS[status].lower() in result["resposta"].lower()


def test_external_exception_is_safe_failed_through_agent2(monkeypatch):
    def fail_collection(value):
        raise RuntimeError("C:\\segredo\\browser CAPTCHA token")

    adapter = collector_adapter.CollectorAdapter(
        validator=lambda value: NUMBER,
        lookup=lambda value: None,
        collector=fail_collection,
        persist=lambda value: pytest.fail("falha externa não pode persistir"),
        reload=lambda value: None,
    )
    monkeypatch.setattr(agent2_context_collection, "create_collector_adapter", lambda: adapter)
    monkeypatch.setattr(
        agent2_context_collection,
        "retrieve_rag_context",
        lambda **kwargs: {"status": "not_needed", "chunks": [], "sources": []},
    )

    context = agent2_context_collection.build_context_and_collect(
        f"Consulte {FORMATTED_NUMBER}",
        {"intent": "process_lookup", "process_number": FORMATTED_NUMBER},
        {"conversation": [], "active_process": None, "last_intent": None},
    )

    assert context["collection_status"] == "failed"


def test_failed_replacement_rolls_back_and_preserves_previous_tree_and_chunks(
    isolated_database, monkeypatch
):
    original = collected_tree()
    process_repository.ingest_processes([original], source_name="estado-anterior")
    tree_before = process_repository.find_process_by_number(NUMBER)
    chunks_before = process_repository.get_chunks_for_process(NUMBER)
    replacement = deepcopy(original)
    replacement["processo"]["assunto"] = "não deve persistir"

    monkeypatch.setattr(
        process_repository,
        "build_process_chunks",
        lambda process: (_ for _ in ()).throw(RuntimeError("falha sintética")),
    )
    with pytest.raises(RuntimeError, match="falha sintética"):
        process_repository.ingest_processes([replacement], source_name="falha")

    assert process_repository.find_process_by_number(NUMBER) == tree_before
    assert process_repository.get_chunks_for_process(NUMBER) == chunks_before
