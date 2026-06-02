"""Agente de contexto.

Usa Ollama para entender a intencao do usuario e decidir o proximo passo. Este
agente nao responde ao usuario, nao consulta processo e nao valida numero.
"""

import json
import re
import unicodedata

from ..llm.ollama_client import call_ollama
from ..utils.json_tools import extract_json_from_text


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
ALLOWED_MEMORY_TARGETS = {"last_collection", "last_answer", "last_reasoning", None}
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

BOT_FUNCTION_TERMS = (
    "qual a sua funcao",
    "qual sua funcao",
    "sua funcao",
    "o que voce consegue fazer",
    "o que voce faz",
    "quem e voce",
    "como voce pode ajudar",
    "para que voce serve",
    "suas funcoes",
)

GREETING_TERMS = (
    "oi",
    "ola",
    "bom dia",
    "boa tarde",
    "boa noite",
    "tudo bem",
)

THANKS_TERMS = (
    "obrigado",
    "obrigada",
    "valeu",
    "agradeco",
    "grato",
    "gratidao",
)

FEEDBACK_TERMS = (
    "uau",
    "incrivel",
    "perfeito",
    "excelente",
    "sensacional",
    "show",
    "muito bom",
    "boa",
)

SMALL_TALK_TERMS = (
    "beleza",
    "ok",
    "certo",
    "entendi",
    "tranquilo",
    "ta bom",
)

PROCESS_ENTITY_TERMS = ("processo", "autos", "cnj")
PROCESS_LOOKUP_TERMS = (
    "andamento",
    "consult",
    "busc",
    "situacao",
    "moviment",
    "detalh",
    "ver",
    "olhar",
    "acompanhar",
    "meu processo",
    "meus processos",
)

COLLECTION_FOLLOW_UP_TERMS = (
    "acabou de coletar",
    "voce coletou",
    "vc coletou",
    "dados coletados",
    "essa consulta",
    "esta consulta",
    "sobre esse processo",
    "sobre este processo",
    "essa movimentacao",
    "esta movimentacao",
    "explica esses dados",
    "explica a consulta",
    "me explica melhor a consulta",
)

PREVIOUS_ANSWER_FOLLOW_UP_TERMS = (
    "explica melhor isso",
    "me explica melhor isso",
    "nao entendi",
    "fala de outro jeito",
    "resume o que voce disse",
    "resume isso",
    "o que voce quis dizer",
)

LEGAL_TOPIC_TERMS = (
    "juntada",
    "peticao",
    "audiencia",
    "sentenca",
    "decisao",
    "recurso",
    "prazo",
    "contestacao",
    "liminar",
    "custas",
    "intimacao",
    "citacao",
    "advogado",
    "direito",
    "juridic",
    "tribunal",
)

GENERAL_QUESTION_TERMS = (
    "o que significa",
    "o que e",
    "me explica",
    "explique",
    "duvida",
    "qual o significado",
)

OUT_OF_SCOPE_TERMS = (
    "piada",
    "receita",
    "musica",
    "filme",
    "futebol",
    "previsao do tempo",
    "clima",
    "horoscopo",
)


def _fold_text(value: str) -> str:
    """Normaliza texto para comparacoes simples de intencao."""
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    """Indica se algum termo aparece no texto normalizado."""
    return any(term in text for term in terms)


def _word_count(text: str) -> int:
    """Conta palavras de forma tolerante a pontuacao."""
    return len(re.findall(r"\w+", text))


def _mostly_process_number(text: str) -> bool:
    """Detecta mensagens compostas basicamente por um numero de processo."""
    digits = re.sub(r"\D", "", text)
    if len(digits) != 20:
        return False
    letters = re.findall(r"[a-zA-Z]", text)
    return len(letters) <= 3


def _is_greeting_like(text: str) -> bool:
    """Detecta saudacoes curtas sem depender do LLM."""
    if not _has_any(text, GREETING_TERMS):
        return False
    if _has_any(text, PROCESS_ENTITY_TERMS + LEGAL_TOPIC_TERMS):
        return False
    return _word_count(text) <= 8


def _is_short_term_message(text: str, terms: tuple[str, ...]) -> bool:
    """Detecta mensagens curtas baseadas em um conjunto de termos."""
    if _has_any(text, PROCESS_ENTITY_TERMS + LEGAL_TOPIC_TERMS):
        return False
    if not _has_any(text, terms):
        return False
    return _word_count(text) <= 10


