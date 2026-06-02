"""Agente de raciocinio juridico informativo.

Organiza um plano de resposta com fatos, interpretacoes, incertezas e limites.
Ele nao escreve a resposta final amigavel e nao consulta fontes externas.
"""

import json
import unicodedata

from ..llm.ollama_client import call_ollama
from ..utils.json_tools import extract_json_from_text


SAFETY_NOTICE = (
    "Informacao geral. Nao substitui analise juridica profissional ou "
    "consulta oficial."
)
DEFAULT_TONE = "natural, claro, profissional e tranquilo"
ALLOWED_RESPONSE_TYPES = {
    "greeting",
    "small_talk",
    "user_feedback",
    "thanks",
    "bot_function",
    "legal_general_answer",
    "process_lookup",
    "follow_up_collection",
    "follow_up_previous_answer",
    "out_of_scope_redirect",
    "ask_process_number",
    "clarification",
}


def _fold_text(value: str) -> str:
    """Normaliza texto para comparacoes simples."""
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _stringify_item(value) -> str:
    """Converte itens de listas do LLM em texto simples."""
    if isinstance(value, dict):
        for key in ("point", "interpretation", "fact", "description", "message"):
            if value.get(key):
                return str(value[key])
        return json.dumps(value, ensure_ascii=False)

    return str(value)


def _as_list(value) -> list:
    """Garante listas simples no contrato de saida."""
    if isinstance(value, list):
        return [_stringify_item(item) for item in value if item is not None]
    if value is None:
        return []
    return [_stringify_item(value)]


def _plan(
    *,
    response_type: str,
    user_goal: str,
    summary: str,
    known_facts: list | None = None,
    possible_interpretation: list | None = None,
    missing_or_uncertain_points: list | None = None,
    what_to_answer: list | None = None,
    what_not_to_say: list | None = None,
    safety_notice_needed: bool = False,
    extra: dict | None = None,
) -> dict:
    """Monta o contrato estruturado do plano de resposta."""
    result = {
        "response_type": response_type,
        "user_goal": user_goal,
        "summary": summary,
        "known_facts": known_facts or [],
        "possible_interpretation": possible_interpretation or [],
        "missing_or_uncertain_points": missing_or_uncertain_points or [],
        "what_to_answer": what_to_answer or [],
        "what_not_to_say": what_not_to_say or [],
        "tone": DEFAULT_TONE,
        "safety_notice_needed": safety_notice_needed,
        "safety_notice": SAFETY_NOTICE,
    }
    if extra:
        result.update(extra)
    return result


def _process_details(
    process_number_result: dict | None,
    collected_data: dict,
) -> dict:
    """Extrai detalhes mockados de processo em formato estavel."""
    process_number = (
        collected_data.get("process_number")
        or (process_number_result or {}).get("normalized")
        or "numero nao informado"
    )

    movement_texts = []
    for movement in (collected_data.get("movements") or [])[:3]:
        if not isinstance(movement, dict):
            continue
        date = movement.get("date") or "data nao informada"
        description = movement.get("description") or "descricao nao informada"
        movement_texts.append(f"{date}: {description}")

    warnings = _as_list(collected_data.get("warnings")) or [
        "Os dados sao simulados e nao vieram de fonte oficial."
    ]

    return {
        "process_number": process_number,
        "court": collected_data.get("court") or "tribunal nao informado",
        "process_class": collected_data.get("process_class") or "classe nao informada",
        "status": collected_data.get("status") or "status nao informado",
        "movements": movement_texts,
        "warnings": warnings,
        "source": collected_data.get("source") or "mock",
    }


