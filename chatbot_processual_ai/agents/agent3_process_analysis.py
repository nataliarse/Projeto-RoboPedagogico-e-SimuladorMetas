import copy
import json
import re
import unicodedata
from typing import Any

from ollama_client import OllamaError, generate_text
from prompts.agent3_prompt import AGENT3_SYSTEM_PROMPT, build_agent3_prompt


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
    "document_content",
    "legal_concept_with_case_context",
    "generic_process_question",
}
DEFAULT_QUESTION_FOCUS = "generic_process_question"
MODEL_BACKED_INTENTS = {
    "process_lookup",
    "process_question",
    "legal_general_question",
}
NON_MODEL_ANALYSIS_TYPES = {
    "missing_process_context",
    "insufficient_data",
    "greeting",
    "out_of_scope",
    "unclear",
}
FACT_SOURCE_RE = re.compile(
    r"^(processo|partes_interessadas|movimentacoes|documentos|pendencias|coleta)"
    r"($|[.\[])"
)
MAX_CONVERSATION_FOR_MODEL = 8
INTERNAL_TERMS = {"agente", "prompt", "ollama", "json"}


def analyze_process_context(message: str, context_data: dict) -> dict:
    if not isinstance(context_data, dict):
        context_data = {}

    intent_data = context_data.get("intent_data")
    if not isinstance(intent_data, dict):
        intent_data = {}

    intent = intent_data.get("intent")
    active_process = context_data.get("active_process")
    if not isinstance(active_process, dict):
        active_process = {}

    sanitized_process = _sanitize_process_for_model(active_process)
    analysis_type = _target_analysis_type(intent, active_process, context_data)
    fallback = _build_deterministic_analysis(
        message,
        analysis_type,
        context_data,
        sanitized_process,
    )
    fallback = _normalize_analysis_output(fallback)

    if intent not in MODEL_BACKED_INTENTS or analysis_type in NON_MODEL_ANALYSIS_TYPES:
        return fallback

    try:
        prompt = build_agent3_prompt(
            message=message,
            intent_data=intent_data,
            conversation=_recent_conversation(context_data),
            sanitized_process=sanitized_process,
            analysis_type=analysis_type,
        )
        response = generate_text(prompt, system_prompt=AGENT3_SYSTEM_PROMPT)
        model_analysis = _parse_model_json(response)
        validated = _validate_model_analysis(model_analysis)
        _reject_unsafe_model_analysis(validated, active_process)
        return _normalize_analysis_output(validated)
    except (OllamaError, ValueError, TypeError, json.JSONDecodeError):
        return fallback


def cpf_cnpj_removed_from_model_context(context_data: dict) -> bool:
    if not isinstance(context_data, dict):
        return True

    active_process = context_data.get("active_process")
    if not isinstance(active_process, dict):
        return True

    original_documents = _party_document_values(active_process)
    sanitized_process = _sanitize_process_for_model(active_process)
    sanitized_text = json.dumps(sanitized_process, ensure_ascii=False)

    no_party_document_fields = all(
        "documento" not in party
        for party in sanitized_process.get("partes_interessadas", [])
        if isinstance(party, dict)
    )
    no_private_values = all(
        document not in sanitized_text for document in original_documents
    )
    return no_party_document_fields and no_private_values


def _target_analysis_type(
    intent: Any,
    active_process: dict,
    context_data: dict,
) -> str:
    collection_status = context_data.get("collection_status")

    if intent == "process_lookup":
        if collection_status in {"missing_number", "not_found"}:
            return "insufficient_data"
        if _has_active_process(active_process):
            return "process_summary"
        return "insufficient_data"

    if intent == "process_question":
        if _has_active_process(active_process):
            return "process_question"
        return "missing_process_context"

    if intent == "legal_general_question":
        return "legal_general_explanation"

    if _has_active_process(active_process) and _looks_like_active_process_question(
        context_data.get("message")
    ):
        return "process_question"

    if intent == "greeting":
        return "greeting"

    if intent == "out_of_scope":
        return "out_of_scope"

    return "unclear"


def _build_deterministic_analysis(
    message: str,
    analysis_type: str,
    context_data: dict,
    process: dict,
) -> dict:
    if analysis_type == "process_summary":
        return _process_summary_analysis(process)

    if analysis_type == "process_question":
        return _process_question_analysis(
            message,
            process,
            _recent_conversation(context_data),
        )

    if analysis_type == "legal_general_explanation":
        return _legal_general_analysis(message, process)

    if analysis_type == "missing_process_context":
        return {
            "analysis_type": "missing_process_context",
            "facts": [],
            "explanation": "Não há processo ativo disponível para responder à pergunta.",
            "limitations": [
                "É necessário consultar um processo antes de analisar informações específicas."
            ],
            "response_focus": (
                "Solicitar o número completo do processo ou orientar o usuário a "
                "realizar uma consulta."
            ),
        }

    if analysis_type == "insufficient_data":
        return _insufficient_data_analysis(context_data)

    if analysis_type == "greeting":
        return {
            "analysis_type": "greeting",
            "facts": [],
            "explanation": "A mensagem é uma saudação ou abertura de conversa.",
            "limitations": [],
            "response_focus": "Cumprimentar o usuário e indicar que é possível consultar ou explicar informações processuais.",
        }

    if analysis_type == "out_of_scope":
        return {
            "analysis_type": "out_of_scope",
            "facts": [],
            "explanation": "A mensagem não trata de consulta processual nem de conceito jurídico-processual geral.",
            "limitations": [
                "O escopo atual cobre apenas análise processual com dados disponíveis e explicações processuais gerais."
            ],
            "response_focus": "Informar de forma breve que o pedido está fora do escopo atual.",
        }

    return {
        "analysis_type": "unclear",
        "facts": [],
        "explanation": "A mensagem não trouxe informação suficiente para identificar a análise necessária.",
        "limitations": [
            "É necessário mais contexto para decidir se o usuário quer consultar processo, perguntar sobre processo ativo ou pedir explicação geral."
        ],
        "response_focus": "Pedir uma reformulação objetiva da solicitação.",
    }


def _process_summary_analysis(process: dict) -> dict:
    process_data = _dict_value(process.get("processo"))
    facts: list[dict[str, str]] = []

    _add_fact(facts, "Número do processo", process_data.get("numero"), "processo.numero")
    _add_fact(facts, "Assunto", process_data.get("assunto"), "processo.assunto")
    _add_fact(
        facts,
        "Órgão julgador",
        process_data.get("orgao_julgador"),
        "processo.orgao_julgador",
    )
    _add_fact(
        facts,
        "Situação processual",
        process_data.get("situacao"),
        "processo.situacao",
    )

    latest = _latest_movement(process)
    if latest is not None:
        index, movement = latest
        _add_fact(
            facts,
            "Última movimentação",
            _movement_summary(movement),
            f"movimentacoes[{index}]",
        )

    number = process_data.get("numero") or "o processo consultado"
    situation = process_data.get("situacao")
    explanation = f"Foram encontrados dados para {number}."
    if situation:
        explanation += f" A situação registrada é {situation}."
    if latest is not None:
        explanation += " A movimentação mais recente disponível foi destacada nos fatos."

    limitations = _standard_limitations(process)
    if not facts:
        limitations.append("Não há campos processuais suficientes para resumir o processo.")

    return {
        "analysis_type": "process_summary",
        "question_focus": "process_overview",
        "target_event": None,
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Apresentar somente situação, última movimentação e um contexto relevante do processo.",
    }


def _process_question_analysis(
    message: str,
    process: dict,
    conversation: list | None = None,
) -> dict:
    normalized = _normalize_text(message)

    if _is_process_overview_question(normalized):
        return _process_summary_analysis(process)

    if _is_current_status_question(normalized):
        return _situation_question_analysis(process)

    if _is_timeline_before_event_question(normalized):
        target_event = _target_event_from_message(message, conversation or [])
        return _timeline_before_event_analysis(process, target_event)

    if _is_legal_concept_with_case_context_question(normalized):
        return _legal_general_analysis(message, process)

    if _has_any(normalized, {"parte", "partes", "reclamante", "reclamado"}):
        return _parties_question_analysis(process)

    if _has_any(normalized, {"pendencia", "pendencias", "pendente"}):
        return _pending_question_analysis(process)

    if _is_document_content_question(normalized):
        return _sentence_question_analysis(process)

    if "arquiv" in normalized:
        return _archive_question_analysis(process)

    if "moviment" in normalized and _has_any(normalized, {"ultima", "recente"}):
        return _latest_movement_question_analysis(process)

    if "situacao" in normalized:
        return _situation_question_analysis(process)

    return _generic_process_question_analysis(process)


