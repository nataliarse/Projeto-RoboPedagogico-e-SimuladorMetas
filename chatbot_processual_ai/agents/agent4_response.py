import os
import re
import unicodedata
from typing import Any

from ollama_client import OllamaError, generate_text
from progress import ProgressReporter, progress_clock, report_progress
from prompts.agent4_prompt import AGENT4_SYSTEM_PROMPT, build_agent4_prompt


ALLOWED_ANALYSIS_TYPES = {
    "process_summary",
    "process_question",
    "legal_general_explanation",
    "missing_process_context",
    "insufficient_data",
    "greeting",
    "out_of_scope",
    "unclear",
}
ALLOWED_QUESTION_FOCUS = {
    "process_overview",
    "current_status",
    "parties",
    "pending_issues",
    "timeline_before_event",
    "latest_movement",
    "earliest_movement",
    "first_and_latest_movement",
    "movement_list",
    "movement_timeline",
    "document_content",
    "case_value",
    "structured_field",
    "legal_concept_with_case_context",
    "generic_process_question",
}
DEFAULT_QUESTION_FOCUS = "generic_process_question"
INTERNAL_TERM_RE = re.compile(
    r"\b(agente|json|prompt|ollama|modelo|pipeline)\b|"
    r"coleta\s+(?:interna|local)|dados\s+estruturados|detalhes?\s+t[eé]cnicos?",
    re.IGNORECASE,
)
PRIVATE_DOCUMENT_RE = re.compile(
    r"(?<!\d)(?:\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})(?!\d)"
)
INTERNAL_FIELD_RE = re.compile(
    r"\b(?:cpf_cnpj|id_documento|parties|partes_interessadas|pendencias)\b",
    re.IGNORECASE,
)
INTERNAL_PATH_RE = re.compile(
    r"\b[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*|\[[^\]]+\])+\b"
)
TECHNICAL_IDENTIFIER_RE = re.compile(r"\b[A-Z]{2,}-\d+\b")
PROCESS_NUMBER_PATTERN = r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
PROCESS_NUMBER_RE = re.compile(rf"(?<!\d){PROCESS_NUMBER_PATTERN}(?!\d)")
COLLECTION_SUMMARY_RE = re.compile(
    rf"\bA\s+coleta\s+local\s+encontrou\s+dados\s+estruturados\s+para\s+({PROCESS_NUMBER_PATTERN})\.?",
    re.IGNORECASE,
)
USER_INVISIBLE_REFERENCE_RE = re.compile(
    r"\b(?:(?:destacad[ao]s?|indicad[ao]s?|listad[ao]s?)\s+nos\s+fatos|conforme\s+a\s+an[áa]lise|"
    r"conforme\s+os\s+dados\s+internos|o\s+sistema\s+identificou|"
    r"a\s+coleta\s+local)\b",
    re.IGNORECASE,
)
USER_INVISIBLE_SENTENCE_RE = re.compile(
    r"(^|(?<=[.!?])\s*)[^.!?\n]*(?:(?:destacad[ao]s?|indicad[ao]s?|listad[ao]s?)\s+nos\s+fatos|"
    r"conforme\s+a\s+an[áa]lise|conforme\s+os\s+dados\s+internos|"
    r"o\s+sistema\s+identificou|a\s+coleta\s+local)[^.!?\n]*(?:[.!?]|$)",
    re.IGNORECASE,
)
PRIVATE_FIELD_SEGMENT_RE = re.compile(
    r"(?:^|\s*[|;]\s*)\b(?:cpf|cnpj|cpf\s*/\s*cnpj|cpf_cnpj|"
    r"documento(?:\s+pessoal)?|documentos?)\b\s*:\s*(?:\[[^\]]*\]|[^|;\n]*)",
    re.IGNORECASE,
)
DOCUMENT_ID_SEGMENT_RE = re.compile(
    r"(?:^|\s*[|;]\s*)\b(?:id|id_documento|identificador)\b\s*:\s*[^|;\n]*",
    re.IGNORECASE,
)
PRIVACY_DETAIL_RE = re.compile(
    r"\b(?:cpf|cnpj|mascaramento|privacidade)\b|"
    r"documentos?\s+pessoais?|campos?\s+removid[oa]s?",
    re.IGNORECASE,
)
PRIVACY_SENTENCE_RE = re.compile(
    r"(^|(?<=[.!?])\s*)[^.!?\n]*(?:cpf|cnpj|mascaramento|privacidade|"
    r"documentos?\s+pessoais?|campos?\s+removid[oa]s?)[^.!?\n]*(?:[.!?]|$)",
    re.IGNORECASE,
)
PARTY_LABEL_RE = re.compile(
    r"\b(partes?|polo|reclamante|reclamado|autor|r[eé]u|exequente|executado|"
    r"recorrente|recorrido)\b",
    re.IGNORECASE,
)
PARTY_FIELD_RE = re.compile(r"\b(polo|tipo|nome)\s*:\s*([^|;\n]+)", re.IGNORECASE)
SIMPLE_PARTY_RE = re.compile(
    r"^\s*[-*]?\s*(reclamante|reclamado|autor|r[eé]u|exequente|executado|"
    r"recorrente|recorrido)\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)
SIMPLE_PARTY_LABEL_RE = re.compile(
    r"^(reclamante|reclamado|autor|r[eé]u|exequente|executado|"
    r"recorrente|recorrido)$",
    re.IGNORECASE,
)
PARTY_METADATA_START_RE = re.compile(
    r"\s*[|;]\s*(?:polo|tipo|representantes?|advogados?|procuradores?)\s*:",
    re.IGNORECASE,
)
COLLECTION_STATUS_LABEL_RE = re.compile(
    r"situa[cç][aã]o\s+(?:da\s+coleta|dos\s+dados\s+consultados)",
    re.IGNORECASE,
)
FORBIDDEN_LEGAL_PHRASES = (
    "vai acontecer",
    "deve acontecer",
    "tem chance de ganhar",
    "tem chance de perder",
)
MAX_RESPONSE_LENGTH = 3000


def create_user_response(
    message: str,
    analysis_data: dict,
    progress_reporter: ProgressReporter | None = None,
) -> str:
    normalized = _normalize_analysis(analysis_data)
    safe_message = _string_value(message)

    if _requires_deterministic_response(normalized):
        report_progress(
            progress_reporter,
            code="response.local",
            level="success",
            message="resposta final montada por regras locais.",
            details={
                "response_mode": "local",
                "uses_model": False,
            },
        )
        return _fallback_response(normalized, safe_message)

    if not _ollama_rewrite_enabled():
        report_progress(
            progress_reporter,
            code="response.local",
            level="success",
            message="resposta final montada por regras locais.",
            details={
                "response_mode": "local",
                "uses_model": False,
            },
        )
        return _fallback_response(normalized, safe_message)

    model_started_at = progress_clock()
    try:
        prompt = build_agent4_prompt(
            message=safe_message,
            analysis_type=normalized["analysis_type"],
            question_focus=normalized["question_focus"],
            target_event=normalized["target_event"],
            facts=_facts_for_prompt(normalized["facts"]),
            explanation=normalized["explanation"],
            limitations=normalized["limitations"],
            response_focus=normalized["response_focus"],
        )
        report_progress(
            progress_reporter,
            code="response.model.started",
            level="started",
            message="consultando modelo local para redigir a resposta...",
            details={"uses_model": True},
        )
        response = generate_text(prompt, system_prompt=AGENT4_SYSTEM_PROMPT)
        validated_response = _validate_model_response(response)
        report_progress(
            progress_reporter,
            code="response.model.finished",
            level="success",
            message="modelo local retornou a resposta final.",
            details={"uses_model": True},
            started_at=model_started_at,
        )
        return validated_response
    except (OllamaError, ValueError, TypeError) as exc:
        report_progress(
            progress_reporter,
            code="response.model.fallback",
            level="warning",
            message="modelo local indisponivel para redacao; usando resposta segura.",
            details={
                "fallback": True,
                "error_type": type(exc).__name__,
            },
            started_at=model_started_at,
        )
        return _fallback_response(normalized, safe_message)


def _requires_deterministic_response(analysis: dict) -> bool:
    return analysis["analysis_type"] == "greeting" or analysis["question_focus"] in {
        "case_value",
        "current_status",
        "earliest_movement",
        "first_and_latest_movement",
        "latest_movement",
        "movement_list",
        "movement_timeline",
        "parties",
        "pending_issues",
        "process_overview",
        "structured_field",
        "timeline_before_event",
    }


def _ollama_rewrite_enabled() -> bool:
    value = os.getenv("AGENT4_USE_OLLAMA", "")
    return value.strip().lower() in {"1", "true", "yes", "sim"}


def _normalize_analysis(analysis_data: dict) -> dict:
    if not isinstance(analysis_data, dict):
        analysis_data = {}

    analysis_type = analysis_data.get("analysis_type")
    if analysis_type not in ALLOWED_ANALYSIS_TYPES:
        analysis_type = "unclear"

    facts = []
    raw_facts = analysis_data.get("facts")
    if isinstance(raw_facts, list):
        for fact in raw_facts:
            if not isinstance(fact, dict):
                continue

            label = _safe_text(fact.get("label"))
            value = _safe_text(fact.get("value"))
            if label and value:
                facts.append({"label": label, "value": value})

    limitations = []
    raw_limitations = analysis_data.get("limitations")
    if isinstance(raw_limitations, list):
        limitations = [
            text for text in (_safe_text(item) for item in raw_limitations) if text
        ]

    return {
        "analysis_type": analysis_type,
        "question_focus": _normalize_question_focus(
            analysis_data.get("question_focus")
        ),
        "target_event": _normalize_target_event(analysis_data.get("target_event")),
        "facts": facts,
        "explanation": _safe_text(analysis_data.get("explanation")),
        "limitations": limitations,
        "response_focus": _safe_text(analysis_data.get("response_focus")),
    }


def _normalize_question_focus(value: Any) -> str:
    if isinstance(value, str) and value.strip() in ALLOWED_QUESTION_FOCUS:
        return value.strip()
    return DEFAULT_QUESTION_FOCUS


def _normalize_target_event(value: Any) -> str | None:
    if value is None:
        return None
    text = _safe_text(value)
    return text or None


def _facts_for_prompt(facts: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "label": fact["label"],
            "value": fact["value"],
        }
        for fact in facts
    ]


