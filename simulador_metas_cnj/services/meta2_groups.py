"""Cálculo isolado da Meta 2 para os grupos A e ANT."""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional

import numpy as np


YEAR = 2026
GROUPS = {
    "A": {
        "D": 27548,
        "description": "Processos distribuídos até 31/12/2024",
        "formula": "Meta 2-A = (Julgados_base + Julgados_ano) ÷ (D − Suspensos_dez) × (1000÷9,4)",
    },
    "ANT": {
        "D": 72,
        "description": "Processos distribuídos até 31/12/2021",
        "formula": "Meta 2-ANT = Julgados_ano ÷ (D − Suspensos_dez − Dessobrestados_ano) × 100",
    },
}

HISTORY = {
    "A": {
        "months": [f"2025-{month:02d}" for month in range(1, 13)] + ["2026-01", "2026-02"],
        "julgados": [1820, 1680, 2050, 1920, 2100, 1850, 1750, 2200, 1980, 2050, 1900, 1735, 180, 137],
        "suspensos": [95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 97, 92, 90],
        "dessobrestados": [8, 7, 9, 6, 10, 8, 7, 9, 8, 7, 9, 8, 2, 0],
        "prior_judgments": 25863,
    },
    "ANT": {
        "months": [f"2025-{month:02d}" for month in range(1, 13)] + ["2026-01", "2026-02"],
        "julgados": [0] * 12 + [2, 0],
        "suspensos": [0] * 12 + [1, 1],
        "dessobrestados": [0] * 14,
        "prior_judgments": 0,
    },
}

FORECAST = {
    "A": {
        "months": [f"2026-{month:02d}" for month in range(3, 13)],
        "julgados": [75, 72, 78, 71, 69, 74, 73, 70, 68, 77],
        "suspensos": [89, 88, 87, 86, 85, 84, 83, 82, 81, 190],
        "dessobrestados": [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    },
    "ANT": {
        "months": [f"2026-{month:02d}" for month in range(3, 13)],
        "julgados": [2] * 10,
        "suspensos": [1] * 9 + [28],
        "dessobrestados": [2, 2, 2, 2, 2, 2, 2, 3, 3, 24],
    },
}

RESULT_2025 = {
    "A": {"meta": 106.22, "julgados": 25985, "distribuidos": 26121, "suspensos": 97, "dessobrestados": 0},
    "ANT": {"meta": 100.0, "julgados": 0, "distribuidos": 0, "suspensos": 0, "dessobrestados": 0},
}
AVAILABLE_MONTHS = frozenset(HISTORY["A"]["months"] + FORECAST["A"]["months"])


def _meta_a(judgments: float, distributed: float, suspended: float) -> Optional[float]:
    denominator = distributed - suspended
    if denominator <= 0 or np.isnan(denominator):
        return None
    return float(judgments / denominator * (1000 / 9.4))


def _meta_ant(judgments: float, distributed: float, suspended: float, reopened: float) -> Optional[float]:
    denominator = distributed - suspended - reopened
    if denominator <= 0 or np.isnan(denominator):
        return None
    return float(judgments / denominator * 100)


def build_series(group: str, changes: Optional[Dict[str, dict]] = None) -> List[dict]:
    if group not in GROUPS:
        raise ValueError(f"Grupo inválido: {group}")
    changes = changes or {}
    records = []
    for source, kind in ((HISTORY[group], "real"), (FORECAST[group], "previsao")):
        for index, month in enumerate(source["months"]):
            change = changes.get(month, {})
            records.append({
                "data": month,
                "tipo": kind,
                "julgados": max(0, source["julgados"][index] + change.get("julgados", 0)),
                "suspensos": max(0, source["suspensos"][index] + change.get("suspensos", 0)),
                "dessobrestados": max(0, source["dessobrestados"][index] + change.get("dessobrestados", 0)),
            })

    accumulated_judgments = 0
    accumulated_reopened = 0
    for record in records:
        in_year = record["data"].startswith(str(YEAR))
        if in_year:
            accumulated_judgments += record["julgados"]
            accumulated_reopened += record["dessobrestados"]
        record["julgados_acum_2026"] = accumulated_judgments if in_year else None
        record["dessobrestados_acum_2026"] = accumulated_reopened if in_year else None
        if not in_year:
            value = None
        elif group == "A":
            value = _meta_a(HISTORY[group]["prior_judgments"] + accumulated_judgments, GROUPS[group]["D"], record["suspensos"])
        else:
            value = _meta_ant(accumulated_judgments, GROUPS[group]["D"], record["suspensos"], accumulated_reopened)
        record["meta2"] = round(value, 2) if value is not None else None
    return records


def _final(group: str, series: List[dict]) -> dict:
    year_records = [record for record in series if record["data"].startswith(str(YEAR))]
    return {
        "grupo": group,
        "ano": YEAR,
        "meta2": year_records[-1]["meta2"] if year_records else None,
        "distribuidos": GROUPS[group]["D"],
        "descricao": GROUPS[group]["description"],
        "formula": GROUPS[group]["formula"],
    }


def simulate(changes_a: Optional[Dict[str, dict]] = None, changes_ant: Optional[Dict[str, dict]] = None) -> dict:
    series_a = build_series("A", changes_a)
    series_ant = build_series("ANT", changes_ant)
    return {
        "resultado_2025": deepcopy(RESULT_2025),
        "resultado_2026": {"A": _final("A", series_a), "ANT": _final("ANT", series_ant)},
        "serie_A": series_a,
        "serie_ANT": series_ant,
    }
