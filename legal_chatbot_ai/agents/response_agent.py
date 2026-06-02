"""Agente de resposta final.

Transforma o plano tecnico do agente de raciocinio em uma resposta clara,
humana e segura para o usuario. Nao chama requests diretamente.
"""

import json
import re
import unicodedata

from ..llm.ollama_client import call_ollama


SAFETY_NOTICE = (
    "Informacao geral. Nao substitui analise juridica profissional ou "
    "consulta oficial."
)


def _fold_text(value: str) -> str:
    """Normaliza texto para comparacoes sem acento."""
    normalized = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _compact_text(value: str) -> str:
    """Remove pontuacao/espacos extras para comparacoes aproximadas."""
    return re.sub(r"[^a-z0-9]+", " ", _fold_text(value)).strip()


def _contains_safety_notice(final_text: str) -> bool:
    """Detecta aviso mesmo com pequenas variacoes de texto."""
    compact = _compact_text(final_text)
    return "nao substitui" in compact and (
        "consulta oficial" in compact or "analise juridica" in compact
    )


def _is_low_value_response(final_text: str) -> bool:
    """Identifica resposta que so repetiu aviso juridico."""
    if not _contains_safety_notice(final_text):
        return False

    compact = _compact_text(final_text)
    safety_compact = _compact_text(SAFETY_NOTICE)
    return len(compact) <= len(safety_compact) + 40


def _stringify_item(value) -> str:
    """Converte itens heterogeneos em texto simples."""
    if isinstance(value, dict):
        for key in ("point", "interpretation", "fact", "description", "message"):
            if value.get(key):
                return str(value[key])
        return json.dumps(value, ensure_ascii=False)

    return str(value)


def _as_list(value) -> list:
    """Converte campos opcionais em listas simples para montar fallback."""
    if isinstance(value, list):
        return [_stringify_item(item) for item in value if item is not None]
    if value is None:
        return []
    return [_stringify_item(value)]


def _append_safety_notice(final_text: str, reasoning_json: dict) -> str:
    """Inclui aviso juridico somente quando o plano pedir."""
    if reasoning_json.get("safety_notice_needed") is not True:
        return final_text

    if _contains_safety_notice(final_text):
        return final_text

    safety_notice = reasoning_json.get("safety_notice") or SAFETY_NOTICE
    return f"{final_text}\n\n{safety_notice}"


def _format_process_lookup_response(reasoning_json: dict) -> str:
    """Monta resposta final para consulta mockada de processo."""
    details = reasoning_json.get("process_details") or {}
    process_number = details.get("process_number") or "informado"
    court = details.get("court")
    process_class = details.get("process_class")
    status = details.get("status")

    paragraphs = [
        (
            f"Encontrei uma consulta simulada para o processo {process_number}. "
            "Pelo mock, o ponto principal e olhar o status e as movimentacoes, "
            "porque eles indicam o momento aparente do processo na simulacao."
        )
    ]

    status_parts = []
    if court:
        status_parts.append(f"tribunal: {court}")
    if process_class:
        status_parts.append(f"classe: {process_class}")
    if status:
        status_parts.append(f"status: {status}")
    if status_parts:
        paragraphs.append("Os dados mostram " + "; ".join(status_parts) + ".")

    movements = _as_list(details.get("movements"))
    if movements:
        paragraphs.append(
            "As movimentacoes mais recentes aparecem assim:\n- "
            + "\n- ".join(movements)
        )
        paragraphs.append(
            "Isso nao significa, sozinho, que houve decisao final. Significa "
            "apenas que existem registros recentes de andamento nos dados simulados."
        )

    warnings = _as_list(
        details.get("warnings") or reasoning_json.get("missing_or_uncertain_points")
    )
    if warnings:
        paragraphs.append("Observacao: " + " ".join(warnings))

    return _append_safety_notice("\n\n".join(paragraphs), reasoning_json)


def _format_follow_up_collection_response(reasoning_json: dict) -> str:
    """Monta resposta final explicando a ultima coleta em linguagem simples."""
    details = reasoning_json.get("process_details") or {}
    process_number = details.get("process_number") or "informado"
    status = details.get("status") or "status nao informado"
    court = details.get("court")
    process_class = details.get("process_class")
    movements = _as_list(details.get("movements"))

    paragraphs = [
        (
            f"Em linguagem simples: a coleta simulada encontrou o processo "
            f"{process_number} e ele aparece como {status}."
        )
    ]

    context_parts = []
    if court:
        context_parts.append(f"ele esta associado a {court}")
    if process_class:
        context_parts.append(f"a classe informada e {process_class}")
    if context_parts:
        paragraphs.append("Tambem aparece que " + " e ".join(context_parts) + ".")

    if movements:
        paragraphs.append(
            "A lista de movimentacoes funciona como um historico dos ultimos "
            "acontecimentos registrados:\n- "
            + "\n- ".join(movements)
        )

    paragraphs.append(
        "Pelo mock, da para entender o andamento aparente, mas nao da para "
        "concluir resultado do processo nem tratar isso como consulta oficial."
    )

    warnings = _as_list(
        details.get("warnings") or reasoning_json.get("missing_or_uncertain_points")
    )
    if warnings:
        paragraphs.append("Observacao: " + " ".join(warnings))

    return _append_safety_notice("\n\n".join(paragraphs), reasoning_json)


