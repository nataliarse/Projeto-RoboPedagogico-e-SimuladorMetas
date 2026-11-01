"""
Simulador das Metas 1 e 2 do Poder Judiciário — API REST
FastAPI + Pandas + lógica do script Python original

Endpoints:
  GET  /api/base              → base consolidada com metas calculadas
  POST /api/simular           → simular cenário com alterações
  POST /api/comparar          → comparar múltiplos cenários
  POST /api/otimizador        → encontrar ajuste mínimo (Meta 1 ou 2)
  GET  /api/health            → health check
"""

from __future__ import annotations

import os
import re
import unicodedata
import math
from datetime import datetime
from functools import reduce
from typing import Any, Dict, List, Literal, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, confloat, conint, validator

from services.meta2_groups import AVAILABLE_MONTHS, simulate as simulate_meta2_groups

# ── Caminhos dos arquivos Excel ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(
    os.path.join(BASE_DIR, os.getenv("SIMULADOR_DATA_DIR", "dados"))
)

ARQ_NOVOS          = os.path.join(DATA_DIR, "casos_novos.xlsx")
ARQ_JULGADOS       = os.path.join(DATA_DIR, "julgados.xlsx")
ARQ_DESSOBRESTADOS = os.path.join(DATA_DIR, "dessobrestados.xlsx")
ARQ_SUSPENSOS      = os.path.join(DATA_DIR, "suspensos.xlsx")
ARQ_META1_EQUIPE_B = os.path.join(DATA_DIR, "dados_simulador_meta1_equipe_b.xlsx")

# ── Configurações ────────────────────────────────────────────────────────────
META_ALVO          = 100.0
ANO_SIMULACAO      = 2026
DATA_CORTE_REAL    = pd.Timestamp("2026-02-01")
DATA_FINAL         = pd.Timestamp("2027-02-01")
VARIAVEIS_EDITAVEIS = ["julgados", "dessobrestados", "suspensos"]
COLUNA_EDITADA = {
    "julgados": "julgados",
    "dessobrestados": "dessobrestados",
    "suspensos": "susm1",
}


# ════════════════════════════════════════════════════════════════════════════
# ETL — leitura e consolidação (igual ao script Python original)
# ════════════════════════════════════════════════════════════════════════════

def ler_arquivo(caminho: str) -> pd.DataFrame:
    """Lê xlsx normais e xlsx com CSV colado numa única coluna."""
    df = pd.read_excel(caminho)
    if df.shape[1] == 1 and "," in str(df.columns[0]):
        colunas = str(df.columns[0]).split(",")
        linhas  = df.iloc[:, 0].astype(str).str.split(",", expand=True)
        linhas.columns = colunas
        for c in linhas.columns:
            if c not in ("data_oficial", "data_referencia"):
                linhas[c] = pd.to_numeric(linhas[c], errors="coerce")
        return linhas
    return df


def converter_data(data) -> pd.Timestamp:
    if isinstance(data, pd.Timestamp):
        return pd.Timestamp(data.year, data.month, 1)
    data = str(data).strip().upper()
    if "-" in data:
        ts = pd.Timestamp(data)
        return pd.Timestamp(ts.year, ts.month, 1)
    meses_ingles = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
        "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
        "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
    }
    if "M" in data and data[:2].isdigit():
        mes = int(data.split("M")[0])
        ano = int(data.split("M")[1])
        return pd.Timestamp(ano, mes, 1)
    mes_txt = data[:3]
    ano     = int(data[3:])
    return pd.Timestamp(ano, meses_ingles[mes_txt], 1)


def calcular_susm1(suspensos: pd.Series) -> pd.Series:
    """Incrementos positivos mensais do estoque de suspensos."""
    return suspensos.diff().clip(lower=0).fillna(0)


def carregar_base_meta1(caminho: str, corte=DATA_CORTE_REAL) -> pd.DataFrame:
    """Carrega a série integrada e validada pela equipe responsável."""
    df = ler_arquivo(caminho)
    df["data"] = df["data_oficial"].apply(converter_data)
    df["novos"] = df["distribuidos"]
    df = df.sort_values("data").reset_index(drop=True)
    df["susm1"] = calcular_susm1(df["suspensos"])

    tipo = np.where(df["data"] <= corte, "real", "previsao_sas")
    for col in ("novos", "julgados", "dessobrestados", "suspensos"):
        df[f"{col}_tipo"] = tipo

    base = df[df["data"] <= DATA_FINAL].copy()
    for col in ("novos", "julgados", "dessobrestados", "suspensos"):
        if col not in base.columns:
            raise ValueError(f"Coluna '{col}' não encontrada.")
        if base[col].isna().any():
            raise ValueError(f"Coluna '{col}' possui valores nulos.")
    base["baixados"] = np.nan
    base["ano"] = base["data"].dt.year
    base["mes"] = base["data"].dt.month
    return base[[
        "data", "ano", "mes", "novos", "julgados", "dessobrestados",
        "suspensos", "susm1", "baixados", "novos_tipo", "julgados_tipo",
        "dessobrestados_tipo", "suspensos_tipo",
    ]]


def carregar_base_forecast(caminho, variavel, col_data="data_oficial", col_valor=None):
    df = ler_arquivo(caminho)
    if col_valor is None:
        col_valor = variavel
    df["data"]              = df[col_data].apply(converter_data)
    df[f"{variavel}_real"]  = df[col_valor]
    df[f"{variavel}_forecast"] = df["FORECAST"] if "FORECAST" in df.columns else np.nan
    df[variavel]            = df[f"{variavel}_real"].combine_first(df[f"{variavel}_forecast"])
    df[f"{variavel}_tipo"]  = np.where(df[f"{variavel}_real"].notna(), "real", "previsao_sas")
    colunas = ["data", variavel, f"{variavel}_real",
               f"{variavel}_forecast", f"{variavel}_tipo"]
    for extra in ("STD", "L95", "U95", "RESIDUAL"):
        if extra in df.columns:
            colunas.append(extra)
    return df[[c for c in colunas if c in df.columns]]


def carregar_julgados(caminho, corte=DATA_CORTE_REAL):
    df = ler_arquivo(caminho)
    df["data"] = df["data_oficial"].apply(converter_data)
    df["julgados_real"]     = np.where(df["data"] <= corte, df["julgados"], np.nan)
    df["julgados_forecast"] = np.where(df["data"] >  corte, df["julgados"], np.nan)
    df["julgados_tipo"]     = np.where(df["data"] <= corte, "real", "previsao_sas")
    return df[["data", "julgados", "julgados_real", "julgados_forecast", "julgados_tipo"]]


def consolidar_bases(*bases) -> pd.DataFrame:
    bases_validas = [b for b in bases if b is not None]
    base = reduce(
        lambda e, d: pd.merge(e, d, on="data", how="outer"),
        bases_validas,
    ).sort_values("data").reset_index(drop=True)
    if "baixados" not in base.columns:
        base["baixados"] = np.nan
    base = base[base["data"] <= DATA_FINAL].copy()
    for col in ["dessobrestados", "suspensos", "novos", "julgados"]:
        if col not in base.columns:
            raise ValueError(f"Coluna '{col}' não encontrada.")
        if base[col].isna().any():
            raise ValueError(f"Coluna '{col}' possui valores nulos.")
    base["ano"] = base["data"].dt.year
    base["mes"] = base["data"].dt.month
    return base


# ── Carrega uma vez ao iniciar ───────────────────────────────────────────────
BASE_GLOBAL: pd.DataFrame = carregar_base_meta1(ARQ_META1_EQUIPE_B)


# ════════════════════════════════════════════════════════════════════════════
# FÓRMULAS CNJ (idênticas ao script original)
# ════════════════════════════════════════════════════════════════════════════

def denominador_meta1(novos, dessobrestados, susm1):
    denominador = novos + dessobrestados - susm1
    if denominador is None or pd.isna(denominador) or denominador <= 0:
        return np.nan
    return denominador


def calcular_meta1(novos, julgados, dessobrestados, susm1):
    denominador = denominador_meta1(novos, dessobrestados, susm1)
    if pd.isna(denominador):
        return np.nan
    if julgados is None or pd.isna(julgados):
        return np.nan
    return (julgados / denominador) * 100