def _validate_model_response(response: str) -> str:
    text = _string_value(response)
    if not text:
        raise ValueError("Resposta vazia.")

    if text.startswith("{") or text.startswith("[") or "```" in text:
        raise ValueError("Resposta em formato invalido.")

    if len(text) > MAX_RESPONSE_LENGTH:
        raise ValueError("Resposta longa demais.")

    if _contains_internal_terms(text):
        raise ValueError("Resposta menciona detalhe interno.")

    if _contains_user_invisible_reference(text):
        raise ValueError("Resposta menciona referencia interna.")

    if _contains_privacy_details(text):
        raise ValueError("Resposta menciona detalhe de privacidade.")

    if _contains_private_document(text):
        raise ValueError("Resposta contem documento pessoal.")

    lowered = text.lower()
    if any(phrase in lowered for phrase in FORBIDDEN_LEGAL_PHRASES):
        raise ValueError("Resposta contem previsao ou aconselhamento indevido.")

    return text


def _fallback_response(analysis: dict, message: str = "") -> str:
    analysis_type = analysis["analysis_type"]

    if analysis_type == "greeting":
        if _is_thanks_message(message):
            return (
                "De nada! Estou à disposição para ajudar com informações do processo."
            )
        return (
            "Olá! Posso ajudar a consultar informações de um processo ou explicar "
            "termos processuais."
        )

    if analysis_type == "out_of_scope":
        return (
            "Posso ajudar com informações e explicações sobre processos e termos "
            "processuais. Sobre esse assunto, não tenho como orientar por aqui."
        )

    if analysis_type == "unclear":
        return (
            "Não consegui identificar a que informação você se refere. Você pode "
            "explicar um pouco mais ou informar o número do processo?"
        )

    if analysis_type == "missing_process_context":
        return (
            "Para responder sobre um processo específico, preciso que você consulte "
            "ou informe o número completo do processo."
        )

    if analysis_type == "insufficient_data":
        return _compose_insufficient_data_response(analysis)

    question_focus = analysis["question_focus"]
    if question_focus == "process_overview":
        return _compose_process_overview_response(analysis)

    if question_focus == "current_status":
        return _compose_current_status_response(analysis)

    if question_focus == "parties":
        return _compose_parties_response(analysis)

    if question_focus == "pending_issues":
        return _compose_pending_issues_response(analysis)

    if question_focus == "timeline_before_event":
        return _compose_timeline_before_event_response(analysis)

    if question_focus == "latest_movement":
        return _compose_latest_movement_response(analysis)

    if question_focus == "earliest_movement":
        return _compose_earliest_movement_response(analysis)

    if question_focus == "first_and_latest_movement":
        return _compose_first_and_latest_movement_response(analysis)

    if question_focus == "movement_list":
        return _compose_movement_list_response(analysis)

    if question_focus == "movement_timeline":
        return _compose_movement_timeline_response(analysis)

    if question_focus == "legal_concept_with_case_context":
        return _compose_legal_concept_with_case_context_response(analysis)

    if question_focus == "document_content":
        return _compose_document_content_response(analysis)

    if question_focus == "case_value":
        return _compose_case_value_response(analysis)

    if question_focus == "structured_field":
        return _compose_structured_field_response(analysis)

    if (
        question_focus == "generic_process_question"
        and analysis_type in {"process_summary", "process_question"}
    ):
        return _compose_generic_process_question_response(analysis)

    if analysis_type == "legal_general_explanation":
        return _compose_legal_general_response(analysis)

    return _compose_process_response(analysis)


