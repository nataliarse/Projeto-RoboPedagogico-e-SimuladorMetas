from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from typing import Any


EVENT_KEYWORDS = {
    "julgamento": ("sentenca", "julgado", "julgamento"),
    "baixa": ("baixado", "baixa"),
    "arquivamento": ("arquivado", "arquivamento"),
    "distribuicao": ("distribuido", "distribuicao", "autuacao", "autuado"),
}

EXPECTED_FIELDS = ("processo", "movimentacoes", "documentos", "pendencias")


def extract_process_events(process: dict) -> dict:
    """Extract relevant procedural events from an already collected process JSON."""
    sources = list(_iter_expected_sources(process))
    has_searchable_data = bool(sources)

    eventos_detectados = []
    movement_events = []
    detected_types = set()

    for source in sources:
        normalized_text = _normalize_text(source["texto"])

        for event_type, keywords in EVENT_KEYWORDS.items():
            if not _has_any_keyword(normalized_text, keywords):
                continue

            detected_types.add(event_type)
            event = _build_event(event_type, source)
            eventos_detectados.append(event)

            if source["origem"] == "movimentacoes":
                movement_events.append((source["posicao"], _movement_summary(source), event))

    observacoes = []
    if not has_searchable_data:
        observacoes.append(
            "Dados insuficientes nos campos esperados para identificar eventos processuais."
        )

    ultima_movimentacao_relevante = None
    if movement_events:
        ultima_movimentacao_relevante = max(movement_events, key=lambda item: item[0])[1]

    return {
        "eventos_detectados": eventos_detectados,
        "possui_distribuicao": _event_flag("distribuicao", detected_types, has_searchable_data),
        "possui_julgamento": _event_flag("julgamento", detected_types, has_searchable_data),
        "possui_baixa": _event_flag("baixa", detected_types, has_searchable_data),
        "possui_arquivamento": _event_flag(
            "arquivamento", detected_types, has_searchable_data
        ),
        "ultima_movimentacao_relevante": ultima_movimentacao_relevante,
        "observacoes": observacoes,
    }


def _event_flag(event_type: str, detected_types: set[str], has_searchable_data: bool) -> bool | None:
    if not has_searchable_data:
        return None
    return event_type in detected_types


def _iter_expected_sources(process: dict) -> Iterable[dict]:
    if not isinstance(process, dict):
        return

    for field in EXPECTED_FIELDS:
        value = process.get(field)
        if field == "processo":
            yield from _iter_dict_sources(value, field)
        elif field in {"movimentacoes", "documentos", "pendencias"}:
            yield from _iter_list_sources(value, field)


def _iter_dict_sources(value: Any, origin: str) -> Iterable[dict]:
    if not isinstance(value, dict):
        return

    for key, item_value in value.items():
        if not _has_value(item_value):
            continue

        text = _text_from_field(key, item_value)
        if text:
            yield {
                "origem": origin,
                "campo": str(key),
                "indice": None,
                "posicao": -1,
                "texto": text,
                "registro": value,
            }


def _iter_list_sources(value: Any, origin: str) -> Iterable[dict]:
    if not isinstance(value, list):
        return

    for index, item in enumerate(value):
        if isinstance(item, dict):
            for key, item_value in item.items():
                if not _has_value(item_value):
                    continue

                text = _text_from_field(key, item_value)
                if text:
                    yield {
                        "origem": origin,
                        "campo": str(key),
                        "indice": index,
                        "posicao": index,
                        "texto": text,
                        "registro": item,
                    }
            continue

        if _has_value(item):
            yield {
                "origem": origin,
                "campo": None,
                "indice": index,
                "posicao": index,
                "texto": str(item),
                "registro": item,
            }


def _text_from_field(key: Any, value: Any) -> str | None:
    if isinstance(value, (dict, list, tuple, set)):
        return None
    return f"{key}: {value}"


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _build_event(event_type: str, source: dict) -> dict:
    event = {
        "tipo": event_type,
        "origem": source["origem"],
        "campo": source["campo"],
        "texto": source["texto"],
    }

    if source["indice"] is not None:
        event["indice"] = source["indice"]

    record = source["registro"]
    if isinstance(record, dict):
        for optional_field in ("data", "ordem"):
            if _has_value(record.get(optional_field)):
                event[optional_field] = record[optional_field]

    return event


def _movement_summary(source: dict) -> str:
    record = source["registro"]
    if not isinstance(record, dict):
        return source["texto"]

    descricao = record.get("descricao")
    complemento = record.get("complemento")
    if _has_value(descricao) and _has_value(complemento):
        return f"{descricao} - {complemento}"
    if _has_value(descricao):
        return str(descricao)
    return source["texto"]


def _normalize_text(value: Any) -> str:
    text = str(value).casefold()
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _has_any_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)
