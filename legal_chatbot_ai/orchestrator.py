"""Orquestracao sequencial do chatbot.

Este modulo concentra o fluxo principal para ser reutilizado pelo terminal.
Ele tambem aplica as protecoes deterministicas entre agentes.
"""

import json

from .agents.context_agent import run_context_agent
from .agents.legal_reasoning_agent import run_legal_reasoning_agent
from .agents.response_agent import run_response_agent
from .agents.user_input_agent import run_user_input_agent
from .collection.collection_router import run_collection_router
from .utils.process_number import normalize_process_number


ALLOWED_NEXT_ACTIONS = {"NO_COLLECTION", "REQUEST_COLLECTION", "ASK_CLARIFICATION"}
ALLOWED_INTENTS = {
    "greeting",
    "small_talk",
    "user_feedback",
    "thanks",
    "bot_function_question",
    "legal_general_question",
    "process_lookup_request",
    "process_follow_up",
    "previous_answer_follow_up",
    "out_of_scope_request",
    "unclear",
}
ALLOWED_RESPONSE_STRATEGIES = {
    "greet_and_offer_help",
    "acknowledge_and_offer_next_step",
    "explain_previous_collection_clearly",
    "explain_previous_answer_clearly",
    "answer_legal_general_question",
    "explain_collected_process_data",
    "ask_for_process_number",
    "polite_scope_redirect",
    "ask_clarification",
    "explain_bot_capabilities",
}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_MEMORY_TARGETS = {"last_collection", "last_answer", "last_reasoning", None}
NO_COLLECTION_INTENTS = {
    "greeting",
    "small_talk",
    "user_feedback",
    "thanks",
    "bot_function_question",
    "legal_general_question",
    "process_follow_up",
    "previous_answer_follow_up",
    "out_of_scope_request",
    "unclear",
}