def _process_lookup_reasoning(
    context_decision: dict,
    process_number_result: dict | None,
    collected_data: dict,
) -> dict:
    """Monta plano deterministico para dados mockados de processo."""
    details = _process_details(process_number_result, collected_data)

    known_facts = [
        f"Numero consultado: {details['process_number']}.",
        f"Fonte: dados simulados ({details['source']}).",
        f"Tribunal: {details['court']}.",
        f"Classe: {details['process_class']}.",
        f"Status informado nos dados simulados: {details['status']}.",
    ]
    if details["movements"]:
        known_facts.append(
            "Movimentacoes recentes nos dados simulados: "
            + " | ".join(details["movements"])
        )

    return _plan(
        response_type="process_lookup",
        user_goal=context_decision.get("user_goal")
        or "Consultar dados simulados de um processo especifico.",
        summary=(
            "Consulta simulada encontrada para o processo "
            f"{details['process_number']}."
        ),
        known_facts=known_facts,
        possible_interpretation=[
            "A leitura inicial deve se limitar aos dados mockados exibidos.",
            "Movimentacoes indicam registros no historico, nao resultado final.",
        ],
        missing_or_uncertain_points=details["warnings"],
        what_to_answer=[
            "Explicar o status em linguagem simples.",
            "Listar as movimentacoes recentes sem transformar isso em promessa juridica.",
            "Deixar claro que os dados sao simulados.",
        ],
        what_not_to_say=[
            "Nao afirmar decisao final.",
            "Nao prometer resultado juridico.",
            "Nao dizer que houve consulta oficial.",
        ],
        safety_notice_needed=True,
        extra={"process_details": details},
    )


def _follow_up_collection_reasoning(
    user_input: dict,
    context_decision: dict,
    process_number_result: dict | None,
    collected_data: dict | None,
) -> dict:
    """Monta plano para explicar a ultima coleta em linguagem simples."""
    if not isinstance(collected_data, dict) or collected_data.get("error") is True:
        return _plan(
            response_type="clarification",
            user_goal=context_decision.get("user_goal")
            or "Entender dados coletados anteriormente.",
            summary="O usuario pediu follow-up da coleta, mas nao ha coleta na memoria.",
            missing_or_uncertain_points=[
                "Nao encontrei dados de coleta anteriores nesta sessao."
            ],
            what_to_answer=[
                "Explicar que e preciso consultar um processo antes para comentar a coleta."
            ],
            what_not_to_say=["Nao inventar dados de processo."],
            safety_notice_needed=False,
        )

    lookup_plan = _process_lookup_reasoning(
        context_decision,
        process_number_result,
        collected_data,
    )
    details = lookup_plan["process_details"]

    return _plan(
        response_type="follow_up_collection",
        user_goal=context_decision.get("user_goal")
        or "Entender melhor os dados coletados anteriormente.",
        summary="O usuario pediu uma explicacao clara sobre a ultima coleta.",
        known_facts=lookup_plan["known_facts"],
        possible_interpretation=[
            (
                "Em termos simples, a coleta simulada mostra um processo com "
                f"status '{details['status']}' e movimentacoes registradas."
            ),
            "A movimentacao mais recente costuma ser o melhor ponto de partida.",
        ],
        missing_or_uncertain_points=details["warnings"],
        what_to_answer=[
            "Explicar que status e movimentacoes sao pistas do momento processual.",
            "Traduzir os dados para linguagem leiga.",
            "Separar o que aparece no mock do que nao da para concluir.",
        ],
        what_not_to_say=[
            "Nao listar JSON bruto.",
            "Nao afirmar resultado do processo.",
            "Nao fingir que houve consulta oficial.",
        ],
        safety_notice_needed=True,
        extra={
            "process_details": details,
            "user_request": user_input.get("normalized_message")
            or user_input.get("raw_message"),
        },
    )


def _previous_answer_follow_up_reasoning(
    context_decision: dict,
    session_memory: dict | None,
) -> dict:
    """Monta plano para explicar a resposta anterior."""
    session_memory = session_memory or {}
    previous_answer = (
        session_memory.get("last_final_response")
        or session_memory.get("last_answer")
        or ""
    )
    last_reasoning = session_memory.get("last_legal_reasoning") or {}
    safety_needed = bool(last_reasoning.get("safety_notice_needed"))

    if not previous_answer:
        return _plan(
            response_type="clarification",
            user_goal=context_decision.get("user_goal")
            or "Receber nova explicacao da resposta anterior.",
            summary="O usuario pediu follow-up, mas nao ha resposta anterior na memoria.",
            missing_or_uncertain_points=[
                "Nao encontrei uma resposta anterior nesta sessao para reformular."
            ],
            what_to_answer=[
                "Pedir que o usuario indique qual ponto quer que seja explicado."
            ],
            safety_notice_needed=False,
        )

    return _plan(
        response_type="follow_up_previous_answer",
        user_goal=context_decision.get("user_goal")
        or "Receber uma explicacao mais clara da resposta anterior.",
        summary="O usuario pediu para reformular ou explicar a resposta anterior.",
        known_facts=["Existe uma resposta anterior disponivel na memoria curta."],
        possible_interpretation=[
            "O usuario quer a mesma informacao em linguagem mais simples."
        ],
        what_to_answer=[
            "Reformular a resposta anterior em linguagem mais direta.",
            "Evitar detalhes internos sobre agentes, JSON ou normalizacao.",
        ],
        what_not_to_say=["Nao inventar informacao nova."],
        safety_notice_needed=safety_needed,
        extra={
            "previous_answer": previous_answer,
            "previous_reasoning": last_reasoning,
        },
    )


def _ask_process_number_reasoning(
    context_decision: dict,
    process_number_result: dict | None,
) -> dict:
    """Monta plano deterministico para pedir dado faltante."""
    missing_information = _as_list(context_decision.get("missing_information"))
    if process_number_result:
        missing_information.extend(_as_list(process_number_result.get("errors")))
    if not missing_information:
        missing_information = ["Informe o numero do processo no formato CNJ."]

    return _plan(
        response_type="ask_process_number",
        user_goal=context_decision.get("user_goal")
        or "Consultar andamento ou detalhes de um processo.",
        summary="Falta numero CNJ valido para consultar o processo.",
        missing_or_uncertain_points=missing_information,
        what_to_answer=[
            "Pedir o numero CNJ de forma simples.",
            "Mostrar o formato esperado: 0000000-00.0000.0.00.0000.",
        ],
        what_not_to_say=[
            "Nao chamar a coleta.",
            "Nao sugerir que ha dados do processo sem numero valido.",
        ],
        safety_notice_needed=False,
    )


def _bot_function_reasoning(context_decision: dict) -> dict:
    """Monta plano sobre a funcao do assistente."""
    return _plan(
        response_type="bot_function",
        user_goal=context_decision.get("user_goal")
        or "Entender o que o assistente consegue fazer.",
        summary="O usuario perguntou sobre a funcao do assistente.",
        known_facts=[
            "O assistente e um chatbot juridico informativo.",
            "Ele pode ajudar com duvidas juridicas gerais.",
            "Nesta PoC, ele consulta dados simulados de processo pelo numero CNJ.",
        ],
        missing_or_uncertain_points=[
            "Esta versao nao faz consulta oficial em tribunais."
        ],
        what_to_answer=[
            "Explicar capacidades em linguagem direta.",
            "Dizer que a consulta processual e simulada.",
        ],
        what_not_to_say=["Nao prometer consulta oficial ou orientacao profissional."],
        safety_notice_needed=False,
    )


def _greeting_reasoning(context_decision: dict) -> dict:
    """Monta plano para saudacao simples."""
    return _plan(
        response_type="greeting",
        user_goal=context_decision.get("user_goal") or "Cumprimentar o assistente.",
        summary="O usuario fez uma saudacao.",
        known_facts=["O assistente pode ajudar dentro do escopo juridico informativo."],
        what_to_answer=[
            "Cumprimentar de forma natural.",
            "Oferecer ajuda com duvida juridica geral ou consulta simulada por CNJ.",
        ],
        what_not_to_say=[
            "Nao pedir numero de processo.",
            "Nao inserir aviso juridico nesta saudacao.",
        ],
        safety_notice_needed=False,
    )


