from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import LOCAL_DB_PATH
from services.chunking import ProcessChunk, build_process_chunks
from services.text_normalization import (
    clean_text,
    normalize_process_number,
    resolve_project_path,
    text_hash,
)


SCHEMA_VERSION = 1
SAMPLE_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_processes.json"


def find_process_by_number(process_number: str) -> dict | None:
    ensure_database_seeded()
    normalized_number = normalize_process_number(process_number)
    if normalized_number is None:
        return None

    connection = _connect()
    try:
        return _load_process_tree(connection, normalized_number)
    finally:
        connection.close()


def ensure_database_seeded() -> None:
    connection = _connect()
    try:
        _ensure_schema(connection)
        if _process_count(connection) == 0 and SAMPLE_DATA_FILE.exists():
            with SAMPLE_DATA_FILE.open("r", encoding="utf-8") as file:
                processes = json.load(file)
            ingest_processes(processes, source_name="sample_processes.json", connection=connection)
    finally:
        connection.close()


def ingest_processes(
    processes: list[dict],
    *,
    source_name: str,
    connection: sqlite3.Connection | None = None,
) -> dict[str, int]:
    owns_connection = connection is None
    if connection is None:
        connection = _connect()

    try:
        _ensure_schema(connection)
        stats = {"processes": 0, "chunks": 0}
        run_id = _start_ingestion_run(connection, source_name)

        for process in processes:
            if not isinstance(process, dict):
                continue

            normalized_number = _process_number(process)
            if normalized_number is None:
                continue

            _replace_process(connection, process, normalized_number)
            chunks = build_process_chunks(_sanitized_process_tree(process))
            _replace_chunks(connection, normalized_number, chunks)
            stats["processes"] += 1
            stats["chunks"] += len(chunks)

        _finish_ingestion_run(connection, run_id, stats)
        connection.commit()
        return stats
    except Exception:
        connection.rollback()
        raise
    finally:
        if owns_connection:
            connection.close()