def formula_meta2(julgm2a, dism2a, susm2a):
    den = dism2a - susm2a
    if den is None or pd.isna(den) or den <= 0:
        return np.nan
    if julgm2a is None or pd.isna(julgm2a):
        return np.nan
    return (julgm2a / den) * (1000 / 9.4)


def calcular_acumulados(df: pd.DataFrame) -> pd.DataFrame:
    r = df.copy().sort_values("data").reset_index(drop=True)
    r["ano"] = r["data"].dt.year
    r["novos_acum"]          = r.groupby("ano")["novos"].cumsum()
    r["distribuidos"]        = r["novos"]
    r["distribuidos_acum"]   = r["novos_acum"]
    r["julgados_acum"]       = r.groupby("ano")["julgados"].cumsum()
    r["dessobrestados_acum"] = r.groupby("ano")["dessobrestados"].cumsum()
    r["suspensos_acum"]      = r.groupby("ano")["suspensos"].cumsum()
    r["susm1_acum"]          = r.groupby("ano")["susm1"].cumsum()
    return r


def calcular_metas(df: pd.DataFrame) -> pd.DataFrame:
    r = calcular_acumulados(df)
    r["meta1"] = r.apply(
        lambda l: calcular_meta1(
            l["novos_acum"], l["julgados_acum"],
            l["dessobrestados_acum"], l["susm1_acum"],
        ), axis=1,
    ).round(2)
    r["meta2_denominador"] = r["distribuidos_acum"] - r["suspensos"]
    r["meta2"] = r.apply(
        lambda l: formula_meta2(l["julgados_acum"], l["distribuidos_acum"], l["suspensos"]),
        axis=1,
    ).round(2)
    r["meta2_status"] = np.select(
        [r["meta2"].isna(), r["meta2"] >= 100, r["meta2"] >= 95],
        ["não calculável", "cumprida (≥100%)", "≥95%, <100%"],
        default="abaixo de 95%",
    )
    return r


def simular_cenario(df: pd.DataFrame, alteracoes: dict) -> pd.DataFrame:
    sim = df.copy()
    for periodo, variaveis in alteracoes.items():
        data    = pd.Timestamp(periodo + "-01")
        mascara = sim["data"] == data
        if not mascara.any():
            continue
        for var, inc in variaveis.items():
            if var not in VARIAVEIS_EDITAVEIS:
                continue
            coluna = COLUNA_EDITADA[var]
            sim.loc[mascara, coluna] = (sim.loc[mascara, coluna] + inc).clip(lower=0)
    return calcular_metas(sim)


def meses_do_ano(df: pd.DataFrame, ano: int = ANO_SIMULACAO) -> List[str]:
    return list(df[df["ano"] == ano]["data"].dt.strftime("%Y-%m"))


def meses_projetados(df: pd.DataFrame, ano: int = ANO_SIMULACAO) -> List[str]:
    linhas = df[(df["ano"] == ano) & (df["data"] > DATA_CORTE_REAL)]
    return list(linhas["data"].dt.strftime("%Y-%m"))


def _com_julgados_extra(alteracoes: dict, meses: List[str], extra: int) -> dict:
    resultado = {mes: dict(valores) for mes, valores in alteracoes.items()}
    for mes in meses:
        resultado.setdefault(mes, {})
        resultado[mes]["julgados"] = resultado[mes].get("julgados", 0) + extra
    return resultado


def quanto_falta_meta1(
    df: pd.DataFrame,
    meta_alvo: float,
    mes_inicio: str,
    alteracoes: dict,
    ano: int = ANO_SIMULACAO,
) -> dict:
    partida = simular_cenario(df, alteracoes)
    linhas_ano = partida[partida["ano"] == ano]
    dezembro = linhas_ano.iloc[-1]
    meses = [mes for mes in meses_do_ano(df, ano) if mes >= mes_inicio]
    meses_reais = [mes for mes in meses if mes not in meses_projetados(df, ano)]

    meta_atual = None if pd.isna(dezembro["meta1"]) else float(dezembro["meta1"])
    denominador = denominador_meta1(
        dezembro["novos_acum"],
        dezembro["dessobrestados_acum"],
        dezembro["susm1_acum"],
    )
    julgados_acumulados = float(dezembro["julgados_acum"])
    julgados_periodo = float(
        linhas_ano[linhas_ano["data"].dt.strftime("%Y-%m").isin(meses)]["julgados"].sum()
    )
    resposta = {
        "meta_alvo": meta_alvo,
        "meta_atual": meta_atual,
        "mes_inicio": mes_inicio,
        "meses": meses,
        "n_meses": len(meses),
        "meses_reais": meses_reais,
        "julgados_previstos_periodo": round(julgados_periodo),
        "conta": {
            "denominador": None if pd.isna(denominador) else round(float(denominador)),
            "julgados_acumulados": round(julgados_acumulados),
            "julgados_necessarios": None
            if pd.isna(denominador)
            else math.ceil(meta_alvo / 100 * float(denominador)),
        },
    }
    if meta_atual is None or pd.isna(denominador) or not meses:
        return {
            **resposta,
            "ok": False,
            "ja_atingida": False,
            "incremento_mensal": None,
            "total_adicional": None,
            "meta_resultante": None,
            "mensagem": "Não é possível calcular a Meta 1 para o cenário informado.",
        }
    if meta_atual >= meta_alvo:
        return {
            **resposta,
            "ok": True,
            "ja_atingida": True,
            "incremento_mensal": 0,
            "total_adicional": 0,
            "meta_resultante": meta_atual,
            "mensagem": f"A meta de {meta_alvo:g}% já é atingida ({meta_atual:.2f}%).",
        }

    faltam = meta_alvo / 100 * float(denominador) - julgados_acumulados
    incremento = max(math.ceil(faltam / len(meses)), 0)
    for _ in range(1000):
        simulado = simular_cenario(
            df, _com_julgados_extra(alteracoes, meses, incremento)
        )
        meta_resultante = simulado[simulado["ano"] == ano].iloc[-1]["meta1"]
        if not pd.isna(meta_resultante) and meta_resultante >= meta_alvo:
            break
        incremento += 1
    else:
        return {
            **resposta,
            "ok": False,
            "ja_atingida": False,
            "incremento_mensal": None,
            "total_adicional": None,
            "meta_resultante": None,
            "mensagem": "Não foi possível confirmar o resultado pela simulação.",
        }
    return {
        **resposta,
        "ok": True,
        "ja_atingida": False,
        "incremento_mensal": incremento,
        "total_adicional": incremento * len(meses),
        "meta_resultante": float(meta_resultante),
        "mensagem": f"São necessários +{incremento} julgamentos por mês em {len(meses)} meses.",
    }


# ════════════════════════════════════════════════════════════════════════════
# OTIMIZADOR (busca binária — igual ao script original)
# ════════════════════════════════════════════════════════════════════════════

def _meta_final(df, variavel, mes, incremento, meta: str, ano=ANO_SIMULACAO):
    res  = simular_cenario(df, {mes: {variavel: incremento}})
    rows = res[res["ano"] == ano]
    if rows.empty:
        return np.nan
    return rows.iloc[-1][meta]


def encontrar_ajuste_minimo(df, variavel, mes, meta_alvo, meta="meta1", ano=ANO_SIMULACAO):
    if variavel not in VARIAVEIS_EDITAVEIS:
        raise ValueError(f"'{variavel}' não é editável.")
    meta_atual = _meta_final(df, variavel, mes, 0, meta, ano)
    if not np.isnan(meta_atual) and meta_atual >= meta_alvo:
        return {
            "variavel": variavel, "mes": mes, "meta_alvo": meta_alvo,
            "meta_atual": round(meta_atual, 2), "incremento_necessario": 0,
            "meta_resultante": round(meta_atual, 2),
            "mensagem": f"Meta de {meta_alvo}% já atingida ({round(meta_atual,2)}%). Nenhum ajuste necessário.",
            "ok": True,
        }
    # Direção
    meta_teste = _meta_final(df, variavel, mes, 50, meta, ano)
    direcao    = 1 if (not np.isnan(meta_teste) and meta_teste > meta_atual) else -1
    lo, hi = 0.0, 50.0
    for _ in range(40):
        m_hi = _meta_final(df, variavel, mes, int(direcao * hi), meta, ano)
        if not np.isnan(m_hi) and m_hi >= meta_alvo:
            break
        hi *= 2
    else:
        return {
            "variavel": variavel, "mes": mes, "meta_alvo": meta_alvo,
            "meta_atual": round(float(meta_atual), 2) if not np.isnan(meta_atual) else None,
            "incremento_necessario": None, "meta_resultante": None,
            "mensagem": "Meta não atingível ajustando apenas esta variável neste mês.",
            "ok": False,
        }
    for _ in range(60):
        meio = (lo + hi) / 2
        m_m  = _meta_final(df, variavel, mes, int(direcao * meio), meta, ano)
        if not np.isnan(m_m) and m_m >= meta_alvo:
            hi = meio
        else:
            lo = meio
        if hi - lo < 0.5:
            break
    inc = int(np.ceil(direcao * hi)) if direcao == 1 else int(np.floor(direcao * hi))
    m_r = _meta_final(df, variavel, mes, inc, meta, ano)
    while np.isnan(m_r) or m_r < meta_alvo:
        inc += direcao
        m_r = _meta_final(df, variavel, mes, inc, meta, ano)
    return {
        "variavel": variavel, "mes": mes, "meta_alvo": meta_alvo,
        "meta_atual": round(float(meta_atual), 2) if not np.isnan(meta_atual) else None,
        "incremento_necessario": inc,
        "meta_resultante": round(float(m_r), 2),
        "mensagem": f"Para atingir {meta_alvo}% são necessários {inc:+d} em '{variavel}' em {mes}.",
        "ok": True,
    }


# ════════════════════════════════════════════════════════════════════════════
# SERIALIZAÇÃO (converte NaN → None para JSON)
# ════════════════════════════════════════════════════════════════════════════

def df_para_json(df: pd.DataFrame) -> list:
    return (
        df.replace({np.nan: None})
          .assign(data=lambda d: d["data"].dt.strftime("%Y-%m"))
          .to_dict(orient="records")
    )


# ════════════════════════════════════════════════════════════════════════════
# MODELOS PYDANTIC
# ════════════════════════════════════════════════════════════════════════════

class ModeloEntrada(BaseModel):
    class Config:
        extra = "forbid"


InteiroEstrito = conint(strict=True)


class AlteracaoMes(ModeloEntrada):
    julgados:       InteiroEstrito = 0
    dessobrestados: InteiroEstrito = 0
    suspensos:      InteiroEstrito = 0


def validar_meses_disponiveis(alteracoes):
    if not isinstance(alteracoes, dict):
        return alteracoes

    meses_disponiveis = set(BASE_GLOBAL["data"].dt.strftime("%Y-%m"))
    for mes in alteracoes:
        if not isinstance(mes, str) or re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", mes) is None:
            raise ValueError(f"Mês '{mes}' inválido; use o formato YYYY-MM com um mês de calendário válido.")
        try:
            datetime.strptime(mes, "%Y-%m")
        except ValueError:
            raise ValueError(f"Mês '{mes}' inválido; use o formato YYYY-MM com um mês de calendário válido.")
        if mes not in meses_disponiveis:
            raise ValueError(f"Mês '{mes}' não está disponível na base.")
    return alteracoes


class SimularRequest(ModeloEntrada):
    alteracoes: Dict[str, AlteracaoMes] = Field(default_factory=dict)

    _validar_meses = validator("alteracoes", pre=True, allow_reuse=True)(validar_meses_disponiveis)


class QuantoFaltaRequest(ModeloEntrada):
    meta_alvo: confloat(gt=0, le=200) = 100.0
    mes_inicio: Optional[str] = None
    alteracoes: Dict[str, AlteracaoMes] = Field(default_factory=dict)

    _validar_meses = validator("alteracoes", pre=True, allow_reuse=True)(validar_meses_disponiveis)


class QuantoFaltaContaResponse(BaseModel):
    denominador: Optional[float]
    julgados_acumulados: float
    julgados_necessarios: Optional[float]


class QuantoFaltaResponse(BaseModel):
    ok: bool
    ja_atingida: bool
    meta_alvo: float
    meta_atual: Optional[float]
    meta_resultante: Optional[float]
    mes_inicio: str
    meses: List[str]
    n_meses: int
    meses_reais: List[str]
    incremento_mensal: Optional[int]
    total_adicional: Optional[int]
    julgados_previstos_periodo: float
    conta: QuantoFaltaContaResponse
    mensagem: str


def validar_meses_meta2(alteracoes):
    if isinstance(alteracoes, dict):
        for mes in alteracoes:
            if mes not in AVAILABLE_MONTHS:
                raise ValueError(f"Mês '{mes}' não está disponível na série da Meta 2.")
    return alteracoes


class SimularMeta2Request(ModeloEntrada):
    alteracoes_A: Dict[str, AlteracaoMes] = Field(default_factory=dict)
    alteracoes_ANT: Dict[str, AlteracaoMes] = Field(default_factory=dict)

    _validar_meses = validator(
        "alteracoes_A", "alteracoes_ANT", pre=True, allow_reuse=True
    )(validar_meses_meta2)


class Meta2GroupsResponse(BaseModel):
    resultado_2025: Dict[str, Dict[str, Any]]
    resultado_2026: Dict[str, Dict[str, Any]]
    reproducao_original_2026: Dict[str, Dict[str, Any]]
    serie_A: List[Dict[str, Any]]
    serie_ANT: List[Dict[str, Any]]


class CenarioItem(ModeloEntrada):
    nome:       str
    alteracoes: Dict[str, AlteracaoMes] = Field(default_factory=dict)

    _validar_meses = validator("alteracoes", pre=True, allow_reuse=True)(validar_meses_disponiveis)


class CompararRequest(ModeloEntrada):
    cenarios: List[CenarioItem]


class OtimizadorRequest(ModeloEntrada):
    variavel:   Literal["julgados", "dessobrestados", "suspensos"] = "julgados"
    mes:        str   = "2026-06"
    meta_alvo:  float = 100.0
    meta:       Literal["meta1", "meta2"] = "meta1"

    _validar_mes = validator("mes", allow_reuse=True)(
        lambda value: next(iter(validar_meses_disponiveis({value: {}})))
    )


class ResultadoMetasResponse(BaseModel):
    registros: List[Dict[str, Any]]
    meta1_final: Optional[float]
    meta2_final: Optional[float]


class CenarioComparadoResponse(BaseModel):
    nome: str
    meta1_final: Optional[float]
    meta2_final: Optional[float]
    dif_meta1: Optional[float]
    dif_meta2: Optional[float]
    mensal: List[Dict[str, Any]]


class CompararResponse(BaseModel):
    cenarios: List[CenarioComparadoResponse]
    meta1_base: Optional[float]
    meta2_base: Optional[float]


class OtimizadorResponse(BaseModel):
    variavel: str
    mes: str
    meta_alvo: float
    meta_atual: Optional[float]
    incremento_necessario: Optional[int]
    meta_resultante: Optional[float]
    mensagem: str
    ok: bool


# ════════════════════════════════════════════════════════════════════════════
# APP FASTAPI
# ════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Simulador Metas CNJ",
    description="API REST para o Simulador das Metas 1 e 2 do Poder Judiciário",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "SIMULADOR_CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200"
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "registros": len(BASE_GLOBAL)}


@app.get("/api/base", response_model=ResultadoMetasResponse)
def get_base():
    """Retorna a base consolidada com Meta 1 e Meta 2 calculadas."""
    resultado = calcular_metas(BASE_GLOBAL)
    return {
        "registros": df_para_json(resultado),
        "meta1_final": _meta_final_ano(resultado, "meta1"),
        "meta2_final": _meta_final_ano(resultado, "meta2"),
    }


@app.post("/api/simular", response_model=ResultadoMetasResponse)
def simular(req: SimularRequest):
    """Simula um cenário com alterações e retorna os resultados calculados."""
    alteracoes = {
        mes: {k: v for k, v in alt.dict().items() if v != 0}
        for mes, alt in req.alteracoes.items()
    }
    resultado = simular_cenario(BASE_GLOBAL, alteracoes)
    return {
        "registros": df_para_json(resultado),
        "meta1_final": _meta_final_ano(resultado, "meta1"),
        "meta2_final": _meta_final_ano(resultado, "meta2"),
    }


