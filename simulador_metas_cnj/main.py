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
from datetime import datetime
from functools import reduce
from typing import Any, Dict, List, Literal, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint, validator

# ── Caminhos dos arquivos Excel ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(
    os.path.join(BASE_DIR, os.getenv("SIMULADOR_DATA_DIR", "dados"))
)

ARQ_NOVOS          = os.path.join(DATA_DIR, "casos_novos.xlsx")
ARQ_JULGADOS       = os.path.join(DATA_DIR, "julgados.xlsx")
ARQ_DESSOBRESTADOS = os.path.join(DATA_DIR, "dessobrestados.xlsx")
ARQ_SUSPENSOS      = os.path.join(DATA_DIR, "suspensos.xlsx")

# ── Configurações ────────────────────────────────────────────────────────────
META_ALVO          = 100.0
ANO_SIMULACAO      = 2026
DATA_CORTE_REAL    = pd.Timestamp("2026-02-01")
DATA_FINAL         = pd.Timestamp("2027-02-01")
VARIAVEIS_EDITAVEIS = ["julgados", "dessobrestados", "suspensos"]


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
_novos          = carregar_base_forecast(ARQ_NOVOS, "novos", col_data="data_oficial")
_julgados       = carregar_julgados(ARQ_JULGADOS)
_dessobrestados = carregar_base_forecast(
    ARQ_DESSOBRESTADOS, "dessobrestados",
    col_data="data_referencia", col_valor="qtd_eventos_dessobrestamento",
)
_suspensos      = carregar_base_forecast(
    ARQ_SUSPENSOS, "suspensos",
    col_data="data_referencia", col_valor="suspensos",
)
BASE_GLOBAL: pd.DataFrame = consolidar_bases(_novos, None, _julgados, _dessobrestados, _suspensos)


# ════════════════════════════════════════════════════════════════════════════
# FÓRMULAS CNJ (idênticas ao script original)
# ════════════════════════════════════════════════════════════════════════════

def calcular_meta1(novos, julgados, dessobrestados, suspensos, piso=None):
    denominador = novos + dessobrestados - suspensos
    if denominador is None or pd.isna(denominador) or denominador == 0:
        return np.nan
    if piso is None:
        piso = max(novos + dessobrestados, 1)
    denominador = max(denominador, piso)
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
    return r


def calcular_metas(df: pd.DataFrame) -> pd.DataFrame:
    r = calcular_acumulados(df)
    r["meta1"] = r.apply(
        lambda l: calcular_meta1(
            l["novos_acum"], l["julgados_acum"],
            l["dessobrestados_acum"], l["suspensos_acum"],
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
            sim.loc[mascara, var] = (sim.loc[mascara, var] + inc).clip(lower=0)
    return calcular_metas(sim)


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
