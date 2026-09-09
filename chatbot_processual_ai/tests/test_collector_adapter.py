import sys
import socket
from pathlib import Path

import pytest

import collector_adapter
from collector_adapter import AdapterStatus, CollectorAdapter, CollectorResult


NUMBER = "00110008219815180051"


def tree(status="SUCESSO", number=NUMBER):
    return {
        "processo": {"numero": number, "numero_normalizado": number},
        "partes_interessadas": [],
        "movimentacoes": [],
        "documentos": [],
        "pendencias": [],
        "coleta": {"status_coleta": status},
    }


def adapter(*, validator=None, lookup=None, collector=None, persist=None, reload=None):
    return CollectorAdapter(
        validator=validator or (lambda value: NUMBER),
        lookup=lookup or (lambda value: None),
        collector=collector or (lambda value: tree()),
        persist=persist or (lambda value: None),
        reload=reload or (lambda value: tree()),
    )


@pytest.mark.parametrize("status", list(AdapterStatus))
def test_all_seven_results_can_be_constructed_with_their_invariants(status):
    process = tree() if status in {AdapterStatus.LOCAL_HIT, AdapterStatus.COLLECTED} else None
    result = CollectorResult(status, process, "mensagem", False)
    assert result.status is status


def test_result_rejects_process_presence_in_wrong_states():
    with pytest.raises(ValueError):
        CollectorResult(AdapterStatus.FAILED, tree(), "mensagem", True)
    with pytest.raises(ValueError):
        CollectorResult(AdapterStatus.LOCAL_HIT, None, "mensagem", False)


def test_legacy_lookup_remains_a_transparent_wrapper(monkeypatch):
    expected = tree()
    monkeypatch.setattr(collector_adapter, "_find_process_by_number", lambda value: expected)
    assert collector_adapter.find_process_by_number(NUMBER) is expected


def test_local_hit_prevents_collection_and_writes():
    calls = []
    result = adapter(
        lookup=lambda value: tree(),
        collector=lambda value: calls.append("collector"),
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload"),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.LOCAL_HIT
    assert calls == []


def test_lookup_exception_is_failed_and_prevents_collection():
    calls = []
    result = adapter(
        lookup=lambda value: (_ for _ in ()).throw(OSError("database path")),
        collector=lambda value: calls.append("collector"),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert result.process is None
    assert calls == []
    assert "database path" not in result.public_message


def test_invalid_number_prevents_lookup_and_collection():
    calls = []
    result = adapter(
        validator=lambda value: (_ for _ in ()).throw(ValueError("private input")),
        lookup=lambda value: calls.append("lookup"),
        collector=lambda value: calls.append("collector"),
    ).lookup_or_acquire_process("private input")
    assert result.status is AdapterStatus.INVALID_NUMBER
    assert calls == []
    assert "private input" not in result.public_message


def test_collection_runs_only_after_valid_local_miss():
    calls = []
    result = adapter(
        validator=lambda value: calls.append("validate") or NUMBER,
        lookup=lambda value: calls.append("lookup"),
        collector=lambda value: calls.append("collect") or tree(),
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload") or tree(),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.COLLECTED
    assert calls == ["validate", "lookup", "collect", "persist", "reload"]


@pytest.mark.parametrize(
    ("producer_status", "adapter_status"),
    [
        ("SUCESSO", AdapterStatus.COLLECTED),
        ("NAO_ENCONTRADO", AdapterStatus.NOT_FOUND),
        ("PARCIAL", AdapterStatus.PARTIAL),
        ("BLOQUEADO", AdapterStatus.BLOCKED),
        ("FALHA", AdapterStatus.FAILED),
    ],
)
def test_translates_producer_states_without_exposing_non_success_tree(
    producer_status, adapter_status
):
    candidate = tree(producer_status)
    if producer_status == "NAO_ENCONTRADO":
        candidate["processo"] = {}
    result = adapter(collector=lambda value: candidate).lookup_or_acquire_process(NUMBER)
    assert result.status is adapter_status
    assert (result.process is not None) is (adapter_status is AdapterStatus.COLLECTED)


@pytest.mark.parametrize(
    "producer_status", ["NAO_ENCONTRADO", "PARCIAL", "BLOQUEADO", "FALHA"]
)
def test_non_success_states_never_persist(producer_status):
    calls = []
    candidate = tree(producer_status)
    if producer_status == "NAO_ENCONTRADO":
        candidate["processo"] = {}
    adapter(
        collector=lambda value: candidate,
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload"),
    ).lookup_or_acquire_process(NUMBER)
    assert calls == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"coleta": {}},
        tree("DESCONHECIDO"),
        {**tree(), "movimentacoes": {}},
    ],
)
def test_missing_unknown_or_invalid_status_is_failed(payload):
    result = adapter(collector=lambda value: payload).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert result.process is None