def _feedback_reasoning(context_decision: dict, response_type: str) -> dict:
    """Monta plano para elogio, agradecimento ou conversa curta."""
    if response_type == "thanks":
        summary = "O usuario agradeceu."
        what_to_answer = [
            "Responder de forma breve e simpatica.",
            "Oferecer proximo passo dentro do escopo juridico.",
        ]
    elif response_type == "user_feedback":
        summary = "O usuario fez um elogio ou comentario positivo."
        what_to_answer = [
            "Reconhecer o comentario de forma natural.",
            "Oferecer explicar dados coletados ou seguir com outra duvida juridica.",
        ]
    else:
        summary = "O usuario fez uma interacao casual curta."
        what_to_answer = [
            "Responder de forma breve.",
            "Manter o foco disponivel para duvida juridica ou consulta simulada.",
        ]

    return _plan(
        response_type=response_type,
        user_goal=context_decision.get("user_goal") or "Interagir brevemente.",
        summary=summary,
        known_facts=["Nao ha pedido de consulta processual nesta mensagem."],
        what_to_answer=what_to_answer,
        what_not_to_say=[
            "Nao pedir numero CNJ.",
            "Nao inserir aviso juridico.",
            "Nao chamar coleta.",
        ],
        safety_notice_needed=False,
    )


def _out_of_scope_reasoning(context_decision: dict) -> dict:
    """Monta plano para pedido fora do escopo."""
    return _plan(
        response_type="out_of_scope_redirect",
        user_goal=context_decision.get("user_goal")
        or "Pedir algo fora do escopo juridico informativo.",
        summary="O pedido foge do papel do assistente nesta PoC.",
        known_facts=["O assistente deve permanecer no escopo juridico informativo."],
        what_to_answer=[
            "Recusar gentilmente a parte fora do escopo.",
            "Redirecionar para duvidas juridicas, termos juridicos ou consulta simulada por CNJ.",
        ],
        what_not_to_say=[
            "Nao contar piada ou responder a tarefa fora do escopo.",
            "Nao pedir numero CNJ.",
            "Nao inserir aviso juridico.",
        ],
        safety_notice_needed=False,
    )


def _legal_general_reasoning(user_input: dict, context_decision: dict) -> dict:
    """Monta plano para duvida juridica geral."""
    message = _fold_text(
        user_input.get("normalized_message") or user_input.get("raw_message")
    )

    what_to_answer = [
        "Responder de forma informativa e simples.",
        "Nao depender de coleta de processo.",
        "Separar significado geral de aplicacao ao caso concreto.",
    ]
    possible_interpretation = [
        "A pergunta parece ser sobre conceito juridico geral."
    ]

    if "juntada" in message and "petic" in message:
        possible_interpretation = [
            "O usuario quer entender o termo 'juntada de peticao'."
        ]
        what_to_answer = [
            (
                "Explicar que juntada de peticao normalmente significa que uma "
                "peticao ou documento foi anexado aos autos."
            ),
            "Dizer que a juntada, sozinha, nao significa decisao final.",
            "Explicar que o efeito depende do conteudo da peticao e do contexto do processo.",
        ]

    return _plan(
        response_type="legal_general_answer",
        user_goal=context_decision.get("user_goal")
        or "Entender um termo ou tema juridico de forma geral.",
        summary="O usuario fez uma duvida juridica geral.",
        known_facts=["Nao ha necessidade de coleta processual para responder."],
        possible_interpretation=possible_interpretation,
        missing_or_uncertain_points=[
            "Sem dados de um caso concreto, a resposta deve ficar no nivel informativo."
        ],
        what_to_answer=what_to_answer,
        what_not_to_say=[
            "Nao inventar lei, artigo ou prazo.",
            "Nao prometer resultado juridico.",
            "Nao afirmar efeito processual especifico sem dados do caso.",
        ],
        safety_notice_needed=True,
    )