def _format_ask_process_number_response() -> str:
    """Monta resposta final pedindo numero de processo."""
    return (
        "Para consultar um processo, preciso que voce informe o numero no "
        "formato CNJ. Exemplo: 0000000-00.0000.0.00.0000."
    )


def _format_bot_function_response() -> str:
    """Monta resposta final sobre a funcao do assistente."""
    return (
        "Eu sou um chatbot juridico informativo. Posso ajudar com duvidas "
        "juridicas gerais, explicar termos em linguagem simples e, nesta PoC, "
        "fazer uma consulta simulada de processo quando voce informa o numero CNJ.\n\n"
        "Nesta versao eu nao faco consulta oficial em tribunais, nem substituo "
        "analise profissional."
    )


def _format_greeting_response() -> str:
    """Monta resposta final para saudacao simples."""
    return (
        "Ola! Tudo certo por aqui. Posso te ajudar com uma duvida juridica "
        "geral ou com uma consulta simulada de processo pelo numero CNJ."
    )


def _format_feedback_response(response_type: str) -> str:
    """Monta resposta curta para elogio, agradecimento ou conversa casual."""
    if response_type == "thanks":
        return (
            "Por nada. Quando quiser, posso ajudar com uma duvida juridica "
            "geral, explicar um termo ou consultar um processo simulado pelo CNJ."
        )

    if response_type == "user_feedback":
        return (
            "Que bom! Essa simulacao ja mostra o fluxo principal funcionando. "
            "Posso explicar melhor os dados coletados ou ajudar com outra duvida juridica."
        )

    return (
        "Certo. Posso seguir te ajudando com uma duvida juridica geral, uma "
        "explicacao de termo ou uma consulta simulada por numero CNJ."
    )


def _format_out_of_scope_response() -> str:
    """Monta resposta final para pedido fora do escopo."""
    return (
        "Essa parte foge um pouco do meu papel aqui. Eu sou um assistente "
        "juridico informativo, entao funciono melhor ajudando com duvidas "
        "juridicas, explicacao de termos ou consulta simulada de processo por "
        "numero CNJ."
    )


def _format_legal_general_response(reasoning_json: dict) -> str:
    """Monta resposta final para duvida juridica geral."""
    combined = _fold_text(
        " ".join(
            _as_list(reasoning_json.get("possible_interpretation"))
            + _as_list(reasoning_json.get("what_to_answer"))
            + [reasoning_json.get("summary") or ""]
        )
    )

    if "juntada" in combined and "petic" in combined:
        answer = (
            "Juntada de peticao, em geral, significa que uma peticao ou documento "
            "foi anexado aos autos do processo.\n\n"
            "Isso, sozinho, nao quer dizer que o juiz decidiu algo ou que houve "
            "resultado final. Normalmente quer dizer apenas que aquele documento "
            "passou a fazer parte do processo e podera ser analisado conforme o "
            "andamento do caso.\n\n"
            "O efeito pratico depende do conteudo da peticao e do contexto do processo."
        )
        return _append_safety_notice(answer, reasoning_json)

    what_to_answer = _as_list(reasoning_json.get("what_to_answer"))
    if what_to_answer:
        answer = (
            "Posso explicar em termos gerais: "
            + " ".join(item.rstrip(".") + "." for item in what_to_answer)
        )
    else:
        answer = (
            "Posso responder essa duvida de forma geral, mas sem afirmar efeito "
            "especifico para um caso concreto sem ver os dados do processo."
        )

    return _append_safety_notice(answer, reasoning_json)


def _format_previous_answer_follow_up(reasoning_json: dict) -> str:
    """Reformula a resposta anterior em linguagem simples."""
    previous_answer = str(reasoning_json.get("previous_answer") or "").strip()
    if not previous_answer:
        return (
            "Nao encontrei uma resposta anterior nesta sessao para reformular. "
            "Me diga qual ponto voce quer que eu explique melhor."
        )

    answer = (
        "Claro. Em outras palavras, a ideia principal foi esta:\n\n"
        f"{previous_answer}"
    )
    return _append_safety_notice(answer, reasoning_json)