def _compose_process_overview_response(analysis: dict) -> str:
    facts = analysis["facts"]
    parts = []

    situation = _fact_value_by_label(facts, "situacao", "processual")
    if situation:
        parts.append(f"O processo consta como {situation}.")

    second_paragraph = []
    latest = _movement_sentence(
        _fact_by_label(facts, "ultima", "movimentacao"),
        'A última movimentação registrada é',
    )
    if latest:
        second_paragraph.append(latest)

    context = _overview_context_sentence(facts)
    if context:
        second_paragraph.append(context)

    if second_paragraph:
        parts.append(" ".join(second_paragraph))

    return _join_parts_or_default(parts)


def _compose_current_status_response(analysis: dict) -> str:
    facts = analysis["facts"]
    parts = []

    situation = _fact_value_by_label(facts, "situacao", "processual")
    if situation:
        parts.append(f"Nos dados consultados, o processo consta como {situation}.")

    latest = _movement_sentence(
        _fact_by_label(facts, "ultima", "movimentacao"),
        'A última movimentação registrada é',
    )
    if latest:
        parts.append(latest)

    return _join_parts_or_default([" ".join(parts)])


def _compose_parties_response(analysis: dict) -> str:
    party_lines = []
    for fact in analysis["facts"]:
        party_lines.extend(_extract_party_lines(fact))

    party_lines = _unique_lines(party_lines)
    if party_lines:
        return "As partes registradas são:\n\n" + "\n".join(party_lines)

    return "Não há partes registradas nos dados consultados."


