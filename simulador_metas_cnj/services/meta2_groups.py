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
A_2026_FACTOR = 1000 / 9.4
ORIGINAL_ANT_FACTOR = 100

GROUPS = {
    "A": {
        "D": 27548,
        "description": "Processos distribuídos até 31/12/2024",
        "formula": "Meta 2-A = (Julgados_base + Julgados_ano) ÷ (D − Suspensos_dez − Dessobrestados_ano) × (1000÷9,4)",
    },
    "ANT": {
        "D": 72,
        "description": "Processos distribuídos até 31/12/2021",
        "formula": "Meta 2-ANT = Julgados ÷ (D − Suspensos − Dessobrestados) × (1000÷9,9)",
    },
}

# Séries agregadas reconstruídas offline com os fontes e o ZIP da entrega. O ZIP
# processual e os arquivos por processo permanecem fora do repositório; os hashes
# permitem conferir novamente a mesma evidência sem publicar dados sensíveis.
DATASET_METADATA = {
    "A": {
        "proveniencia": {
            "fonte": "Entrega 06 / TRT18.csv, agregado pelo código original",
            "versao": "sha256:7da8d2d89b7f2df078dbda2df38e68577a53f906d629baf90cbe11b7251065bd",
            "referencia": "jan/2025 a fev/2026 observado; mar a dez/2026 ARIMA",
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
            "fonte": "Entrega 06 / TRT18.csv, agregado pelo código original",
            "versao": "sha256:7da8d2d89b7f2df078dbda2df38e68577a53f906d629baf90cbe11b7251065bd",
            "referencia": "jan/2025 a fev/2026 observado; mar a dez/2026 ARIMA",
            "homologada": False,
        },
        "semantica_temporal": {
            "julgados": MONTHLY_FLOW,
            "suspensos": CONSOLIDATED_LOAD,
            "dessobrestados": MONTHLY_FLOW,
        },
    },
}

HISTORY = {
    "A": {
        "months": [f"2025-{month:02d}" for month in range(1, 13)] + ["2026-01", "2026-02"],
        "julgados": [4284, 6700, 4038, 2829, 2300, 1547, 1277, 910, 728, 503, 336, 277, 127, 190],
        "suspensos": [150, 147, 135, 132, 147, 158, 170, 176, 182, 187, 188, 198, 194, 192],
        "dessobrestados": [31, 72, 37, 29, 46, 40, 19, 30, 19, 9, 14, 4, 22, 11],
        "prior_judgments": 25863,
    },
    "ANT": {
        "months": [f"2025-{month:02d}" for month in range(1, 13)] + ["2026-01", "2026-02"],
        "julgados": [0] * 13 + [2],
        "suspensos": [7, 8, 8, 8, 10, 10, 12, 12, 13, 14, 14, 14, 15, 16],
        "dessobrestados": [0, 0, 1, 2, 6, 11, 1, 4, 3, 2, 0, 0, 5, 1],
        "prior_judgments": 0,
    },
}

