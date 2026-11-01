"""Cálculo isolado da Meta 2 para os grupos A e ANT."""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Dict, List, Optional


YEAR = 2026
CONSOLIDATED_LOAD = "carga_consolidada"
MONTHLY_FLOW = "fluxo_mensal"
UNDEFINED_SEMANTICS = "indefinida"
ANT_2026_FACTOR = 1000 / 9.9

GROUPS = {
    "A": {
        "D": 27548,
        "description": "Processos distribuídos até 31/12/2024",
        "formula": "Meta 2-A = (Julgados_base + Julgados_ano) ÷ (D − Suspensos_dez) × (1000÷9,4)",
    },
    "ANT": {
        "D": 72,
        "description": "Processos distribuídos até 31/12/2021",
        "formula": "Meta 2-ANT = Julgados ÷ (D − Suspensos − Dessobrestados) × (1000÷9,9)",
    },
}

# As séries recebidas foram preservadas para comparação histórica. Elas não têm
# extrato de origem, versão do modelo ARIMA ou homologação que permita tratá-las
# como dados oficiais. A semântica de ANT permanece indefinida de propósito: o
# código não tenta inferir se cada número é fluxo mensal ou carga consolidada.
DATASET_METADATA = {
    "A": {
        "proveniencia": {
            "fonte": "Série estática recebida da Equipe B",
            "versao": None,
            "referencia": "jan/2025 a dez/2026",
            "homologada": False,
        },
        "semantica_temporal": {
            "julgados": MONTHLY_FLOW,
            "suspensos": CONSOLIDATED_LOAD,
            "dessobrestados": MONTHLY_FLOW,
        },
    },
    "ANT": {
        "proveniencia": {
            "fonte": "Série estática recebida da Equipe B",
            "versao": None,
            "referencia": "jan/2025 a dez/2026",
            "homologada": False,
        },
        "semantica_temporal": {
            "julgados": UNDEFINED_SEMANTICS,
            "suspensos": UNDEFINED_SEMANTICS,
            "dessobrestados": UNDEFINED_SEMANTICS,
        },
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


def _finite(*values: float) -> bool:
    return all(value is not None and math.isfinite(float(value)) for value in values)


def calculate_ant_percentage(
    judgments: float,
    distributed: float,
    suspended: float,
    reopened: float,
    factor: float,
) -> Optional[float]:
    """Calcula ANT com fator explícito, sem piso ou fallback artificial."""
    if not _finite(judgments, distributed, suspended, reopened, factor):
        return None
    denominator = distributed - suspended - reopened
    if denominator <= 0:
        return None
    value = judgments / denominator * factor
    return float(value) if math.isfinite(value) else None


def calculate_meta_ant_2026(
    judgments: float,
    distributed: float,
    suspended: float,
    reopened: float,
) -> Optional[float]:
    """Meta 2 ANT/TRTs conforme o Glossário CNJ 2026, versão 1."""
    return calculate_ant_percentage(
        judgments, distributed, suspended, reopened, ANT_2026_FACTOR
    )


def _meta_a(judgments: float, distributed: float, suspended: float) -> Optional[float]:
    if not _finite(judgments, distributed, suspended):
        return None
    denominator = distributed - suspended
    if denominator <= 0:
        return None
    value = judgments / denominator * (1000 / 9.4)
    return float(value) if math.isfinite(value) else None


def _resolved_temporal_value(current: float, accumulated: float, semantics: str) -> Optional[float]:
    if semantics == CONSOLIDATED_LOAD:
        return current
    if semantics == MONTHLY_FLOW:
        return accumulated
    return None


def classify_dataset(metadata: dict) -> tuple[str, str, bool]:
    semantics = metadata["semantica_temporal"]
    semantics_defined = all(value in (CONSOLIDATED_LOAD, MONTHLY_FLOW) for value in semantics.values())
    provenance = metadata["proveniencia"]
    provenance_defined = bool(provenance.get("fonte") and provenance.get("versao"))
    homologated = bool(provenance.get("homologada") and provenance_defined and semantics_defined)
    if not semantics_defined:
        return "pendente_validacao", "Indicador pendente de validação", False
    if not homologated:
        return "demonstrativo", "Simulação com dados não homologados", False
    return "homologado", "Indicador calculado com dados homologados", True


def build_ant_series(
    records: List[dict],
    distributed: float,
    metadata: dict,
) -> List[dict]:
    """Calcula uma série ANT somente com semântica temporal declarada."""
    result = deepcopy(records)
    accumulated = {"julgados": 0, "suspensos": 0, "dessobrestados": 0}
    status, message, _ = classify_dataset(metadata)
    semantics = metadata["semantica_temporal"]

    for record in result:
        in_year = record["data"].startswith(str(YEAR))
        if in_year:
            for field in accumulated:
                accumulated[field] += record[field]

        record["julgados_acum_2026"] = accumulated["julgados"] if in_year else None
        record["dessobrestados_acum_2026"] = accumulated["dessobrestados"] if in_year else None
        record["status_validacao"] = status
        record["mensagem_validacao"] = message

        if not in_year:
            calculation_values = (None, None, None)
        else:
            calculation_values = tuple(
                _resolved_temporal_value(record[field], accumulated[field], semantics[field])
                for field in ("julgados", "suspensos", "dessobrestados")
            )

        judgments, suspended, reopened = calculation_values
        record["julgados_calculo"] = judgments
        record["suspensos_calculo"] = suspended
        record["dessobrestados_calculo"] = reopened
        record["denominador"] = (
            distributed - suspended - reopened
            if _finite(distributed, suspended, reopened)
            else None
        )
        value = (
            calculate_meta_ant_2026(judgments, distributed, suspended, reopened)
            if _finite(judgments, distributed, suspended, reopened)
            else None
        )
        record["meta2"] = round(value, 2) if value is not None else None
    return result


def _input_records(group: str, changes: Optional[Dict[str, dict]]) -> List[dict]:
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
    return records


def build_series(group: str, changes: Optional[Dict[str, dict]] = None) -> List[dict]:
    if group not in GROUPS:
        raise ValueError(f"Grupo inválido: {group}")
    records = _input_records(group, changes)
    if group == "ANT":
        return build_ant_series(records, GROUPS[group]["D"], DATASET_METADATA[group])

    accumulated_judgments = 0
    accumulated_reopened = 0
    status, message, _ = classify_dataset(DATASET_METADATA[group])
    for record in records:
        in_year = record["data"].startswith(str(YEAR))
        if in_year:
            accumulated_judgments += record["julgados"]
            accumulated_reopened += record["dessobrestados"]
        record["julgados_acum_2026"] = accumulated_judgments if in_year else None
        record["dessobrestados_acum_2026"] = accumulated_reopened if in_year else None
        record["status_validacao"] = status
        record["mensagem_validacao"] = message
        value = (
            _meta_a(HISTORY[group]["prior_judgments"] + accumulated_judgments, GROUPS[group]["D"], record["suspensos"])
            if in_year else None
        )
        record["meta2"] = round(value, 2) if value is not None else None
    return records


def _final(group: str, series: List[dict]) -> dict:
    year_records = [record for record in series if record["data"].startswith(str(YEAR))]
    status, message, homologated = classify_dataset(DATASET_METADATA[group])
    return {
        "grupo": group,
        "ano": YEAR,
        "meta2": year_records[-1]["meta2"] if year_records else None,
        "distribuidos": GROUPS[group]["D"],
        "descricao": GROUPS[group]["description"],
        "formula": GROUPS[group]["formula"],
        "homologado": homologated,
        "status_validacao": status,
        "mensagem_validacao": message,
        "proveniencia": deepcopy(DATASET_METADATA[group]["proveniencia"]),
        "semantica_temporal": deepcopy(DATASET_METADATA[group]["semantica_temporal"]),
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
