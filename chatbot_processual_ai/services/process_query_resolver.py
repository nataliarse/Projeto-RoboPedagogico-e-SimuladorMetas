from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from services.text_normalization import normalize_process_number, normalize_text_for_match


SCOPE_PROCESS = "process"
SCOPE_GENERAL = "general"
SCOPE_UNCLEAR = "unclear"

TARGET_CASE_VALUE = "case_value"
TARGET_STRUCTURED_FIELD = "structured_field"
TARGET_DOCUMENT_CONTENT = "document_content"
TARGET_LEGAL_CONCEPT = "legal_concept"
TARGET_LEGAL_CONCEPT_WITH_CASE_CONTEXT = "legal_concept_with_case_context"
TARGET_GENERIC_PROCESS = "generic_process"
TARGET_UNCLEAR = "unclear"

STRUCTURED_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "valor_causa": (
        "valor da causa",
        "valor causa",
        "valor informado",
        "valor atribuido",
        "valor do processo",
        "valor descrito",
        "valor registrado",
        "valor indicado",
        "valor declarado",
        "valor desse processo",
        "valor deste processo",
        "qual o valor",
    ),
    "assunto": (
        "assunto",
        "materia",
        "tema",
    ),
    "classe_judicial": (
        "classe judicial",
        "classe processual",
        "classe",
    ),
    "orgao_julgador": (
        "orgao julgador",
        "juizo",
        "vara",
    ),
    "data_autuacao": (
        "data de autuacao",
        "data da autuacao",
        "data autuacao",
        "autuacao",
        "quando foi autuado",
        "quando foi ajuizado",
    ),
    "situacao": (
        "situacao",
        "status",
        "estado do processo",
    ),
}

FIELD_LABELS: dict[str, str] = {
    "valor_causa": "Valor da causa",
    "assunto": "Assunto",
    "classe_judicial": "Classe judicial",
    "orgao_julgador": "Orgao julgador",
    "data_autuacao": "Data de autuacao",
    "situacao": "Situacao processual",
}


@dataclass(frozen=True)
class ProcessQuerySpec:
    scope: str
    target: str
    field_key: str | None
    requires_rag: bool
    confidence: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def process_query_spec_from_dict(value: Any) -> ProcessQuerySpec:
    if isinstance(value, ProcessQuerySpec):
        return value

    if not isinstance(value, dict):
        return empty_process_query_spec()

    return ProcessQuerySpec(
        scope=_safe_choice(value.get("scope"), {SCOPE_PROCESS, SCOPE_GENERAL}, SCOPE_UNCLEAR),
        target=_safe_choice(
            value.get("target"),
            {
                TARGET_CASE_VALUE,
                TARGET_STRUCTURED_FIELD,
                TARGET_DOCUMENT_CONTENT,
                TARGET_LEGAL_CONCEPT,
                TARGET_LEGAL_CONCEPT_WITH_CASE_CONTEXT,
                TARGET_GENERIC_PROCESS,
            },
            TARGET_UNCLEAR,
        ),
        field_key=_safe_field_key(value.get("field_key")),
        requires_rag=bool(value.get("requires_rag")),
        confidence=_safe_choice(value.get("confidence"), {"high", "medium", "low"}, "low"),
        reason=str(value.get("reason") or "").strip() or "Especificacao ausente.",
    )


def empty_process_query_spec() -> ProcessQuerySpec:
    return ProcessQuerySpec(
        scope=SCOPE_UNCLEAR,
        target=TARGET_UNCLEAR,
        field_key=None,
        requires_rag=False,
        confidence="low",
        reason="Nenhum alvo processual claro foi identificado.",
    )


