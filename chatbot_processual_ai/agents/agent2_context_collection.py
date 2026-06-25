import re
import unicodedata

from collector_adapter import find_process_by_number


MAX_CONVERSATION_ENTRIES = 10
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
_ACTIVE_PROCESS_REFERENCE_PHRASES = {
    "antes do arquivamento",
    "esse processo",
    "este processo",
    "nesse caso",
    "neste caso",
    "transito em julgado",
    "ultima decisao",
    "ultima movimentacao",
}
_ACTIVE_PROCESS_REFERENCE_TOKENS = {
    "andamento",
    "ele",
    "isso",
    "movimentacao",
    "movimentacoes",
    "recurso",
    "recursos",
    "situacao",
}
_NEW_PROCESS_LOOKUP_PHRASES = {
    "outro processo",
    "processo diferente",
}
_NEW_PROCESS_REFERENCE_TOKENS = {
    "cliente",
    "diferente",
    "esposa",
    "esposo",
    "filha",
    "filho",
    "irma",
    "irmao",
    "mae",
    "meu",
    "minha",
    "outro",
    "pai",
}


def build_context_and_collect(
    message: str,
    intent_data: dict,
    session_state: dict,
) -> dict:
    intent = intent_data.get("intent")
    process_number = intent_data.get("process_number")
    transported_intent_data = dict(intent_data)

    _register_conversation_entry(message, intent, session_state)

    collection_status = "not_needed"
    if intent == "process_lookup":
        if _should_use_active_process(message, process_number, session_state):
            transported_intent_data["intent"] = "process_question"
        else:
            collection_status = _handle_process_lookup(process_number, session_state)

    return {
        "message": message,
        "intent_data": transported_intent_data,
        "active_process": session_state.get("active_process") or {},
        "collection_status": collection_status,
        "conversation": list(session_state.get("conversation", [])),
    }


def _handle_process_lookup(process_number: str | None, session_state: dict) -> str:
    normalized_number = _normalize_process_number(process_number)
    if normalized_number is None:
        return "missing_number"

    active_process = session_state.get("active_process")
    active_number = _active_process_number(active_process)
    if active_number == normalized_number:
        return "already_active"

    process = find_process_by_number(normalized_number)
    if process is None:
        return "not_found"

    session_state["active_process"] = process
    session_state["last_intent"] = "process_lookup"
    return "success"


def _register_conversation_entry(
    message: str,
    intent: str | None,
    session_state: dict,
) -> None:
    conversation = session_state.setdefault("conversation", [])
    conversation.append(
        {
            "role": "user",
            "message": message,
            "intent": intent,
        }
    )
    del conversation[:-MAX_CONVERSATION_ENTRIES]


def _should_use_active_process(
    message: str,
    process_number: str | None,
    session_state: dict,
) -> bool:
    if _normalize_process_number(process_number) is not None:
        return False

    if not session_state.get("active_process"):
        return False

    normalized_message = _normalize_text(message)
    tokens = set(_TOKEN_RE.findall(normalized_message))

    return (
        not _is_new_process_lookup_without_number(normalized_message, tokens)
        and _references_active_process(normalized_message, tokens)
    )


def _references_active_process(normalized_message: str, tokens: set[str]) -> bool:
    return bool(tokens & _ACTIVE_PROCESS_REFERENCE_TOKENS) or any(
        phrase in normalized_message for phrase in _ACTIVE_PROCESS_REFERENCE_PHRASES
    )


def _is_new_process_lookup_without_number(
    normalized_message: str,
    tokens: set[str],
) -> bool:
    if any(phrase in normalized_message for phrase in _NEW_PROCESS_LOOKUP_PHRASES):
        return True

    return (
        bool(_LOOKUP_ACTION_RE.search(normalized_message))
        and "processo" in tokens
        and bool(tokens & _NEW_PROCESS_REFERENCE_TOKENS)
    )


def _active_process_number(active_process: dict | None) -> str | None:
    if not active_process:
        return None

    process_data = active_process.get("processo", {})
    return _normalize_process_number(process_data.get("numero_normalizado"))


def _normalize_process_number(process_number: str | None) -> str | None:
    normalized_number = re.sub(r"\D", "", process_number or "")
    if len(normalized_number) != 20:
        return None

    return normalized_number


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )
