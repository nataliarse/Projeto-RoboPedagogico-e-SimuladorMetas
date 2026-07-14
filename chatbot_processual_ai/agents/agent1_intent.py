import json
import re
import unicodedata
from typing import Any

from ollama_client import OllamaError, generate_text
from progress import ProgressReporter, progress_clock, report_progress
from prompts.agent1_prompt import AGENT1_SYSTEM_PROMPT, build_agent1_prompt
from services.process_query_resolver import (
    SCOPE_GENERAL,
    TARGET_GENERIC_PROCESS,
    TARGET_LEGAL_CONCEPT,
    is_document_content_spec,
    is_structured_process_spec,
    resolve_process_query,
)


ALLOWED_INTENTS = {
    "greeting",
    "process_lookup",
    "process_question",
    "legal_general_question",
    "out_of_scope",
    "unclear",
}
ALLOWED_CONFIDENCES = {"high", "medium", "low"}
FALLBACK_GOAL = "Nao foi possivel interpretar a mensagem automaticamente."
LIMITED_GOAL = "Necessidade do usuario identificada de forma limitada."
THANKS_GOAL = "Agradecimento ou encerramento positivo da interação."
MAX_USER_GOAL_LENGTH = 180

_PROCESS_NUMBER_CANDIDATE_RE = re.compile(r"\d(?:[\d\s.\-/]*\d)?")
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_LOOKUP_ACTION_RE = re.compile(
    r"\b("
    r"acompanhar|acompanhe|"
    r"buscar|busca|busque|"
    r"checar|cheque|"
    r"consultar|consulta|consulte|"
    r"localizar|localize|"
    r"verificar|verifique"
    r")\b"
)

_PLACEHOLDER_GOALS = {
    "resumo curto da necessidade do usuario",
    "<objetivo concreto em poucas palavras>",
}
_GREETING_TOKENS = {
    "ajuda",
    "ai",
    "ate",
    "bem",
    "boa",
    "bom",
    "como",
    "dia",
    "e",
    "mais",
    "noite",
    "obrigada",
    "obrigado",
    "oi",
    "ola",
    "pela",
    "por",
    "tarde",
    "tchau",
    "tudo",
    "valeu",
    "vai",
    "voce",
}
_GREETING_ANCHORS = {
    "ai",
    "ate",
    "boa",
    "bom",
    "obrigada",
    "obrigado",
    "oi",
    "ola",
    "tchau",
    "valeu",
}
_THANKS_TOKENS = {
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
_THANKS_ANCHORS = {
    "agradeco",
    "agradecida",
    "agradecido",
    "grata",
    "grato",
    "obrigada",
    "obrigado",
    "valeu",
}
_PROCESS_LOOKUP_CONTEXT = {
    "andamento",
    "autos",
    "caso",
    "processo",
    "situacao",
}
_LEGAL_GENERAL_TERMS = {
    "arquivamento",
    "audiencia",
    "causa",
    "definitivo",
    "despacho",
    "execucao",
    "julgado",
    "prazo",
    "processo",
    "reclamado",
    "reclamante",
    "recurso",
    "sentenca",
    "transito",
    "valor",
}
_PROCESS_QUESTION_TERMS = {
    "andamento",
    "arquivada",
    "arquivado",
    "audiencia",
    "causa",
    "classe",
    "despacho",
    "documento",
    "documentos",
    "encerrada",
    "encerrado",
    "movimentacao",
    "movimentacoes",
    "nome",
    "nomes",
    "orgao",
    "partes",
    "pendencia",
    "pendencias",
    "pendente",
    "reclamado",
    "reclamante",
    "sentenca",
    "situacao",
    "autuacao",
    "valor",
    "vinculada",
    "vinculadas",
    "vinculado",
    "vinculados",
}
_PROCESS_QUESTION_PHRASES = {
    "situacao atual",
    "ultima movimentacao",
    "valor da causa",
}
_OUT_OF_SCOPE_WORDS = {
    "aleatoria",
    "aleatorio",
    "bolo",
    "computador",
    "filme",
    "hardware",
    "jogo",
    "placa",
    "receita",
    "restaurante",
    "video",
    "viagem",
}
_STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "da",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "eu",
    "me",
    "minha",
    "meu",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "ou",
    "para",
    "pela",
    "pelo",
    "por",
    "que",
    "um",
    "uma",
    "usuario",
    "usuaria",
}
_PROMPT_EXAMPLE_TOPIC_TOKENS = {
    "arquivamento",
    "audiencia",
    "bolo",
    "definitivo",
    "filme",
    "julgado",
    "partes",
    "placa",
    "processo",
    "reclamado",
    "reclamante",
    "sentenca",
    "transito",
    "video",
}


def extract_process_number(message: str) -> str | None:
    for candidate in _PROCESS_NUMBER_CANDIDATE_RE.findall(message):
        normalized = re.sub(r"\D", "", candidate)
        if len(normalized) == 20:
            return normalized

    return None


