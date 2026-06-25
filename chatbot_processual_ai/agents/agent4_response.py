import os
import re
from typing import Any

from ollama_client import OllamaError, generate_text
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
INTERNAL_TERM_RE = re.compile(
    r"\b(agente|json|prompt|ollama|modelo|pipeline)\b|"
    r"coleta\s+(?:interna|local)|dados\s+estruturados|detalhes?\s+t[eé]cnicos?",
    re.IGNORECASE,
)
PRIVATE_DOCUMENT_RE = re.compile(
    r"(?<!\d)(?:\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})(?!\d)"
)
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
) -> str:
    normalized = _normalize_analysis(analysis_data)

    if not _ollama_rewrite_enabled():
        return _fallback_response(normalized)

    try:
        prompt = build_agent4_prompt(
            message=_string_value(message),
            analysis_type=normalized["analysis_type"],
            facts=_facts_for_prompt(normalized["facts"]),
            explanation=normalized["explanation"],
            limitations=normalized["limitations"],
            response_focus=normalized["response_focus"],
        )
        response = generate_text(prompt, system_prompt=AGENT4_SYSTEM_PROMPT)
        return _validate_model_response(response)
    except (OllamaError, ValueError, TypeError):
        return _fallback_response(normalized)


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
        "facts": facts,
        "explanation": _safe_text(analysis_data.get("explanation")),
        "limitations": limitations,
        "response_focus": _safe_text(analysis_data.get("response_focus")),
    }


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


def _fallback_response(analysis: dict) -> str:
    analysis_type = analysis["analysis_type"]

    if analysis_type == "greeting":
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

    if analysis_type == "legal_general_explanation":
        return _compose_legal_general_response(analysis)

    return _compose_process_response(analysis)


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
            return f"A última movimentação disponível é “{description}”, em {date}."
        return f"A última movimentação disponível é “{description}”."

    return ""


def _is_latest_movement_label(label: str) -> bool:
    normalized = _normalize_for_match(label)
    return "ultima" in normalized and "movimentacao" in normalized


def _parse_movement_fact(value: str) -> dict[str, str]:
    text = _sanitize_visible_text(value)
    date = _movement_date(text)
    description = ""

    for segment in re.split(r"\s*[|;]\s*", text):
        segment = _clean_visible_text(segment)
        if not segment:
            continue

        label_match = re.match(r"^([a-zA-ZÀ-ÿ_ ]+):\s*(.+)$", segment)
        if label_match:
            label = _normalize_for_match(label_match.group(1))
            content = _clean_visible_text(label_match.group(2))
            if label in {"ordem", "data", "complemento", "referencia"}:
                continue
            if label == "descricao" and content:
                description = content
                break

        if re.match(r"^(ordem|data|complemento|referencia)\s*:", segment, re.IGNORECASE):
            continue

        description = segment
        break

    return {
        "description": description,
        "date": date,
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
            parsed_lines.append(f"- {party_type}: {name}")

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
            simple_lines.append(f"- {party_type}: {name}")

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
        return text
    return ""


def _name_from_party_value(value: str) -> str:
    text = _sanitize_visible_text(value)
    text = PARTY_METADATA_START_RE.split(text, maxsplit=1)[0]
    return _sanitize_party_field(text)


def _sanitize_party_field(value: str) -> str:
    text = _sanitize_visible_text(value)
    text = re.sub(r"\s+", " ", text).strip(" -;,.")
    return text


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
    return bool(INTERNAL_TERM_RE.search(text))


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
    replacements = str.maketrans(
        {
            "á": "a",
            "à": "a",
            "â": "a",
            "ã": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ü": "u",
            "ç": "c",
            "Á": "a",
            "À": "a",
            "Â": "a",
            "Ã": "a",
            "É": "e",
            "Ê": "e",
            "Í": "i",
            "Ó": "o",
            "Ô": "o",
            "Õ": "o",
            "Ú": "u",
            "Ü": "u",
            "Ç": "c",
        }
    )
    return text.translate(replacements).lower().strip()