FORECAST = {
    "A": {
        "months": [f"2026-{month:02d}" for month in range(3, 13)],
        "julgados": [155, 126, 103, 84, 68, 55, 45, 37, 30, 24],
        "suspensos": [191, 191, 190, 190, 190, 190, 190, 190, 190, 190],
        "dessobrestados": [17, 13, 16, 14, 15, 14, 15, 14, 15, 14],
    },
    "ANT": {
        "months": [f"2026-{month:02d}" for month in range(3, 13)],
        "julgados": [2] * 10,
        "suspensos": [17, 18, 19, 20, 21, 22, 23, 25, 26, 28],
        "dessobrestados": [1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
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
    """Meta 2 ANT/TRTs conforme o Glossário CNJ 2026, versão 3."""
    return calculate_ant_percentage(
        judgments, distributed, suspended, reopened, ANT_2026_FACTOR
    )


def _meta_a(
    judgments: float,
    distributed: float,
    suspended: float,
    reopened: float,
) -> Optional[float]:
    """Meta 2 A/TRTs conforme a versão 3, inclusive dessobrestados."""
    if not _finite(judgments, distributed, suspended, reopened):
        return None
    denominator = distributed - suspended - reopened
    if denominator <= 0:
        return None
    value = judgments / denominator * A_2026_FACTOR
    return float(value) if math.isfinite(value) else None


def _meta_a_original(
    judgments: float,
    distributed: float,
    suspended: float,
) -> Optional[float]:
    """Reproduz a entrega, que não descontava dessobrestados em A."""
    if not _finite(judgments, distributed, suspended):
        return None
    denominator = distributed - suspended
    if denominator <= 0:
        return None
    value = judgments / denominator * A_2026_FACTOR
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
        original_value = (
            calculate_ant_percentage(
                judgments, distributed, suspended, reopened, ORIGINAL_ANT_FACTOR
            )
            if _finite(judgments, distributed, suspended, reopened)
            else None
        )
        record["denominador_original"] = record["denominador"]
        record["meta2_original"] = (
            round(original_value, 2) if original_value is not None else None
        )
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
        judgments = HISTORY[group]["prior_judgments"] + accumulated_judgments
        record["julgados_calculo"] = judgments if in_year else None
        record["suspensos_calculo"] = record["suspensos"] if in_year else None
        record["dessobrestados_calculo"] = accumulated_reopened if in_year else None
        record["denominador"] = (
            GROUPS[group]["D"] - record["suspensos"] - accumulated_reopened
            if in_year else None
        )
        record["denominador_original"] = (
            GROUPS[group]["D"] - record["suspensos"] if in_year else None
        )
        value = _meta_a(
            judgments,
            GROUPS[group]["D"],
            record["suspensos"],
            accumulated_reopened,
        ) if in_year else None
        original_value = _meta_a_original(
            judgments, GROUPS[group]["D"], record["suspensos"]
        ) if in_year else None
        record["meta2"] = round(value, 2) if value is not None else None
        record["meta2_original"] = (
            round(original_value, 2) if original_value is not None else None
        )
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
        "mensagem_validacao": (
            "Metodologia oficial CNJ 2026 v3 aplicada a dados não homologados"
            if status == "demonstrativo" else message
        ),
        "proveniencia": deepcopy(DATASET_METADATA[group]["proveniencia"]),
        "semantica_temporal": deepcopy(DATASET_METADATA[group]["semantica_temporal"]),
    }


def _original_final(group: str, series: List[dict]) -> dict:
    year_records = [record for record in series if record["data"].startswith(str(YEAR))]
    return {
        "grupo": group,
        "ano": YEAR,
        "meta2": year_records[-1]["meta2_original"] if year_records else None,
        "distribuidos": GROUPS[group]["D"],
        "descricao": "Reprodução histórica da entrega da equipe",
        "formula": (
            "Meta 2-A = Julgados ÷ (D − Suspensos_dez) × (1000÷9,4)"
            if group == "A"
            else "Meta 2-ANT = Julgados ÷ (D − Suspensos_dez − Dessobrestados_ano) × 100"
        ),
        "homologado": False,
        "status_validacao": "demonstrativo",
        "mensagem_validacao": "Reprodução não homologada; não corresponde à metodologia CNJ 2026 v3",
        "proveniencia": deepcopy(DATASET_METADATA[group]["proveniencia"]),
        "semantica_temporal": deepcopy(DATASET_METADATA[group]["semantica_temporal"]),
    }


def simulate(changes_a: Optional[Dict[str, dict]] = None, changes_ant: Optional[Dict[str, dict]] = None) -> dict:
    series_a = build_series("A", changes_a)
    series_ant = build_series("ANT", changes_ant)
    return {
        "resultado_2025": deepcopy(RESULT_2025),
        "resultado_2026": {"A": _final("A", series_a), "ANT": _final("ANT", series_ant)},
        "reproducao_original_2026": {
            "A": _original_final("A", series_a),
            "ANT": _original_final("ANT", series_ant),
        },
        "serie_A": series_a,
        "serie_ANT": series_ant,
    }