def interpret_user_message(
    message: str,
    progress_reporter: ProgressReporter | None = None,
) -> dict:
    process_number = extract_process_number(message)
    inferred_intent = _infer_intent(message, process_number)

    if inferred_intent is not None:
        report_progress(
            progress_reporter,
            code="intent.local",
            level="success",
            message="intencao resolvida por regras locais.",
            details={
                "intent": inferred_intent,
                "uses_model": False,
            },
        )
        return _build_response(inferred_intent, process_number, message)

    model_started_at = progress_clock()
    try:
        prompt = build_agent1_prompt(message, process_number)
        report_progress(
            progress_reporter,
            code="intent.model.started",
            level="started",
            message="consultando modelo local para entender a mensagem...",
            details={"uses_model": True},
        )
        response = generate_text(prompt, system_prompt=AGENT1_SYSTEM_PROMPT)
        parsed_response = _parse_model_json(response)
        validated_response = _validate_model_response(
            parsed_response,
            message,
            process_number,
        )
        report_progress(
            progress_reporter,
            code="intent.model.finished",
            level="success",
            message="modelo local retornou uma interpretacao valida.",
            details={"uses_model": True},
            started_at=model_started_at,
        )
        return validated_response
    except (OllamaError, ValueError, TypeError, json.JSONDecodeError) as exc:
        report_progress(
            progress_reporter,
            code="intent.model.fallback",
            level="warning",
            message="modelo local indisponivel para interpretacao; usando fallback seguro.",
            details={
                "fallback": True,
                "error_type": type(exc).__name__,
            },
            started_at=model_started_at,
        )
        return _fallback_response(process_number)


def _parse_model_json(response: str) -> dict[str, Any]:
    text = response.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Resposta do Agente 1 nao e um objeto JSON.")

    return data


def _validate_model_response(
    response: dict[str, Any],
    message: str,
    process_number: str | None,
) -> dict:
    intent = response.get("intent")
    if intent not in ALLOWED_INTENTS:
        intent = "unclear"

    confidence = response.get("confidence")
    if confidence not in ALLOWED_CONFIDENCES:
        confidence = "low"

    user_goal = response.get("user_goal")
    if not isinstance(user_goal, str):
        user_goal = ""

    user_goal = user_goal.strip()
    if intent == "greeting":
        if _is_greeting_message(message):
            user_goal = _default_goal(intent, process_number, message)
            confidence = "high"
        else:
            intent = "unclear"
            user_goal = LIMITED_GOAL
            confidence = "low"
    elif not _is_acceptable_model_goal(user_goal, message):
        user_goal = LIMITED_GOAL

    if len(user_goal) > MAX_USER_GOAL_LENGTH:
        user_goal = user_goal[:MAX_USER_GOAL_LENGTH].rstrip()

    return {
        "intent": intent,
        "process_number": process_number,
        "user_goal": user_goal,
        "confidence": confidence,
    }


def _validate_final_response(response: dict, process_number: str | None) -> dict:
    intent = response.get("intent")
    if intent not in ALLOWED_INTENTS:
        raise ValueError("Intent invalida.")

    confidence = response.get("confidence")
    if confidence not in ALLOWED_CONFIDENCES:
        raise ValueError("Confidence invalida.")

    user_goal = response.get("user_goal")
    if not isinstance(user_goal, str):
        raise ValueError("User goal invalido.")

    user_goal = user_goal.strip()
    if not user_goal:
        raise ValueError("User goal vazio.")

    if len(user_goal) > MAX_USER_GOAL_LENGTH:
        user_goal = user_goal[:MAX_USER_GOAL_LENGTH].rstrip()

    return {
        "intent": intent,
        "process_number": process_number,
        "user_goal": user_goal,
        "confidence": confidence,
    }


def _build_response(
    intent: str,
    process_number: str | None,
    message: str = "",
) -> dict:
    return _validate_final_response(
        {
            "intent": intent,
            "process_number": process_number,
            "user_goal": _default_goal(intent, process_number, message),
            "confidence": _default_confidence(intent),
        },
        process_number,
    )


def _infer_intent(message: str, process_number: str | None) -> str | None:
    normalized = _normalize_text(message)
    token_list = _tokenize(normalized)
    compact = " ".join(token_list)
    tokens = set(token_list)
    query_spec = resolve_process_query(message, process_number=process_number)

    if not compact:
        return "unclear"

    if process_number is not None:
        if (
            query_spec.scope == "process"
            and query_spec.target != TARGET_GENERIC_PROCESS
        ):
            return "process_question"
        return "process_lookup"

    if _is_greeting_message(message):
        return "greeting"

    if _is_process_lookup(normalized, token_list, tokens):
        return "process_lookup"

    if query_spec.scope == SCOPE_GENERAL and query_spec.target == TARGET_LEGAL_CONCEPT:
        return "legal_general_question"

    if _is_legal_general_question(compact, tokens):
        return "legal_general_question"

    if is_structured_process_spec(query_spec) or is_document_content_spec(query_spec):
        return "process_question"

    if _is_process_question(message, compact, tokens):
        return "process_question"

    if tokens & _OUT_OF_SCOPE_WORDS:
        return "out_of_scope"

    return None


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