def _compose_pending_issues_response(analysis: dict) -> str:
    pending_lines = []
    has_no_pending_record = False

    for fact in analysis["facts"]:
        value = _humanize_fact_value(fact["value"])
        if not value:
            continue

        normalized_value = _normalize_for_match(value)
        if _is_no_pending_text(normalized_value):
            has_no_pending_record = True
            continue

        if "pendencia" in _normalize_for_match(fact["label"]) or "pendencia" in normalized_value:
            pending_lines.append("- " + _ensure_sentence(value))

    pending_lines = _unique_lines(pending_lines)
    if pending_lines:
        return "Pendências registradas:\n\n" + "\n".join(pending_lines)

    if has_no_pending_record or not analysis["facts"]:
        response = "Nos dados consultados, não há pendências registradas."
        if analysis["limitations"]:
            response += (
                "\n\nIsso não confirma, por si só, a inexistência de qualquer "
                "pendência fora das informações disponíveis."
            )
        return response

    return "Não há informação suficiente disponível para responder sobre pendências."


def _compose_case_value_response(analysis: dict) -> str:
    value = _fact_value_by_label(analysis["facts"], "valor", "causa")
    if value:
        return f"O valor da causa informado é {value}."

    return "Não há valor da causa informado nos dados consultados."


def _compose_structured_field_response(analysis: dict) -> str:
    fact_lines = _format_fact_lines(analysis["facts"])
    if fact_lines:
        return "\n".join(fact_lines)

    return _join_parts_or_default([analysis["explanation"]])


def _compose_timeline_before_event_response(analysis: dict) -> str:
    fact = _fact_by_label(analysis["facts"], "movimentacao", "anterior")
    movement = _parse_movement_fact(fact["value"]) if fact else {}
    description = movement.get("description", "")
    if not description:
        return _join_parts_or_default([analysis["explanation"]])

    target_event = analysis.get("target_event") or "evento solicitado"
    prefix = _before_event_prefix(target_event)
    sentence = f"{prefix}, há registro de \"{description}\""

    date = movement.get("date", "")
    if date:
        sentence += f" em {date}"

    complement = movement.get("complement", "")
    if complement:
        sentence += f", com o complemento \"{complement}\""

    return _ensure_sentence(sentence)


def _compose_latest_movement_response(analysis: dict) -> str:
    fact = _fact_by_label(analysis["facts"], "ultima", "movimentacao")
    movement = _parse_movement_fact(fact["value"]) if fact else {}
    description = movement.get("description", "")
    if not description:
        return _join_parts_or_default([analysis["explanation"]])

    sentence = f'A ultima movimentacao disponivel e "{description}"'
    date = movement.get("date", "")
    if date:
        sentence += f", em {date}"

    complement = movement.get("complement", "")
    if complement:
        sentence += f', com o complemento "{complement}"'

    return _ensure_sentence(sentence)


def _compose_earliest_movement_response(analysis: dict) -> str:
    fact = (
        _fact_by_label(analysis["facts"], "primeira", "movimentacao")
        or _fact_by_label(analysis["facts"], "movimentacao", "antiga")
    )
    movement = _parse_movement_fact(fact["value"]) if fact else {}
    description = movement.get("description", "")
    if not description:
        return _join_parts_or_default([analysis["explanation"]])

    sentence = f'A movimentação mais antiga disponível é "{description}"'
    date = movement.get("date", "")
    if date:
        sentence += f", em {date}"

    complement = movement.get("complement", "")
    if complement:
        sentence += f', com o complemento "{complement}"'

    return _ensure_sentence(sentence)


def _compose_first_and_latest_movement_response(analysis: dict) -> str:
    first_fact = (
        _fact_by_label(analysis["facts"], "primeira", "movimentacao")
        or _fact_by_label(analysis["facts"], "movimentacao", "antiga")
    )
    latest_fact = _fact_by_label(analysis["facts"], "ultima", "movimentacao")

    lines = []
    first_line = _movement_labeled_line(first_fact, "Primeira")
    if first_line:
        lines.append(first_line)

    latest_line = _movement_labeled_line(latest_fact, "Ultima")
    if latest_line:
        lines.append(latest_line)

    if lines:
        return "\n".join(lines)

    return _join_parts_or_default([analysis["explanation"]])


def _compose_movement_list_response(analysis: dict) -> str:
    lines = _movement_fact_lines(analysis["facts"])
    if not lines:
        return _join_parts_or_default([analysis["explanation"]])

    parts = ["Movimentacoes:\n\n" + "\n".join(lines)]
    limitation_text = _movement_cap_limitations_text(analysis["limitations"])
    if limitation_text:
        parts.append(limitation_text)
    return "\n\n".join(parts)


