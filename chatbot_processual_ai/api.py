from __future__ import annotations

from dataclasses import asdict
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from agents.agent2_context_collection import MAX_CONVERSATION_ENTRIES
from orchestrators.hybrid_orchestrator import run_process_meta_impact
from orchestrators.processual_chat_orchestrator import run_processual_chat_step
from schemas.meta_contracts import MetaSimulationRequest
from services.meta_explanation_service import (
    explain_meta_simulation,
    explain_process_meta_impact,
)
from services.meta_simulator_adapter import (
    InvalidSimulatorSchemaError,
    SimulatorUnavailableError,
    simulate_meta,
)
from session_state import create_session_state


app = FastAPI(title="Chatbot Processual AI")
_SESSIONS: dict[str, dict[str, Any]] = {}


class ProcessualChatHTTPRequest(BaseModel):
    session_id: str | None = None
    mensagem: str

    @field_validator("mensagem")
    @classmethod
    def validate_message_has_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("mensagem deve conter texto")
        return value


class ProcessualChatHTTPResult(BaseModel):
    tipo: Literal["processual_chat"]
    intent: str | None
    resposta: str
    processo_ativo: str | None
    collection_status: str | None
    failed_stage: str | None
    rag_status: str | None
    fontes: list[dict[str, Any]] = Field(default_factory=list)


class ProcessualChatHTTPResponse(BaseModel):
    session_id: str
    resultado: ProcessualChatHTTPResult


class MetaSimulationHTTPRequest(BaseModel):
    session_id: str | None = None
    pergunta_usuario: str | None = None
    meta_id: str
    ano: int
    unidade: str | None = None
    cenario: dict[str, Any] = Field(default_factory=dict)


class ProcessMetaImpactHTTPRequest(BaseModel):
    session_id: str | None = None
    pergunta_usuario: str | None = None
    numero_processo: str
    meta_id: str
    ano: int


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/processos/chat", response_model=ProcessualChatHTTPResponse)
def chat_processual(request: ProcessualChatHTTPRequest) -> ProcessualChatHTTPResponse:
    session_id = _normalize_session_id(request.session_id)
    session_state = _get_session_state(session_id)

    result = run_processual_chat_step(request.mensagem, session_state)
    _register_assistant_message(result.response.resposta, session_state)

    return ProcessualChatHTTPResponse(
        session_id=session_id,
        resultado=ProcessualChatHTTPResult.model_validate(asdict(result.response)),
    )


@app.post("/api/metas/simular")
def simular_meta(request: MetaSimulationHTTPRequest) -> dict[str, Any]:
    session_id = _normalize_session_id(request.session_id)
    _get_session_state(session_id)

    simulation_request = MetaSimulationRequest(
        meta_id=request.meta_id,
        ano=request.ano,
        unidade=request.unidade,
        cenario=request.cenario,
    )
    try:
        simulation_response = simulate_meta(simulation_request)
    except SimulatorUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail="Motor de metas indisponível; nenhum resultado foi calculado.",
        ) from exc
    except InvalidSimulatorSchemaError as exc:
        raise HTTPException(
            status_code=502,
            detail="Resposta inválida do motor de metas; nenhum resultado foi calculado.",
        ) from exc
    explanation = explain_meta_simulation(
        request.pergunta_usuario or "",
        simulation_response,
    )

    return {
        "session_id": session_id,
        "resultado": asdict(simulation_response),
        "explicacao": explanation,
    }


@app.post("/api/metas/impacto-processo")
def impacto_processo_meta(request: ProcessMetaImpactHTTPRequest) -> dict[str, Any]:
    session_id = _normalize_session_id(request.session_id)
    _get_session_state(session_id)

    impact_response = run_process_meta_impact(
        request.numero_processo,
        request.meta_id,
        request.ano,
    )
    explanation = explain_process_meta_impact(
        request.pergunta_usuario or "",
        impact_response,
    )

    return {
        "session_id": session_id,
        "resultado": asdict(impact_response),
        "explicacao": explanation,
    }


def _normalize_session_id(session_id: str | None) -> str:
    if isinstance(session_id, str) and session_id.strip():
        return session_id.strip()
    return str(uuid4())


def _get_session_state(session_id: str) -> dict[str, Any]:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = create_session_state()
    return _SESSIONS[session_id]


def _register_assistant_message(response: str, session_state: dict[str, Any]) -> None:
    conversation = session_state.setdefault("conversation", [])
    conversation.append(
        {
            "role": "assistant",
            "message": response,
        }
    )
    del conversation[:-MAX_CONVERSATION_ENTRIES]
