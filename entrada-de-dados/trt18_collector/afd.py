"""
Autômato Finito Determinístico (AFD) para classificação do estado processual.

Especificação formal
--------------------
O autômato é a quíntupla M = (Q, Σ, δ, q0, F), onde:

Q  = {INICIAL, EM_TRAMITACAO, JULGADO, SUSPENSO, ARQUIVADO_PROVISORIO, BAIXADO}
Σ  = {DISTRIBUICAO, CONVERSAO, JULGAMENTO, BAIXA, REMESSA, ARQ_PROVISORIO,
      SUSPENSAO, REATIVACAO}        (ver `movimentos_tpu.Categoria`)
q0 = INICIAL
F  = {BAIXADO}                       (estado de aceitação: processo baixado)
δ  : Q × Σ → Q                       (tabela TRANSICOES, abaixo)

Movimentos que não pertencem a Σ — a tramitação comum, que é a maior parte dos
registros — não produzem transição: o autômato permanece no estado corrente.
Essa é a razão de o alfabeto ser restrito aos atos que efetivamente alteram a
situação do processo para fins de apuração das Metas 1 e 2.

Decisão de modelagem relevante
------------------------------
BAIXADO é um estado absorvente por definição das Situações do Datamart: uma vez
baixado, o processo sai do acervo pendente. Entretanto, observou-se na amostra
que processos baixados retornam à tramitação por desarquivamento. Para preservar
a fidelidade ao dado real, admite-se a transição BAIXADO --REATIVACAO-->
EM_TRAMITACAO, registrando-se a ocorrência como reabertura. Sem essa transição,
o autômato classificaria como baixado um processo que voltou a tramitar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from .movimentos_tpu import Categoria, classificar_movimento


class Estado(str, Enum):
    """Conjunto Q de estados do autômato."""

    INICIAL = "INICIAL"
    EM_TRAMITACAO = "EM_TRAMITACAO"
    JULGADO = "JULGADO"
    SUSPENSO = "SUSPENSO"
    ARQUIVADO_PROVISORIO = "ARQUIVADO_PROVISORIO"
    BAIXADO = "BAIXADO"


# Função de transição δ: (estado, símbolo) -> estado
TRANSICOES: dict[tuple[Estado, Categoria], Estado] = {}


def _t(origens: list[Estado], simbolo: Categoria, destino: Estado) -> None:
    for o in origens:
        TRANSICOES[(o, simbolo)] = destino


_TODOS = list(Estado)

# entrada do processo
_t([Estado.INICIAL], Categoria.DISTRIBUICAO, Estado.EM_TRAMITACAO)
_t([Estado.INICIAL], Categoria.CONVERSAO, Estado.EM_TRAMITACAO)
# distribuição/conversão em processo já em curso não retrocede o estado
_t([Estado.EM_TRAMITACAO, Estado.JULGADO, Estado.SUSPENSO,
    Estado.ARQUIVADO_PROVISORIO], Categoria.DISTRIBUICAO, Estado.EM_TRAMITACAO)
for _e in (Estado.EM_TRAMITACAO, Estado.JULGADO, Estado.SUSPENSO,
           Estado.ARQUIVADO_PROVISORIO, Estado.BAIXADO):
    TRANSICOES[(_e, Categoria.CONVERSAO)] = _e  # conversão não altera a situação

# ato decisório
_t([Estado.INICIAL, Estado.EM_TRAMITACAO, Estado.SUSPENSO,
    Estado.ARQUIVADO_PROVISORIO, Estado.JULGADO], Categoria.JULGAMENTO, Estado.JULGADO)

# suspensão e arquivamento provisório: processo segue pendente
_t([Estado.INICIAL, Estado.EM_TRAMITACAO, Estado.JULGADO,
    Estado.ARQUIVADO_PROVISORIO, Estado.SUSPENSO], Categoria.SUSPENSAO, Estado.SUSPENSO)
_t([Estado.INICIAL, Estado.EM_TRAMITACAO, Estado.JULGADO,
    Estado.SUSPENSO, Estado.ARQUIVADO_PROVISORIO],
   Categoria.ARQ_PROVISORIO, Estado.ARQUIVADO_PROVISORIO)

# retomada da tramitação (inclui reabertura de processo baixado)
_t(_TODOS, Categoria.REATIVACAO, Estado.EM_TRAMITACAO)

# baixa e remessa a outro órgão
_t(_TODOS, Categoria.BAIXA, Estado.BAIXADO)
_t(_TODOS, Categoria.REMESSA, Estado.BAIXADO)

ESTADOS_FINAIS = {Estado.BAIXADO}


@dataclass
class PassoTransicao:
    """Registro de um passo do autômato — base da auditabilidade do artefato."""

    ordem: int
    data: Optional[datetime]
    denominacao: str
    simbolo: Optional[Categoria]
    motivo: str
    estado_anterior: Estado
    estado_novo: Estado

    @property
    def houve_transicao(self) -> bool:
        return self.estado_anterior != self.estado_novo


@dataclass
class ResultadoAFD:
    estado_final: Estado
    aceito: bool                       # estado_final ∈ F
    trilha: list[PassoTransicao] = field(default_factory=list)
    simbolos_ignorados: int = 0

    @property
    def situacao(self) -> str:
        """Tradução do estado final para o vocabulário das Metas (PENDENTE/BAIXADO)."""
        return "BAIXADO" if self.estado_final in ESTADOS_FINAIS else "PENDENTE"

    def transicoes_efetivas(self) -> list[PassoTransicao]:
        return [p for p in self.trilha if p.houve_transicao]

    def explicar(self) -> str:
        """Explicação legível da classificação — camada de \"legal design\"."""
        efetivas = self.transicoes_efetivas()
        if not efetivas:
            return ("Nenhum movimento com efeito sobre a situação processual foi "
                    f"identificado em {len(self.trilha)} registros analisados.")
        linhas = [f"Situação classificada: {self.situacao} (estado {self.estado_final.value})",
                  f"Movimentos analisados: {len(self.trilha)} | "
                  f"com efeito na situação: {len(efetivas)}", "",
                  "Sequência de transições:"]
        for p in efetivas:
            data = p.data.strftime("%d/%m/%Y") if p.data else "sem data"
            linhas.append(
                f"  {data} · {p.estado_anterior.value} -> {p.estado_novo.value}"
                f" ({p.simbolo.value}: {p.motivo})"
            )
            linhas.append(f"      movimento: {p.denominacao[:88]}")
        decisivo = efetivas[-1]
        linhas += ["", f"Movimento determinante: \"{decisivo.denominacao[:88]}\"",
                   f"Fundamento: {decisivo.motivo}."]
        return "\n".join(linhas)


def executar(movimentacoes: list[dict]) -> ResultadoAFD:
    """
    Executa o autômato sobre a lista de movimentações de um processo.

    Espera a lista já em ordem cronológica, no formato do bloco
    `movimentacoes` da árvore JSON (chaves `ordem`, `data`, `descricao`).
    """
    estado = Estado.INICIAL
    trilha: list[PassoTransicao] = []
    ignorados = 0

    for i, mov in enumerate(movimentacoes, start=1):
        denominacao = (mov.get("descricao") or "").strip()
        simbolo, motivo = classificar_movimento(denominacao)

        if simbolo is None:
            ignorados += 1
            novo = estado
        else:
            novo = TRANSICOES.get((estado, simbolo), estado)

        data = mov.get("data")
        if isinstance(data, str):
            try:
                data = datetime.fromisoformat(data)
            except ValueError:
                data = None

        trilha.append(
            PassoTransicao(
                ordem=mov.get("ordem", i),
                data=data,
                denominacao=denominacao,
                simbolo=simbolo,
                motivo=motivo,
                estado_anterior=estado,
                estado_novo=novo,
            )
        )
        estado = novo

    return ResultadoAFD(
        estado_final=estado,
        aceito=estado in ESTADOS_FINAIS,
        trilha=trilha,
        simbolos_ignorados=ignorados,
    )


def especificacao() -> str:
    """Devolve a especificação formal — útil para documentação e para o TCC."""
    return (
        f"Q  = {{{', '.join(e.value for e in Estado)}}}\n"
        f"Σ  = {{{', '.join(c.value for c in Categoria)}}}\n"
        f"q0 = {Estado.INICIAL.value}\n"
        f"F  = {{{', '.join(e.value for e in ESTADOS_FINAIS)}}}\n"
        f"|δ| = {len(TRANSICOES)} transições definidas"
    )


__all__ = ["Estado", "TRANSICOES", "ESTADOS_FINAIS", "ResultadoAFD",
           "PassoTransicao", "executar", "especificacao"]