def _debug_print(title: str, payload) -> None:
    """Imprime um bloco de debug em JSON para acompanhar a passagem de dados."""
    print(f"\n[DEBUG] {title}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _copy_session_state(session_state: dict | None) -> dict:
    """Cria uma copia rasa do estado conversacional."""
    return dict(session_state or {})


def _as_list(value) -> list:
    """Garante lista para campos opcionais."""
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _context_defaults(context_decision: dict | None) -> dict:
    """Preenche campos ausentes do contrato de contexto."""
    context_decision = dict(context_decision or {})
    return {
        "next_action": context_decision.get("next_action") or "NO_COLLECTION",
        "intent": context_decision.get("intent") or "unclear",
        "user_goal": context_decision.get("user_goal")
        or "Interpretar a mensagem dentro do escopo juridico informativo.",
        "needs_collection": bool(context_decision.get("needs_collection")),
        "should_use_memory": bool(context_decision.get("should_use_memory")),
        "memory_target": context_decision.get("memory_target"),
        "response_strategy": context_decision.get("response_strategy")
        or "ask_clarification",
        "collection_request": context_decision.get("collection_request"),
        "missing_information": _as_list(context_decision.get("missing_information")),
        "confidence": context_decision.get("confidence") or "low",
    }


def _safe_no_collection(context_decision: dict, response_strategy: str | None = None) -> dict:
    """Remove qualquer pedido de coleta de um contexto que nao deve coletar."""
    return {
        **context_decision,
        "next_action": "NO_COLLECTION",
        "needs_collection": False,
        "collection_request": None,
        "response_strategy": response_strategy
        or context_decision.get("response_strategy")
        or "ask_clarification",
    }


def _safe_ask_process_number(
    context_decision: dict,
    missing_information: list | None = None,
) -> dict:
    """Converte o contexto para pedido de numero CNJ."""
    missing = list(context_decision.get("missing_information") or [])
    missing.extend(missing_information or [])
    if not missing:
        missing = ["Informe o numero do processo no formato CNJ."]

    return {
        **context_decision,
        "next_action": "ASK_CLARIFICATION",
        "intent": "process_lookup_request",
        "user_goal": context_decision.get("user_goal")
        or "Consultar andamento ou detalhes de um processo.",
        "needs_collection": False,
        "should_use_memory": False,
        "memory_target": None,
        "response_strategy": "ask_for_process_number",
        "collection_request": None,
        "missing_information": missing,
        "confidence": "low",
    }


def _validate_context_decision(context_decision: dict, user_input: dict) -> dict:
    """Valida e corrige o contrato retornado pelo context_agent."""
    context_decision = _context_defaults(context_decision)

    if context_decision["next_action"] not in ALLOWED_NEXT_ACTIONS:
        context_decision["next_action"] = "NO_COLLECTION"

    if context_decision["intent"] not in ALLOWED_INTENTS:
        context_decision["intent"] = "unclear"

    if context_decision["response_strategy"] not in ALLOWED_RESPONSE_STRATEGIES:
        context_decision["response_strategy"] = "ask_clarification"

    if context_decision["confidence"] not in ALLOWED_CONFIDENCE:
        context_decision["confidence"] = "low"

    if context_decision["memory_target"] not in ALLOWED_MEMORY_TARGETS:
        context_decision["memory_target"] = None

    if context_decision["intent"] == "process_follow_up":
        context_decision["should_use_memory"] = True
        context_decision["memory_target"] = "last_collection"
        return _safe_no_collection(
            context_decision,
            "explain_previous_collection_clearly",
        )

    if context_decision["intent"] == "previous_answer_follow_up":
        context_decision["should_use_memory"] = True
        context_decision["memory_target"] = "last_answer"
        return _safe_no_collection(
            context_decision,
            "explain_previous_answer_clearly",
        )

    if context_decision["intent"] in NO_COLLECTION_INTENTS:
        context_decision["should_use_memory"] = False
        context_decision["memory_target"] = None
        return _safe_no_collection(context_decision)

    if context_decision["next_action"] == "REQUEST_COLLECTION":
        if context_decision["intent"] != "process_lookup_request":
            return _safe_no_collection(context_decision)

        collection_request = context_decision.get("collection_request")
        process_number_raw = None
        if isinstance(collection_request, dict):
            if collection_request.get("type") == "process_lookup":
                process_number_raw = collection_request.get("process_number_raw")

        process_number_raw = process_number_raw or user_input.get(
            "possible_process_number"
        )
        if not process_number_raw:
            return _safe_ask_process_number(context_decision)

        return {
            **context_decision,
            "needs_collection": True,
            "should_use_memory": False,
            "memory_target": None,
            "response_strategy": "explain_collected_process_data",
            "collection_request": {
                "type": "process_lookup",
                "process_number_raw": process_number_raw,
            },
        }

    if context_decision["next_action"] == "ASK_CLARIFICATION":
        return _safe_ask_process_number(context_decision)

    return {
        **context_decision,
        "needs_collection": False,
        "collection_request": None,
    }


def _get_process_number_raw(user_input: dict, context_decision: dict) -> str | None:
    """Busca o numero indicado pelo contexto."""
    collection_request = context_decision.get("collection_request") or {}
    if not isinstance(collection_request, dict):
        return None
    return collection_request.get("process_number_raw")


def _get_last_collection_data(session_state: dict) -> dict | None:
    """Le a ultima coleta com compatibilidade para a chave antiga."""
    value = session_state.get("last_collection_data")
    if isinstance(value, dict):
        return value

    legacy_value = session_state.get("last_collected_data")
    if isinstance(legacy_value, dict):
        return legacy_value

    return None


def _get_last_process_number_result(session_state: dict) -> dict | None:
    """Le o ultimo resultado de validacao do numero CNJ."""
    value = session_state.get("last_process_number_result")
    if isinstance(value, dict):
        return value
    return None


def run_chatbot_flow(
    user_message: str,
    debug_mode: bool = False,
    session_state: dict | None = None,
) -> dict:
    """Executa o fluxo completo e retorna resposta final com dados de debug."""
    session_state = _copy_session_state(session_state)
    debug = {
        "user_input": {},
        "context_decision": {},
        "process_number_result": None,
        "collected_data": None,
        "legal_reasoning": {},
        "memory_used": None,
    }

    # 1: entrada bruta vira o primeiro JSON do fluxo.
    user_input = run_user_input_agent(user_message)
    debug["user_input"] = user_input
    if debug_mode:
        _debug_print("saida do user_input_agent", user_input)

    # 2: contexto decide a proxima acao sem coletar dados.
    context_decision = run_context_agent(user_input)
    context_decision = _validate_context_decision(context_decision, user_input)
    debug["context_decision"] = context_decision
    if context_decision.get("should_use_memory"):
        debug["memory_used"] = context_decision.get("memory_target")
    if debug_mode:
        _debug_print("saida do context_agent", context_decision)

    process_number_result = None
    collected_data = None

    # 3: coleta mockada so acontece com pedido claro e numero CNJ validado.
    if context_decision.get("next_action") == "REQUEST_COLLECTION":
        process_number_raw = _get_process_number_raw(user_input, context_decision)
        process_number_result = normalize_process_number(process_number_raw)
        debug["process_number_result"] = process_number_result
        if debug_mode:
            _debug_print("resultado de process_number.py", process_number_result)

        if process_number_result.get("is_valid") is True:
            collected_data = run_collection_router(process_number_result)
            debug["collected_data"] = collected_data
            if debug_mode:
                _debug_print("saida do collection_router", collected_data)
        else:
            context_decision = _safe_ask_process_number(
                context_decision,
                process_number_result.get("errors"),
            )
            debug["context_decision"] = context_decision
            if debug_mode:
                _debug_print("contexto ajustado para ASK_CLARIFICATION", context_decision)

    collected_data_for_reasoning = collected_data
    process_number_for_reasoning = process_number_result
    if context_decision.get("memory_target") == "last_collection":
        collected_data_for_reasoning = _get_last_collection_data(session_state)
        process_number_for_reasoning = _get_last_process_number_result(session_state)
        debug["memory_used"] = "last_collection"

    session_memory = {
        "last_collection_data": _get_last_collection_data(session_state),
        "last_process_number_result": _get_last_process_number_result(session_state),
        "last_legal_reasoning": session_state.get("last_legal_reasoning"),
        "last_final_response": session_state.get("last_final_response")
        or session_state.get("last_answer"),
    }

    # 4: organiza um plano tecnico de resposta.
    reasoning_json = run_legal_reasoning_agent(
        user_input=user_input,
        context_decision=context_decision,
        process_number_result=process_number_for_reasoning,
        collected_data=collected_data_for_reasoning,
        session_memory=session_memory,
    )
    debug["legal_reasoning"] = reasoning_json
    if debug_mode:
        _debug_print("saida do legal_reasoning_agent", reasoning_json)

    # 5: transforma o plano em resposta final amigavel.
    final_response = run_response_agent(reasoning_json)
    if debug_mode:
        _debug_print("resposta final", {"final_response": final_response})

    next_state = _copy_session_state(session_state)
    if collected_data:
        next_state["last_collection_data"] = collected_data
        next_state["last_process_number_result"] = process_number_result
    next_state["last_user_message"] = user_message
    next_state["last_legal_reasoning"] = reasoning_json
    next_state["last_final_response"] = final_response
    next_state["last_answer"] = final_response

    return {
        "answer": final_response,
        "debug": debug,
        "state": next_state,
    }
