import re
import unicodedata

from agents.agent1_intent import interpret_user_message
from agents.agent2_context_collection import build_context_and_collect
from agents.agent3_process_analysis import analyze_process_context
from agents.agent4_response import create_user_response
from progress import ProgressReporter, progress_clock, report_progress
from schemas.processual_contracts import ProcessualChatResponse, ProcessualChatStepResult
from services.meta_diagnosis_service import (
    META_IMPACT_INTENT,
    answer_meta_question,
    build_meta_block,
    has_process_number,
    is_meta_question,
)


SAFE_CHAT_ERROR_RESPONSE = (
    "Não consegui processar essa mensagem agora. Tente reformular a pergunta."
)
PROCESSUAL_CHAT_RESPONSE_TYPE = "processual_chat"


def run_processual_chat_step(
    message: str,
    session_state: dict,
    progress_reporter: ProgressReporter | None = None,
) -> ProcessualChatStepResult:
    intent_data: dict = {}
    context_data: dict = {}
    analysis: dict = {}
    stage = "Agente 1"
    stage_code = "intent"
    stage_started_at: float | None = None

    # Pergunta sobre as Metas 1 e 2 a respeito do processo já consultado: a resposta vem das
    # regras determinísticas (autômato + glossário das metas), sem passar pelos agentes.
    active_process = session_state.get("active_process")
    if is_meta_question(message) and not has_process_number(message) and active_process:
        return ProcessualChatStepResult(
            response=_build_processual_chat_response(
                intent_data={"intent": META_IMPACT_INTENT},
                context_data={"active_process": active_process},
                session_state=session_state,
                response=answer_meta_question(message, active_process),
                failed_stage=None,
            ),
            intent_data={"intent": META_IMPACT_INTENT},
            context_data={"active_process": active_process},
            analysis={},
        )

    try:
        stage_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="intent.started",
            level="started",
            message="entendendo a pergunta...",
        )
        intent_data = interpret_user_message(
            message,
            progress_reporter=progress_reporter,
        )
        report_progress(
            progress_reporter,
            code="intent.finished",
            level="success",
            message="intencao identificada.",
            details={
                "intent": intent_data.get("intent"),
                "confidence": intent_data.get("confidence"),
            },
            started_at=stage_started_at,
        )

        stage = "Agente 2"
        stage_code = "context"
        stage_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="context.started",
            level="started",
            message="localizando contexto do processo...",
        )
        context_data = build_context_and_collect(
            message,
            intent_data,
            session_state,
            progress_reporter=progress_reporter,
        )
        report_progress(
            progress_reporter,
            code="context.finished",
            level="success",
            message="contexto preparado.",
            details={
                "collection_status": context_data.get("collection_status"),
                "has_active_process": bool(context_data.get("active_process")),
                "rag_status": _rag_status(context_data),
            },
            started_at=stage_started_at,
        )

        stage = "Agente 3"
        stage_code = "analysis"
        stage_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="analysis.started",
            level="started",
            message="analisando informacoes disponiveis...",
        )
        analysis_message = _message_for_process_analysis(message, intent_data)
        analysis = analyze_process_context(
            analysis_message,
            context_data,
            progress_reporter=progress_reporter,
        )
        report_progress(
            progress_reporter,
            code="analysis.finished",
            level="success",
            message="analise concluida.",
            details={
                "analysis_type": analysis.get("analysis_type"),
                "question_focus": analysis.get("question_focus"),
                "facts_count": _safe_len(analysis.get("facts")),
                "limitations_count": _safe_len(analysis.get("limitations")),
            },
            started_at=stage_started_at,
        )

        stage = "Agente 4"
        stage_code = "response"
        stage_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="response.started",
            level="started",
            message="montando resposta final...",
        )
        response = create_user_response(
            message,
            analysis,
            progress_reporter=progress_reporter,
        )
        report_progress(
            progress_reporter,
            code="response.finished",
            level="success",
            message="resposta pronta.",
            details={"response_length": len(response)},
            started_at=stage_started_at,
        )
    except Exception as exc:
        report_progress(
            progress_reporter,
            code=f"{stage_code}.failed",
            level="error",
            message="falha controlada; preparando resposta segura.",
            details={
                "failed_stage": stage,
                "error_type": type(exc).__name__,
            },
            started_at=stage_started_at,
        )
        return ProcessualChatStepResult(
            response=_build_processual_chat_response(
                intent_data=intent_data,
                context_data=context_data,
                session_state=session_state,
                response=SAFE_CHAT_ERROR_RESPONSE,
                failed_stage=stage,
            ),
            intent_data=intent_data,
            context_data=context_data,
            analysis=analysis,
        )

    response = _append_meta_block(response, intent_data, context_data)

    return ProcessualChatStepResult(
        response=_build_processual_chat_response(
            intent_data=intent_data,
            context_data=context_data,
            session_state=session_state,
            response=response,
            failed_stage=None,
        ),
        intent_data=intent_data,
        context_data=context_data,
        analysis=analysis,
    )


