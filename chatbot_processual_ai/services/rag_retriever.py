from __future__ import annotations

from typing import Any

from config import RAG_ENABLED, RAG_MIN_SCORE, RAG_TOP_K
from services.embedding_service import EmbeddingError, generate_embedding
from services.process_repository import get_chunks_for_process, update_chunk_vector_id
from services.qdrant_vector_store import (
    QdrantError,
    deterministic_point_id,
    ensure_collection,
    search_points,
    upsert_point,
)
from services.text_normalization import normalize_process_number


RAG_NOT_NEEDED = "not_needed"
RAG_SUCCESS = "success"
RAG_EMPTY = "empty"
RAG_UNAVAILABLE = "unavailable"
RAG_ERROR = "error"


def empty_rag_context(status: str = RAG_NOT_NEEDED, query: str = "") -> dict[str, Any]:
    return {
        "status": status,
        "query": query,
        "chunks": [],
        "sources": [],
    }


def retrieve_rag_context(
    *,
    query: str,
    process_number: str | None,
    requires_rag: bool,
) -> dict[str, Any]:
    if not requires_rag:
        return empty_rag_context(RAG_NOT_NEEDED, query)

    if not RAG_ENABLED:
        return empty_rag_context(RAG_UNAVAILABLE, query)

    normalized_number = normalize_process_number(process_number)
    if normalized_number is None:
        return empty_rag_context(RAG_EMPTY, query)

    chunks = get_chunks_for_process(normalized_number)
    if not chunks:
        return empty_rag_context(RAG_EMPTY, query)

    try:
        query_vector = generate_embedding(query)
        ensure_collection(len(query_vector))
        _sync_process_chunks(normalized_number, chunks)
        results = search_points(
            vector=query_vector,
            process_number=normalized_number,
            top_k=RAG_TOP_K,
            min_score=RAG_MIN_SCORE,
        )
    except (EmbeddingError, QdrantError):
        return empty_rag_context(RAG_UNAVAILABLE, query)
    except Exception:
        return empty_rag_context(RAG_ERROR, query)

    retrieved_chunks = [_chunk_from_result(item) for item in results]
    retrieved_chunks = [chunk for chunk in retrieved_chunks if chunk]
    if not retrieved_chunks:
        return empty_rag_context(RAG_EMPTY, query)

    return {
        "status": RAG_SUCCESS,
        "query": query,
        "chunks": retrieved_chunks,
        "sources": _sources_from_chunks(retrieved_chunks),
    }


def _sync_process_chunks(process_number: str, chunks: list[dict[str, Any]]) -> None:
    for chunk in chunks:
        text = str(chunk.get("text") or "").strip()
        if not text:
            continue

        vector = generate_embedding(text)
        point_id = deterministic_point_id(
            process_number,
            str(chunk.get("source_type") or ""),
            str(chunk.get("source_id") or ""),
            str(chunk.get("chunk_index") or 0),
            str(chunk.get("text_hash") or ""),
        )
        payload = {
            "chunk_id": chunk.get("id"),
            "numero_processo": process_number,
            "source_type": chunk.get("source_type"),
            "source_id": chunk.get("source_id"),
            "chunk_index": chunk.get("chunk_index"),
            "title": chunk.get("title"),
            "date": chunk.get("date"),
            "content_kind": chunk.get("content_kind"),
            "text_hash": chunk.get("text_hash"),
            "text": text,
        }
        upsert_point(point_id=point_id, vector=vector, payload=payload)

        chunk_id = chunk.get("id")
        if isinstance(chunk_id, int):
            update_chunk_vector_id(chunk_id, point_id)


def _chunk_from_result(result: dict[str, Any]) -> dict[str, Any]:
    payload = result.get("payload")
    if not isinstance(payload, dict):
        return {}

    text = str(payload.get("text") or "").strip()
    if not text:
        return {}

    return {
        "score": result.get("score"),
        "text": text,
        "source_type": payload.get("source_type"),
        "source_id": payload.get("source_id"),
        "chunk_index": payload.get("chunk_index"),
        "title": payload.get("title"),
        "date": payload.get("date"),
        "content_kind": payload.get("content_kind"),
        "text_hash": payload.get("text_hash"),
    }


def _sources_from_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = []
    seen = set()
    for chunk in chunks:
        key = (
            chunk.get("source_type"),
            chunk.get("source_id"),
            chunk.get("title"),
            chunk.get("date"),
        )
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "tipo": chunk.get("source_type"),
                "titulo": chunk.get("title"),
                "data": chunk.get("date"),
                "conteudo": chunk.get("content_kind"),
            }
        )
    return sources
