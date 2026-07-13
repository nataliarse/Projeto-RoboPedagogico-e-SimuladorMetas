from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from ollama_client import OllamaError
from orchestrators.processual_chat_orchestrator import run_processual_chat_step
from services import process_repository
from services.process_repository import (
    find_process_by_number,
    get_chunks_for_process,
    ingest_processes,
)
from services.process_query_router import route_process_query
from services.qdrant_vector_store import QdrantError
from services.rag_retriever import retrieve_rag_context


SAMPLE_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_processes.json"


class RagBaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        temp_root = Path(__file__).resolve().parents[1] / "data"
        self.db_path = temp_root / f"test_rag_base_{uuid.uuid4().hex}.sqlite3"
        self.addCleanup(self._cleanup_db_file)

        self.original_db_path = process_repository.LOCAL_DB_PATH
        process_repository.LOCAL_DB_PATH = str(self.db_path)
        self.addCleanup(self._restore_db_path)

        with SAMPLE_DATA_FILE.open("r", encoding="utf-8") as file:
            self.sample_processes = json.load(file)

    def _restore_db_path(self) -> None:
        process_repository.LOCAL_DB_PATH = self.original_db_path

    def _cleanup_db_file(self) -> None:
        self.db_path.unlink(missing_ok=True)

    def test_sqlite_ingestion_is_idempotent_and_sanitized(self) -> None:
        first = ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )
        second = ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )

        process = find_process_by_number("0011000-82.1981.5.18.0051")
        self.assertEqual(first["processes"], 1)
        self.assertEqual(second["processes"], 1)
        self.assertIsNotNone(process)
        self.assertEqual(
            process["processo"]["numero_normalizado"],
            "00110008219815180051",
        )
        self.assertNotIn("documento", process["partes_interessadas"][0])
        self.assertNotIn("id_documento", process["documentos"][0])

    def test_chunking_preserves_process_link_and_metadata(self) -> None:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )

        chunks = get_chunks_for_process("0011000-82.1981.5.18.0051")

        self.assertGreaterEqual(len(chunks), 1)
        self.assertTrue(all(chunk["text"] for chunk in chunks))
        self.assertTrue(
            all(chunk["source_type"] in {"movement", "document"} for chunk in chunks)
        )
        self.assertTrue(all(chunk["content_kind"] == "metadata" for chunk in chunks))

    def test_rag_unavailable_does_not_raise(self) -> None:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )

        with patch(
            "services.rag_retriever.generate_embedding",
            return_value=[0.1, 0.2],
        ), patch(
            "services.rag_retriever.ensure_collection",
            side_effect=QdrantError("offline"),
        ):
            context = retrieve_rag_context(
                query="O que a sentenca decidiu?",
                process_number="0011000-82.1981.5.18.0051",
                requires_rag=True,
            )

        self.assertEqual(context["status"], "unavailable")
        self.assertEqual(context["chunks"], [])

    def test_rag_success_maps_vector_results_to_safe_sources(self) -> None:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )

        result_payload = {
            "payload": {
                "numero_processo": "00110008219815180051",
                "source_type": "document",
                "source_id": "1",
                "chunk_index": 0,
                "title": "Sentenca",
                "date": "1982-08-15",
                "content_kind": "full_text",
                "text_hash": "hash",
                "text": "Julgo procedente em parte o pedido apresentado.",
            },
            "score": 0.91,
        }

        with patch(
            "services.rag_retriever.generate_embedding",
            return_value=[0.1, 0.2],
        ), patch(
            "services.rag_retriever.ensure_collection",
        ), patch(
            "services.rag_retriever.upsert_point",
        ), patch(
            "services.rag_retriever.search_points",
            return_value=[result_payload],
        ):
            context = retrieve_rag_context(
                query="O que a sentenca decidiu?",
                process_number="0011000-82.1981.5.18.0051",
                requires_rag=True,
            )

        self.assertEqual(context["status"], "success")
        self.assertEqual(context["chunks"][0]["content_kind"], "full_text")
        self.assertEqual(context["sources"][0]["titulo"], "Sentenca")

    def test_chat_uses_structured_data_when_rag_is_unavailable(self) -> None:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )
        active_process = find_process_by_number("0011000-82.1981.5.18.0051")
        session_state = {
            "conversation": [],
            "active_process": active_process,
            "last_intent": "process_lookup",
        }

        with patch(
            "agents.agent2_context_collection.retrieve_rag_context",
            return_value={
                "status": "unavailable",
                "query": "O que a sentenca decidiu?",
                "chunks": [],
                "sources": [],
            },
        ):
            result = run_processual_chat_step(
                "O que a sentenca decidiu?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.response.rag_status, "unavailable")
        self.assertIn("teor", result.response.resposta.lower())

    def test_recent_movement_question_uses_structured_route(self) -> None:
        route = route_process_query(
            "qua a movimentação mais recente?",
            "process_question",
            has_active_process=True,
        )

        self.assertEqual(route.route, "structured")
        self.assertFalse(route.requires_rag)

    def test_chat_answers_earliest_movement_from_structured_data(self) -> None:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )
        active_process = find_process_by_number("0011000-82.1981.5.18.0051")
        session_state = {
            "conversation": [],
            "active_process": active_process,
            "last_intent": "process_lookup",
        }

        with patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=OllamaError("offline"),
        ), patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=False,
        ):
            result = run_processual_chat_step(
                "e a movimentação mais antiga?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "not_needed")
        self.assertEqual(result.analysis["question_focus"], "earliest_movement")
        self.assertIn("mais antiga", result.response.resposta.lower())
        self.assertIn("Distribu", result.response.resposta)
        self.assertIn("12/03/1981", result.response.resposta)
        self.assertNotIn("05/02/1984", result.response.resposta)


if __name__ == "__main__":
    unittest.main()