def _asks_for_process_lookup(text: str, possible_process_number: str | None) -> bool:
    """Detecta pedido de consulta de processo."""
    has_process_entity = _has_any(text, PROCESS_ENTITY_TERMS)
    has_lookup_term = _has_any(text, PROCESS_LOOKUP_TERMS)

    if possible_process_number:
        return has_process_entity or has_lookup_term or _mostly_process_number(text)

    return has_process_entity and has_lookup_term


def _is_collection_follow_up(text: str) -> bool:
    """Detecta pergunta sobre a ultima coleta."""
    if _has_any(text, COLLECTION_FOLLOW_UP_TERMS):
        return True

    has_process_reference = "processo" in text or "autos" in text
    has_explanation_request = _has_any(
        text,
        ("explica", "entender", "claro", "resum", "significa", "quer dizer"),
    )
    return has_process_reference and has_explanation_request


def _is_previous_answer_follow_up(text: str) -> bool:
    """Detecta pedido para explicar a ultima resposta."""
    return _has_any(text, PREVIOUS_ANSWER_FOLLOW_UP_TERMS)


def _is_legal_general_question(text: str) -> bool:
    """Detecta pergunta juridica geral que nao precisa de coleta."""
    if _has_any(text, PROCESS_ENTITY_TERMS) and _has_any(text, PROCESS_LOOKUP_TERMS):
        return False
    return _has_any(text, LEGAL_TOPIC_TERMS) or (
        _has_any(text, GENERAL_QUESTION_TERMS) and "juridic" in text
    )


def _result(
    *,
    next_action: str,
    intent: str,
    user_goal: str,
    needs_collection: bool,
    should_use_memory: bool,
    memory_target: str | None,
    response_strategy: str,
    collection_request: dict | None = None,
    missing_information: list | None = None,
    confidence: str = "high",
) -> dict:
    """Monta o contrato estruturado do agente de contexto."""
    return {
        "next_action": next_action,
        "intent": intent,
        "user_goal": user_goal,
        "needs_collection": needs_collection,
        "should_use_memory": should_use_memory,
        "memory_target": memory_target,
        "response_strategy": response_strategy,
        "collection_request": collection_request,
        "missing_information": missing_information or [],
        "confidence": confidence,
    }


def _deterministic_result(input_json: dict) -> dict | None:
    """Resolve casos obvios para evitar variacao do modelo local."""
    possible_process_number = input_json.get("possible_process_number")
    message = _fold_text(
        input_json.get("normalized_message") or input_json.get("raw_message")
    )

    if _asks_for_process_lookup(message, possible_process_number):
        if possible_process_number:
            return _result(
                next_action="REQUEST_COLLECTION",
                intent="process_lookup_request",
                user_goal="Consultar dados simulados de um processo especifico.",
                needs_collection=True,
                should_use_memory=False,
                memory_target=None,
                response_strategy="explain_collected_process_data",
                collection_request={
                    "type": "process_lookup",
                    "process_number_raw": possible_process_number,
                },
                confidence="high",
            )

        return _result(
            next_action="ASK_CLARIFICATION",
            intent="process_lookup_request",
            user_goal="Consultar andamento ou detalhes de um processo.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="ask_for_process_number",
            missing_information=["Informe o numero do processo no formato CNJ."],
            confidence="high",
        )

    if _is_collection_follow_up(message):
        return _result(
            next_action="NO_COLLECTION",
            intent="process_follow_up",
            user_goal="Entender melhor os dados coletados anteriormente.",
            needs_collection=False,
            should_use_memory=True,
            memory_target="last_collection",
            response_strategy="explain_previous_collection_clearly",
            confidence="high",
        )

    if _is_previous_answer_follow_up(message):
        return _result(
            next_action="NO_COLLECTION",
            intent="previous_answer_follow_up",
            user_goal="Receber uma nova explicacao da resposta anterior.",
            needs_collection=False,
            should_use_memory=True,
            memory_target="last_answer",
            response_strategy="explain_previous_answer_clearly",
            confidence="high",
        )

    if _has_any(message, BOT_FUNCTION_TERMS):
        return _result(
            next_action="NO_COLLECTION",
            intent="bot_function_question",
            user_goal="Entender o que o assistente consegue fazer.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="explain_bot_capabilities",
            confidence="high",
        )

    if _is_greeting_like(message):
        return _result(
            next_action="NO_COLLECTION",
            intent="greeting",
            user_goal="Cumprimentar o assistente.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="greet_and_offer_help",
            confidence="high",
        )

    if _is_short_term_message(message, THANKS_TERMS):
        return _result(
            next_action="NO_COLLECTION",
            intent="thanks",
            user_goal="Agradecer ao assistente.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="acknowledge_and_offer_next_step",
            confidence="high",
        )

    if _is_short_term_message(message, FEEDBACK_TERMS):
        return _result(
            next_action="NO_COLLECTION",
            intent="user_feedback",
            user_goal="Comentar positivamente sobre a conversa ou simulacao.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="acknowledge_and_offer_next_step",
            confidence="high",
        )

    if _is_short_term_message(message, SMALL_TALK_TERMS):
        return _result(
            next_action="NO_COLLECTION",
            intent="small_talk",
            user_goal="Manter uma interacao breve de conversa.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="acknowledge_and_offer_next_step",
            confidence="high",
        )

    if _has_any(message, OUT_OF_SCOPE_TERMS):
        return _result(
            next_action="NO_COLLECTION",
            intent="out_of_scope_request",
            user_goal="Pedir algo fora do escopo juridico informativo.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="polite_scope_redirect",
            confidence="high",
        )

    if _is_legal_general_question(message):
        return _result(
            next_action="NO_COLLECTION",
            intent="legal_general_question",
            user_goal="Entender um termo ou tema juridico de forma geral.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="answer_legal_general_question",
            confidence="high",
        )

    return None