def _compose_movement_timeline_response(analysis: dict) -> str:
    lines = _movement_fact_lines(analysis["facts"])
    if not lines:
        return _join_parts_or_default([analysis["explanation"]])

    return "Linha do tempo do processo:\n\n" + "\n".join(lines)


def _movement_fact_lines(facts: list[dict[str, str]]) -> list[str]:
    lines = []
    for fact in facts:
        line = _movement_labeled_line(fact, fact["label"])
        if line:
            lines.append(line)
    return lines


def _movement_cap_limitations_text(limitations: list[str]) -> str:
    relevant = []
    for limitation in limitations:
        normalized = _normalize_for_match(limitation)
        if "foram listadas" in normalized or "maximo" in normalized:
            relevant.append(limitation)
    return _important_limitations_text(relevant)


def _movement_labeled_line(fact: dict[str, str] | None, label: str) -> str:
    movement = _parse_movement_fact(fact["value"]) if fact else {}
    description = movement.get("description", "")
    if not description:
        return ""

    line = f'- {label}: "{description}"'
    date = movement.get("date", "")
    if date:
        line += f", em {date}"

    complement = movement.get("complement", "")
    if complement:
        line += f', com o complemento "{complement}"'

    return _ensure_sentence(line)


def _compose_legal_concept_with_case_context_response(analysis: dict) -> str:
    parts = []
    if analysis["explanation"]:
        parts.append(f"De forma geral, {_lower_first(_ensure_sentence(analysis['explanation']))}")

    fact = _fact_by_label(analysis["facts"], "movimentacao", "relacionada")
    movement = _parse_movement_fact(fact["value"]) if fact else {}
    description = movement.get("description", "")
    if description:
        sentence = f"Neste processo, há uma movimentação registrada como \"{description}\""
        date = movement.get("date", "")
        if date:
            sentence += f" em {date}"
        complement = movement.get("complement", "")
        if complement:
            sentence += f", com o complemento \"{complement}\""
        parts.append(_ensure_sentence(sentence))
    else:
        fact_lines = _format_fact_lines(analysis["facts"])
        if fact_lines:
            parts.append("Neste processo, há estes dados relacionados:\n" + "\n".join(fact_lines))

    return _join_parts_or_default(parts)


def _compose_document_content_response(analysis: dict) -> str:
    recovered_text_lines = _retrieved_text_lines(analysis["facts"])
    if recovered_text_lines:
        response = "Encontrei estes trechos textuais relacionados:\n\n"
        response += "\n".join(recovered_text_lines)
        response += (
            "\n\nA resposta deve ficar limitada a esses trechos; eles nÃ£o autorizam "
            "conclusÃµes alÃ©m do texto recuperado."
        )
        return response

    record = _document_record_sentence(analysis["facts"])
    if not record:
        record = _movement_record_sentence(
            _fact_by_label(analysis["facts"], "movimentacao", "sentenca")
        )

    limitation = (
        "mas o teor da decisão não foi disponibilizado. Por isso, não é possível "
        "informar o que foi decidido ou para quem a sentença foi favorável."
    )

    if record:
        return f"{record}, {limitation}"

    return (
        "O teor da decisão não foi disponibilizado. Por isso, não é possível "
        "informar o que foi decidido ou para quem a sentença foi favorável."
    )


def _retrieved_text_lines(facts: list[dict[str, str]]) -> list[str]:
    lines = []
    for fact in facts:
        label = _normalize_for_match(fact["label"])
        if "trecho" not in label or "textual" not in label:
            continue

        value = _sanitize_visible_text(fact["value"])
        if not value:
            continue

        if len(value) > 700:
            value = value[:700].rstrip() + "..."
        lines.append(f"- \"{value}\"")

    return _unique_lines(lines)


def _compose_generic_process_question_response(analysis: dict) -> str:
    facts = analysis["facts"]
    parts = []

    situation = _fact_value_by_label(facts, "situacao", "processual")
    if situation:
        parts.append(f"Com as informações disponíveis, o processo consta como {situation}.")

    latest = _movement_sentence(
        _fact_by_label(facts, "ultima", "movimentacao"),
        'A última movimentação registrada é',
    )
    if latest:
        parts.append(latest)

    if parts:
        parts.append(
            "Para detalhar melhor, indique se quer saber sobre partes, movimentações, pendências ou documentos."
        )

    return _join_parts_or_default(parts)


def _compose_process_response(analysis: dict) -> str:
    parts = []
    if analysis["explanation"]:
        parts.append(_ensure_sentence(analysis["explanation"]))

    latest_movement_text = ""
    if analysis["analysis_type"] in {"process_summary", "process_question"}:
        latest_movement_text = _latest_movement_text(analysis["facts"])
        if latest_movement_text:
            parts.append(latest_movement_text)

    fact_lines = _format_fact_lines(
        analysis["facts"],
        skip_latest_movement=bool(latest_movement_text),
    )
    if fact_lines:
        parts.append("\n".join(fact_lines))

    limitation_text = _important_limitations_text(analysis["limitations"])
    if limitation_text:
        parts.append(limitation_text)

    return _join_parts_or_default(parts)


