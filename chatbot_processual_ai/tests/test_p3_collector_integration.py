from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

import collector_adapter
from agents import agent2_context_collection
from services import process_repository


NUMBER = "00110008219815180051"
FORMATTED_NUMBER = "0011000-82.1981.5.18.0051"


def collected_tree() -> dict:
    return {
        "processo": {
            "numero": FORMATTED_NUMBER,
            "numero_normalizado": NUMBER,
            "classe_judicial": "Ação sintética",
            "assunto": "Teste offline",
            "valor_causa": 100.0,
        },
        "partes_interessadas": [
            {"polo": "ATIVO", "nome": "Parte sintética", "documento": "remover"}
        ],
        "movimentacoes": [
            {"ordem": 1, "data": "2026-01-01", "descricao": "Movimento sintético"}
        ],
        "documentos": [
            {"titulo": "Documento sintético", "conteudo": "Conteúdo", "id_documento": "remover"}
        ],
        "pendencias": [],
        "coleta": {"status_coleta": "SUCESSO"},
    }


@pytest.fixture
def isolated_database(monkeypatch):
    database = Path(__file__).parent / f".p3-{uuid4().hex}.sqlite3"
    monkeypatch.setattr(process_repository, "database_path", lambda: database)
    monkeypatch.setattr(
        process_repository,
        "SAMPLE_DATA_FILE",
        database.with_suffix(".missing.json"),
    )
    yield database
    database.unlink(missing_ok=True)


def _install_fake_collector(monkeypatch, calls: list[str]) -> None:
    monkeypatch.setattr(
        collector_adapter,
        "collect_process",
        lambda number: calls.append(number) or collected_tree(),
    )


def test_success_is_persisted_reloaded_sanitized_and_chunked(
    isolated_database, monkeypatch
):
    calls: list[str] = []
    _install_fake_collector(monkeypatch, calls)

    result = collector_adapter.create_collector_adapter().lookup_or_acquire_process(
        FORMATTED_NUMBER
    )

    assert result.status is collector_adapter.AdapterStatus.COLLECTED
    assert calls == [NUMBER]
    assert result.process == process_repository.find_process_by_number(NUMBER)
    assert "documento" not in result.process["partes_interessadas"][0]
    assert "id_documento" not in result.process["documentos"][0]
    assert process_repository.get_chunks_for_process(NUMBER)


@pytest.mark.parametrize(
    ("producer_status", "adapter_status"),
    [
        ("NAO_ENCONTRADO", collector_adapter.AdapterStatus.NOT_FOUND),
        ("PARCIAL", collector_adapter.AdapterStatus.PARTIAL),
        ("BLOQUEADO", collector_adapter.AdapterStatus.BLOCKED),
        ("FALHA", collector_adapter.AdapterStatus.FAILED),
        ("DESCONHECIDO", collector_adapter.AdapterStatus.FAILED),
    ],
)
def test_non_persistable_states_do_not_write(
    isolated_database, monkeypatch, producer_status, adapter_status
):
    tree = collected_tree()
    tree["coleta"]["status_coleta"] = producer_status
    if producer_status == "NAO_ENCONTRADO":
        tree = {
            "processo": {},
            "partes_interessadas": [],
            "movimentacoes": [],
            "documentos": [],
            "pendencias": [],
            "coleta": {"status_coleta": producer_status},
        }
    monkeypatch.setattr(collector_adapter, "collect_process", lambda number: tree)

    result = collector_adapter.create_collector_adapter().lookup_or_acquire_process(
        FORMATTED_NUMBER
    )

    assert result.status is adapter_status
    assert process_repository.find_process_by_number(NUMBER) is None


def test_ingestion_failure_rolls_back_process_relations_chunks_and_run(
    isolated_database, monkeypatch
):
    monkeypatch.setattr(
        process_repository,
        "build_process_chunks",
        lambda process: (_ for _ in ()).throw(RuntimeError("synthetic failure")),
    )

    with pytest.raises(RuntimeError, match="synthetic failure"):
        process_repository.ingest_processes(
            [collected_tree()], source_name=collector_adapter.COLLECTOR_SOURCE_NAME
        )

    connection = sqlite3.connect(isolated_database)
    try:
        for table in (
            "processes",
            "parties",
            "movements",
            "documents",
            "pending_items",
            "collection_metadata",
            "rag_chunks",
            "ingestion_runs",
        ):
            assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
    finally:
        connection.close()