def _build_prompt(input_json: dict) -> str:
    """Monta prompt curto para classificar a proxima acao."""
    return f"""
Voce classifica a mensagem e decide o proximo passo. Nao responda ao usuario.
Nao consulte processo. Nao valide numero. Nao invente numero.

Regras:
- REQUEST_COLLECTION somente quando o usuario pedir consulta/andamento/situacao/detalhes de processo especifico e houver possible_process_number.
- ASK_CLARIFICATION quando o usuario quiser consultar processo, mas faltar numero CNJ.
- NO_COLLECTION para saudacao, agradecimento, elogio, pergunta juridica geral, follow-up, pergunta sobre o bot e pedido fora do escopo.
- Nao solicite coleta apenas porque a palavra "processo" apareceu.
- should_use_memory=true quando o usuario se referir ao que foi dito ou coletado antes.

Responda neste JSON:
{{
  "next_action": "NO_COLLECTION",
  "intent": "legal_general_question",
  "user_goal": "descreva em uma frase o que o usuario quer",
  "needs_collection": false,
  "should_use_memory": false,
  "memory_target": null,
  "response_strategy": "answer_legal_general_question",
  "collection_request": null,
  "missing_information": [],
  "confidence": "medium"
}}

Valores permitidos:
next_action: NO_COLLECTION, REQUEST_COLLECTION, ASK_CLARIFICATION
intent: {", ".join(sorted(ALLOWED_INTENTS))}
memory_target: last_collection, last_answer, last_reasoning, null
response_strategy: {", ".join(sorted(ALLOWED_RESPONSE_STRATEGIES))}
confidence: low, medium, high

Entrada:
{json.dumps(input_json, ensure_ascii=False, indent=2)}

Retorne apenas JSON valido. Nao use markdown. Nao escreva fora do JSON.
""".strip()


def _safe_fallback(reason: str, input_json: dict | None = None) -> dict:
    """Contrato seguro quando o modelo falha ou retorna JSON invalido."""
    input_json = input_json or {}
    possible_process_number = input_json.get("possible_process_number")
    message = _fold_text(
        input_json.get("normalized_message") or input_json.get("raw_message")
    )

    if _asks_for_process_lookup(message, possible_process_number):
        if possible_process_number:
            return _result(
                next_action="REQUEST_COLLECTION",
                intent="process_lookup_request",
                user_goal="Consultar dados simulados de um processo especifico.",
                needs_collection=True,
                should_use_memory=False,
                memory_target=None,
                response_strategy="explain_collected_process_data",
                collection_request={
                    "type": "process_lookup",
                    "process_number_raw": possible_process_number,
                },
                confidence="low",
            )

        return _result(
            next_action="ASK_CLARIFICATION",
            intent="process_lookup_request",
            user_goal="Consultar andamento ou detalhes de um processo.",
            needs_collection=False,
            should_use_memory=False,
            memory_target=None,
            response_strategy="ask_for_process_number",
            missing_information=[reason, "Informe o numero do processo no formato CNJ."],
            confidence="low",
        )

    return _result(
        next_action="NO_COLLECTION",
        intent="unclear",
        user_goal="Mensagem nao classificada com seguranca.",
        needs_collection=False,
        should_use_memory=False,
        memory_target=None,
        response_strategy="ask_clarification",
        missing_information=[reason],
        confidence="low",
    )