def get_chunks_for_process(process_number: str) -> list[dict[str, Any]]:
    ensure_database_seeded()
    normalized_number = normalize_process_number(process_number)
    if normalized_number is None:
        return []

    connection = _connect()
    try:
        rows = connection.execute(
            """
            SELECT id, source_type, source_id, chunk_index, text, title, date,
                   content_kind, text_hash, qdrant_point_id
            FROM rag_chunks
            WHERE process_number = ?
            ORDER BY source_type, source_id, chunk_index
            """,
            (normalized_number,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_all_chunks() -> list[dict[str, Any]]:
    ensure_database_seeded()
    connection = _connect()
    try:
        rows = connection.execute(
            """
            SELECT id, process_number, source_type, source_id, chunk_index, text,
                   title, date, content_kind, text_hash, qdrant_point_id
            FROM rag_chunks
            ORDER BY process_number, source_type, source_id, chunk_index
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def update_chunk_vector_id(chunk_id: int, point_id: str) -> None:
    ensure_database_seeded()
    connection = _connect()
    try:
        connection.execute(
            "UPDATE rag_chunks SET qdrant_point_id = ? WHERE id = ?",
            (point_id, chunk_id),
        )
        connection.commit()
    finally:
        connection.close()


def database_path() -> Path:
    return resolve_project_path(LOCAL_DB_PATH)


def _connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _ensure_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS processes (
            numero_normalizado TEXT PRIMARY KEY,
            numero TEXT,
            classe_judicial TEXT,
            assunto TEXT,
            orgao_julgador TEXT,
            unidade TEXT,
            jurisdicao TEXT,
            grau TEXT,
            data_autuacao TEXT,
            valor_causa REAL,
            situacao TEXT,
            raw_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_number TEXT NOT NULL,
            party_index INTEGER NOT NULL,
            polo TEXT,
            nome TEXT,
            tipo TEXT,
            representantes_json TEXT NOT NULL DEFAULT '[]',
            FOREIGN KEY(process_number) REFERENCES processes(numero_normalizado)
                ON DELETE CASCADE,
            UNIQUE(process_number, party_index)
        );

        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_number TEXT NOT NULL,
            movement_index INTEGER NOT NULL,
            ordem INTEGER,
            data TEXT,
            descricao TEXT,
            complemento TEXT,
            referencia TEXT,
            raw_json TEXT NOT NULL,
            FOREIGN KEY(process_number) REFERENCES processes(numero_normalizado)
                ON DELETE CASCADE,
            UNIQUE(process_number, movement_index)
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_number TEXT NOT NULL,
            document_index INTEGER NOT NULL,
            data TEXT,
            titulo TEXT,
            tipo TEXT,
            conteudo TEXT,
            raw_json TEXT NOT NULL,
            FOREIGN KEY(process_number) REFERENCES processes(numero_normalizado)
                ON DELETE CASCADE,
            UNIQUE(process_number, document_index)
        );

        CREATE TABLE IF NOT EXISTS pending_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_number TEXT NOT NULL,
            pending_index INTEGER NOT NULL,
            value_json TEXT NOT NULL,
            FOREIGN KEY(process_number) REFERENCES processes(numero_normalizado)
                ON DELETE CASCADE,
            UNIQUE(process_number, pending_index)
        );

        CREATE TABLE IF NOT EXISTS collection_metadata (
            process_number TEXT PRIMARY KEY,
            metadata_json TEXT NOT NULL,
            FOREIGN KEY(process_number) REFERENCES processes(numero_normalizado)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS rag_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_number TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            title TEXT,
            date TEXT,
            content_kind TEXT NOT NULL DEFAULT 'metadata',
            text_hash TEXT NOT NULL,
            qdrant_point_id TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(process_number) REFERENCES processes(numero_normalizado)
                ON DELETE CASCADE,
            UNIQUE(process_number, source_type, source_id, chunk_index, text_hash)
        );

        CREATE TABLE IF NOT EXISTS ingestion_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            stats_json TEXT NOT NULL DEFAULT '{}'
        );

        CREATE INDEX IF NOT EXISTS idx_rag_chunks_process
            ON rag_chunks(process_number);
        CREATE INDEX IF NOT EXISTS idx_movements_process_order
            ON movements(process_number, ordem);
        """
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO schema_migrations(version, applied_at)
        VALUES (?, ?)
        """,
        (SCHEMA_VERSION, _utc_now()),
    )
    _ensure_column(
        connection,
        "rag_chunks",
        "content_kind",
        "TEXT NOT NULL DEFAULT 'metadata'",
    )
    connection.commit()


def _process_count(connection: sqlite3.Connection) -> int:
    row = connection.execute("SELECT COUNT(*) AS count FROM processes").fetchone()
    return int(row["count"]) if row else 0


def _ensure_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {str(row["name"]) for row in rows}
    if column_name in existing_columns:
        return

    connection.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
    )


def _start_ingestion_run(connection: sqlite3.Connection, source_name: str) -> int:
    cursor = connection.execute(
        """
        INSERT INTO ingestion_runs(source_name, started_at, stats_json)
        VALUES (?, ?, ?)
        """,
        (source_name, _utc_now(), "{}"),
    )
    return int(cursor.lastrowid)


def _finish_ingestion_run(
    connection: sqlite3.Connection,
    run_id: int,
    stats: dict[str, int],
) -> None:
    connection.execute(
        """
        UPDATE ingestion_runs
        SET finished_at = ?, stats_json = ?
        WHERE id = ?
        """,
        (_utc_now(), json.dumps(stats, ensure_ascii=False), run_id),
    )


def _replace_process(
    connection: sqlite3.Connection,
    process: dict,
    normalized_number: str,
) -> None:
    process = _sanitized_process_tree(process)
    process_data = _dict_value(process.get("processo"))
    raw_json = json.dumps(process, ensure_ascii=False, sort_keys=True)

    connection.execute(
        """
        INSERT INTO processes (
            numero_normalizado, numero, classe_judicial, assunto, orgao_julgador,
            unidade, jurisdicao, grau, data_autuacao, valor_causa, situacao,
            raw_json, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(numero_normalizado) DO UPDATE SET
            numero = excluded.numero,
            classe_judicial = excluded.classe_judicial,
            assunto = excluded.assunto,
            orgao_julgador = excluded.orgao_julgador,
            unidade = excluded.unidade,
            jurisdicao = excluded.jurisdicao,
            grau = excluded.grau,
            data_autuacao = excluded.data_autuacao,
            valor_causa = excluded.valor_causa,
            situacao = excluded.situacao,
            raw_json = excluded.raw_json,
            updated_at = excluded.updated_at
        """,
        (
            normalized_number,
            _string_or_none(process_data.get("numero")),
            _string_or_none(process_data.get("classe_judicial")),
            _string_or_none(process_data.get("assunto")),
            _string_or_none(process_data.get("orgao_julgador")),
            _string_or_none(process_data.get("unidade")),
            _string_or_none(process_data.get("jurisdicao")),
            _string_or_none(process_data.get("grau")),
            _date_only(process_data.get("data_autuacao")),
            process_data.get("valor_causa"),
            _string_or_none(process_data.get("situacao")),
            raw_json,
            _utc_now(),
        ),
    )

    _delete_children(connection, normalized_number)
    _insert_parties(connection, normalized_number, process)
    _insert_movements(connection, normalized_number, process)
    _insert_documents(connection, normalized_number, process)
    _insert_pending_items(connection, normalized_number, process)
    _insert_collection_metadata(connection, normalized_number, process)


def _delete_children(connection: sqlite3.Connection, normalized_number: str) -> None:
    for table_name in (
        "parties",
        "movements",
        "documents",
        "pending_items",
        "collection_metadata",
        "rag_chunks",
    ):
        connection.execute(
            f"DELETE FROM {table_name} WHERE process_number = ?",
            (normalized_number,),
        )


def _insert_parties(
    connection: sqlite3.Connection,
    normalized_number: str,
    process: dict,
) -> None:
    for index, party in enumerate(_list_value(process.get("partes_interessadas"))):
        if not isinstance(party, dict):
            continue

        connection.execute(
            """
            INSERT INTO parties (
                process_number, party_index, polo, nome, tipo, representantes_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                normalized_number,
                index,
                _string_or_none(party.get("polo")),
                _string_or_none(party.get("nome")),
                _string_or_none(party.get("tipo")),
                json.dumps(_list_value(party.get("representantes")), ensure_ascii=False),
            ),
        )


def _insert_movements(
    connection: sqlite3.Connection,
    normalized_number: str,
    process: dict,
) -> None:
    for index, movement in enumerate(_list_value(process.get("movimentacoes"))):
        if not isinstance(movement, dict):
            continue

        connection.execute(
            """
            INSERT INTO movements (
                process_number, movement_index, ordem, data, descricao,
                complemento, referencia, raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalized_number,
                index,
                _int_or_none(movement.get("ordem")),
                _string_or_none(movement.get("data")),
                _string_or_none(movement.get("descricao")),
                _string_or_none(movement.get("complemento")),
                _string_or_none(movement.get("referencia")),
                json.dumps(movement, ensure_ascii=False, sort_keys=True),
            ),
        )


def _insert_documents(
    connection: sqlite3.Connection,
    normalized_number: str,
    process: dict,
) -> None:
    for index, document in enumerate(_list_value(process.get("documentos"))):
        if not isinstance(document, dict):
            continue

        content = _first_text(document, "conteudo", "texto", "teor")
        connection.execute(
            """
            INSERT INTO documents (
                process_number, document_index, data, titulo, tipo, conteudo,
                raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalized_number,
                index,
                _string_or_none(document.get("data")),
                _string_or_none(document.get("titulo")),
                _string_or_none(document.get("tipo")),
                content,
                json.dumps(_sanitize_document(document), ensure_ascii=False, sort_keys=True),
            ),
        )


def _insert_pending_items(
    connection: sqlite3.Connection,
    normalized_number: str,
    process: dict,
) -> None:
    for index, item in enumerate(_list_value(process.get("pendencias"))):
        connection.execute(
            """
            INSERT INTO pending_items(process_number, pending_index, value_json)
            VALUES (?, ?, ?)
            """,
            (normalized_number, index, json.dumps(item, ensure_ascii=False)),
        )


def _insert_collection_metadata(
    connection: sqlite3.Connection,
    normalized_number: str,
    process: dict,
) -> None:
    metadata = process.get("coleta")
    if not isinstance(metadata, dict):
        metadata = {}

    connection.execute(
        """
        INSERT OR REPLACE INTO collection_metadata(process_number, metadata_json)
        VALUES (?, ?)
        """,
        (normalized_number, json.dumps(metadata, ensure_ascii=False, sort_keys=True)),
    )


def _replace_chunks(
    connection: sqlite3.Connection,
    normalized_number: str,
    chunks: list[ProcessChunk],
) -> None:
    connection.execute(
        "DELETE FROM rag_chunks WHERE process_number = ?",
        (normalized_number,),
    )

    for chunk in chunks:
        connection.execute(
            """
            INSERT OR IGNORE INTO rag_chunks (
                process_number, source_type, source_id, chunk_index, text, title,
                date, content_kind, text_hash, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalized_number,
                chunk.source_type,
                chunk.source_id,
                chunk.chunk_index,
                chunk.text,
                chunk.title,
                chunk.date,
                chunk.content_kind,
                text_hash(chunk.text),
                _utc_now(),
            ),
        )


def _load_process_tree(
    connection: sqlite3.Connection,
    normalized_number: str,
) -> dict | None:
    process_row = connection.execute(
        """
        SELECT * FROM processes WHERE numero_normalizado = ?
        """,
        (normalized_number,),
    ).fetchone()
    if process_row is None:
        return None

    return {
        "processo": {
            "numero": process_row["numero"],
            "numero_normalizado": process_row["numero_normalizado"],
            "classe_judicial": process_row["classe_judicial"],
            "assunto": process_row["assunto"],
            "orgao_julgador": process_row["orgao_julgador"],
            "unidade": process_row["unidade"],
            "jurisdicao": process_row["jurisdicao"],
            "grau": process_row["grau"],
            "data_autuacao": process_row["data_autuacao"],
            "valor_causa": process_row["valor_causa"],
            "situacao": process_row["situacao"],
        },
        "partes_interessadas": _load_parties(connection, normalized_number),
        "movimentacoes": _load_movements(connection, normalized_number),
        "documentos": _load_documents(connection, normalized_number),
        "pendencias": _load_pending_items(connection, normalized_number),
        "coleta": _load_collection_metadata(connection, normalized_number),
    }


def _load_parties(connection: sqlite3.Connection, normalized_number: str) -> list[dict]:
    rows = connection.execute(
        """
        SELECT polo, nome, tipo, representantes_json
        FROM parties
        WHERE process_number = ?
        ORDER BY party_index
        """,
        (normalized_number,),
    ).fetchall()
    parties = []
    for row in rows:
        parties.append(
            {
                "polo": row["polo"],
                "nome": row["nome"],
                "tipo": row["tipo"],
                "representantes": json.loads(row["representantes_json"] or "[]"),
            }
        )
    return parties


def _load_movements(connection: sqlite3.Connection, normalized_number: str) -> list[dict]:
    rows = connection.execute(
        """
        SELECT ordem, data, descricao, complemento, referencia
        FROM movements
        WHERE process_number = ?
        ORDER BY movement_index
        """,
        (normalized_number,),
    ).fetchall()
    return [dict(row) for row in rows]


def _load_documents(connection: sqlite3.Connection, normalized_number: str) -> list[dict]:
    rows = connection.execute(
        """
        SELECT data, titulo, tipo, conteudo
        FROM documents
        WHERE process_number = ?
        ORDER BY document_index
        """,
        (normalized_number,),
    ).fetchall()
    documents = []
    for row in rows:
        document = {
            "data": row["data"],
            "titulo": row["titulo"],
            "tipo": row["tipo"],
        }
        if row["conteudo"]:
            document["conteudo"] = row["conteudo"]
        documents.append(document)
    return documents


def _load_pending_items(
    connection: sqlite3.Connection,
    normalized_number: str,
) -> list[Any]:
    rows = connection.execute(
        """
        SELECT value_json
        FROM pending_items
        WHERE process_number = ?
        ORDER BY pending_index
        """,
        (normalized_number,),
    ).fetchall()
    return [json.loads(row["value_json"]) for row in rows]


def _load_collection_metadata(
    connection: sqlite3.Connection,
    normalized_number: str,
) -> dict:
    row = connection.execute(
        """
        SELECT metadata_json
        FROM collection_metadata
        WHERE process_number = ?
        """,
        (normalized_number,),
    ).fetchone()
    if row is None:
        return {}
    return json.loads(row["metadata_json"] or "{}")


def _sanitized_process_tree(process: dict) -> dict:
    process = json.loads(json.dumps(process, ensure_ascii=False))

    parties = process.get("partes_interessadas")
    if isinstance(parties, list):
        for party in parties:
            if isinstance(party, dict):
                party.pop("documento", None)

    documents = process.get("documentos")
    if isinstance(documents, list):
        for document in documents:
            if isinstance(document, dict):
                document.pop("id_documento", None)

    return process


def _sanitize_document(document: dict) -> dict:
    sanitized = dict(document)
    sanitized.pop("id_documento", None)
    return sanitized


def _process_number(process: dict) -> str | None:
    process_data = _dict_value(process.get("processo"))
    return normalize_process_number(
        process_data.get("numero_normalizado") or process_data.get("numero")
    )


def _dict_value(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _list_value(value: Any) -> list:
    return value if isinstance(value, list) else []


def _string_or_none(value: Any) -> str | None:
    text = clean_text(value)
    return text or None


def _first_text(document: dict, *field_names: str) -> str | None:
    for field_name in field_names:
        text = clean_text(document.get(field_name))
        if text:
            return text
    return None


def _date_only(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    if "T" in text:
        return text.split("T", 1)[0]
    return text


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
