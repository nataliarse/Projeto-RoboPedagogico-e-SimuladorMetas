"""
Classificação dos movimentos processuais em categorias do alfabeto do AFD.

Contexto do problema
--------------------
O portal de Consulta Processual do PJe devolve cada movimento apenas por sua
DENOMINAÇÃO textual (ex.: "Arquivados os autos definitivamente"), sem o código
da Tabela Processual Unificada (TPU). Como o autômato opera sobre um alfabeto
finito de símbolos, é necessário traduzir a denominação em uma categoria.

Este módulo faz essa tradução por REGRAS sobre a denominação, e não por uma
lista fechada de strings. A opção é deliberada: a denominação traz partes
variáveis (nomes de partes, datas, números de processo) e novos processos
trazem variantes não observadas na amostra. Regras generalizam; listas, não.

Princípios de classificação adotados
------------------------------------
1. **Ator do movimento.** Petições das partes ("Juntada a petição de...") não
   alteram o estado do processo, ainda que o seu teor mencione suspensão ou
   sentença. Somente atos do juízo produzem transição.
2. **Ato preparatório x ato decisório.** "Conclusos os autos para julgamento"
   antecede o julgamento; não é o julgamento.
3. **Natureza da remessa.** Remessa a outro órgão jurisdicional encerra a
   tramitação na unidade (relevante para a Baixa); remessa interna (Contadoria,
   CEJUSC) é tramitação comum.
4. **Definitivo x provisório.** Arquivamento provisório não é baixa: o processo
   segue pendente e pode ser desarquivado.

Referência: Situações do Datamart CNJ (versão 14) e Tabela de Movimentos do SGT.
"""

from __future__ import annotations

import re
import unicodedata
from enum import Enum


class Categoria(str, Enum):
    """Alfabeto de entrada do autômato (símbolos que causam transição)."""

    DISTRIBUICAO = "DISTRIBUICAO"
    CONVERSAO = "CONVERSAO"              # meio físico -> eletrônico
    JULGAMENTO = "JULGAMENTO"
    BAIXA = "BAIXA"
    REMESSA = "REMESSA"                  # a outro órgão jurisdicional
    ARQ_PROVISORIO = "ARQ_PROVISORIO"
    SUSPENSAO = "SUSPENSAO"
    REATIVACAO = "REATIVACAO"


# Correspondência entre as categorias do alfabeto e as Situações do Datamart do
# CNJ (versão 16). Permite rastrear cada transição do autômato até a norma que a
# fundamenta — requisito de auditabilidade do artefato.
# Fonte: data/referencia/situacoes_datamart_v16.json
SITUACOES_DATAMART: dict[Categoria, dict[int, str]] = {
    Categoria.DISTRIBUICAO: {24: "Distribuído", 40: "Redistribuído"},
    Categoria.CONVERSAO: {},  # sem situação própria: não altera a apuração
    Categoria.JULGAMENTO: {
        27: "Julgamento com resolução de mérito",
        28: "Julgamento sem resolução de mérito",
        29: "Julgamento homologatório proferido",
        62: "Julgamento",
    },
    Categoria.BAIXA: {
        2: "Arquivado definitivamente",
        10: "Baixado definitivamente",
        23: "Distribuição cancelada",
    },
    Categoria.REMESSA: {
        41: "Remetido",
        132: "Remetido em grau de recurso",
        134: "Remetido para outra instância",
    },
    Categoria.ARQ_PROVISORIO: {},  # mantém Pendente (88): não é baixa
    Categoria.SUSPENSAO: {
        45: "Suspenso/sobrestado por despacho judicial",
        46: "Suspenso/sobrestado por decisão judicial",
        47: "Suspenso/Sobrestado por IRDR",
        48: "Suspenso/sobrestado por Recurso Repetitivo",
        49: "Suspenso/sobrestado por Repercussão Geral",
    },
    Categoria.REATIVACAO: {
        37: "Reativado",
        106: "Levantada suspensão/sobrestamento por decisão judicial",
        107: "Levantada suspensão/sobrestamento por despacho judicial",
    },
}

# Situações que definem a apuração das Metas (dicionário v16):
#   ind2 (Pendentes)          -> Situação 88 (Pendente)
#   ind5 (Pendentes líquidos) -> Situação 25 (Pendente Líquido)
#   ind3 (Baixados)           -> Situações 2, 10, 23, 41 abertas OU
#                                Situação 88 finalizada por 26, 65, 91 ou 132
SITUACAO_PENDENTE = 88
SITUACAO_PENDENTE_LIQUIDO = 25
SITUACOES_BAIXA_ABERTA = (2, 10, 23, 41)
SITUACOES_QUE_FINALIZAM_PENDENTE = {
    26: "Execução não criminal iniciada",
    65: "Fase processual iniciada",
    91: "Liquidação iniciada",
    132: "Remetido em grau de recurso",
}


def _sem_acento(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    ).lower()


def normalizar_denominacao(titulo: str) -> str:
    """
    Remove as partes variáveis da denominação, preservando o núcleo do movimento.

    Exemplo:
        "Decorrido o prazo de JOÃO DA SILVA em 01/12/2025"
        -> "Decorrido o prazo"
    """
    s = re.sub(r"\s+", " ", titulo or "").strip()
    s = re.sub(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", "<PROCESSO>", s)
    s = re.sub(r"\d{1,2}/\d{1,2}/\d{2,4}", "<DATA>", s)
    s = re.sub(r"\b\d{1,2}:\d{2}(:\d{2})?\b", "<HORA>", s)
    s = re.sub(r"R\$\s?[\d.,]+", "<VALOR>", s)
    s = re.sub(
        r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ]+"
        r"(?:\s+(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ&/.-]+|d[aeo]s?|e)\b)+",
        "<NOME>",
        s,
    )
    s = re.sub(r"\b\d{4,}\b", "<NUM>", s)
    return re.sub(r"\s+", " ", s).strip(" .-")


# Remessas internas: não encerram a tramitação na unidade.
_DESTINOS_INTERNOS = (
    "contadoria",
    "cejusc",
    "metodos consensuais",
    "central de mandados",
    "secretaria",
    "distribuicao",
)


def classificar_movimento(titulo: str) -> tuple[Categoria | None, str]:
    """
    Classifica uma denominação de movimento.

    Retorna `(categoria, motivo)`. Categoria `None` significa que o movimento
    não altera o estado do processo (tramitação comum) — o motivo explica por quê,
    o que sustenta a auditabilidade exigida do artefato.
    """
    t = _sem_acento(normalizar_denominacao(titulo))

    # 1. petições das partes nunca alteram o estado
    if t.startswith("juntada a peticao") or t.startswith("juntada a manifestacao"):
        return None, "petição da parte (não é ato do juízo)"

    # 2. atos preparatórios
    if t.startswith("conclusos os autos") or t.startswith("encerrada a conclusao"):
        return None, "ato preparatório (conclusão)"

    # 3. baixa definitiva
    if "arquivados os autos definitivamente" in t or "arquivamento definitivo" in t:
        return Categoria.BAIXA, "arquivamento definitivo"
    # o trânsito em julgado encerra o mérito, mas não é baixa (Situações 2, 10, 23 e 41 do
    # Datamart): o processo segue pendente na execução até a baixa ou o arquivamento definitivo
    if "transitado em julgado" in t or "transito em julgado" in t:
        return None, "trânsito em julgado (não é baixa: o processo segue para a execução)"
    if "baixa definitiva" in t or t.startswith("baixado"):
        return Categoria.BAIXA, "baixa definitiva"

    # 4. remessa — depende do destino
    if "remetidos os autos" in t or t.startswith("remetido"):
        if any(k in t for k in _DESTINOS_INTERNOS):
            return None, "remessa interna (segue na unidade)"
        if "orgao jurisdicional competente" in t or "vara do trabalho" in t or "tribunal" in t:
            return Categoria.REMESSA, "remessa a outro órgão jurisdicional"
        return None, "remessa sem destino jurisdicional identificado"

    # 5. arquivamento provisório (não é baixa)
    if "arquivados os autos provisoriamente" in t:
        return Categoria.ARQ_PROVISORIO, "arquivamento provisório"

    # 6. julgamento (ato decisório)
    if t.startswith("extinta a execucao") or t.startswith("extincao da execucao"):
        return Categoria.JULGAMENTO, "extinção da execução"
    if t.startswith("homologada"):
        return Categoria.JULGAMENTO, "homologação"
    if t.startswith("proferida decisao") or t.startswith("proferida sentenca"):
        return Categoria.JULGAMENTO, "decisão ou sentença proferida"
    if t.startswith("julgado"):
        return Categoria.JULGAMENTO, "julgamento do pedido"

    # 7. suspensão
    if t.startswith("suspenso o processo") or t.startswith("suspenso ou sobrestado"):
        return Categoria.SUSPENSAO, "suspensão determinada pelo juízo"
    if t.startswith("sobrestado"):
        return Categoria.SUSPENSAO, "sobrestamento"

    # 8. reativação
    if "desarquivados os autos" in t:
        return Categoria.REATIVACAO, "desarquivamento"
    if t.startswith("encerrada a suspensao") or t.startswith("revogada a suspensao"):
        return Categoria.REATIVACAO, "encerramento da suspensão"
    if t.startswith("dessobrestad"):
        return Categoria.REATIVACAO, "dessobrestamento"
    if "recebidos os autos para prosseguir" in t:
        return Categoria.REATIVACAO, "retomada da tramitação"

    # 9. entrada do processo
    if t.startswith("distribuido") or t.startswith("redistribuido"):
        return Categoria.DISTRIBUICAO, "distribuição"
    if "convertida a tramitacao do processo do meio fisico" in t:
        return Categoria.CONVERSAO, "conversão do meio físico para o eletrônico"

    return None, "tramitação comum"


__all__ = ["Categoria", "classificar_movimento", "normalizar_denominacao"]