def _clarification_reasoning(context_decision: dict) -> dict:
    """Monta plano para mensagem pouco clara."""
    return _plan(
        response_type="clarification",
        user_goal=context_decision.get("user_goal")
        or "Continuar a conversa dentro do escopo juridico informativo.",
        summary="A mensagem nao ficou clara o suficiente para uma resposta especifica.",
        missing_or_uncertain_points=_as_list(
            context_decision.get("missing_information")
        ),
        what_to_answer=[
            "Pedir que o usuario detalhe se quer duvida juridica geral ou consulta simulada de processo."
        ],
        what_not_to_say=["Nao chamar coleta sem numero CNJ e pedido claro."],
        safety_notice_needed=False,
    )


def _deterministic_reasoning(
    user_input: dict,
    context_decision: dict,
    process_number_result: dict | None,
    collected_data: dict | None,
    session_memory: dict | None,
) -> dict | None:
    """Resolve fluxos fechados sem depender de geracao livre."""
    next_action = context_decision.get("next_action")
    intent = context_decision.get("intent")

    if (
        next_action == "REQUEST_COLLECTION"
        and isinstance(collected_data, dict)
        and collected_data.get("error") is not True
    ):
        return _process_lookup_reasoning(
            context_decision,
            process_number_result,
            collected_data,
        )

    if intent == "process_follow_up":
        return _follow_up_collection_reasoning(
            user_input,
            context_decision,
            process_number_result,
            collected_data,
        )

    if intent == "previous_answer_follow_up":
        return _previous_answer_follow_up_reasoning(context_decision, session_memory)

    if next_action == "ASK_CLARIFICATION":
        return _ask_process_number_reasoning(context_decision, process_number_result)

    if intent == "greeting":
        return _greeting_reasoning(context_decision)

    if intent == "bot_function_question":
        return _bot_function_reasoning(context_decision)

    if intent in {"small_talk", "user_feedback", "thanks"}:
        return _feedback_reasoning(context_decision, intent)

    if intent == "out_of_scope_request":
        return _out_of_scope_reasoning(context_decision)

    if intent == "legal_general_question":
        return _legal_general_reasoning(user_input, context_decision)

    if intent == "unclear":
        return _clarification_reasoning(context_decision)

    return None


def _build_prompt(
    user_input: dict,
    context_decision: dict,
    process_number_result: dict | None,
    collected_data: dict | None,
    session_memory: dict | None,
) -> str:
    """Monta prompt curto para organizar o plano tecnico."""
    payload = {
        "user_input": user_input,
        "context_decision": context_decision,
        "process_number_result": process_number_result,
        "collected_data": collected_data,
        "session_memory": session_memory or {},
    }

    return f"""
Voce organiza um plano de resposta juridica informativa em JSON.
Nao escreva a resposta final ao usuario.

Regras:
- Use apenas os dados recebidos.
- Separe fatos, interpretacao e incertezas.
- Nao invente leis, artigos, prazos, decisoes ou resultados.
- Nao fale sobre agentes internos, normalizacao ou JSON.
- safety_notice_needed deve ser true apenas para duvida juridica, processo ou explicacao de processo.

Responda neste JSON:
{{
  "response_type": "legal_general_answer",
  "user_goal": "objetivo do usuario",
  "summary": "resumo do cenario",
  "known_facts": [],
  "possible_interpretation": [],
  "missing_or_uncertain_points": [],
  "what_to_answer": [],
  "what_not_to_say": [],
  "tone": "natural, claro, profissional e tranquilo",
  "safety_notice_needed": true,
  "safety_notice": "{SAFETY_NOTICE}"
}}

response_type permitido: {", ".join(sorted(ALLOWED_RESPONSE_TYPES))}

Dados:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Retorne apenas JSON valido. Nao use markdown. Nao escreva fora do JSON.
""".strip()