def _compose_legal_general_response(analysis: dict) -> str:
    parts = []
    if analysis["explanation"]:
        parts.append(f"De forma geral, {_lower_first(_ensure_sentence(analysis['explanation']))}")

    fact_lines = _format_fact_lines(analysis["facts"])
    if fact_lines:
        parts.append("No processo consultado, há estes dados relacionados:\n" + "\n".join(fact_lines))

    limitation_text = _important_limitations_text(analysis["limitations"])
    if limitation_text:
        parts.append(limitation_text)

    return _join_parts_or_default(parts)


def _compose_insufficient_data_response(analysis: dict) -> str:
    parts = []
    if analysis["explanation"]:
        parts.append(_ensure_sentence(analysis["explanation"]))

    limitation_text = _important_limitations_text(analysis["limitations"])
    if limitation_text:
        parts.append(limitation_text)

    if not parts:
        parts.append(
            "Não há informação suficiente disponível para responder a essa pergunta."
        )

    return "\n\n".join(parts)


def _fact_by_label(
    facts: list[dict[str, str]],
    *terms: str,
) -> dict[str, str] | None:
    normalized_terms = [_normalize_for_match(term) for term in terms if term]
    for fact in facts:
        label = _normalize_for_match(fact["label"])
        if all(term in label for term in normalized_terms):
            return fact
    return None


def _fact_value_by_label(
    facts: list[dict[str, str]],
    *terms: str,
) -> str:
    fact = _fact_by_label(facts, *terms)
    if not fact:
        return ""
    return _sanitize_visible_text(fact["value"])


def _overview_context_sentence(facts: list[dict[str, str]]) -> str:
    subject = _fact_value_by_label(facts, "assunto")
    if subject:
        return f"O assunto registrado é {subject}."

    court = _fact_value_by_label(facts, "orgao", "julgador")
    if court:
        return f"O órgão julgador registrado é {court}."

    return ""


def _movement_sentence(fact: dict[str, str] | None, prefix: str) -> str:
    if not fact:
        return ""

    movement = _parse_movement_fact(fact["value"])
    description = movement.get("description", "")
    if not description:
        return ""

    sentence = f'{prefix} "{description}"'
    date = movement.get("date", "")
    if date:
        sentence += f", em {date}"
    return _ensure_sentence(sentence)


def _before_event_prefix(target_event: str) -> str:
    normalized = _normalize_for_match(target_event)
    article = "da" if normalized in {"sentenca", "audiencia", "distribuicao"} else "do"
    return f"Antes {article} {target_event}"


def _document_record_sentence(facts: list[dict[str, str]]) -> str:
    fact = _fact_by_label(facts, "documento")
    if not fact:
        return ""

    fields = _parse_labeled_fields(fact["value"])
    title = fields.get("titulo", "")
    document_type = fields.get("tipo", "")
    date = _movement_date(_sanitize_visible_text(fact["value"]))

    parts = ["Há documento de sentença registrado"]
    if date:
        parts.append(f"em {date}")

    details = []
    if title:
        details.append(f"título {title}")
    if document_type:
        details.append(f"tipo {document_type}")
    if details:
        parts.append("com " + " e ".join(details))

    return " ".join(parts)


def _movement_record_sentence(fact: dict[str, str] | None) -> str:
    if not fact:
        return ""

    movement = _parse_movement_fact(fact["value"])
    description = movement.get("description", "")
    if not description:
        return ""

    sentence = f'Há movimentação de sentença registrada como "{description}"'
    date = movement.get("date", "")
    if date:
        sentence += f", em {date}"
    return sentence