@pytest.mark.parametrize(
    "payload",
    [tree("SUCESSO", "00110008219815180052"), tree("NAO_ENCONTRADO")],
)
def test_contradictory_producer_result_is_failed(payload):
    result = adapter(collector=lambda value: payload).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert result.process is None


def test_technical_exception_is_failed_not_not_found():
    result = adapter(
        collector=lambda value: (_ for _ in ()).throw(RuntimeError("playwright secret"))
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert "playwright secret" not in result.public_message.lower()


@pytest.mark.parametrize(
    "failure_adapter",
    [
        adapter(persist=lambda value: (_ for _ in ()).throw(OSError("path secret"))),
        adapter(reload=lambda value: None),
        adapter(reload=lambda value: (_ for _ in ()).throw(OSError("db secret"))),
    ],
)
def test_collected_requires_successful_persist_and_non_null_reload(failure_adapter):
    result = failure_adapter.lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert result.process is None


def test_collected_returns_the_reloaded_tree_not_the_producer_object():
    producer = tree()
    reloaded = tree()
    reloaded["coleta"] = {"status_coleta": "SUCESSO", "origin": "local"}
    result = adapter(
        collector=lambda value: producer,
        reload=lambda value: reloaded,
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.COLLECTED
    assert result.process is reloaded
    assert result.process is not producer


@pytest.mark.parametrize(
    ("status", "message", "retryable"),
    [
        (AdapterStatus.LOCAL_HIT, "Processo localizado.", False),
        (
            AdapterStatus.COLLECTED,
            "Processo localizado e atualizado com sucesso.",
            False,
        ),
        (
            AdapterStatus.NOT_FOUND,
            "Processo não encontrado na fonte consultada.",
            True,
        ),
        (
            AdapterStatus.PARTIAL,
            "A consulta retornou dados incompletos. Tente novamente mais tarde.",
            True,
        ),
        (
            AdapterStatus.BLOCKED,
            "A consulta externa está temporariamente indisponível. Tente novamente mais tarde.",
            True,
        ),
        (
            AdapterStatus.FAILED,
            "Não foi possível consultar o processo agora. Tente novamente mais tarde.",
            True,
        ),
        (
            AdapterStatus.INVALID_NUMBER,
            "Número de processo inválido. Confira os dados informados.",
            False,
        ),
    ],
)
def test_public_messages_and_retry_policy_are_frozen(status, message, retryable):
    process = tree() if status in {AdapterStatus.LOCAL_HIT, AdapterStatus.COLLECTED} else None
    result = collector_adapter._result(status, process)
    assert result.public_message == message
    assert result.retryable is retryable


def test_adapter_import_keeps_collector_and_heavy_dependencies_lazy():
    source = Path(collector_adapter.__file__).read_text(encoding="utf-8")
    assert "from trt18_collector import obter_processo" in source
    for module in ("trt18_collector", "playwright", "cv2", "ddddocr"):
        assert module not in sys.modules


def test_local_hit_returns_the_approved_local_tree_without_reloading():
    local_tree = tree()
    calls = []
    result = adapter(
        lookup=lambda value: calls.append(("lookup", value)) or local_tree,
        collector=lambda value: calls.append(("collect", value)),
        persist=lambda value: calls.append(("persist", value)),
        reload=lambda value: calls.append(("reload", value)),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.LOCAL_HIT
    assert result.process is local_tree
    assert calls == [("lookup", NUMBER)]


def test_invalid_number_prevents_every_dependency_including_persistence_cycle():
    calls = []
    result = adapter(
        validator=lambda value: (_ for _ in ()).throw(ValueError("raw input")),
        lookup=lambda value: calls.append("lookup"),
        collector=lambda value: calls.append("collector"),
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload"),
    ).lookup_or_acquire_process("not a process")
    assert result.status is AdapterStatus.INVALID_NUMBER
    assert calls == []


def test_invalid_local_tree_is_failed_without_calling_the_collector():
    calls = []
    result = adapter(
        lookup=lambda value: {"processo": {"numero": NUMBER}},
        collector=lambda value: calls.append("collector"),
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload"),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert result.process is None
    assert calls == []


@pytest.mark.parametrize(
    ("producer_status", "expected_status", "expected_retryable"),
    [
        ("NAO_ENCONTRADO", AdapterStatus.NOT_FOUND, True),
        ("PARCIAL", AdapterStatus.PARTIAL, True),
        ("BLOQUEADO", AdapterStatus.BLOCKED, True),
        ("FALHA", AdapterStatus.FAILED, True),
    ],
)
def test_non_success_translation_is_sanitized_and_stops_the_cycle(
    producer_status, expected_status, expected_retryable
):
    candidate = tree(producer_status)
    if producer_status == "NAO_ENCONTRADO":
        candidate["processo"] = {}
    candidate["coleta"]["internal"] = "C:\\private\\playwright CAPTCHA 123.456.789-09"
    calls = []
    result = adapter(
        collector=lambda value: calls.append("collector") or candidate,
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload"),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is expected_status
    assert result.process is None
    assert result.retryable is expected_retryable
    assert calls == ["collector"]
    for private_detail in ("private", "playwright", "captcha", "123.456.789-09"):
        assert private_detail not in result.public_message.lower()
    assert result.diagnostic_id is None


@pytest.mark.parametrize(
    "candidate",
    [
        [],
        {"coleta": {"status_coleta": "SUCESSO"}},
        {**tree(), "coleta": {}},
        {**tree(), "processo": {}},
        {**tree(), "processo": {"classe_judicial": "sintetica"}},
        tree("SUCESSO", "00110008219815180052"),
        {**tree(), "pendencias": {}},
    ],
)
def test_invalid_success_candidates_fail_without_persistence(candidate):
    calls = []
    result = adapter(
        collector=lambda value: candidate,
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload"),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert result.process is None
    assert calls == []


@pytest.mark.parametrize(
    "reloaded",
    [
        tree("SUCESSO", "00110008219815180052"),
        {**tree(), "documentos": {}},
    ],
)
def test_invalid_or_wrong_reloaded_tree_is_failed_after_persistence(reloaded):
    calls = []
    result = adapter(
        persist=lambda value: calls.append("persist") or {"ignored": "allowed"},
        reload=lambda value: calls.append("reload") or reloaded,
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.FAILED
    assert result.process is None
    assert calls == ["persist", "reload"]


def test_fake_boundary_never_opens_a_socket_or_loads_external_runtime(monkeypatch):
    def forbidden_socket(*args, **kwargs):
        raise AssertionError("network must not be used by adapter tests")

    monkeypatch.setattr(socket, "socket", forbidden_socket)
    calls = []
    result = adapter(
        validator=lambda value: calls.append("validate") or NUMBER,
        lookup=lambda value: calls.append("lookup"),
        collector=lambda value: calls.append("collect") or tree(),
        persist=lambda value: calls.append("persist"),
        reload=lambda value: calls.append("reload") or tree(),
    ).lookup_or_acquire_process(NUMBER)
    assert result.status is AdapterStatus.COLLECTED
    assert calls == ["validate", "lookup", "collect", "persist", "reload"]
    assert not {"playwright", "cv2", "ddddocr"}.intersection(sys.modules)
