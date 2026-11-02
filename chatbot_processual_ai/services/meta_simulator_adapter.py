from __future__ import annotations

import os
from numbers import Real
from typing import Protocol

import requests

from schemas.meta_contracts import MetaSimulationRequest, MetaSimulationResponse


class SimulatorUnavailableError(RuntimeError):
    """O motor real não está configurado ou não pôde responder."""


class InvalidSimulatorSchemaError(RuntimeError):
    """O motor respondeu, mas fora do contrato numérico esperado."""


class SimulatorGateway(Protocol):
    def simulate(self, request: MetaSimulationRequest) -> MetaSimulationResponse:
        """Executa o cenário no motor real e devolve somente resposta validada."""


class HttpSimulatorGateway:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("SIMULATOR_API_URL", "http://127.0.0.1:8001")).rstrip("/")
        self.timeout_seconds = timeout_seconds or float(os.getenv("SIMULATOR_TIMEOUT_SECONDS", "20"))
        self.session = session or requests.Session()

    def simulate(self, request: MetaSimulationRequest) -> MetaSimulationResponse:
        alterations = request.cenario.get("alteracoes", request.cenario)
        try:
            response = self.session.post(
                f"{self.base_url}/api/simular",
                json={"alteracoes": alterations},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SimulatorUnavailableError("Motor de metas indisponível.") from exc

        meta1 = _numeric_or_none(payload, "meta1_final")
        meta2 = _numeric_or_none(payload, "meta2_final")
        records = payload.get("registros")
        if not isinstance(records, list):
            raise InvalidSimulatorSchemaError("Campo registros ausente ou inválido.")

        normalized_meta = request.meta_id.strip().lower().replace(" ", "")
        if normalized_meta not in {"meta1", "meta2"}:
            raise InvalidSimulatorSchemaError("meta_id deve ser meta1 ou meta2.")
        result = meta1 if normalized_meta == "meta1" else meta2
        if result is None:
            raise InvalidSimulatorSchemaError("Resultado solicitado não foi calculado.")

        return MetaSimulationResponse(
            tipo="meta_simulation",
            meta_id=normalized_meta,
            ano=request.ano,
            status="success",
            resultado=result,
            meta_alvo=100.0,
            indicadores={
                "unidade": request.unidade,
                "cenario": request.cenario,
                "meta1_final": meta1,
                "meta2_final": meta2,
                "registros": len(records),
            },
            observacoes=["Resultado calculado pelo motor real do simulador de metas."],
        )


def _numeric_or_none(payload: object, field: str) -> float | None:
    if not isinstance(payload, dict) or field not in payload:
        raise InvalidSimulatorSchemaError(f"Campo {field} ausente.")
    value = payload[field]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InvalidSimulatorSchemaError(f"Campo {field} não é numérico.")
    return float(value)


def simulate_meta(
    request: MetaSimulationRequest,
    gateway: SimulatorGateway | None = None,
) -> MetaSimulationResponse:
    return (gateway or HttpSimulatorGateway()).simulate(request)