def test_same_session_reuses_active_process_without_recollection(
    isolated_database, monkeypatch
):
    calls: list[str] = []
    _install_fake_collector(monkeypatch, calls)
    state = {"active_process": None, "last_intent": None}

    assert agent2_context_collection._handle_process_lookup(FORMATTED_NUMBER, state) == "collected"
    assert agent2_context_collection._handle_process_lookup(FORMATTED_NUMBER, state) == "already_active"
    assert calls == [NUMBER]


def test_new_session_reuses_persisted_process_without_recollection(
    isolated_database, monkeypatch
):
    first_calls: list[str] = []
    _install_fake_collector(monkeypatch, first_calls)
    assert agent2_context_collection._handle_process_lookup(
        FORMATTED_NUMBER, {"active_process": None, "last_intent": None}
    ) == "collected"

    monkeypatch.setattr(
        collector_adapter,
        "collect_process",
        lambda number: pytest.fail("persisted process must prevent recollection"),
    )
    new_state = {"active_process": None, "last_intent": None}
    assert agent2_context_collection._handle_process_lookup(FORMATTED_NUMBER, new_state) == "success"
    assert new_state["active_process"] == process_repository.find_process_by_number(NUMBER)
    assert first_calls == [NUMBER]


def test_logical_restart_reuses_same_sqlite_without_recollection(
    isolated_database, monkeypatch
):
    process_repository.ingest_processes(
        [collected_tree()], source_name=collector_adapter.COLLECTOR_SOURCE_NAME
    )
    monkeypatch.setattr(
        collector_adapter,
        "collect_process",
        lambda number: pytest.fail("logical restart must use SQLite"),
    )

    restarted_adapter = collector_adapter.create_collector_adapter()
    result = restarted_adapter.lookup_or_acquire_process(FORMATTED_NUMBER)

    assert result.status is collector_adapter.AdapterStatus.LOCAL_HIT
    assert result.process == process_repository.find_process_by_number(NUMBER)


def test_collected_process_continues_through_existing_context_route(
    isolated_database, monkeypatch
):
    calls: list[str] = []
    _install_fake_collector(monkeypatch, calls)
    monkeypatch.setattr(
        agent2_context_collection,
        "retrieve_rag_context",
        lambda **kwargs: {"status": "not_needed", "chunks": [], "sources": []},
    )
    state = {"conversation": [], "active_process": None, "last_intent": None}

    context = agent2_context_collection.build_context_and_collect(
        f"Qual o valor da causa no processo {FORMATTED_NUMBER}?",
        {"intent": "process_question", "process_number": FORMATTED_NUMBER},
        state,
    )

    assert context["collection_status"] == "collected"
    assert context["active_process"] is state["active_process"]
    assert context["intent_data"]["intent"] == "process_question"
    assert context["query_route"]["route"] != "missing_process"
    assert calls == [NUMBER]


def test_progress_covers_p3_stages_without_internal_data(
    isolated_database, monkeypatch
):
    calls: list[str] = []
    events = []
    _install_fake_collector(monkeypatch, calls)
    monkeypatch.setattr(
        agent2_context_collection,
        "retrieve_rag_context",
        lambda **kwargs: {"status": "not_needed", "chunks": [], "sources": []},
    )

    agent2_context_collection.build_context_and_collect(
        f"Consulte {FORMATTED_NUMBER}",
        {"intent": "process_lookup", "process_number": FORMATTED_NUMBER},
        {"conversation": [], "active_process": None, "last_intent": None},
        progress_reporter=events.append,
    )

    codes = {event.code for event in events}
    assert {
        "collector.local_lookup.started",
        "collector.acquisition.started",
        "collector.persistence.started",
        "collector.persistence.finished",
        "collector.result",
        "context.lookup.finished",
    }.issubset(codes)
    public_text = " ".join(
        text
        for event in events
        for text in (event.message, str(event.details))
    ).lower()
    for forbidden in (
        "captcha",
        "playwright",
        "cookie",
        "token",
        "stack trace",
        "html bruto",
        str(isolated_database).lower(),
    ):
        assert forbidden not in public_text