def _parse_labeled_fields(value: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    text = _sanitize_visible_text(value)
    for segment in re.split(r"\s*[|;]\s*", text):
        segment = _clean_visible_text(segment)
        if not segment:
            continue

        label_match = re.match(r"^([a-zA-ZÀ-ÿ_ ]+):\s*(.+)$", segment)
        if not label_match:
            continue

        label = _normalize_for_match(label_match.group(1))
        fields[label] = _clean_visible_text(label_match.group(2))

    return fields


def _format_fact_lines(
    facts: list[dict[str, str]],
    *,
    skip_latest_movement: bool = False,
) -> list[str]:
    party_lines = []
    regular_lines = []

    for fact in facts:
        if skip_latest_movement and _is_latest_movement_label(fact["label"]):
            continue

        extracted_party_lines = _extract_party_lines(fact)
        if extracted_party_lines:
            party_lines.extend(extracted_party_lines)
            continue

        if _is_collection_status_label(fact["label"]):
            continue

        value = _humanize_fact_value(fact["value"])
        if value:
            regular_lines.append(f"{fact['label']}: {_ensure_sentence(value)}")

    lines = []
    if party_lines:
        lines.append("As partes registradas são:\n\n" + "\n".join(_unique_lines(party_lines)))

    lines.extend(regular_lines)
    return lines


def _latest_movement_text(facts: list[dict[str, str]]) -> str:
    for fact in facts:
        if not _is_latest_movement_label(fact["label"]):
            continue

        movement = _parse_movement_fact(fact["value"])
        description = movement.get("description", "")
        if not description:
            return ""

        date = movement.get("date", "")
        if date:
            return f'A última movimentação disponível é "{description}", em {date}.'
        return f'A última movimentação disponível é "{description}".'

    return ""


def _is_latest_movement_label(label: str) -> bool:
    normalized = _normalize_for_match(label)
    return "ultima" in normalized and "movimentacao" in normalized


def _parse_movement_fact(value: str) -> dict[str, str]:
    text = _sanitize_visible_text(value)
    date = _movement_date(text)
    description = ""
    complement = ""

    for segment in re.split(r"\s*[|;]\s*", text):
        segment = _clean_visible_text(segment)
        if not segment:
            continue

        label_match = re.match(r"^([a-zA-ZÀ-ÿ_ ]+):\s*(.+)$", segment)
        if label_match:
            label = _normalize_for_match(label_match.group(1))
            content = _clean_visible_text(label_match.group(2))
            if label == "complemento":
                complement = content
                continue
            if label in {"ordem", "data", "referencia"}:
                continue
            if label == "descricao" and content:
                if not description:
                    description = content
                continue

        if re.match(r"^(ordem|data|complemento|referencia)\s*:", segment, re.IGNORECASE):
            continue

        if not description:
            description = segment

    return {
        "description": description,
        "date": date,
        "complement": complement,
    }


def _movement_date(text: str) -> str:
    iso_match = re.search(r"\bdata:\s*(\d{4})-(\d{2})-(\d{2})\b", text, re.IGNORECASE)
    if iso_match:
        return f"{iso_match.group(3)}/{iso_match.group(2)}/{iso_match.group(1)}"

    br_match = re.search(r"\bdata:\s*(\d{2}/\d{2}/\d{4})\b", text, re.IGNORECASE)
    if br_match:
        return br_match.group(1)

    return ""


def _humanize_fact_value(value: str) -> str:
    text = _sanitize_visible_text(value)
    text = re.sub(r"\bordem:\s*\d+\s*\|\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\bdata:\s*(\d{4})-(\d{2})-(\d{2})\b",
        lambda match: f"data: {match.group(3)}/{match.group(2)}/{match.group(1)}",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*\|\s*", "; ", text).strip()
    text = _clean_visible_text(text)
    return text


def _extract_party_lines(fact: dict[str, str]) -> list[str]:
    label = fact["label"]
    value = fact["value"]
    if not _is_party_fact(label, value):
        return []

    parsed_lines = []
    records = _party_records(value)
    for record in records:
        fields = {
            key.lower(): _sanitize_party_field(raw_value)
            for key, raw_value in PARTY_FIELD_RE.findall(record)
        }
        name = fields.get("nome", "")
        if not name:
            continue

        party_type = fields.get("tipo") or fields.get("polo")
        if party_type:
            parsed_lines.append(f"- {_human_party_type(party_type)}: {name}")

    if parsed_lines:
        return parsed_lines

    label_party_line = _party_line_from_label_and_value(label, value)
    if label_party_line:
        return [label_party_line]

    simple_lines = []
    for record in records:
        match = SIMPLE_PARTY_RE.match(record)
        if not match:
            continue

        party_type = _sanitize_party_field(match.group(1))
        name = _sanitize_party_field(match.group(2))
        if party_type and name:
            simple_lines.append(f"- {_human_party_type(party_type)}: {name}")

    return simple_lines


def _is_party_fact(label: str, value: str) -> bool:
    return bool(PARTY_LABEL_RE.search(label) or PARTY_FIELD_RE.search(value))


def _party_records(value: str) -> list[str]:
    normalized = _sanitize_visible_text(value)
    records = []
    for line in normalized.splitlines():
        line = line.strip(" -;\t")
        if line:
            records.append(line)

    if records:
        return records

    return [part.strip(" -;\t") for part in normalized.split(";") if part.strip()]


def _party_line_from_label_and_value(label: str, value: str) -> str:
    party_type = _party_type_from_label(label)
    if not party_type:
        return ""

    name = _name_from_party_value(value)
    if not name:
        return ""

    return f"- {party_type}: {name}"


def _party_type_from_label(label: str) -> str:
    text = _sanitize_party_field(label)
    if SIMPLE_PARTY_LABEL_RE.match(text):
        return _human_party_type(text)
    normalized = _normalize_for_match(text)
    if normalized in {"ativo", "passivo"}:
        return _human_party_type(text)
    return ""


def _name_from_party_value(value: str) -> str:
    text = _sanitize_visible_text(value)
    text = PARTY_METADATA_START_RE.split(text, maxsplit=1)[0]
    return _sanitize_party_field(text)


def _sanitize_party_field(value: str) -> str:
    text = _sanitize_visible_text(value)
    text = re.sub(r"\s+", " ", text).strip(" -;,.")
    return text


def _human_party_type(value: str) -> str:
    text = _sanitize_party_field(value)
    normalized = _normalize_for_match(text)
    if normalized == "ativo":
        return "Reclamante"
    if normalized == "passivo":
        return "Reclamado"
    return text


def _is_no_pending_text(normalized_text: str) -> bool:
    return any(
        phrase in normalized_text
        for phrase in (
            "nenhuma pendencia",
            "nao ha pendencia",
            "nao ha pendencias",
            "nao registraram pendencias",
            "sem pendencias",
        )
    )


def _unique_lines(lines: list[str]) -> list[str]:
    unique = []
    seen = set()
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        unique.append(line)
    return unique


def _important_limitations_text(limitations: list[str]) -> str:
    if not limitations:
        return ""

    return "Limitação: " + " ".join(_ensure_sentence(item) for item in limitations)


def _join_parts_or_default(parts: list[str]) -> str:
    response = "\n\n".join(part for part in parts if part.strip()).strip()
    if response:
        return response

    return (
        "Não há informação suficiente disponível para responder a essa pergunta "
        "com segurança."
    )


def _safe_text(value: Any) -> str:
    text = _string_value(value)
    if not text:
        return ""

    text = text.replace("```", "").strip()
    text = _sanitize_visible_text(text)
    if _contains_internal_terms(text):
        return ""

    if _contains_privacy_details(text):
        return ""

    return text


def _is_thanks_message(message: str) -> bool:
    tokens = re.findall(r"[a-z0-9]+", _normalize_for_match(message))
    token_set = set(tokens)
    allowed_tokens = {
        "a",
        "agradeco",
        "agradecida",
        "agradecido",
        "ajuda",
        "demais",
        "grata",
        "grato",
        "muito",
        "obrigada",
        "obrigado",
        "pela",
        "pelo",
        "perfeito",
        "valeu",
    }
    anchors = {
        "agradeco",
        "agradecida",
        "agradecido",
        "grata",
        "grato",
        "obrigada",
        "obrigado",
        "valeu",
    }
    return 0 < len(tokens) <= 7 and token_set <= allowed_tokens and bool(
        token_set & anchors
    )


def _string_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _ensure_sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    if text.endswith((".", "!", "?")):
        return text
    return f"{text}."


def _lower_first(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def _contains_internal_terms(text: str) -> bool:
    return bool(
        INTERNAL_TERM_RE.search(text)
        or INTERNAL_FIELD_RE.search(text)
        or INTERNAL_PATH_RE.search(text)
        or TECHNICAL_IDENTIFIER_RE.search(text)
    )


def _contains_user_invisible_reference(text: str) -> bool:
    return bool(USER_INVISIBLE_REFERENCE_RE.search(text))


def _contains_privacy_details(text: str) -> bool:
    return bool(PRIVACY_DETAIL_RE.search(text))


def _contains_private_document(text: str) -> bool:
    return bool(PRIVATE_DOCUMENT_RE.search(text))


def _is_collection_status_label(text: str) -> bool:
    return bool(COLLECTION_STATUS_LABEL_RE.search(text))


def _redact_private_documents(text: str) -> str:
    return PRIVATE_DOCUMENT_RE.sub("[documento pessoal omitido]", text)


def _sanitize_visible_text(text: str) -> str:
    text = _redact_private_documents(text)
    text = COLLECTION_SUMMARY_RE.sub(
        lambda match: f"Encontrei informações para o processo {match.group(1)}.",
        text,
    )
    text = USER_INVISIBLE_SENTENCE_RE.sub("", text)
    text = PRIVATE_FIELD_SEGMENT_RE.sub("", text)
    text = DOCUMENT_ID_SEGMENT_RE.sub("", text)
    text = PRIVACY_SENTENCE_RE.sub("", text)
    text = text.replace("[documento pessoal omitido]", "")
    text = re.sub(
        r"\bA coleta registra\b",
        "Os dados consultados registram",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bA coleta n[aã]o registrou\b",
        "Os dados consultados não registraram",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bmas n[aã]o disponibiliza\b",
        "mas não disponibilizam",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bna coleta\b", "nos dados consultados", text, flags=re.IGNORECASE)
    text = re.sub(r"\bda coleta\b", "dos dados consultados", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\bcoleta dispon[ií]vel\b",
        "consulta disponível",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bdos dados consultados dispon[ií]vel\b",
        "da consulta disponível",
        text,
        flags=re.IGNORECASE,
    )
    return _clean_visible_text(text)


def _clean_visible_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([.;,:])", r"\1", text)
    text = re.sub(r"(?:\s*;\s*){2,}", "; ", text)
    text = re.sub(r"^\s*[;|]\s*", "", text)
    text = re.sub(r"\s*[;|]\s*$", "", text)
    return text.strip()


def _normalize_for_match(text: str) -> str:
    lowered = _string_value(text).lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    ).strip()
