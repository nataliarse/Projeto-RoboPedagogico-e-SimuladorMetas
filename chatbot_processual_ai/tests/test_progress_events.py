from __future__ import annotations

import unittest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

import main as terminal_main
from orchestrators.processual_chat_orchestrator import run_processual_chat_step
from schemas.processual_contracts import ProcessProgressEvent
from services.embedding_service import EmbeddingError
from services.rag_retriever import retrieve_rag_context
from session_state import create_session_state


class ProgressEventsTestCase(unittest.TestCase):
    def test_chat_step_remains_compatible_without_progress_reporter(self) -> None:
        result = run_processual_chat_step("oi", create_session_state())

        self.assertIsNone(result.response.failed_stage)
        self.assertIsInstance(result.response.resposta, str)

    def test_chat_step_reports_basic_pipeline_order(self) -> None:
        events: list[ProcessProgressEvent] = []

        result = run_processual_chat_step(
            "oi",
            create_session_state(),
            progress_reporter=events.append,
        )

        self.assertIsNone(result.response.failed_stage)
        codes = [event.code for event in events]
        expected_order = [
            "intent.started",
            "context.started",
            "analysis.started",
            "response.started",
            "response.finished",
        ]
        positions = [codes.index(code) for code in expected_order]
        self.assertEqual(positions, sorted(positions))

    def test_chat_step_reports_controlled_failure_event(self) -> None:
        events: list[ProcessProgressEvent] = []

        with patch(
            "orchestrators.processual_chat_orchestrator.interpret_user_message",
            side_effect=RuntimeError("boom"),
        ):
            result = run_processual_chat_step(
                "oi",
                create_session_state(),
                progress_reporter=events.append,
            )

        self.assertEqual(result.response.failed_stage, "Agente 1")
        failure_events = [event for event in events if event.code == "intent.failed"]
        self.assertEqual(len(failure_events), 1)
        self.assertEqual(failure_events[0].level, "error")

    def test_rag_reports_unavailable_when_embedding_fails(self) -> None:
        events: list[ProcessProgressEvent] = []
        chunks = [_sample_chunk()]

        with patch("services.rag_retriever.RAG_ENABLED", True), patch(
            "services.rag_retriever.get_chunks_for_process",
            return_value=chunks,
        ), patch(
            "services.rag_retriever.generate_embedding",
            side_effect=EmbeddingError("offline"),
        ):
            context = retrieve_rag_context(
                query="O que a sentenca decidiu?",
                process_number="0011000-82.1981.5.18.0051",
                requires_rag=True,
                progress_reporter=events.append,
            )

        self.assertEqual(context["status"], "unavailable")
        self.assertIn("rag.embedding_query.started", [event.code for event in events])
        self.assertIn("rag.unavailable", [event.code for event in events])

    def test_rag_reports_successful_vector_search(self) -> None:
        events: list[ProcessProgressEvent] = []
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

        with patch("services.rag_retriever.RAG_ENABLED", True), patch(
            "services.rag_retriever.get_chunks_for_process",
            return_value=[_sample_chunk()],
        ), patch(
            "services.rag_retriever.generate_embedding",
            return_value=[0.1, 0.2],
        ), patch(
            "services.rag_retriever.ensure_collection",
        ), patch(
            "services.rag_retriever._sync_process_chunks",
        ), patch(
            "services.rag_retriever.search_points",
            return_value=[result_payload],
        ):
            context = retrieve_rag_context(
                query="O que a sentenca decidiu?",
                process_number="0011000-82.1981.5.18.0051",
                requires_rag=True,
                progress_reporter=events.append,
            )

        self.assertEqual(context["status"], "success")
        codes = [event.code for event in events]
        self.assertIn("rag.search.finished", codes)
        self.assertIn("rag.finished", codes)

    def test_terminal_progress_formatter_uses_styles_and_safe_details(self) -> None:
        original_console = terminal_main.console
        try:
            terminal_main.console = Console(
                file=StringIO(),
                record=True,
                width=120,
            )
            event = ProcessProgressEvent(
                code="rag.unavailable",
                level="warning",
                message="busca semantica indisponivel; usando dados estruturados.",
                details={
                    "rag_status": "unavailable",
                    "prompt": "123.456.789-10",
                },
                elapsed_ms=12,
            )

            terminal_main._print_progress_event(event, trace_enabled=True)
            output = terminal_main.console.export_text()
        finally:
            terminal_main.console = original_console

        self.assertEqual(
            terminal_main._progress_styles_for_level("warning"),
            ("bold yellow", "yellow"),
        )
        self.assertIn("Fluxo:", output)
        self.assertIn("busca semantica indisponivel", output)
        self.assertIn("rag_status=unavailable", output)
        self.assertNotIn("123.456.789-10", output)


def _sample_chunk() -> dict:
    return {
        "id": 1,
        "source_type": "document",
        "source_id": "1",
        "chunk_index": 0,
        "title": "Sentenca",
        "date": "1982-08-15",
        "content_kind": "metadata",
        "text_hash": "hash",
        "text": "Documento de sentenca registrado em 1982.",
    }


if __name__ == "__main__":
    unittest.main()