def resolve_process_query(
    message: str,
    *,
    process_number: str | None = None,
    has_active_process: bool = False,
) -> ProcessQuerySpec:
    normalized = normalize_text_for_match(message)
    compact = " ".join(normalized.split())
    has_process_number = normalize_process_number(process_number) is not None
    mentions_process = _mentions_process_context(compact)
    field_key = detect_structured_field_key(compact)

    if _looks_like_documentary_value_question(compact):
        return ProcessQuerySpec(
            scope=SCOPE_PROCESS,
            target=TARGET_DOCUMENT_CONTENT,
            field_key=None,
            requires_rag=True,
            confidence="high",
            reason="A pergunta busca valor em documento, decisao, sentenca, calculo ou teor textual.",
        )

    if field_key is not None and _is_legal_concept_question(compact):
        return ProcessQuerySpec(
            scope=SCOPE_GENERAL,
            target=TARGET_LEGAL_CONCEPT,
            field_key=None,
            requires_rag=False,
            confidence="high",
            reason="A mensagem pede explicacao conceitual sobre um campo processual.",
        )

    if field_key is not None:
        return ProcessQuerySpec(
            scope=SCOPE_PROCESS,
            target=TARGET_CASE_VALUE if field_key == "valor_causa" else TARGET_STRUCTURED_FIELD,
            field_key=field_key,
            requires_rag=False,
            confidence="high",
            reason="Campo estruturado do processo identificado por alias deterministico.",
        )

    if _looks_like_document_content_question(compact):
        return ProcessQuerySpec(
            scope=SCOPE_PROCESS,
            target=TARGET_DOCUMENT_CONTENT,
            field_key=None,
            requires_rag=True,
            confidence="high",
            reason="A pergunta busca teor, fundamento ou resultado textual de documento.",
        )

    if _looks_like_case_bound_legal_concept(compact, has_active_process):
        return ProcessQuerySpec(
            scope=SCOPE_PROCESS,
            target=TARGET_LEGAL_CONCEPT_WITH_CASE_CONTEXT,
            field_key=None,
            requires_rag=True,
            confidence="medium",
            reason="A pergunta combina conceito juridico com contexto do processo.",
        )

    if has_process_number or mentions_process or has_active_process:
        return ProcessQuerySpec(
            scope=SCOPE_PROCESS,
            target=TARGET_GENERIC_PROCESS,
            field_key=None,
            requires_rag=False,
            confidence="low",
            reason="A mensagem tem contexto processual, mas sem alvo especifico mapeado.",
        )

    if _is_legal_concept_question(compact):
        return ProcessQuerySpec(
            scope=SCOPE_GENERAL,
            target=TARGET_LEGAL_CONCEPT,
            field_key=None,
            requires_rag=False,
            confidence="medium",
            reason="A mensagem pede explicacao juridico-processual geral.",
        )

    return empty_process_query_spec()


def detect_structured_field_key(message: str) -> str | None:
    normalized = normalize_text_for_match(message)
    compact = " ".join(normalized.split())

    for field_key, aliases in STRUCTURED_FIELD_ALIASES.items():
        if field_key == "valor_causa" and _looks_like_documentary_value_question(compact):
            continue
        if any(alias in compact for alias in aliases):
            return field_key

    return None


def is_structured_process_spec(spec: ProcessQuerySpec | dict | None) -> bool:
    normalized = _normalize_spec(spec)
    return (
        normalized.scope == SCOPE_PROCESS
        and normalized.field_key is not None
        and normalized.target in {TARGET_CASE_VALUE, TARGET_STRUCTURED_FIELD}
    )


def is_document_content_spec(spec: ProcessQuerySpec | dict | None) -> bool:
    normalized = _normalize_spec(spec)
    return (
        normalized.scope == SCOPE_PROCESS
        and normalized.target == TARGET_DOCUMENT_CONTENT
    )


def field_label(field_key: str | None) -> str:
    if field_key is None:
        return "Campo"
    return FIELD_LABELS.get(field_key, field_key)


def _normalize_spec(spec: ProcessQuerySpec | dict | None) -> ProcessQuerySpec:
    if isinstance(spec, ProcessQuerySpec):
        return spec
    return process_query_spec_from_dict(spec)


def _mentions_process_context(compact: str) -> bool:
    markers = (
        "processo",
        "nesse caso",
        "neste caso",
        "nesse processo",
        "neste processo",
        "desse processo",
        "do processo",
        "autos",
    )
    return any(marker in compact for marker in markers)


def _is_legal_concept_question(compact: str) -> bool:
    patterns = (
        "defina",
        "explicar",
        "explique",
        "me explica",
        "me explique",
        "o que e",
        "o que significa",
        "qual o significado",
        "significado",
        "conceito",
        "qual a diferenca",
    )
    return any(pattern in compact for pattern in patterns)


def _looks_like_document_content_question(compact: str) -> bool:
    markers = (
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
        "resultado da sentenca",
    )
    return any(marker in compact for marker in markers)


def _looks_like_documentary_value_question(compact: str) -> bool:
    if "valor" not in compact:
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
    return any(marker in compact for marker in documentary_markers)


def _looks_like_case_bound_legal_concept(compact: str, has_active_process: bool) -> bool:
    if not _is_legal_concept_question(compact):
        return False

    case_markers = (
        "nesse caso",
        "neste caso",
        "nesse processo",
        "neste processo",
        "desse processo",
        "do processo",
        "isso no processo",
    )
    return has_active_process or any(marker in compact for marker in case_markers)


def _safe_choice(value: Any, allowed: set[str], default: str) -> str:
    if isinstance(value, str) and value.strip() in allowed:
        return value.strip()
    return default


def _safe_field_key(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text in FIELD_LABELS:
        return text
    return None