def _build_processual_chat_response(
    *,
    intent_data: dict,
    context_data: dict,
    session_state: dict,
    response: str,
    failed_stage: str | None,
) -> ProcessualChatResponse:
    return ProcessualChatResponse(
        tipo=PROCESSUAL_CHAT_RESPONSE_TYPE,
        intent=_effective_intent(intent_data, context_data),
        resposta=response,
        processo_ativo=_active_process_number(context_data, session_state),
        collection_status=_collection_status(context_data),
        failed_stage=failed_stage,
        rag_status=_rag_status(context_data),
        fontes=_rag_sources(context_data),
    )


def _append_meta_block(response: str, intent_data: dict, context_data: dict) -> str:
    """Na consulta de um processo, acrescenta o diagnóstico das Metas 1 e 2."""
    if _effective_intent(intent_data, context_data) != "process_lookup":
        return response

    active_process = context_data.get("active_process")
    if not isinstance(active_process, dict) or not active_process:
        return response

    meta_block = build_meta_block(active_process)
    if not meta_block:
        return response
    return f"{response}\n\n{meta_block}"


def _effective_intent(intent_data: dict, context_data: dict) -> str | None:
    transported_intent_data = context_data.get("intent_data")
    if isinstance(transported_intent_data, dict):
        transported_intent = transported_intent_data.get("intent")
        if isinstance(transported_intent, str) and transported_intent.strip():
            return transported_intent.strip()

    intent = intent_data.get("intent")
    if isinstance(intent, str) and intent.strip():
        return intent.strip()

    return None


def _collection_status(context_data: dict) -> str | None:
    collection_status = context_data.get("collection_status")
    if isinstance(collection_status, str) and collection_status.strip():
        return collection_status.strip()

    return None


def _rag_status(context_data: dict) -> str | None:
    rag_context = context_data.get("rag_context")
    if not isinstance(rag_context, dict):
        return None

    status = rag_context.get("status")
    if isinstance(status, str) and status.strip():
        return status.strip()
    return None


def _rag_sources(context_data: dict) -> list[dict]:
    rag_context = context_data.get("rag_context")
    if not isinstance(rag_context, dict):
        return []

    sources = rag_context.get("sources")
    if not isinstance(sources, list):
        return []

    return [source for source in sources if isinstance(source, dict)]


def _safe_len(value: object) -> int:
    if isinstance(value, list):
        return len(value)
    return 0


def _active_process_number(context_data: dict, session_state: dict) -> str | None:
    active_process = context_data.get("active_process")
    if not isinstance(active_process, dict) or not active_process:
        active_process = session_state.get("active_process")

    if not isinstance(active_process, dict):
        return None

    process_data = active_process.get("processo")
    if not isinstance(process_data, dict):
        return None

    for field_name in ("numero", "numero_normalizado"):
        process_number = process_data.get(field_name)
        if isinstance(process_number, str) and process_number.strip():
            return process_number.strip()

    return None


def _message_for_process_analysis(message: str, intent_data: dict) -> str:
    if intent_data.get("intent") != "process_question":
        return message

    if _looks_like_party_name_question(message):
        return "Quais sao as partes vinculadas a esse processo?"

    return message


def _looks_like_party_name_question(message: str) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", _normalize_for_match(message)))
    return (
        bool(tokens & {"nome", "nomes"})
        and bool(tokens & {"vinculada", "vinculadas", "vinculado", "vinculados"})
        and "processo" in tokens
    )


def _normalize_for_match(text: str) -> str:
    lowered = str(text).lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )
