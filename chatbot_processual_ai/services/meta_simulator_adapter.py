from __future__ import annotations

from typing import Protocol

from schemas.meta_contracts import MetaSimulationRequest, MetaSimulationResponse


class SimulatorUnavailableError(RuntimeError):
    """O motor real não está configurado ou não pôde responder."""


class SimulatorGateway(Protocol):
    def simulate(self, request: MetaSimulationRequest) -> MetaSimulationResponse:
        """Executa o cenário no motor real e devolve somente resposta validada."""


def simulate_meta(
    request: MetaSimulationRequest,
    gateway: SimulatorGateway | None = None,
) -> MetaSimulationResponse:
    if gateway is None:
        raise SimulatorUnavailableError("Gateway do simulador real não configurado.")
    return gateway.simulate(request)