def _is_process_overview_question(normalized_message: str) -> bool:
    return (
        "resum" in normalized_message
        or "o que esta acontecendo" in normalized_message
        or "como esta esse processo" in normalized_message
        or "como esta o processo" in normalized_message
        or "situacao geral" in normalized_message
        or "situacao do processo" in normalized_message
    )


def _looks_like_active_process_question(message: Any) -> bool:
    normalized = _normalize_text(message)
    if not normalized:
        return False

    if (
        _is_process_overview_question(normalized)
        or _is_current_status_question(normalized)
        or _is_timeline_before_event_question(normalized)
        or _is_legal_concept_with_case_context_question(normalized)
        or _is_document_content_question(normalized)
    ):
        return True

    return (
        "processo" in normalized
        or "arquiv" in normalized
        or "moviment" in normalized
        or "sentenc" in normalized
        or ("transito" in normalized and "julgado" in normalized)
        or _has_any(normalized, {"parte", "partes", "pendencia", "pendencias"})
    )


def _is_current_status_question(normalized_message: str) -> bool:
    return (
        "aberto" in normalized_message
        or "em andamento" in normalized_message
        or "situacao atual" in normalized_message
        or "ja terminou" in normalized_message
        or "terminou" in normalized_message
        or "encerrado" in normalized_message
        or "baixado" in normalized_message
    )


def _is_timeline_before_event_question(normalized_message: str) -> bool:
    before_markers = (
        "antes do",
        "antes da",
        "antes de",
        "antes disso",
        "veio antes",
        "ocorreu antes",
        "aconteceu antes",
    )
    return any(marker in normalized_message for marker in before_markers)


def _is_legal_concept_with_case_context_question(normalized_message: str) -> bool:
    if "transito" not in normalized_message or "julgado" not in normalized_message:
        return False
    return any(
        marker in normalized_message
        for marker in (
            "nesse caso",
            "neste caso",
            "nesse processo",
            "neste processo",
            "desse processo",
            "do processo",
            "isso no processo",
        )
    )


def _is_document_content_question(normalized_message: str) -> bool:
    return (
        _has_any(normalized_message, {"sentenca", "decisao", "decidiu"})
        or "favoravel" in normalized_message
        or "quem ganhou" in normalized_message
        or "ganhou" in normalized_message
    )


def _target_event_from_message(message: str, conversation: list) -> str | None:
    detected = _detect_target_event(_normalize_text(message))
    if detected:
        return detected

    for entry in reversed(conversation[:-1]):
        if not isinstance(entry, dict):
            continue
        if entry.get("role") != "user":
            continue
        detected = _detect_target_event(_normalize_text(entry.get("message")))
        if detected:
            return detected

    return None


def _detect_target_event(normalized_message: str) -> str | None:
    if "transito" in normalized_message and "julgado" in normalized_message:
        return "trânsito em julgado"
    if "arquiv" in normalized_message:
        return "arquivamento"
    if "sentenc" in normalized_message:
        return "sentença"
    if "audienc" in normalized_message:
        return "audiência"
    if "distribu" in normalized_message:
        return "distribuição"
    return None


def _parties_question_analysis(process: dict) -> dict:
    parties = _list_value(process.get("partes_interessadas"))
    facts: list[dict[str, str]] = []

    for index, party in enumerate(parties):
        if not isinstance(party, dict):
            continue

        details = [
            _string_value(party.get("nome")),
            _label_value("tipo", party.get("tipo")),
            _label_value("polo", party.get("polo")),
        ]
        representatives = _list_value(party.get("representantes"))
        if representatives:
            details.append("representantes: " + ", ".join(map(str, representatives)))

        value = " | ".join(detail for detail in details if detail)
        label = party.get("tipo") or party.get("polo") or "Parte"
        _add_fact(facts, str(label), value, f"partes_interessadas[{index}]")

    if facts:
        explanation = "A coleta registrou as partes interessadas listadas nos fatos, sem uso de CPF ou CNPJ."
        limitations = ["CPF e CNPJ das partes não são usados na análise."]
    else:
        explanation = "A coleta não trouxe partes interessadas para o processo ativo."
        limitations = ["Não há dados de partes interessadas disponíveis na coleta."]

    return {
        "analysis_type": "process_question",
        "question_focus": "parties",
        "target_event": None,
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Listar as partes registradas na coleta, omitindo qualquer CPF ou CNPJ.",
    }


