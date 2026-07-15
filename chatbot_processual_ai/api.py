from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agents.agent2_context_collection import MAX_CONVERSATION_ENTRIES
from orchestrators.hybrid_orchestrator import run_process_meta_impact
from orchestrators.processual_chat_orchestrator import run_processual_chat_step
from schemas.meta_contracts import MetaSimulationRequest
from services.meta_explanation_service import (
    explain_meta_simulation,
    explain_process_meta_impact,
)
from services.meta_simulator_adapter import simulate_meta
from session_state import create_session_state


DEFAULT_SESSION_ID = "default"

app = FastAPI(title="Chatbot Processual AI")
_SESSIONS: dict[str, dict[str, Any]] = {}


class ProcessualChatHTTPRequest(BaseModel):
    session_id: str | None = None
    mensagem: str


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


@app.post("/api/processos/chat")
def chat_processual(request: ProcessualChatHTTPRequest) -> dict[str, Any]:
    session_id = _normalize_session_id(request.session_id)
    session_state = _get_session_state(session_id)

    result = run_processual_chat_step(request.mensagem, session_state)
    _register_assistant_message(result.response.resposta, session_state)

    return {
        "session_id": session_id,
        "resultado": asdict(result.response),
    }


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
    simulation_response = simulate_meta(simulation_request)
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
    return DEFAULT_SESSION_ID


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