@app.post("/api/meta1/quanto-falta", response_model=QuantoFaltaResponse)
def quanto_falta(req: QuantoFaltaRequest):
    meses = meses_do_ano(BASE_GLOBAL)
    projetados = meses_projetados(BASE_GLOBAL)
    mes_inicio = req.mes_inicio or (projetados[0] if projetados else None)
    if mes_inicio not in meses:
        raise HTTPException(
            400,
            f"Mês inicial deve ser um mês de {ANO_SIMULACAO}: {', '.join(meses)}.",
        )
    alteracoes = {
        mes: {chave: valor for chave, valor in alt.dict().items() if valor != 0}
        for mes, alt in req.alteracoes.items()
    }
    return quanto_falta_meta1(BASE_GLOBAL, req.meta_alvo, mes_inicio, alteracoes)


@app.get("/api/meta2/base", response_model=Meta2GroupsResponse)
def get_meta2_groups_base():
    return simulate_meta2_groups()


@app.post("/api/meta2/simular", response_model=Meta2GroupsResponse)
def simulate_meta2_groups_endpoint(req: SimularMeta2Request):
    changes_a = {
        month: {key: value for key, value in change.dict().items() if value != 0}
        for month, change in req.alteracoes_A.items()
    }
    changes_ant = {
        month: {key: value for key, value in change.dict().items() if value != 0}
        for month, change in req.alteracoes_ANT.items()
    }
    return simulate_meta2_groups(changes_a, changes_ant)


@app.post("/api/comparar", response_model=CompararResponse)
def comparar(req: CompararRequest):
    """Executa e compara múltiplos cenários."""
    comparacao = []
    base_result = calcular_metas(BASE_GLOBAL)
    meta1_base  = _meta_final_ano(base_result, "meta1")
    meta2_base  = _meta_final_ano(base_result, "meta2")

    for cenario in req.cenarios:
        alteracoes = {
            mes: {k: v for k, v in alt.dict().items() if v != 0}
            for mes, alt in cenario.alteracoes.items()
        }
        resultado   = simular_cenario(BASE_GLOBAL, alteracoes)
        meta1_final = _meta_final_ano(resultado, "meta1")
        meta2_final = _meta_final_ano(resultado, "meta2")

        comparacao.append({
            "nome":        cenario.nome,
            "meta1_final": meta1_final,
            "meta2_final": meta2_final,
            "dif_meta1":   round(meta1_final - meta1_base, 2) if meta1_final is not None and meta1_base is not None else None,
            "dif_meta2":   round(meta2_final - meta2_base, 2) if meta2_final is not None and meta2_base is not None else None,
            "mensal":      df_para_json(
                resultado[resultado["ano"] == ANO_SIMULACAO][
                    ["data","meta1","meta2","julgados_acum","novos_acum",
                     "dessobrestados_acum","suspensos_acum","suspensos"]
                ]
            ),
        })
    return {"cenarios": comparacao, "meta1_base": meta1_base, "meta2_base": meta2_base}


@app.post("/api/otimizador", response_model=OtimizadorResponse)
def otimizador(req: OtimizadorRequest):
    """Encontra o ajuste mínimo para atingir a meta desejada."""
    if req.variavel not in VARIAVEIS_EDITAVEIS:
        raise HTTPException(400, f"Variável '{req.variavel}' não é editável.")
    if req.meta not in ("meta1", "meta2"):
        raise HTTPException(400, "meta deve ser 'meta1' ou 'meta2'.")
    return encontrar_ajuste_minimo(
        BASE_GLOBAL, req.variavel, req.mes, req.meta_alvo, req.meta
    )


# ── Utilitário ───────────────────────────────────────────────────────────────
def _meta_final_ano(df: pd.DataFrame, col: str, ano: int = ANO_SIMULACAO):
    rows = df[df["ano"] == ano]
    if rows.empty:
        return None
    val = rows.iloc[-1][col]
    return None if pd.isna(val) else round(float(val), 2)


# ════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO LOCAL
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    reload_enabled = os.getenv("SIMULADOR_RELOAD", "true").strip().lower() in {
        "1", "true", "yes", "sim",
    }
    uvicorn.run(
        "main:app",
        host=os.getenv("SIMULADOR_HOST", "127.0.0.1"),
        port=int(os.getenv("SIMULADOR_PORT", "8001")),
        reload=reload_enabled,
    )
