import re
import unicodedata

from collector_adapter import AdapterStatus, CollectorResult, create_collector_adapter
from progress import ProgressReporter, progress_clock, report_progress
from services.process_query_resolver import (
    is_structured_process_spec,
    resolve_process_query,
)
from services.process_query_router import route_process_query
from services.rag_retriever import retrieve_rag_context


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
    "historico do processo",
    "linha do tempo",
    "nesse caso",
    "neste caso",
    "transito em julgado",
    "ultima decisao",
    "ultima movimentacao",
    "ultimas movimentacoes",
}
_ACTIVE_PROCESS_REFERENCE_TOKENS = {
    "andamento",
    "assunto",
    "autuacao",
    "causa",
    "classe",
    "ele",
    "historico",
    "isso",
    "julgador",
    "linha",
    "movimentacao",
    "movimentacoes",
    "orgao",
    "recurso",
    "recursos",
    "situacao",
    "tempo",
    "valor",
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
    progress_reporter: ProgressReporter | None = None,
) -> dict:
    intent = intent_data.get("intent")
    process_number = intent_data.get("process_number")
    transported_intent_data = dict(intent_data)

    _register_conversation_entry(message, intent, session_state)
    report_progress(
        progress_reporter,
        code="context.conversation",
        level="success",
        message="historico recente atualizado.",
        details={"conversation_entries": len(session_state.get("conversation", []))},
    )

    collection_status = "not_needed"
    if intent == "process_lookup":
        if _should_use_active_process(message, process_number, session_state):
            transported_intent_data["intent"] = "process_question"
            report_progress(
                progress_reporter,
                code="context.active_reused",
                level="success",
                message="processo ativo reaproveitado para a pergunta.",
                details={"collection_status": collection_status},
            )
        else:
            lookup_started_at = progress_clock()
            collection_status = _handle_process_lookup(
                process_number,
                session_state,
                progress_reporter,
            )
            _report_lookup_result(
                progress_reporter, collection_status, lookup_started_at
            )
    elif intent == "process_question" and _normalize_process_number(process_number):
        lookup_started_at = progress_clock()
        collection_status = _handle_process_lookup(
            process_number,
            session_state,
            progress_reporter,
        )
        _report_lookup_result(progress_reporter, collection_status, lookup_started_at)

    active_process = session_state.get("active_process") or {}
    query_spec = resolve_process_query(
        message,
        process_number=process_number,
        has_active_process=bool(active_process),
    )
    if is_structured_process_spec(query_spec) and active_process:
        transported_intent_data["intent"] = "process_question"
    transported_intent_data["process_query_spec"] = query_spec.to_dict()

    query_route = route_process_query(
        message,
        transported_intent_data.get("intent"),
        bool(active_process),
        process_query_spec=query_spec,
    )
    report_progress(
        progress_reporter,
        code="route.finished",
        level="success",
        message=_route_message(query_route.route, query_route.requires_rag),
        details={
            "route": query_route.route,
            "requires_rag": query_route.requires_rag,
        },
    )
    rag_context = retrieve_rag_context(
        query=message,
        process_number=_active_process_number(active_process),
        requires_rag=query_route.requires_rag,
        progress_reporter=progress_reporter,
    )

    return {
        "message": message,
        "intent_data": transported_intent_data,
        "active_process": active_process,
        "collection_status": collection_status,
        "query_route": {
            "route": query_route.route,
            "reason": query_route.reason,
            "requires_rag": query_route.requires_rag,
        },
        "process_query_spec": query_spec.to_dict(),
        "rag_context": rag_context,
        "conversation": list(session_state.get("conversation", [])),
    }


def _handle_process_lookup(
    process_number: str | None,
    session_state: dict,
    progress_reporter: ProgressReporter | None = None,
) -> str:
    normalized_number = _normalize_process_number(process_number)
    if normalized_number is None:
        return "missing_number"

    active_process = session_state.get("active_process")
    active_number = _active_process_number(active_process)
    if active_number == normalized_number:
        return "already_active"

    result = create_collector_adapter().lookup_or_acquire_process(
        normalized_number,
        progress_reporter,
    )
    if result.status not in {AdapterStatus.LOCAL_HIT, AdapterStatus.COLLECTED}:
        return result.status.value.lower()

    session_state["active_process"] = result.process
    session_state["last_intent"] = "process_lookup"
    return _successful_collection_status(result)


def _successful_collection_status(result: CollectorResult) -> str:
    if result.status is AdapterStatus.LOCAL_HIT:
        return "success"
    return "collected"


def _report_lookup_result(
    progress_reporter: ProgressReporter | None,
    collection_status: str,
    started_at: float,
) -> None:
    report_progress(
        progress_reporter,
        code="context.lookup.finished",
        level=_collection_status_level(collection_status),
        message=_collection_status_message(collection_status),
        details={"collection_status": collection_status},
        started_at=started_at,
    )


def _collection_status_level(collection_status: str) -> str:
    if collection_status in {"success", "collected", "already_active", "not_needed"}:
        return "success"
    return "warning"


def _collection_status_message(collection_status: str) -> str:
    messages = {
        "success": "processo localizado na base local.",
        "collected": "processo coletado, persistido e carregado.",
        "already_active": "processo informado ja estava ativo.",
        "missing_number": "numero de processo ausente ou incompleto.",
        "not_found": "processo nao encontrado na base local.",
        "partial": "a consulta retornou dados incompletos.",
        "blocked": "a consulta externa esta temporariamente indisponivel.",
        "failed": "nao foi possivel consultar o processo agora.",
        "invalid_number": "numero de processo invalido.",
        "not_needed": "consulta local nao necessaria.",
    }
    return messages.get(collection_status, "coleta concluida.")


def _route_message(route: str, requires_rag: bool) -> str:
    if requires_rag:
        return "rota definida: busca semantica sera consultada."
    if route == "missing_process":
        return "rota definida: pergunta depende de processo ativo."
    if route == "out_of_scope":
        return "rota definida: pedido fora do escopo processual."
    return "rota definida: dados estruturados sao suficientes."


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