def _pending_question_analysis(process: dict) -> dict:
    pending_items = _list_value(process.get("pendencias"))
    facts: list[dict[str, str]] = []

    if pending_items:
        for index, item in enumerate(pending_items):
            _add_fact(
                facts,
                f"Pendência {index + 1}",
                _format_value(item),
                f"pendencias[{index}]",
            )
        explanation = "A coleta registrou as pendências listadas nos fatos."
        limitations = ["A análise usa somente o campo pendencias disponibilizado pela coleta."]
    else:
        _add_fact(
            facts,
            "Pendências registradas",
            "Nenhuma pendência registrada na coleta.",
            "pendencias",
        )
        explanation = "A coleta não registrou pendências no campo pendencias."
        limitations = [
            "A ausência de pendências na coleta não garante inexistência de qualquer pendência jurídica real."
        ]

    return {
        "analysis_type": "process_question",
        "question_focus": "pending_issues",
        "target_event": None,
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Responder somente com base no campo pendencias da coleta.",
    }


def _sentence_question_analysis(process: dict) -> dict:
    sentence_documents = _matching_documents(process, {"sentenc", "decis"})
    sentence_movements = _matching_movements(process, {"sentenc"})
    facts: list[dict[str, str]] = []

    for index, document in sentence_documents:
        _add_fact(
            facts,
            "Documento de sentença",
            _document_summary(document),
            f"documentos[{index}]",
        )

    for index, movement in sentence_movements:
        _add_fact(
            facts,
            "Movimentação de sentença",
            _movement_summary(movement),
            f"movimentacoes[{index}]",
        )

    if facts:
        explanation = (
            "A coleta registra sentença ou movimentação relacionada, mas não disponibiliza "
            "o conteúdo da decisão. Portanto, não é possível informar o que foi decidido."
        )
        limitations = [
            "Há apenas metadados, como título, tipo, data ou descrição da movimentação.",
            "Sem o teor da decisão, a análise não pode afirmar o conteúdo da sentença.",
        ]
    else:
        explanation = "A coleta não trouxe documento ou movimentação de sentença para o processo ativo."
        limitations = [
            "Não há dados suficientes na coleta para informar se houve sentença ou o que foi decidido."
        ]

    return {
        "analysis_type": "process_question",
        "question_focus": "document_content",
        "target_event": "sentença",
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Informar que há registro de sentença somente se os metadados existirem, sem inventar o conteúdo decisório.",
    }


def _archive_question_analysis(process: dict) -> dict:
    archive_movements = _matching_movements(process, {"arquiv"})
    facts: list[dict[str, str]] = []

    if archive_movements:
        index, movement = archive_movements[-1]
        _add_fact(
            facts,
            "Movimentação de arquivamento",
            _movement_summary(movement),
            f"movimentacoes[{index}]",
        )
        explanation = "A coleta registra movimentação relacionada a arquivamento na data indicada nos fatos."
        limitations = [
            "A análise não presume efeitos jurídicos além do texto da movimentação coletada."
        ]
    else:
        explanation = "A coleta não contém movimentação relacionada a arquivamento."
        limitations = [
            "Sem movimentação de arquivamento na coleta, não é possível informar quando o processo foi arquivado."
        ]

    return {
        "analysis_type": "process_question",
        "question_focus": "generic_process_question",
        "target_event": "arquivamento",
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Indicar a movimentação de arquivamento encontrada, sem inferir encerramento definitivo por conta própria.",
    }


def _timeline_before_event_analysis(process: dict, target_event: str | None) -> dict:
    facts: list[dict[str, str]] = []

    if not target_event:
        return {
            "analysis_type": "process_question",
            "question_focus": "timeline_before_event",
            "target_event": None,
            "facts": facts,
            "explanation": "Não foi possível identificar o evento solicitado para localizar a movimentação anterior.",
            "limitations": [
                "A pergunta precisa indicar qual evento deve ser usado como referência."
            ],
            "response_focus": "Pedir que o usuário informe o evento de referência.",
        }

    previous = _movement_before_event(process, target_event)
    if previous is not None:
        index, movement = previous
        _add_fact(
            facts,
            "Movimentação anterior",
            _movement_summary(movement),
            f"movimentacoes[{index}]",
        )
        explanation = (
            f"Foi localizada a movimentação imediatamente anterior ao evento {target_event}."
        )
        limitations = [
            "A análise usa a ordem das movimentações fornecidas nos dados disponíveis."
        ]
    else:
        explanation = (
            f"Não foi encontrada movimentação anterior ao evento {target_event} nos dados disponíveis."
        )
        limitations = [
            "Sem uma movimentação anterior ordenada, não é possível informar o que ocorreu antes do evento."
        ]

    return {
        "analysis_type": "process_question",
        "question_focus": "timeline_before_event",
        "target_event": target_event,
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Informar somente a movimentação imediatamente anterior ao evento solicitado.",
    }


