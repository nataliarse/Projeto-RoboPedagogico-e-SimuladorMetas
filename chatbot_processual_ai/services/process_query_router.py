from __future__ import annotations

from dataclasses import dataclass

from services.process_query_resolver import (
    SCOPE_PROCESS,
    TARGET_LEGAL_CONCEPT_WITH_CASE_CONTEXT,
    is_document_content_spec,
    is_structured_process_spec,
    process_query_spec_from_dict,
)
from services.text_normalization import normalize_text_for_match


STRUCTURED_ROUTE = "structured"
RAG_ROUTE = "rag"
HYBRID_ROUTE = "hybrid"
MISSING_PROCESS_ROUTE = "missing_process"
OUT_OF_SCOPE_ROUTE = "out_of_scope"


@dataclass(frozen=True)
class ProcessQueryRoute:
    route: str
    reason: str
    requires_rag: bool


def route_process_query(
    message: str,
    intent: str | None,
    has_active_process: bool,
    process_query_spec: object | None = None,
) -> ProcessQueryRoute:
    query_spec = process_query_spec_from_dict(process_query_spec)

    if intent == "out_of_scope":
        return ProcessQueryRoute(
            route=OUT_OF_SCOPE_ROUTE,
            reason="Mensagem fora do escopo processual.",
            requires_rag=False,
        )

    if intent not in {"process_lookup", "process_question", "legal_general_question"}:
        return ProcessQueryRoute(
            route=STRUCTURED_ROUTE,
            reason="Intencao nao exige recuperacao semantica.",
            requires_rag=False,
        )

    if query_spec.scope == SCOPE_PROCESS and query_spec.target != "unclear":
        if not has_active_process:
            return ProcessQueryRoute(
                route=MISSING_PROCESS_ROUTE,
                reason="Pergunta depende de processo ativo.",
                requires_rag=False,
            )

        if is_structured_process_spec(query_spec):
            return ProcessQueryRoute(
                route=STRUCTURED_ROUTE,
                reason="Pergunta respondida por campo estruturado do processo.",
                requires_rag=False,
            )

        if is_document_content_spec(query_spec):
            return ProcessQueryRoute(
                route=RAG_ROUTE,
                reason="Pergunta busca teor ou conteudo textual de documento.",
                requires_rag=True,
            )

        if query_spec.target == TARGET_LEGAL_CONCEPT_WITH_CASE_CONTEXT:
            return ProcessQueryRoute(
                route=HYBRID_ROUTE,
                reason="Pergunta combina conceito juridico com contexto do processo.",
                requires_rag=True,
            )

    if intent == "process_lookup":
        return ProcessQueryRoute(
            route=STRUCTURED_ROUTE,
            reason="Consulta inicial usa dados estruturados do processo.",
            requires_rag=False,
        )

    if intent == "legal_general_question" and not _mentions_case_context(message):
        return ProcessQueryRoute(
            route=STRUCTURED_ROUTE,
            reason="Explicacao juridica geral nao precisa de chunks do processo.",
            requires_rag=False,
        )

    if not has_active_process:
        return ProcessQueryRoute(
            route=MISSING_PROCESS_ROUTE,
            reason="Pergunta depende de processo ativo.",
            requires_rag=False,
        )

    normalized = normalize_text_for_match(message)

    if _looks_like_structured_question(normalized):
        return ProcessQueryRoute(
            route=STRUCTURED_ROUTE,
            reason="Pergunta respondida por campos estruturados.",
            requires_rag=False,
        )

    if _looks_like_document_content_question(normalized):
        return ProcessQueryRoute(
            route=RAG_ROUTE,
            reason="Pergunta busca teor ou conteudo textual de documento.",
            requires_rag=True,
        )

    if _mentions_case_context(message):
        return ProcessQueryRoute(
            route=HYBRID_ROUTE,
            reason="Pergunta combina conceito ou evento com contexto do processo.",
            requires_rag=True,
        )

    return ProcessQueryRoute(
        route=HYBRID_ROUTE,
        reason="Pergunta aberta sobre processo pode se beneficiar de chunks.",
        requires_rag=True,
    )


def _looks_like_structured_question(normalized: str) -> bool:
    if (
        _looks_like_documentary_value_question(normalized)
        or _looks_like_document_content_question(normalized)
    ):
        return False

    if _looks_like_movement_structured_question(normalized):
        return True

    structured_markers = (
        "situacao",
        "aberto",
        "baixado",
        "encerrado",
        "pendencia",
        "pendencias",
        "parte",
        "partes",
        "reclamante",
        "reclamado",
        "ultima movimentacao",
        "movimentacao mais recente",
        "movimentacao recente",
        "primeira movimentacao",
        "movimentacao mais antiga",
        "movimentacao inicial",
        "antes do arquivamento",
        "antes da sentenca",
        "antes do transito",
        "valor da causa",
        "valor causa",
        "valor informado",
        "valor descrito",
        "valor registrado",
        "valor indicado",
        "valor declarado",
        "valor desse processo",
        "valor deste processo",
        "qual o valor",
        "assunto",
        "classe judicial",
        "classe processual",
        "orgao julgador",
        "data de autuacao",
        "data autuacao",
        "quando foi arquivado",
        "quando ele foi arquivado",
    )
    return any(marker in normalized for marker in structured_markers)


def _looks_like_movement_structured_question(normalized: str) -> bool:
    movement_markers = (
        "movimentacao",
        "movimentacoes",
        "historico do processo",
        "linha do tempo",
        "o que aconteceu nesse processo",
        "o que aconteceu neste processo",
        "o que aconteceu no processo",
        "o que aconteceu ate agora",
    )
    return any(marker in normalized for marker in movement_markers)


def _looks_like_document_content_question(normalized: str) -> bool:
    if _looks_like_documentary_value_question(normalized):
        return True

    document_markers = (
        "teor",
        "conteudo",
        "documento",
        "sentenca decidiu",
        "decisao decidiu",
        "o que a sentenca decidiu",
        "o que foi decidido",
        "favoravel",
        "quem ganhou",
        "ganhou",
        "fundamento",
        "fundamentacao",
    )
    return any(marker in normalized for marker in document_markers)


def _looks_like_documentary_value_question(normalized: str) -> bool:
    if "valor" not in normalized:
        return False

    documentary_markers = (
        "calculo",
        "calculos",
        "conteudo",
        "decisao",
        "documento",
        "fundamentacao",
        "fundamento",
        "sentenca",
        "teor",
    )
    return any(marker in normalized for marker in documentary_markers)


def _mentions_case_context(message: str) -> bool:
    normalized = normalize_text_for_match(message)
    context_markers = (
        "nesse caso",
        "neste caso",
        "nesse processo",
        "neste processo",
        "desse processo",
        "do processo",
        "isso no processo",
    )
    return any(marker in normalized for marker in context_markers)
