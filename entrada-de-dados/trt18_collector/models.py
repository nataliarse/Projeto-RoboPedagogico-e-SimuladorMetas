"""
Esquema de dados padronizado dos processos do TRT18 (Pydantic v2).

Este módulo define a "árvore JSON" única que todo processo deve seguir
(etapas 4 e 6 do tarefas.md). É o contrato de dados entregue ao chatbot.

Estrutura de alto nível:

    {
      "processo":            { ... dados de cabeçalho ... },
      "partes_interessadas": [ ... ],
      "movimentacoes":       [ ... ],
      "documentos":          [ ... ],
      "pendencias":          [ ... ],
      "coleta":              { ... metadados da raspagem ... }
    }
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums (vocabulário controlado)
# ---------------------------------------------------------------------------
class Polo(str, Enum):
    ATIVO = "ATIVO"
    PASSIVO = "PASSIVO"
    OUTROS = "OUTROS"


class SituacaoProcesso(str, Enum):
    PENDENTE = "PENDENTE"
    BAIXADO = "BAIXADO"
    INDEFINIDO = "INDEFINIDO"


class StatusColeta(str, Enum):
    SUCESSO = "SUCESSO"
    PARCIAL = "PARCIAL"
    FALHA = "FALHA"
    NAO_ENCONTRADO = "NAO_ENCONTRADO"  # número válido, mas sem processo no TRT18
    BLOQUEADO = "BLOQUEADO"  # portal recusou o acesso (HTTP 403) por excesso de consultas


# ---------------------------------------------------------------------------
# Sub-modelos
# ---------------------------------------------------------------------------
class Parte(BaseModel):
    """Parte interessada no processo (polo ativo, passivo ou outros)."""

    model_config = ConfigDict(extra="forbid")

    polo: Polo = Polo.OUTROS
    nome: str
    tipo: Optional[str] = Field(
        default=None, description="Papel processual: Reclamante, Reclamado, Advogado etc."
    )
    documento: Optional[str] = Field(
        default=None, description="CPF/CNPJ quando disponível (apenas dígitos)."
    )
    representantes: list[str] = Field(
        default_factory=list, description="Advogados/representantes da parte."
    )


class Movimentacao(BaseModel):
    """Um movimento do histórico processual (o que mais importa para o chatbot)."""

    model_config = ConfigDict(extra="forbid")

    ordem: int = Field(description="Ordem cronológica (1 = mais antigo).")
    data: Optional[datetime] = None
    descricao: str
    complemento: Optional[str] = None
    referencia: Optional[str] = Field(
        default=None, description="Link/referência do movimento, quando disponível."
    )


class Documento(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: Optional[datetime] = None
    titulo: str
    tipo: Optional[str] = None
    id_documento: Optional[str] = None


class DadosProcesso(BaseModel):
    """Cabeçalho / dados básicos do processo."""

    model_config = ConfigDict(extra="forbid")

    numero: str = Field(description="Número CNJ formatado (com pontuação).")
    numero_normalizado: str = Field(description="Apenas os 20 dígitos do número CNJ.")
    classe_judicial: Optional[str] = None
    assunto: Optional[str] = None
    orgao_julgador: Optional[str] = None
    unidade: Optional[str] = Field(default=None, description="Unidade judiciária / vara.")
    jurisdicao: Optional[str] = None
    grau: Optional[str] = "1º Grau"
    data_autuacao: Optional[date] = Field(
        default=None, description="Data de autuação original do processo (marco da Meta 2)."
    )
    data_distribuicao: Optional[date] = Field(
        default=None, description="Data de distribuição/conversão para o meio eletrônico."
    )
    valor_causa: Optional[float] = None
    situacao: SituacaoProcesso = SituacaoProcesso.INDEFINIDO


class Coleta(BaseModel):
    """Metadados sobre a raspagem — ajudam a auditar a qualidade dos dados."""

    model_config = ConfigDict(extra="forbid")

    fonte: str = "https://pje.trt18.jus.br/consultaprocessual/"
    coletado_em: datetime = Field(default_factory=datetime.now)
    versao_coletor: Optional[str] = Field(default=None, description="Versão do coletor usada.")
    tempo_execucao_seg: Optional[float] = Field(
        default=None, description="Tempo total da coleta deste processo, em segundos."
    )
    status_coleta: StatusColeta = StatusColeta.SUCESSO
    tentativas_captcha: Optional[int] = None
    status_cnj_planilha: Optional[str] = Field(
        default=None, description="Status informado na planilha de entrada (ex.: Pendente)."
    )
    warnings: list[str] = Field(default_factory=list)
    erros: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Modelo raiz
# ---------------------------------------------------------------------------
class Processo(BaseModel):
    """Árvore JSON completa e validada de um processo."""

    model_config = ConfigDict(extra="forbid")

    processo: DadosProcesso
    partes_interessadas: list[Parte] = Field(default_factory=list)
    movimentacoes: list[Movimentacao] = Field(default_factory=list)
    documentos: list[Documento] = Field(default_factory=list)
    pendencias: list[str] = Field(default_factory=list)
    coleta: Coleta


__all__ = [
    "Polo",
    "SituacaoProcesso",
    "StatusColeta",
    "Parte",
    "Movimentacao",
    "Documento",
    "DadosProcesso",
    "Coleta",
    "Processo",
]