def _latest_movement_question_analysis(process: dict) -> dict:
    facts: list[dict[str, str]] = []
    latest = _latest_movement(process)

    if latest is not None:
        index, movement = latest
        _add_fact(
            facts,
            "Última movimentação",
            _movement_summary(movement),
            f"movimentacoes[{index}]",
        )
        explanation = "A última movimentação foi identificada pela maior ordem disponível na coleta."
        limitations = [
            "A análise depende da ordenação e dos dados de movimentação fornecidos pela coleta."
        ]
    else:
        explanation = "A coleta não trouxe movimentações para o processo ativo."
        limitations = ["Não há movimentações disponíveis para identificar a última movimentação."]

    return {
        "analysis_type": "process_question",
        "question_focus": "latest_movement",
        "target_event": None,
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Informar a movimentação mais recente disponível na coleta.",
    }


def _situation_question_analysis(process: dict) -> dict:
    process_data = _dict_value(process.get("processo"))
    facts: list[dict[str, str]] = []

    _add_fact(
        facts,
        "Situação processual",
        process_data.get("situacao"),
        "processo.situacao",
    )

    latest = _latest_movement(process)
    if latest is not None:
        index, movement = latest
        _add_fact(
            facts,
            "Última movimentação",
            _movement_summary(movement),
            f"movimentacoes[{index}]",
        )

    if process_data.get("situacao"):
        explanation = "A situação atual disponível na coleta é a registrada no campo processo.situacao."
        limitations = [
            "A análise não conclui encerramento definitivo sem base expressa nos dados coletados."
        ]
    else:
        explanation = "A coleta não trouxe o campo de situação processual."
        limitations = ["Sem processo.situacao, não é possível informar a situação atual."]

    return {
        "analysis_type": "process_question",
        "question_focus": "current_status",
        "target_event": None,
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Responder sobre a situação registrada e, se útil, citar a última movimentação coletada.",
    }


def _generic_process_question_analysis(process: dict) -> dict:
    process_data = _dict_value(process.get("processo"))
    facts: list[dict[str, str]] = []
    _add_fact(facts, "Número do processo", process_data.get("numero"), "processo.numero")
    _add_fact(
        facts,
        "Situação processual",
        process_data.get("situacao"),
        "processo.situacao",
    )

    latest = _latest_movement(process)
    if latest is not None:
        index, movement = latest
        _add_fact(
            facts,
            "Última movimentação",
            _movement_summary(movement),
            f"movimentacoes[{index}]",
        )

    return {
        "analysis_type": "process_question",
        "question_focus": "generic_process_question",
        "target_event": None,
        "facts": facts,
        "explanation": "Não foi identificado um detalhe processual específico para responder com precisão.",
        "limitations": [
            "A pergunta não indicou com clareza um campo específico para analisar."
        ],
        "response_focus": "Responder de forma conservadora e pedir reformulação se a dúvida específica não ficar clara.",
    }


def _legal_general_analysis(message: str, process: dict) -> dict:
    normalized = _normalize_text(message)
    concept = _detect_legal_concept(normalized)
    explanation = _legal_concept_explanation(concept)
    facts = _related_process_facts_for_concept(concept, process)
    question_focus = (
        "legal_concept_with_case_context"
        if facts
        else DEFAULT_QUESTION_FOCUS
    )
    target_event = _target_event_for_concept(concept) if facts else None

    limitations = [
        "A explicação é geral e não define estratégia, prazo, risco ou resultado para um caso individual."
    ]
    if facts:
        limitations.append(
            "O dado específico citado vem somente da coleta disponível e deve ser separado da explicação conceitual."
        )
    else:
        limitations.append(
            "Nenhum dado específico do processo ativo foi necessário ou encontrado para a explicação."
        )

    return {
        "analysis_type": "legal_general_explanation",
        "question_focus": question_focus,
        "target_event": target_event,
        "facts": facts,
        "explanation": explanation,
        "limitations": limitations,
        "response_focus": "Explicar o conceito de forma geral e separar qualquer dado específico encontrado na coleta.",
    }


