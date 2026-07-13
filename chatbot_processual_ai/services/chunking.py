from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from services.text_normalization import clean_text


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


@dataclass(frozen=True)
class ProcessChunk:
    source_type: str
    source_id: str
    chunk_index: int
    text: str
    title: str | None = None
    date: str | None = None
    content_kind: str = "metadata"


def chunk_text(
    text: str,
    *,
    max_chars: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    normalized = clean_text(text)
    if not normalized:
        return []

    if len(normalized) <= max_chars:
        return [normalized]

    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break

        start = max(0, end - overlap)

    return chunks


def build_process_chunks(process: dict) -> list[ProcessChunk]:
    chunks: list[ProcessChunk] = []

    for index, movement in enumerate(_list_value(process.get("movimentacoes"))):
        if not isinstance(movement, dict):
            continue

        text_parts = [
            _label_value("Movimentação", movement.get("descricao")),
            _label_value("Complemento", movement.get("complemento")),
            _label_value("Referência", movement.get("referencia")),
        ]
        text = ". ".join(part for part in text_parts if part)
        for chunk_index, chunk in enumerate(chunk_text(text)):
            chunks.append(
                ProcessChunk(
                    source_type="movement",
                    source_id=str(index),
                    chunk_index=chunk_index,
                    text=chunk,
                    title=clean_text(movement.get("descricao")) or None,
                    date=_date_only(movement.get("data")),
                    content_kind="metadata",
                )
            )

    for index, document in enumerate(_list_value(process.get("documentos"))):
        if not isinstance(document, dict):
            continue

        content = _document_content(document)
        if content:
            text = content
            content_kind = "full_text"
        else:
            content_kind = "metadata"
            text = ". ".join(
                part
                for part in (
                    _label_value("Documento", document.get("titulo")),
                    _label_value("Tipo", document.get("tipo")),
                    _label_value("Data", _date_only(document.get("data"))),
                )
                if part
            )

        for chunk_index, chunk in enumerate(chunk_text(text)):
            chunks.append(
                ProcessChunk(
                    source_type="document",
                    source_id=str(index),
                    chunk_index=chunk_index,
                    text=chunk,
                    title=clean_text(document.get("titulo")) or None,
                    date=_date_only(document.get("data")),
                    content_kind=content_kind,
                )
            )

    return chunks


def _document_content(document: dict[str, Any]) -> str:
    for field_name in ("conteudo", "texto", "teor"):
        content = clean_text(document.get(field_name))
        if content:
            return content
    return ""


def _label_value(label: str, value: Any) -> str:
    text = clean_text(value)
    if not text:
        return ""
    return f"{label}: {text}"


def _date_only(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    if "T" in text:
        return text.split("T", 1)[0]
    return text


def _list_value(value: Any) -> list:
    return value if isinstance(value, list) else []
