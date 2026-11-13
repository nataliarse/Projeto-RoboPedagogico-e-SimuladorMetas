from schemas.meta_contracts import ProcessMetaImpactResponse


PROVISIONAL_META_NOTICE = (
    "Essa análise é provisória e depende da validação dos critérios oficiais da meta."
)


def explain_process_meta_impact(
    pergunta_usuario: str,
    impact_response: ProcessMetaImpactResponse,
) -> str:
    _ = pergunta_usuario

    impacto = _clean_text(impact_response.impacto)
    if impacto == "processo_nao_encontrado":
        return (
            "Não encontrei esse processo nos dados disponíveis para análise. "
            "Sem o processo, não é possível estimar impacto na meta. "
            "Nenhuma regra oficial da meta foi aplicada."
        )

    if impacto == "possivel_risco_para_meta":
        return (
            "Este processo pode ter possível risco para a meta, porque "
            f"{_risk_reason(impact_response)}. {PROVISIONAL_META_NOTICE}"
        )

    if impacto == "possivel_contribuicao_para_meta":
        return (
            "Este processo pode ter possível contribuição para a meta, porque "
            f"{_contribution_reason(impact_response)}. {PROVISIONAL_META_NOTICE}"
        )

    if impacto == "inconclusivo":
        return (
            "Não foi possível concluir o impacto deste processo na meta com os "
            f"dados disponíveis. {PROVISIONAL_META_NOTICE}"
        )

    return (
        "Ainda não há explicação conclusiva para o impacto deste processo na meta "
        f"com os dados disponíveis. {PROVISIONAL_META_NOTICE}"
    )


def _risk_reason(response: ProcessMetaImpactResponse) -> str:
    if response.conta_como_novo is True and response.conta_como_julgado is False:
        return (
            "foi identificada entrada/distribuição, mas não foi identificado "
            "julgamento"
        )

    if response.conta_como_novo is True and response.conta_como_julgado is None:
        return (
            "foi identificada entrada/distribuição, mas ainda não há confirmação "
            "de julgamento"
        )

    if response.conta_como_julgado is False:
        return (
            "não foi identificado julgamento, e os demais dados não bastam para "
            "confirmar contribuição para a meta"
        )

    return (
        "os eventos identificados ainda não permitem confirmar contribuição para "
        "a meta"
    )


def _contribution_reason(response: ProcessMetaImpactResponse) -> str:
    if response.conta_como_julgado is True:
        return "foi identificado julgamento"

    return (
        "os eventos disponíveis indicam possível contribuição, mas os critérios "
        "ainda precisam ser validados"
    )


def _clean_text(value: object) -> str:
    return " ".join(str(value or "").split())
