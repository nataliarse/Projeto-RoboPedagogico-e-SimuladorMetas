from __future__ import annotations

import re

from collector_adapter import find_process_by_number
from schemas.meta_contracts import ProcessMetaImpactResponse
from services.meta_rules import evaluate_process_meta_impact


PROCESS_META_IMPACT_TYPE = "process_meta_impact"
PROCESS_NOT_FOUND_IMPACT = "processo_nao_encontrado"
PROCESS_NOT_FOUND_REASON = (
    "Processo nao encontrado na base local de processos disponivel para analise."
)
PROCESS_NOT_FOUND_OBSERVATION = (
    "Nenhuma regra oficial de meta foi aplicada porque o processo nao foi encontrado."
)


def run_process_meta_impact(
    numero_processo: str,
    meta_id: str,
    ano: int,
) -> ProcessMetaImpactResponse:
    normalized_number = _normalize_process_number(numero_processo)
    process = find_process_by_number(normalized_number)

    if process is None:
        return _build_process_not_found_response(
            numero_processo=normalized_number,
            meta_id=meta_id,
            ano=ano,
        )

    return evaluate_process_meta_impact(process, meta_id, ano)


def _normalize_process_number(process_number: str | None) -> str:
    return re.sub(r"\D", "", process_number or "")


def _build_process_not_found_response(
    *,
    numero_processo: str,
    meta_id: str,
    ano: int,
) -> ProcessMetaImpactResponse:
    return ProcessMetaImpactResponse(
        tipo=PROCESS_META_IMPACT_TYPE,
        numero_processo=numero_processo,
        meta_id=meta_id,
        ano=ano,
        conta_como_novo=None,
        conta_como_julgado=None,
        conta_como_baixado=None,
        impacto=PROCESS_NOT_FOUND_IMPACT,
        motivo=PROCESS_NOT_FOUND_REASON,
        observacoes=[PROCESS_NOT_FOUND_OBSERVATION],
    )