def _normalize_result(parsed_json: dict, input_json: dict) -> dict:
    """Garante que a saida respeite o contrato esperado pelo fluxo."""
    if parsed_json.get("error") is True:
        return _safe_fallback(
            "Nao foi possivel interpretar a resposta do agente.",
            input_json,
        )

    next_action = parsed_json.get("next_action")
    intent = parsed_json.get("intent")
    confidence = parsed_json.get("confidence")
    memory_target = parsed_json.get("memory_target")
    response_strategy = parsed_json.get("response_strategy")
    possible_process_number = input_json.get("possible_process_number")
    message = _fold_text(
        input_json.get("normalized_message") or input_json.get("raw_message")
    )

    if next_action not in ALLOWED_NEXT_ACTIONS:
        next_action = "NO_COLLECTION"

    if intent not in ALLOWED_INTENTS:
        intent = "unclear"

    if confidence not in ALLOWED_CONFIDENCE:
        confidence = "low"

    if memory_target not in ALLOWED_MEMORY_TARGETS:
        memory_target = None

    if response_strategy not in ALLOWED_RESPONSE_STRATEGIES:
        response_strategy = "ask_clarification"

    if next_action == "REQUEST_COLLECTION":
        if not _asks_for_process_lookup(message, possible_process_number):
            next_action = "NO_COLLECTION"
            intent = "unclear" if intent == "process_lookup_request" else intent
            response_strategy = "ask_clarification"
        elif not possible_process_number:
            next_action = "ASK_CLARIFICATION"
            intent = "process_lookup_request"
            response_strategy = "ask_for_process_number"

    if next_action == "ASK_CLARIFICATION" and intent != "process_lookup_request":
        if _asks_for_process_lookup(message, possible_process_number):
            intent = "process_lookup_request"
            response_strategy = "ask_for_process_number"
        else:
            next_action = "NO_COLLECTION"

    should_use_memory = bool(parsed_json.get("should_use_memory"))
    if intent == "process_follow_up":
        should_use_memory = True
        memory_target = "last_collection"
        response_strategy = "explain_previous_collection_clearly"
    elif intent == "previous_answer_follow_up":
        should_use_memory = True
        memory_target = "last_answer"
        response_strategy = "explain_previous_answer_clearly"

    collection_request = None
    if next_action == "REQUEST_COLLECTION":
        collection_request = {
            "type": "process_lookup",
            "process_number_raw": possible_process_number,
        }

    missing_information = parsed_json.get("missing_information")
    if not isinstance(missing_information, list):
        missing_information = []
    if next_action == "ASK_CLARIFICATION" and not missing_information:
        missing_information = ["Informe o numero do processo no formato CNJ."]

    return _result(
        next_action=next_action,
        intent=intent,
        user_goal=parsed_json.get("user_goal")
        or "Interpretar a mensagem dentro do escopo juridico informativo.",
        needs_collection=next_action == "REQUEST_COLLECTION",
        should_use_memory=should_use_memory,
        memory_target=memory_target,
        response_strategy=response_strategy,
        collection_request=collection_request,
        missing_information=missing_information,
        confidence=confidence,
    )


def run_context_agent(input_json: dict) -> dict:
    """Classifica a entrada e decide a proxima acao do fluxo."""
    deterministic = _deterministic_result(input_json)
    if deterministic:
        return deterministic

    prompt = _build_prompt(input_json)

    try:
        llm_response = call_ollama(prompt)
    except RuntimeError as exc:
        return _safe_fallback(str(exc), input_json)

    parsed_json = extract_json_from_text(llm_response)
    return _normalize_result(parsed_json, input_json)


if __name__ == "__main__":
    example_input = {
        "raw_message": "Quero saber o andamento do processo 0000000-00.0000.0.00.0000",
        "normalized_message": "Quero saber o andamento do processo 0000000-00.0000.0.00.0000",
        "possible_process_number": "0000000-00.0000.0.00.0000",
        "notes": [],
    }

    print(json.dumps(run_context_agent(example_input), ensure_ascii=False, indent=2))
