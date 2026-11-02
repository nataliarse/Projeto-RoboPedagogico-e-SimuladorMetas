from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from progress import ProgressReporter, progress_clock, report_progress
from services.process_repository import find_process_by_number as _find_process_by_number
from services.process_repository import ingest_processes


logger = logging.getLogger(__name__)
COLLECTOR_SOURCE_NAME = "trt18_collector"


class AdapterStatus(str, Enum):
    LOCAL_HIT = "LOCAL_HIT"
    COLLECTED = "COLLECTED"
    NOT_FOUND = "NOT_FOUND"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    INVALID_NUMBER = "INVALID_NUMBER"


_PUBLIC_MESSAGES = {
    AdapterStatus.LOCAL_HIT: "Processo localizado.",
    AdapterStatus.COLLECTED: "Processo localizado e atualizado com sucesso.",
    AdapterStatus.NOT_FOUND: "Processo não encontrado na fonte consultada.",
    AdapterStatus.PARTIAL: (
        "A consulta retornou dados incompletos. Tente novamente mais tarde."
    ),
    AdapterStatus.BLOCKED: (
        "A consulta externa está temporariamente indisponível. "
        "Tente novamente mais tarde."
    ),
    AdapterStatus.FAILED: (
        "Não foi possível consultar o processo agora. Tente novamente mais tarde."
    ),
    AdapterStatus.INVALID_NUMBER: (
        "Número de processo inválido. Confira os dados informados."
    ),
}

_RETRYABLE = {
    AdapterStatus.LOCAL_HIT: False,
    AdapterStatus.COLLECTED: False,
    AdapterStatus.NOT_FOUND: True,
    AdapterStatus.PARTIAL: True,
    AdapterStatus.BLOCKED: True,
    AdapterStatus.FAILED: True,
    AdapterStatus.INVALID_NUMBER: False,
}


@dataclass(frozen=True)
class CollectorResult:
    status: AdapterStatus
    process: dict | None
    public_message: str
    retryable: bool
    diagnostic_id: str | None = None

    def __post_init__(self) -> None:
        process_expected = self.status in {
            AdapterStatus.LOCAL_HIT,
            AdapterStatus.COLLECTED,
        }
        if (self.process is not None) != process_expected:
            raise ValueError("process deve existir somente para LOCAL_HIT e COLLECTED")
        if self.process is not None and not isinstance(self.process, dict):
            raise TypeError("process deve ser dict quando presente")
        if not isinstance(self.public_message, str) or not self.public_message:
            raise ValueError("public_message deve ser uma mensagem não vazia")
        if not isinstance(self.retryable, bool):
            raise TypeError("retryable deve ser bool")
        if self.diagnostic_id is not None and not isinstance(self.diagnostic_id, str):
            raise TypeError("diagnostic_id deve ser str ou None")


Validator = Callable[[str], str]
Lookup = Callable[[str], dict | None]
Collector = Callable[[str], dict]
Persist = Callable[[dict], object]
Reload = Callable[[str], dict | None]


def find_process_by_number(process_number: str) -> dict | None:
    """Preserva a API de lookup local usada pelos consumidores atuais."""
    return _find_process_by_number(process_number)


def validate_process_number(process_number: str) -> str:
    """Usa a validação CNJ canônica do coletor, carregada somente na chamada."""
    from trt18_collector.collector_trt18 import validar_numero_cnj

    return validar_numero_cnj(process_number)


def collect_process(process_number: str) -> dict:
    """Chama exclusivamente a API pública e leve do produtor."""
    from trt18_collector import obter_processo

    return obter_processo(process_number)


@dataclass(frozen=True)
class CollectorAdapter:
    validator: Validator
    lookup: Lookup
    collector: Collector
    persist: Persist
    reload: Reload

    def lookup_or_acquire_process(
        self,
        process_number: str,
        progress_reporter: ProgressReporter | None = None,
    ) -> CollectorResult:
        try:
            normalized_number = self.validator(process_number)
        except (TypeError, ValueError):
            return _result(AdapterStatus.INVALID_NUMBER)
        except Exception as exc:
            _log_failure("validation", exc)
            return _result(AdapterStatus.FAILED)

        lookup_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="collector.local_lookup.started",
            level="started",
            message="consultando base local do processo...",
        )
        try:
            local_process = self.lookup(normalized_number)
        except Exception as exc:
            _log_failure("lookup", exc)
            return _result(AdapterStatus.FAILED)

        if local_process is not None:
            if _tree_matches(local_process, normalized_number):
                result = _result(AdapterStatus.LOCAL_HIT, local_process)
                _report_result(progress_reporter, result, lookup_started_at)
                return result
            _log_failure("lookup_result")
            return _result(AdapterStatus.FAILED)

        report_progress(
            progress_reporter,
            code="collector.acquisition.started",
            level="started",
            message=(
                "processo nao disponivel localmente; iniciando consulta externa..."
            ),
            started_at=lookup_started_at,
        )
        try:
            collected_process = self.collector(normalized_number)
        except Exception as exc:
            _log_failure("collection", exc)
            return _result(AdapterStatus.FAILED)

        producer_status = _producer_status(collected_process)
        translated_status = {
            "NAO_ENCONTRADO": AdapterStatus.NOT_FOUND,
            "PARCIAL": AdapterStatus.PARTIAL,
            "BLOQUEADO": AdapterStatus.BLOCKED,
            "FALHA": AdapterStatus.FAILED,
        }.get(producer_status)
        if translated_status is not None:
            if producer_status == "NAO_ENCONTRADO" and _has_substantive_tree(
                collected_process
            ):
                _log_failure("contradictory_not_found")
                return _result(AdapterStatus.FAILED)
            return _result(translated_status)

        if producer_status != "SUCESSO" or not _tree_matches(
            collected_process, normalized_number
        ):
            _log_failure("invalid_collection_result")
            return _result(AdapterStatus.FAILED)

        persistence_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="collector.persistence.started",
            level="started",
            message="processo obtido; salvando dados...",
        )
        try:
            self.persist(collected_process)
            persisted_process = self.reload(normalized_number)
        except Exception as exc:
            _log_failure("persistence_cycle", exc)
            return _result(AdapterStatus.FAILED)

        if not _tree_matches(persisted_process, normalized_number):
            _log_failure("reload_result")
            return _result(AdapterStatus.FAILED)
        result = _result(AdapterStatus.COLLECTED, persisted_process)
        report_progress(
            progress_reporter,
            code="collector.persistence.finished",
            level="success",
            message="processo persistido e carregado.",
            started_at=persistence_started_at,
        )
        _report_result(progress_reporter, result, lookup_started_at)
        return result


