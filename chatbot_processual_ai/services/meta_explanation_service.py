from schemas.meta_contracts import MetaSimulationResponse, ProcessMetaImpactResponse


PROVISIONAL_META_NOTICE = (
    "Essa análise é provisória e depende da validação dos critérios oficiais da meta."
)
NO_OFFICIAL_RULE_NOTICE = (
    "Essa leitura não afirma regra oficial e depende da validação dos critérios da meta."
)
INTERNAL_TERMS = ("json", "agente", "prompt", "pipeline", "backend", "ollama")


def explain_meta_simulation(
    pergunta_usuario: str,
    simulation_response: MetaSimulationResponse,
) -> str:
    _ = pergunta_usuario

    status = _clean_text(simulation_response.status).casefold()
    if status == "not_integrated":
        return (
            "O simulador de metas ainda não está disponível nesta conversa. "
            "Já existe uma definição inicial de entrada e saída, mas a equipe "
            "precisa validar quais dados o simulador receberá e o que ele devolverá."
        )

    values_text = _simulation_values_text(simulation_response)
    observation_text = _first_safe_observation_text(simulation_response.observacoes)

    if values_text:
        response = (
            "A simulação de metas retornou uma leitura preliminar. "
            f"{values_text} {NO_OFFICIAL_RULE_NOTICE}"
        )
    else:
        response = (
            "A simulação de metas ainda não trouxe um resultado numérico confiável "
            f"para apresentar. {NO_OFFICIAL_RULE_NOTICE}"
        )

    if observation_text:
        response = f"{response} Observação: {observation_text}"

    return response


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


def _simulation_values_text(response: MetaSimulationResponse) -> str:
    parts = []

    if response.resultado is not None:
        parts.append(f"Resultado estimado: {_format_number(response.resultado)}.")

    if response.meta_alvo is not None:
        parts.append(f"Meta de referência: {_format_number(response.meta_alvo)}.")

    return " ".join(parts)


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


def _first_safe_observation_text(observations: list[str]) -> str:
    if not isinstance(observations, list):
        return ""

    for observation in observations:
        text = _clean_text(observation)
        if text and not _mentions_internal_detail(text):
            return _ensure_sentence(text)

    return ""


def _mentions_internal_detail(text: str) -> bool:
    normalized_text = text.casefold()
    return any(term in normalized_text for term in INTERNAL_TERMS)


def _clean_text(value: object) -> str:
    return " ".join(str(value or "").split())


def _ensure_sentence(text: str) -> str:
    if text.endswith((".", "!", "?")):
        return text
    return f"{text}."


def _format_number(value: float) -> str:
    if isinstance(value, int):
        return str(value)

    formatted = f"{value:.2f}".rstrip("0").rstrip(".")
    return formatted.replace(".", ",")
