from __future__ import annotations

from typing import Any

from config import RAG_ENABLED, RAG_MIN_SCORE, RAG_TOP_K
from progress import ProgressReporter, progress_clock, report_progress
from services.embedding_service import EmbeddingError, generate_embedding
from services.process_query_resolver import (
    TARGET_DOCUMENT_CONTENT,
    resolve_process_query,
)
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
    progress_reporter: ProgressReporter | None = None,
) -> dict[str, Any]:
    if not requires_rag:
        report_progress(
            progress_reporter,
            code="rag.skipped",
            level="success",
            message="busca semantica nao necessaria para esta pergunta.",
            details={"rag_status": RAG_NOT_NEEDED},
        )
        return empty_rag_context(RAG_NOT_NEEDED, query)

    if not RAG_ENABLED:
        report_progress(
            progress_reporter,
            code="rag.unavailable",
            level="warning",
            message="busca semantica desativada; usando dados estruturados.",
            details={"rag_status": RAG_UNAVAILABLE},
        )
        return empty_rag_context(RAG_UNAVAILABLE, query)

    normalized_number = normalize_process_number(process_number)
    if normalized_number is None:
        report_progress(
            progress_reporter,
            code="rag.empty",
            level="warning",
            message="sem processo ativo para busca semantica.",
            details={"rag_status": RAG_EMPTY},
        )
        return empty_rag_context(RAG_EMPTY, query)

    chunks = get_chunks_for_process(normalized_number)
    if not chunks:
        report_progress(
            progress_reporter,
            code="rag.empty",
            level="warning",
            message="nenhum trecho local disponivel para busca semantica.",
            details={"rag_status": RAG_EMPTY},
        )
        return empty_rag_context(RAG_EMPTY, query)

    rag_started_at = progress_clock()
    try:
        embedding_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="rag.embedding_query.started",
            level="started",
            message="gerando embedding da pergunta...",
        )
        query_vector = generate_embedding(query)
        report_progress(
            progress_reporter,
            code="rag.embedding_query.finished",
            level="success",
            message="embedding da pergunta gerado.",
            details={"vector_size": len(query_vector)},
            started_at=embedding_started_at,
        )

        collection_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="rag.collection.started",
            level="started",
            message="preparando indice vetorial local...",
        )
        ensure_collection(len(query_vector))
        report_progress(
            progress_reporter,
            code="rag.collection.finished",
            level="success",
            message="indice vetorial pronto.",
            started_at=collection_started_at,
        )

        sync_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="rag.sync.started",
            level="started",
            message="sincronizando trechos do processo...",
            details={"chunks_count": _count_text_chunks(chunks)},
        )
        _sync_process_chunks(normalized_number, chunks)
        report_progress(
            progress_reporter,
            code="rag.sync.finished",
            level="success",
            message="trechos do processo sincronizados.",
            details={"chunks_count": _count_text_chunks(chunks)},
            started_at=sync_started_at,
        )

        search_started_at = progress_clock()
        report_progress(
            progress_reporter,
            code="rag.search.started",
            level="started",
            message="buscando trechos relevantes...",
            details={"top_k": RAG_TOP_K},
        )
        results = search_points(
            vector=query_vector,
            process_number=normalized_number,
            top_k=RAG_TOP_K,
            min_score=RAG_MIN_SCORE,
        )
        results = _rerank_results(query, results)
        report_progress(
            progress_reporter,
            code="rag.search.finished",
            level="success",
            message="busca vetorial concluida.",
            details={"results_count": len(results)},
            started_at=search_started_at,
        )
    except (EmbeddingError, QdrantError) as exc:
        report_progress(
            progress_reporter,
            code="rag.unavailable",
            level="warning",
            message="busca semantica indisponivel; usando dados estruturados.",
            details={
                "rag_status": RAG_UNAVAILABLE,
                "error_type": type(exc).__name__,
            },
            started_at=rag_started_at,
        )
        return empty_rag_context(RAG_UNAVAILABLE, query)
    except Exception as exc:
        report_progress(
            progress_reporter,
            code="rag.error",
            level="error",
            message="busca semantica falhou; usando dados estruturados.",
            details={
                "rag_status": RAG_ERROR,
                "error_type": type(exc).__name__,
            },
            started_at=rag_started_at,
        )
        return empty_rag_context(RAG_ERROR, query)

    retrieved_chunks = [_chunk_from_result(item) for item in results]
    retrieved_chunks = [chunk for chunk in retrieved_chunks if chunk]
    if not retrieved_chunks:
        report_progress(
            progress_reporter,
            code="rag.empty",
            level="warning",
            message="busca semantica nao encontrou trechos uteis.",
            details={"rag_status": RAG_EMPTY},
            started_at=rag_started_at,
        )
        return empty_rag_context(RAG_EMPTY, query)

    sources = _sources_from_chunks(retrieved_chunks)
    report_progress(
        progress_reporter,
        code="rag.finished",
        level="success",
        message="trechos relevantes recuperados.",
        details={
            "rag_status": RAG_SUCCESS,
            "chunks_count": len(retrieved_chunks),
            "sources_count": len(sources),
        },
        started_at=rag_started_at,
    )
    return {
        "status": RAG_SUCCESS,
        "query": query,
        "chunks": retrieved_chunks,
        "sources": sources,
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


def _rerank_results(query: str, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not results:
        return []

    query_spec = resolve_process_query(query)
    query_terms = _query_terms(query)
    ranked = []

    for index, result in enumerate(results):
        if not isinstance(result, dict):
            continue

        score = _safe_score(result.get("score"))
        score += _rerank_bonus(result, query_spec, query_terms)
        ranked.append((score, index, result))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    reranked_results = []
    for score, _index, result in ranked:
        reranked = dict(result)
        reranked["rerank_score"] = score
        reranked_results.append(reranked)

    return reranked_results


def _rerank_bonus(
    result: dict[str, Any],
    query_spec: Any,
    query_terms: set[str],
) -> float:
    payload = result.get("payload")
    if not isinstance(payload, dict):
        return 0.0

    source_type = str(payload.get("source_type") or "")
    source_id = str(payload.get("source_id") or "")
    content_kind = str(payload.get("content_kind") or "")
    searchable = _searchable_payload_text(payload)
    bonus = 0.0

    field_key = getattr(query_spec, "field_key", None)
    if field_key:
        if source_type == "process_field" and source_id == field_key:
            bonus += 0.50
        elif field_key in source_id or field_key.replace("_", " ") in searchable:
            bonus += 0.20
        if content_kind == "structured_field":
            bonus += 0.20

    if getattr(query_spec, "target", None) == TARGET_DOCUMENT_CONTENT:
        if source_type == "document":
            bonus += 0.12
        if content_kind == "full_text":
            bonus += 0.25

    term_matches = sum(1 for term in query_terms if term in searchable)
    bonus += min(0.18, term_matches * 0.03)
    return bonus


def _query_terms(query: str) -> set[str]:
    import re
    import unicodedata

    normalized = unicodedata.normalize("NFD", str(query or "").lower())
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )
    stopwords = {
        "a",
        "ao",
        "da",
        "de",
        "do",
        "e",
        "me",
        "o",
        "os",
        "qual",
        "que",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalized)
        if len(token) > 2 and token not in stopwords
    }


def _searchable_payload_text(payload: dict[str, Any]) -> str:
    import unicodedata

    text = " ".join(
        str(payload.get(field) or "")
        for field in ("source_type", "source_id", "title", "content_kind", "text")
    ).lower()
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


def _safe_score(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _count_text_chunks(chunks: list[dict[str, Any]]) -> int:
    return len([chunk for chunk in chunks if str(chunk.get("text") or "").strip()])


def _chunk_from_result(result: dict[str, Any]) -> dict[str, Any]:
    payload = result.get("payload")
    if not isinstance(payload, dict):
        return {}

    text = str(payload.get("text") or "").strip()
    if not text:
        return {}

    return {
        "score": result.get("rerank_score", result.get("score")),
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
