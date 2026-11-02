from dataclasses import dataclass


@dataclass
class MetaSimulationRequest:
    meta_id: str
    ano: int
    unidade: str | None
    cenario: dict


@dataclass
class MetaSimulationResponse:
    tipo: str
    meta_id: str
    ano: int
    status: str
    resultado: float | None
    meta_alvo: float | None
    indicadores: dict
    observacoes: list[str]


@dataclass
class ProcessMetaImpactRequest:
    numero_processo: str
    meta_id: str
    ano: int


@dataclass
class ProcessMetaImpactResponse:
    tipo: str
    numero_processo: str
    meta_id: str
    ano: int
    conta_como_novo: bool | None
    conta_como_julgado: bool | None
    conta_como_baixado: bool | None
    impacto: str
    motivo: str
    observacoes: list[str]