def _tokenize(normalized_text: str) -> list[str]:
    return _TOKEN_RE.findall(normalized_text)


def _is_short_greeting(tokens: list[str]) -> bool:
    token_set = set(tokens)
    return (
        0 < len(tokens) <= 5
        and token_set <= _GREETING_TOKENS
        and bool(token_set & _GREETING_ANCHORS)
    )


def _is_greeting_message(message: str) -> bool:
    return _is_thanks_message(message) or _is_short_greeting(
        _tokenize(_normalize_text(message))
    )


def _is_thanks_message(message: str) -> bool:
    tokens = _tokenize(_normalize_text(message))
    token_set = set(tokens)
    return (
        0 < len(tokens) <= 7
        and token_set <= _THANKS_TOKENS
        and bool(token_set & _THANKS_ANCHORS)
    )


def _is_process_lookup(
    normalized: str,
    token_list: list[str],
    tokens: set[str],
) -> bool:
    has_numeric_reference = "processo" in tokens and any(
        token.isdigit() for token in token_list
    )
    if has_numeric_reference:
        return True

    return bool(_LOOKUP_ACTION_RE.search(normalized)) and bool(
        tokens & _PROCESS_LOOKUP_CONTEXT
    )


def _is_legal_general_question(compact: str, tokens: set[str]) -> bool:
    concept_patterns = (
        r"\bdefina\b",
        r"\bexplicar\b",
        r"\bexplique\b",
        r"\bme explica\b",
        r"\bme explique\b",
        r"\bo que e\b",
        r"\bo que significa\b",
        r"\bpode me explicar\b",
        r"\bpoderia me explicar\b",
        r"\bqual a diferenca\b",
        r"\bsignificado\b",
    )
    return bool(tokens & _LEGAL_GENERAL_TERMS) and any(
        re.search(pattern, compact) for pattern in concept_patterns
    )


def _is_process_question(message: str, compact: str, tokens: set[str]) -> bool:
    question_starters = (
        "ele",
        "ela",
        "existe",
        "existem",
        "ha",
        "houve",
        "qual",
        "quais",
        "quando",
        "quem",
        "tem",
    )
    has_question_shape = "?" in message or compact.startswith(question_starters)
    has_process_subject = bool(tokens & _PROCESS_QUESTION_TERMS) or any(
        phrase in compact for phrase in _PROCESS_QUESTION_PHRASES
    )

    return has_question_shape and has_process_subject


def _is_placeholder_goal(user_goal: str) -> bool:
    normalized_goal = _normalize_text(user_goal).strip()
    return normalized_goal in _PLACEHOLDER_GOALS


def _is_acceptable_model_goal(user_goal: str, message: str) -> bool:
    if not user_goal or _is_placeholder_goal(user_goal):
        return False

    message_tokens = _meaningful_tokens(message)
    goal_tokens = _meaningful_tokens(user_goal)
    if not goal_tokens:
        return False

    unrelated_example_topics = (
        goal_tokens & _PROMPT_EXAMPLE_TOPIC_TOKENS
    ) - message_tokens
    if unrelated_example_topics:
        return False

    return bool(message_tokens & goal_tokens)


def _meaningful_tokens(text: str) -> set[str]:
    normalized = _normalize_text(text)
    return {
        token
        for token in _tokenize(normalized)
        if len(token) > 2 and token not in _STOPWORDS and not token.isdigit()
    }


def _default_goal(
    intent: str,
    process_number: str | None,
    message: str = "",
) -> str:
    if intent == "greeting":
        if _is_thanks_message(message):
            return THANKS_GOAL
        return "Saudacao informal ou abertura de conversa."
    if intent == "process_lookup" and process_number is not None:
        return "Consultar ou acompanhar o processo informado."
    if intent == "process_lookup":
        return "Consultar ou acompanhar um processo."
    if intent == "process_question":
        return "Responder pergunta sobre processo."
    if intent == "legal_general_question":
        return "Explicar conceito juridico/processual."
    if intent == "out_of_scope":
        return "Pedido fora do contexto processual."
    return "Mensagem sem contexto suficiente."


def _default_confidence(intent: str) -> str:
    if intent == "unclear":
        return "medium"
    return "high"


def _fallback_response(process_number: str | None) -> dict:
    return {
        "intent": "unclear",
        "process_number": process_number,
        "user_goal": FALLBACK_GOAL,
        "confidence": "low",
    }
