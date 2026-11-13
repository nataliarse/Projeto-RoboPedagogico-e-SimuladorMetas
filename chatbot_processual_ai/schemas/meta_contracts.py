from dataclasses import dataclass


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