def _format_clarification_response(reasoning_json: dict) -> str:
    """Monta resposta para mensagem incerta."""
    missing = _as_list(reasoning_json.get("missing_or_uncertain_points"))
    if missing:
        return (
            "Preciso de um pouco mais de contexto para responder bem. "
            + " ".join(missing)
        )

    return (
        "Pode me dizer se voce quer tirar uma duvida juridica geral ou fazer "
        "uma consulta simulada de processo pelo numero CNJ?"
    )


def _deterministic_response(reasoning_json: dict) -> str | None:
    """Responde fluxos fechados sem chamar o modelo."""
    response_type = reasoning_json.get("response_type")

    if response_type == "process_lookup":
        return _format_process_lookup_response(reasoning_json)

    if response_type == "follow_up_collection":
        return _format_follow_up_collection_response(reasoning_json)

    if response_type == "ask_process_number":
        return _format_ask_process_number_response()

    if response_type == "bot_function":
        return _format_bot_function_response()

    if response_type == "greeting":
        return _format_greeting_response()

    if response_type in {"small_talk", "user_feedback", "thanks"}:
        return _format_feedback_response(response_type)

    if response_type == "out_of_scope_redirect":
        return _format_out_of_scope_response()

    if response_type == "legal_general_answer":
        return _format_legal_general_response(reasoning_json)

    if response_type == "follow_up_previous_answer":
        return _format_previous_answer_follow_up(reasoning_json)

    if response_type == "clarification":
        return _format_clarification_response(reasoning_json)

    return None


def _build_prompt(reasoning_json: dict) -> str:
    """Monta prompt curto para gerar a resposta final."""
    safety_rule = (
        "Inclua o aviso juridico do plano."
        if reasoning_json.get("safety_notice_needed") is True
        else "Nao inclua aviso juridico nesta mensagem."
    )

    return f"""
Escreva a resposta final ao usuario com base no reasoning_json.
Use linguagem clara, natural, amigavel e profissional.

Regras:
- Use apenas o reasoning_json.
- Nao invente fatos, leis, artigos, prazos, decisoes ou resultados.
- Nao mencione agentes internos, JSON ou normalizacao.
- Nao peca numero CNJ se o plano nao for ask_process_number.
- {safety_rule}
- Use paragrafos curtos.

reasoning_json:
{json.dumps(reasoning_json, ensure_ascii=False, indent=2)}

Retorne somente o texto final.
""".strip()


def _fallback_response(reasoning_json: dict, error_message: str | None = None) -> str:
    """Resposta segura quando o Ollama falha."""
    deterministic = _deterministic_response(reasoning_json)
    if deterministic:
        return deterministic

    paragraphs = []

    summary = reasoning_json.get("summary")
    if summary:
        paragraphs.append(str(summary))

    known_facts = _as_list(reasoning_json.get("known_facts"))
    if known_facts:
        paragraphs.append("Pelo que aparece nos dados disponiveis, " + " ".join(known_facts))

    interpretations = _as_list(reasoning_json.get("possible_interpretation"))
    if interpretations:
        paragraphs.append("Uma leitura inicial seria: " + " ".join(interpretations))

    missing = _as_list(reasoning_json.get("missing_or_uncertain_points"))
    if missing:
        paragraphs.append("Ainda ha pontos incertos: " + " ".join(missing))

    if error_message and not paragraphs:
        paragraphs.append(
            "Nao foi possivel gerar uma resposta completa agora. "
            "Informe os dados principais da sua duvida para tentar novamente."
        )

    final_text = "\n\n".join(paragraphs)
    return _append_safety_notice(final_text, reasoning_json)


def run_response_agent(reasoning_json: dict) -> str:
    """Gera a resposta final em linguagem natural para o usuario."""
    deterministic = _deterministic_response(reasoning_json)
    if deterministic:
        return deterministic

    prompt = _build_prompt(reasoning_json)

    try:
        response = call_ollama(prompt)
    except RuntimeError as exc:
        return _fallback_response(reasoning_json, str(exc))

    final_text = response.strip()
    if not final_text:
        return _fallback_response(reasoning_json, "Resposta vazia do Ollama.")

    if _is_low_value_response(final_text):
        return _fallback_response(reasoning_json, "Resposta generica do Ollama.")

    return _append_safety_notice(final_text, reasoning_json)


if __name__ == "__main__":
    example_reasoning = {
        "response_type": "legal_general_answer",
        "user_goal": "Entender o que significa juntada de peticao.",
        "summary": "O usuario fez uma duvida juridica geral.",
        "known_facts": [],
        "possible_interpretation": ["O usuario quer entender juntada de peticao."],
        "missing_or_uncertain_points": [],
        "what_to_answer": [],
        "what_not_to_say": [],
        "tone": "natural, claro, profissional e tranquilo",
        "safety_notice_needed": True,
        "safety_notice": SAFETY_NOTICE,
    }

    print(run_response_agent(example_reasoning))
