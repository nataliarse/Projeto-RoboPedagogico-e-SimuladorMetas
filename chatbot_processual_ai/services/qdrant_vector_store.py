from __future__ import annotations

import uuid
from typing import Any

import requests

from config import QDRANT_COLLECTION, QDRANT_URL, RAG_MIN_SCORE, RAG_TOP_K


class QdrantError(Exception):
    pass


def deterministic_point_id(*parts: str) -> str:
    name = ":".join(str(part) for part in parts)
    return str(uuid.uuid5(uuid.NAMESPACE_URL, name))


def ensure_collection(vector_size: int) -> None:
    if vector_size <= 0:
        raise QdrantError("Dimensao de vetor invalida.")

    if _collection_exists():
        return

    _request_json(
        "PUT",
        f"/collections/{QDRANT_COLLECTION}",
        json={
            "vectors": {
                "size": vector_size,
                "distance": "Cosine",
            }
        },
    )


def upsert_point(
    *,
    point_id: str,
    vector: list[float],
    payload: dict[str, Any],
) -> None:
    _request_json(
        "PUT",
        f"/collections/{QDRANT_COLLECTION}/points",
        params={"wait": "true"},
        json={
            "points": [
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": payload,
                }
            ]
        },
    )


def search_points(
    *,
    vector: list[float],
    process_number: str,
    top_k: int | None = None,
    min_score: float | None = None,
) -> list[dict[str, Any]]:
    data = _request_json(
        "POST",
        f"/collections/{QDRANT_COLLECTION}/points/search",
        json={
            "vector": vector,
            "limit": top_k or RAG_TOP_K,
            "score_threshold": RAG_MIN_SCORE if min_score is None else min_score,
            "with_payload": True,
            "filter": {
                "must": [
                    {
                        "key": "numero_processo",
                        "match": {
                            "value": process_number,
                        },
                    }
                ]
            },
        },
    )

    result = data.get("result")
    if not isinstance(result, list):
        raise QdrantError("Qdrant retornou resultado inesperado.")

    return [item for item in result if isinstance(item, dict)]


def _collection_exists() -> bool:
    try:
        _request_json("GET", f"/collections/{QDRANT_COLLECTION}")
        return True
    except QdrantError as exc:
        if "HTTP 404" in str(exc):
            return False
        raise


def _request_json(
    method: str,
    endpoint: str,
    **kwargs: Any,
) -> dict[str, Any]:
    url = f"{QDRANT_URL.rstrip('/')}{endpoint}"
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
    except requests.exceptions.RequestException as exc:
        raise QdrantError("Falha ao chamar o Qdrant local.") from exc

    if not response.ok:
        raise QdrantError(f"Qdrant retornou HTTP {response.status_code}: {response.text}")

    if not response.text.strip():
        return {}

    try:
        data = response.json()
    except ValueError as exc:
        raise QdrantError("Qdrant retornou JSON invalido.") from exc

    if not isinstance(data, dict):
        raise QdrantError("Qdrant retornou payload inesperado.")

    return data