def _safe_fallback(reason: str) -> dict:
    """Contrato seguro quando o LLM falha ou retorna algo inutilizavel."""
    return _plan(
        response_type="clarification",
        user_goal="Continuar a conversa com mais informacoes.",
        summary="Nao foi possivel organizar a analise com seguranca.",
        missing_or_uncertain_points=[reason],
        what_to_answer=[
            "Pedir que o usuario reformule a duvida ou informe os dados principais."
        ],
        what_not_to_say=["Nao inventar informacoes ausentes."],
        safety_notice_needed=False,
    )


def _normalize_result(parsed_json: dict) -> dict:
    """Garante que o dict final tenha todas as chaves esperadas."""
    if parsed_json.get("error") is True:
        return _safe_fallback("Nao foi possivel interpretar a resposta do agente.")

    response_type = parsed_json.get("response_type")
    if response_type not in ALLOWED_RESPONSE_TYPES:
        response_type = "clarification"

    return _plan(
        response_type=response_type,
        user_goal=parsed_json.get("user_goal") or "Responder ao usuario.",
        summary=parsed_json.get("summary")
        or "Plano informativo baseado nos dados disponiveis.",
        known_facts=_as_list(parsed_json.get("known_facts")),
        possible_interpretation=_as_list(parsed_json.get("possible_interpretation")),
        missing_or_uncertain_points=_as_list(
            parsed_json.get("missing_or_uncertain_points")
        ),
        what_to_answer=_as_list(parsed_json.get("what_to_answer")),
        what_not_to_say=_as_list(parsed_json.get("what_not_to_say")),
        safety_notice_needed=bool(parsed_json.get("safety_notice_needed")),
        extra={
            "tone": parsed_json.get("tone") or DEFAULT_TONE,
            "safety_notice": parsed_json.get("safety_notice") or SAFETY_NOTICE,
        },
    )


def run_legal_reasoning_agent(
    user_input: dict,
    context_decision: dict,
    process_number_result: dict | None = None,
    collected_data: dict | None = None,
    session_memory: dict | None = None,
) -> dict:
    """Organiza um plano informativo e seguro com base no contexto."""
    deterministic = _deterministic_reasoning(
        user_input=user_input,
        context_decision=context_decision,
        process_number_result=process_number_result,
        collected_data=collected_data,
        session_memory=session_memory,
    )
    if deterministic:
        return deterministic

    prompt = _build_prompt(
        user_input=user_input,
        context_decision=context_decision,
        process_number_result=process_number_result,
        collected_data=collected_data,
        session_memory=session_memory,
    )

    try:
        llm_response = call_ollama(prompt)
    except RuntimeError as exc:
        return _safe_fallback(str(exc))

    parsed_json = extract_json_from_text(llm_response)
    return _normalize_result(parsed_json)


if __name__ == "__main__":
    example_user_input = {
        "raw_message": "Quero saber o andamento do processo 0000000-00.0000.0.00.0000",
        "normalized_message": "Quero saber o andamento do processo 0000000-00.0000.0.00.0000",
        "possible_process_number": "0000000-00.0000.0.00.0000",
        "notes": [],
    }
    example_context = {
        "next_action": "REQUEST_COLLECTION",
        "intent": "process_lookup_request",
        "user_goal": "Consultar dados simulados de um processo especifico.",
        "needs_collection": True,
        "should_use_memory": False,
        "memory_target": None,
        "response_strategy": "explain_collected_process_data",
        "collection_request": {
            "type": "process_lookup",
            "process_number_raw": "0000000-00.0000.0.00.0000",
        },
        "missing_information": [],
        "confidence": "high",
    }

    print(
        json.dumps(
            run_legal_reasoning_agent(example_user_input, example_context),
            ensure_ascii=False,
            indent=2,
        )
    )