def persist_collected_process(process: dict) -> dict[str, int]:
    """Persiste uma árvore aceita usando a transação canônica do repositório."""
    return ingest_processes([process], source_name=COLLECTOR_SOURCE_NAME)


def create_collector_adapter(
    *,
    persist: Persist | None = None,
    reload: Reload | None = None,
    validator: Validator | None = None,
    lookup: Lookup | None = None,
    collector: Collector | None = None,
) -> CollectorAdapter:
    """Compõe os defaults produtivos e mantém o ciclo de persistência explícito."""
    return CollectorAdapter(
        validator=validator or validate_process_number,
        lookup=lookup or find_process_by_number,
        collector=collector or collect_process,
        persist=persist or persist_collected_process,
        reload=reload or find_process_by_number,
    )


def lookup_or_acquire_process(
    process_number: str,
    *,
    validator: Validator,
    lookup: Lookup,
    collector: Collector,
    persist: Persist,
    reload: Reload,
) -> CollectorResult:
    """Executa o contrato local-first com composição explícita e substituível."""
    adapter = CollectorAdapter(validator, lookup, collector, persist, reload)
    return adapter.lookup_or_acquire_process(process_number)


def _result(status: AdapterStatus, process: dict | None = None) -> CollectorResult:
    return CollectorResult(status, process, _PUBLIC_MESSAGES[status], _RETRYABLE[status])


def _report_result(
    progress_reporter: ProgressReporter | None,
    result: CollectorResult,
    started_at: float,
) -> None:
    report_progress(
        progress_reporter,
        code="collector.result",
        level=(
            "success"
            if result.status in {AdapterStatus.LOCAL_HIT, AdapterStatus.COLLECTED}
            else "warning"
        ),
        message=result.public_message,
        details={"collection_status": result.status.value.lower()},
        started_at=started_at,
    )


def _producer_status(value: object) -> str | None:
    if not isinstance(value, dict) or not isinstance(value.get("coleta"), dict):
        return None
    status = value["coleta"].get("status_coleta")
    if isinstance(status, Enum):
        status = status.value
    return status if isinstance(status, str) else None


def _tree_matches(value: object, normalized_number: str) -> bool:
    if not _is_supported_tree(value):
        return False
    process = value["processo"]
    returned_number = process.get("numero_normalizado") or process.get("numero")
    digits = re.sub(r"\D", "", str(returned_number or ""))
    return len(digits) == 20 and digits == normalized_number


def _is_supported_tree(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if not isinstance(value.get("processo"), dict):
        return False
    if not isinstance(value.get("coleta"), dict):
        return False
    return all(
        isinstance(value.get(field), list)
        for field in (
            "partes_interessadas",
            "movimentacoes",
            "documentos",
            "pendencias",
        )
    )


def _has_substantive_tree(value: dict) -> bool:
    process = value.get("processo")
    if isinstance(process, dict) and any(process.values()):
        return True
    return any(
        isinstance(value.get(field), list) and bool(value[field])
        for field in (
            "partes_interessadas",
            "movimentacoes",
            "documentos",
            "pendencias",
        )
    )


def _log_failure(stage: str, exception: Exception | None = None) -> None:
    exception_name = type(exception).__name__ if exception is not None else "none"
    logger.warning(
        "collector_adapter_failure stage=%s exception=%s", stage, exception_name
    )


__all__ = [
    "AdapterStatus",
    "CollectorAdapter",
    "CollectorResult",
    "COLLECTOR_SOURCE_NAME",
    "collect_process",
    "create_collector_adapter",
    "find_process_by_number",
    "lookup_or_acquire_process",
    "persist_collected_process",
    "validate_process_number",
]
