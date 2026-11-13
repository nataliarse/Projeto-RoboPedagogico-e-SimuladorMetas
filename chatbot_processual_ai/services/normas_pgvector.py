"""Armazenamento dos trechos das normas no PostgreSQL com pgvector (banco da IESB).

A tabela ``normas`` fica no schema do aluno; o tipo ``vector`` vem da extensão instalada no
schema ``public``. A senha nunca fica no código: vem de ``NORMAS_PG_URL`` (uso local) ou do
secret ``TCC_SECRET_ID`` no Secrets Manager, lido com o instance profile da EC2.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

from config import BEDROCK_REGION, NORMAS_PG_SCHEMA, NORMAS_PG_URL, TCC_SECRET_ID


class NormasDBError(Exception):
    pass


DDL = """
CREATE TABLE IF NOT EXISTS normas (
    id bigserial PRIMARY KEY,
    fonte text NOT NULL,
    meta text,
    pagina integer,
    secao text,
    texto text NOT NULL,
    embedding vector({dim}) NOT NULL,
    metadata jsonb DEFAULT '{{}}'::jsonb,
    created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS normas_embedding_idx ON normas USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS normas_fonte_idx ON normas (fonte);
"""


def _url_do_secret() -> str:
    try:
        import boto3
        segredo = boto3.client("secretsmanager", region_name=BEDROCK_REGION).get_secret_value(
            SecretId=TCC_SECRET_ID)
        dados = json.loads(segredo["SecretString"])
    except Exception as exc:
        raise NormasDBError(f"Não foi possível ler o secret do banco ({type(exc).__name__}).") from exc
    for chave in ("url", "conn", "connection_string", "dsn", "DATABASE_URL"):
        if isinstance(dados.get(chave), str) and dados[chave].startswith("postgres"):
            return dados[chave]
    usuario = dados.get("username") or dados.get("user") or dados.get("role")
    senha = dados.get("password")
    host = dados.get("host")
    banco = dados.get("dbname") or dados.get("database") or "iesb"
    porta = dados.get("port") or 5432
    if not (usuario and senha and host):
        raise NormasDBError("O secret do banco não traz usuário, senha e host.")
    return f"postgresql://{quote(str(usuario))}:{quote(str(senha))}@{host}:{porta}/{banco}"


def conectar():
    try:
        import psycopg
        from psycopg import sql
    except ImportError as exc:  # pragma: no cover - depende do ambiente
        raise NormasDBError("psycopg não está instalado.") from exc
    url = NORMAS_PG_URL or _url_do_secret()
    try:
        conexao = psycopg.connect(url, connect_timeout=10)
        # o tipo vector está no schema public; a URL pode restringir o search_path ao schema do aluno
        conexao.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(NORMAS_PG_SCHEMA)))
    except Exception as exc:
        raise NormasDBError(f"Falha ao conectar ao banco das normas ({type(exc).__name__}).") from exc
    return conexao


def _literal(vetor: list[float]) -> str:
    return "[" + ",".join(f"{v:.7f}" for v in vetor) + "]"


def indexar(trechos: list[dict[str, Any]], vetores: list[list[float]], fonte: str) -> int:
    """Substitui os trechos de uma fonte pelos novos, numa única transação."""
    if not trechos:
        return 0
    with conectar() as conexao:
        conexao.execute(DDL.format(dim=len(vetores[0])))
        conexao.execute("DELETE FROM normas WHERE fonte = %s", (fonte,))
        with conexao.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO normas (fonte, meta, pagina, secao, texto, embedding, metadata) "
                "VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb)",
                [
                    (fonte, t.get("meta"), t.get("pagina"), t.get("secao"), t["texto"], _literal(v),
                     json.dumps({"posicao": i}))
                    for i, (t, v) in enumerate(zip(trechos, vetores))
                ],
            )
    return len(trechos)


def buscar(vetor: list[float], metas: list[str] | None, top_k: int, min_score: float) -> list[dict[str, Any]]:
    consulta = (
        "SELECT fonte, meta, pagina, secao, texto, 1 - (embedding <=> %s::vector) AS score "
        "FROM normas {filtro} ORDER BY embedding <=> %s::vector LIMIT %s"
    )
    literal = _literal(vetor)
    if metas:
        consulta = consulta.format(filtro="WHERE meta = ANY(%s)")
        parametros: tuple = (literal, list(metas), literal, top_k)
    else:
        consulta = consulta.format(filtro="")
        parametros = (literal, literal, top_k)
    with conectar() as conexao:
        linhas = conexao.execute(consulta, parametros).fetchall()
    return [
        {"fonte": f, "meta": m, "pagina": p, "secao": s, "texto": t, "score": float(sc)}
        for f, m, p, s, t, sc in linhas
        if sc is not None and float(sc) >= min_score
    ]