def _insufficient_data_analysis(context_data: dict) -> dict:
    collection_status = context_data.get("collection_status")
    facts: list[dict[str, str]] = []

    if collection_status:
        facts.append(
            {
                "label": "Situação da coleta",
                "value": str(collection_status),
                "source": "collection_status",
            }
        )

    if collection_status == "not_found":
        explanation = "A coleta local não encontrou dados para o processo informado."
    elif collection_status == "missing_number":
        explanation = "Não foi informado um número de processo completo para consulta."
    else:
        explanation = "Não há dados processuais suficientes para produzir a análise solicitada."

    return {
        "analysis_type": "insufficient_data",
        "facts": facts,
        "explanation": explanation,
        "limitations": [
            "Sem dados de um processo ativo ou encontrado, a análise não pode inferir situação, partes, movimentações ou documentos."
        ],
        "response_focus": "Solicitar um número de processo completo ou informar que a consulta local não encontrou dados.",
    }


def _sanitize_process_for_model(process: dict) -> dict:
    if not isinstance(process, dict):
        return {}

    sanitized = copy.deepcopy(process)
    parties = sanitized.get("partes_interessadas")
    if isinstance(parties, list):
        for party in parties:
            if isinstance(party, dict):
                party.pop("documento", None)

    documents = sanitized.get("documentos")
    if isinstance(documents, list):
        for document in documents:
            if isinstance(document, dict):
                document.pop("id_documento", None)

    return sanitized


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
        raise ValueError("Resposta do modelo nao e um objeto JSON.")

    return data


def _normalize_analysis_output(analysis: dict) -> dict:
    if not isinstance(analysis, dict):
        analysis = {}

    normalized = dict(analysis)
    normalized["question_focus"] = _validated_question_focus(
        normalized.get("question_focus")
    )
    normalized["target_event"] = _validated_target_event(
        normalized.get("target_event")
    )
    return normalized


def _validated_question_focus(value: Any) -> str:
    if isinstance(value, str) and value.strip() in ALLOWED_QUESTION_FOCUS:
        return value.strip()
    return DEFAULT_QUESTION_FOCUS


