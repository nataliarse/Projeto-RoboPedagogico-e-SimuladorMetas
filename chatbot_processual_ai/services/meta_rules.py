from __future__ import annotations

from schemas.meta_contracts import ProcessMetaImpactResponse
from services.process_event_extractor import extract_process_events


PROVISIONAL_OBSERVATION = (
    "Análise provisória. Critérios oficiais da meta precisam ser validados."
)


def evaluate_process_meta_impact(
    process: dict,
    meta_id: str,
    ano: int,
) -> ProcessMetaImpactResponse:
    events = extract_process_events(process)
    numero_processo = _extract_process_number(process)

    conta_como_novo = events.get("possui_distribuicao")
    conta_como_julgado = events.get("possui_julgamento")
    conta_como_baixado = _combine_event_flags(
        events.get("possui_baixa"),
        events.get("possui_arquivamento"),
    )

    impacto = _classify_impact(conta_como_novo, conta_como_julgado)
    motivo = _build_reason(
        impacto=impacto,
        conta_como_novo=conta_como_novo,
        conta_como_julgado=conta_como_julgado,
        conta_como_baixado=conta_como_baixado,
    )

    return ProcessMetaImpactResponse(
        tipo="process_meta_impact",
        numero_processo=numero_processo,
        meta_id=meta_id,
        ano=ano,
        conta_como_novo=conta_como_novo,
        conta_como_julgado=conta_como_julgado,
        conta_como_baixado=conta_como_baixado,
        impacto=impacto,
        motivo=motivo,
        observacoes=_build_observations(events),
    )


def _extract_process_number(process: dict) -> str:
    if not isinstance(process, dict):
        return ""

    process_data = process.get("processo")
    if isinstance(process_data, dict):
        number = process_data.get("numero") or process_data.get("numero_normalizado")
        if number:
            return str(number)

    number = process.get("numero") or process.get("numero_normalizado")
    if number:
        return str(number)

    return ""


def _combine_event_flags(*flags: bool | None) -> bool | None:
    if any(flag is True for flag in flags):
        return True
    if any(flag is None for flag in flags):
        return None
    return False


def _classify_impact(
    conta_como_novo: bool | None,
    conta_como_julgado: bool | None,
) -> str:
    if conta_como_novo is None and conta_como_julgado is None:
        return "inconclusivo"
    if conta_como_julgado is True:
        return "possivel_contribuicao_para_meta"
    if conta_como_novo is True and conta_como_julgado is False:
        return "possivel_risco_para_meta"
    return "inconclusivo"


def _build_reason(
    impacto: str,
    conta_como_novo: bool | None,
    conta_como_julgado: bool | None,
    conta_como_baixado: bool | None,
) -> str:
    if impacto == "possivel_contribuicao_para_meta":
        return (
            "Foram detectados eventos de julgamento ou sentença no processo. "
            "A avaliação é apenas provisória e não aplica a regra oficial da meta."
        )

    if impacto == "possivel_risco_para_meta":
        return (
            "Foi detectada distribuição ou autuação, mas não foi detectado julgamento "
            "ou sentença nos dados analisados. A avaliação é apenas provisória e não "
            "aplica a regra oficial da meta."
        )

    if (
        conta_como_novo is None
        and conta_como_julgado is None
        and conta_como_baixado is None
    ):
        return (
            "Não há dados processuais suficientes nos campos esperados para avaliar "
            "impacto provisório na meta."
        )

    return (
        "Os eventos detectados não são suficientes para indicar contribuição ou risco "
        "provisório para a meta."
    )


def _build_observations(events: dict) -> list[str]:
    observations = list(events.get("observacoes") or [])
    observations.append(PROVISIONAL_OBSERVATION)
    return observations
