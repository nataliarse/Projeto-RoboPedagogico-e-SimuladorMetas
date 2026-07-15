from __future__ import annotations

from typing import Any

import requests

from config import OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL, OLLAMA_TIMEOUT_SECONDS


class EmbeddingError(Exception):
    pass


def generate_embedding(text: str) -> list[float]:
    normalized = str(text or "").strip()
    if not normalized:
        raise EmbeddingError("Texto vazio para embedding.")

    try:
        return _embed_with_api_embed(normalized)
    except EmbeddingError:
        return _embed_with_api_embeddings(normalized)


def _embed_with_api_embed(text: str) -> list[float]:
    data = _post_ollama_json(
        "/api/embed",
        {
            "model": OLLAMA_EMBED_MODEL,
            "input": text,
        },
    )
    embeddings = data.get("embeddings")
    if (
        isinstance(embeddings, list)
        and embeddings
        and isinstance(embeddings[0], list)
    ):
        return _validate_embedding(embeddings[0])

    embedding = data.get("embedding")
    if isinstance(embedding, list):
        return _validate_embedding(embedding)

    raise EmbeddingError("Resposta de embedding sem vetor.")


def _embed_with_api_embeddings(text: str) -> list[float]:
    data = _post_ollama_json(
        "/api/embeddings",
        {
            "model": OLLAMA_EMBED_MODEL,
            "prompt": text,
        },
    )
    embedding = data.get("embedding")
    if isinstance(embedding, list):
        return _validate_embedding(embedding)

    raise EmbeddingError("Resposta de embedding sem vetor.")


def _post_ollama_json(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{OLLAMA_BASE_URL.rstrip('/')}{endpoint}"
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException as exc:
        raise EmbeddingError("Falha ao chamar o Ollama para embedding.") from exc

    if not response.ok:
        raise EmbeddingError(
            f"Ollama embedding retornou HTTP {response.status_code}: {response.text}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise EmbeddingError("Ollama embedding retornou JSON invalido.") from exc

    if not isinstance(data, dict):
        raise EmbeddingError("Ollama embedding retornou payload inesperado.")

    return data


def _validate_embedding(values: list[Any]) -> list[float]:
    embedding: list[float] = []
    for value in values:
        if not isinstance(value, (int, float)):
            raise EmbeddingError("Embedding contem valor nao numerico.")
        embedding.append(float(value))

    if not embedding:
        raise EmbeddingError("Embedding vazio.")
    return embedding