def _validated_target_event(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None

    text = value.strip()
    return text or None


def _validate_model_analysis(response: dict[str, Any]) -> dict:
    analysis_type = response.get("analysis_type")
    if analysis_type not in ALLOWED_ANALYSIS_TYPES:
        raise ValueError("analysis_type invalido.")

    facts = response.get("facts")
    if not isinstance(facts, list):
        raise ValueError("facts invalido.")

    validated_facts = []
    for fact in facts:
        if not isinstance(fact, dict):
            raise ValueError("fact invalido.")

        label = fact.get("label")
        value = fact.get("value")
        source = fact.get("source")
        if not all(isinstance(item, str) for item in (label, value, source)):
            raise ValueError("campos do fact invalidos.")
        if not label.strip() or not value.strip() or not source.strip():
            raise ValueError("fact vazio.")
        if not FACT_SOURCE_RE.search(source.strip()):
            raise ValueError("source do fact nao aponta para caminho real do processo.")

        validated_facts.append(
            {
                "label": label.strip(),
                "value": value.strip(),
                "source": source.strip(),
            }
        )

    explanation = response.get("explanation")
    limitations = response.get("limitations")
    response_focus = response.get("response_focus")

    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError("explanation invalido.")
    if not isinstance(limitations, list) or not all(
        isinstance(item, str) for item in limitations
    ):
        raise ValueError("limitations invalido.")
    if not isinstance(response_focus, str) or not response_focus.strip():
        raise ValueError("response_focus invalido.")

    return {
        "analysis_type": analysis_type,
        "question_focus": _validated_question_focus(response.get("question_focus")),
        "target_event": _validated_target_event(response.get("target_event")),
        "facts": validated_facts,
        "explanation": explanation.strip(),
        "limitations": [item.strip() for item in limitations if item.strip()],
        "response_focus": response_focus.strip(),
    }


def _reject_unsafe_model_analysis(analysis: dict, active_process: dict) -> None:
    if _analysis_contains_party_documents(analysis, active_process):
        raise ValueError("Resposta contem documento de parte.")

    text = json.dumps(analysis, ensure_ascii=False).lower()
    if any(term in text for term in INTERNAL_TERMS):
        raise ValueError("Resposta menciona detalhes internos.")


def _analysis_contains_party_documents(analysis: dict, active_process: dict) -> bool:
    text = json.dumps(analysis, ensure_ascii=False)
    return any(document in text for document in _party_document_values(active_process))


def _party_document_values(process: dict) -> list[str]:
    documents = []
    parties = process.get("partes_interessadas")
    if not isinstance(parties, list):
        return documents

    for party in parties:
        if not isinstance(party, dict):
            continue
        document = party.get("documento")
        if document is not None:
            value = str(document).strip()
            if value:
                documents.append(value)

    return documents


def _recent_conversation(context_data: dict) -> list:
    conversation = context_data.get("conversation")
    if not isinstance(conversation, list):
        return []

    return conversation[-MAX_CONVERSATION_FOR_MODEL:]


def _has_active_process(process: dict) -> bool:
    return isinstance(process.get("processo"), dict) and bool(process.get("processo"))


def _dict_value(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _list_value(value: Any) -> list:
    return value if isinstance(value, list) else []


def _string_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _label_value(label: str, value: Any) -> str:
    text = _string_value(value)
    if not text:
        return ""
    return f"{label}: {text}"


def _add_fact(
    facts: list[dict[str, str]],
    label: str,
    value: Any,
    source: str,
) -> None:
    if value is None:
        return

    formatted = _format_value(value)
    if not formatted:
        return

    facts.append(
        {
            "label": str(label),
            "value": formatted,
            "source": source,
        }
    )


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _format_date(value: Any) -> str:
    text = _format_value(value)
    if "T" in text:
        return text.split("T", 1)[0]
    return text


def _movement_summary(movement: dict) -> str:
    parts = [
        _label_value("ordem", movement.get("ordem")),
        _label_value("data", _format_date(movement.get("data"))),
        _string_value(movement.get("descricao")),
        _label_value("complemento", movement.get("complemento")),
    ]
    return " | ".join(part for part in parts if part)


def _document_summary(document: dict) -> str:
    parts = [
        _label_value("data", _format_date(document.get("data"))),
        _label_value("titulo", document.get("titulo")),
        _label_value("tipo", document.get("tipo")),
    ]
    return " | ".join(part for part in parts if part)


def _latest_movement(process: dict) -> tuple[int, dict] | None:
    movements = _ordered_movements(process)
    if not movements:
        return None

    return movements[-1]


def _ordered_movements(process: dict) -> list[tuple[int, dict]]:
    movements = [
        (index, movement)
        for index, movement in enumerate(_list_value(process.get("movimentacoes")))
        if isinstance(movement, dict)
    ]
    return sorted(movements, key=lambda item: _movement_sort_key(item[1]))


def _movement_before_event(process: dict, target_event: str) -> tuple[int, dict] | None:
    movements = _ordered_movements(process)
    event_position = None

    for position, (_index, movement) in enumerate(movements):
        if _movement_matches_event(movement, target_event):
            event_position = position

    if event_position is None or event_position == 0:
        return None

    return movements[event_position - 1]


def _movement_matches_event(movement: dict, target_event: str) -> bool:
    normalized_event = _normalize_text(target_event)
    searchable = _normalize_text(
        " ".join(
            _format_value(movement.get(field))
            for field in ("descricao", "complemento", "referencia")
        )
    )

    if normalized_event == "arquivamento":
        return "arquiv" in searchable
    if normalized_event == "transito em julgado":
        return "transito" in searchable and "julgado" in searchable
    if normalized_event == "sentenca":
        return "sentenc" in searchable
    if normalized_event == "audiencia":
        return "audienc" in searchable
    if normalized_event == "distribuicao":
        return "distribu" in searchable

    event_terms = [term for term in normalized_event.split() if term]
    return bool(event_terms) and all(term in searchable for term in event_terms)


def _movement_sort_key(movement: dict) -> tuple[int, str]:
    order = movement.get("ordem")
    if isinstance(order, int):
        return (order, _format_value(movement.get("data")))
    if isinstance(order, str) and order.isdigit():
        return (int(order), _format_value(movement.get("data")))
    return (-1, _format_value(movement.get("data")))


def _matching_movements(process: dict, terms: set[str]) -> list[tuple[int, dict]]:
    matches = []
    for index, movement in enumerate(_list_value(process.get("movimentacoes"))):
        if not isinstance(movement, dict):
            continue

        searchable = _normalize_text(
            " ".join(
                _format_value(movement.get(field))
                for field in ("descricao", "complemento", "referencia")
            )
        )
        if any(term in searchable for term in terms):
            matches.append((index, movement))

    return sorted(matches, key=lambda item: _movement_sort_key(item[1]))


def _matching_documents(process: dict, terms: set[str]) -> list[tuple[int, dict]]:
    matches = []
    for index, document in enumerate(_list_value(process.get("documentos"))):
        if not isinstance(document, dict):
            continue

        searchable = _normalize_text(
            " ".join(
                _format_value(document.get(field))
                for field in ("titulo", "tipo", "data")
            )
        )
        if any(term in searchable for term in terms):
            matches.append((index, document))

    return matches


def _standard_limitations(process: dict) -> list[str]:
    limitations = ["A análise usa somente os dados disponibilizados pela coleta local."]

    documents = _list_value(process.get("documentos"))
    has_document_content = any(
        isinstance(document, dict)
        and any(document.get(field) for field in ("conteudo", "texto", "teor"))
        for document in documents
    )
    if documents and not has_document_content:
        limitations.append(
            "A coleta registra metadados de documentos, mas não disponibiliza o conteúdo integral deles."
        )

    return limitations


def _detect_legal_concept(normalized_message: str) -> str:
    if "transito" in normalized_message and "julgado" in normalized_message:
        return "transito_julgado"
    if "arquiv" in normalized_message:
        return "arquivamento"
    if "audienc" in normalized_message:
        return "audiencia"
    if "sentenc" in normalized_message:
        return "sentenca"
    if "reclamante" in normalized_message or "reclamado" in normalized_message:
        return "partes_trabalhistas"
    return "geral"


def _legal_concept_explanation(concept: str) -> str:
    explanations = {
        "transito_julgado": (
            "Trânsito em julgado indica que não há mais recurso cabível dentro do prazo aplicável."
        ),
        "arquivamento": (
            "Arquivamento é o registro de que os autos foram guardados ou baixados "
            "no sistema após determinada fase processual. O alcance desse registro "
            "depende dos dados concretos do processo."
        ),
        "audiencia": (
            "Audiência é um ato processual em que o juízo pode ouvir partes, "
            "testemunhas ou tratar de conciliação e andamento do processo."
        ),
        "sentenca": (
            "Sentença é um ato decisório do juízo. Para saber o que foi decidido "
            "em um processo específico, é necessário ter acesso ao conteúdo da decisão."
        ),
        "partes_trabalhistas": (
            "Em processos trabalhistas, reclamante costuma ser quem apresenta a "
            "reclamação, e reclamado é quem responde à reclamação."
        ),
        "geral": (
            "A pergunta pede uma explicação jurídico-processual geral, mas o conceito "
            "específico não foi identificado com segurança."
        ),
    }
    return explanations[concept]


def _target_event_for_concept(concept: str) -> str | None:
    events = {
        "transito_julgado": "trânsito em julgado",
        "arquivamento": "arquivamento",
        "audiencia": "audiência",
        "sentenca": "sentença",
    }
    return events.get(concept)


def _related_process_facts_for_concept(concept: str, process: dict) -> list[dict[str, str]]:
    if not _has_active_process(process):
        return []

    facts: list[dict[str, str]] = []

    if concept == "transito_julgado":
        movements = _matching_movements(process, {"transito", "julgado"})
        if movements:
            index, movement = movements[-1]
            _add_fact(
                facts,
                "Movimentação relacionada",
                _movement_summary(movement),
                f"movimentacoes[{index}]",
            )
        return facts

    if concept == "arquivamento":
        movements = _matching_movements(process, {"arquiv"})
        if movements:
            index, movement = movements[-1]
            _add_fact(
                facts,
                "Movimentação relacionada",
                _movement_summary(movement),
                f"movimentacoes[{index}]",
            )
        return facts

    if concept == "audiencia":
        movements = _matching_movements(process, {"audienc"})
        for index, movement in movements:
            _add_fact(
                facts,
                "Movimentação relacionada",
                _movement_summary(movement),
                f"movimentacoes[{index}]",
            )
        return facts

    if concept == "sentenca":
        for index, document in _matching_documents(process, {"sentenc"}):
            _add_fact(
                facts,
                "Documento relacionado",
                _document_summary(document),
                f"documentos[{index}]",
            )
        return facts

    return facts


def _normalize_text(text: Any) -> str:
    lowered = _format_value(text).lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


def _has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)
