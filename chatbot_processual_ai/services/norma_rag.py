"""Recuperação semântica (RAG) sobre as normas das Metas Nacionais.

Indexa o Glossário das Metas Nacionais do Poder Judiciário (Justiça do Trabalho)
em uma coleção própria do banco vetorial e devolve os trechos mais próximos de
uma pergunta, com a página de origem, para que a orientação cite a norma.

Indexação (uma vez, ou quando o glossário mudar):

    python -m services.norma_rag
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from services.embedding_service import EmbeddingError, generate_embedding
from services.qdrant_vector_store import QdrantError, _request_json, deterministic_point_id

NORMAS_COLLECTION = "normas_cnj"
NORMAS_DIR = Path(__file__).resolve().parent.parent / "data" / "normas"
GLOSSARIO_PATH = NORMAS_DIR / "glossario_metas_2026_jt_v3.txt"
GLOSSARIO_FONTE = (
    "CNJ. Glossário das Metas Nacionais do Poder Judiciário 2026 - Justiça do Trabalho, "
    "versão 3 (março/2026)"
)
MAX_CHUNK_CHARS = 700
MIN_SCORE = 0.45

_PAGE_MARK = re.compile(r"===== PAGINA (\d+) =====")
# cabeçalho de versão antiga que sobrou em algumas páginas do PDF oficial
_STALE_HEADER = re.compile(
    r"Metas Nacionais do Poder Judiciário - 2023\s+Glossário e Esclarecimentos – TST e TRTs\s+"
    r"Versão 3 – Agosto/2023\s+\d+"
)
_HEADINGS = (
    "Critério de Cumprimento", "Fórmula de cálculo", "Observação", "Esclarecimentos",
    "Delimitação da Meta 1 – Processos de Conhecimento", "Casos Novos Considerados na Meta",
    "Assuntos Processuais (TPU)", "Critério de Julgamento", "Aba Downloads", "Observações:",
)
_VARIABLES = (
    "cnm1", "primeirasentm1", "baixm1", "julgadom1", "susm1", "desm1",
    "dism2_k", "primeirasentm2_k", "decm2_k", "baixm2_k", "julgadom2_k", "susm2_k", "desm2_k",
)
_DESCRIPTION_START = re.compile(r"(A soma d|Processos de conhecimento pendentes|Processos enquadrados)")


def _meta_of_page(page: int) -> str | None:
    if 3 <= page <= 7:
        return "Meta 1"
    if 8 <= page <= 12:
        return "Meta 2"
    return None


def build_chunks(text: str) -> list[dict[str, Any]]:
    """Corta o glossário em trechos com a meta e a página de origem."""
    chunks: list[dict[str, Any]] = []
    parts = _PAGE_MARK.split(text)
    for i in range(1, len(parts) - 1, 2):
        page = int(parts[i])
        meta = _meta_of_page(page)
        if meta is None:
            continue
        body = _STALE_HEADER.sub(" ", parts[i + 1])
        is_dictionary = "Regra geral: Serão considerados apenas processos de conhecimento" in body \
            or body.lstrip().startswith(("vez no mês", "12", " 12")) or "susm2_k" in body
        sections = (_split_dictionary(body, meta) if is_dictionary
                    else _split_prose(body, first_page=page in (3, 8)))
        for title, content in sections:
            for piece in _wrap(content):
                chunks.append({
                    "meta": meta,
                    "pagina": page,
                    "secao": title,
                    "texto": f"{meta} - {title}: {piece}" if title else f"{meta}: {piece}",
                })
    return chunks


def _clean(text: str) -> str:
    text = text.replace("•", " • ")
    return re.sub(r"\s+", " ", text).strip()


def _split_prose(body: str, first_page: bool = True) -> list[tuple[str, str]]:
    pattern = "(" + "|".join(re.escape(h) for h in _HEADINGS) + ")"
    parts = re.split(pattern, body)
    sections: list[tuple[str, str]] = []
    head = _clean(parts[0])
    if len(head) > 40:
        sections.append(("Enunciado" if first_page else "Esclarecimentos (continuação)", head))
    for i in range(1, len(parts) - 1, 2):
        content = _clean(parts[i + 1])
        if len(content) > 40:
            sections.append((parts[i].rstrip(":"), content))
    return sections


def _split_dictionary(body: str, meta: str = "") -> list[tuple[str, str]]:
    """No dicionário, o PDF intercala colunas; aproveita-se a descrição de cada variável."""
    pattern = r"(?m)^(" + "|".join(re.escape(v) for v in _VARIABLES) + r")\b"
    parts = re.split(pattern, body)
    sections: list[tuple[str, str]] = []
    for i in range(1, len(parts) - 1, 2):
        content = _clean(parts[i + 1])
        found = _DESCRIPTION_START.search(content)
        if found:
            content = content[found.start():]
        content = re.split(r"\bOnde, ", content)[0].strip()
        if len(content) < 100:
            continue  # resto de célula da tabela, sem a descrição do indicador
        name = parts[i]
        if content.startswith("Processos enquadrados em alguma das variáveis primeirasent"):
            name = "julgadom1" if meta == "Meta 1" else "julgadom2_k"  # variável dos julgados
        sections.append((f"variável {name}", content))
    tail = re.search(r"Observações:(.*)$", body, flags=re.S)
    if tail:
        sections.append(("Observações", _clean(tail.group(1))))
    return sections


def _wrap(content: str) -> list[str]:
    if len(content) <= MAX_CHUNK_CHARS:
        return [content]
    pieces, current = [], ""
    for sentence in re.split(r"(?<=[.;])\s+|\s+(?=•)", content):
        if current and len(current) + len(sentence) + 1 > MAX_CHUNK_CHARS:
            pieces.append(current.strip())
            current = ""
        current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def index_normas(path: Path = GLOSSARIO_PATH) -> int:
    """Indexa o glossário na coleção de normas. Devolve o número de trechos gravados."""
    chunks = build_chunks(path.read_text(encoding="utf-8"))
    if not chunks:
        return 0
    first_vector = generate_embedding(chunks[0]["texto"])
    try:
        _request_json("DELETE", f"/collections/{NORMAS_COLLECTION}")
    except QdrantError:
        pass  # coleção ainda não existia
    _request_json(
        "PUT", f"/collections/{NORMAS_COLLECTION}",
        json={"vectors": {"size": len(first_vector), "distance": "Cosine"}},
    )
    for position, chunk in enumerate(chunks):
        vector = first_vector if position == 0 else generate_embedding(chunk["texto"])
        _request_json(
            "PUT", f"/collections/{NORMAS_COLLECTION}/points", params={"wait": "true"},
            json={"points": [{
                "id": deterministic_point_id(NORMAS_COLLECTION, path.name, str(position)),
                "vector": vector,
                "payload": {**chunk, "fonte": GLOSSARIO_FONTE},
            }]},
        )
    return len(chunks)


def search_normas(query: str, metas: list[str] | None = None, top_k: int = 2) -> list[dict[str, Any]]:
    """Trechos da norma mais próximos da pergunta. Lista vazia se a busca não estiver disponível."""
    try:
        vector = generate_embedding(query)
        body: dict[str, Any] = {
            "vector": vector, "limit": top_k, "score_threshold": MIN_SCORE, "with_payload": True,
        }
        if metas:
            body["filter"] = {"must": [{"key": "meta", "match": {"any": metas}}]}
        data = _request_json("POST", f"/collections/{NORMAS_COLLECTION}/points/search", json=body)
    except (EmbeddingError, QdrantError):
        return []

    found = []
    for item in data.get("result") or []:
        payload = item.get("payload") if isinstance(item, dict) else None
        if isinstance(payload, dict) and payload.get("texto"):
            found.append({**payload, "score": item.get("score")})
    return found


if __name__ == "__main__":
    print(f"{index_normas()} trechos indexados na coleção {NORMAS_COLLECTION}.")
