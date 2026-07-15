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
from services.process_query_resolver import resolve_process_query
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

    def _session_with_active_process(self) -> dict:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )
        active_process = find_process_by_number("0011000-82.1981.5.18.0051")
        return {
            "conversation": [],
            "active_process": active_process,
            "last_intent": "process_lookup",
        }

    def _run_active_process_question_without_model(self, message: str):
        session_state = self._session_with_active_process()

        with patch(
            "agents.agent1_intent.generate_text",
            side_effect=AssertionError("Agente 1 nao deveria chamar Ollama."),
        ) as agent1_generate, patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=AssertionError("Agente 3 nao deveria chamar Ollama."),
        ) as agent3_generate, patch(
            "agents.agent4_response.generate_text",
            side_effect=AssertionError("Agente 4 nao deveria chamar Ollama."),
        ) as agent4_generate, patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=True,
        ):
            result = run_processual_chat_step(message, session_state)

        agent1_generate.assert_not_called()
        agent3_generate.assert_not_called()
        agent4_generate.assert_not_called()
        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "not_needed")
        return result

    def _movement_fact_count(self, result) -> int:
        return sum(
            1
            for fact in result.analysis["facts"]
            if fact["source"].startswith("movimentacoes[")
        )

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
            all(
                chunk["source_type"] in {"movement", "document", "process_field"}
                for chunk in chunks
            )
        )
        self.assertTrue(
            all(
                chunk["content_kind"] in {"metadata", "structured_field"}
                for chunk in chunks
            )
        )
        self.assertTrue(any(chunk["source_type"] == "process_field" for chunk in chunks))
        self.assertTrue(any(chunk["content_kind"] == "structured_field" for chunk in chunks))

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
        self.assertEqual(result.context_data["query_route"]["route"], "rag")
        self.assertTrue(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "unavailable")
        self.assertIn("teor", result.response.resposta.lower())

    def test_chat_answers_case_value_from_active_process_without_rag(self) -> None:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )
        session_state = {"conversation": []}

        with patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=OllamaError("offline"),
        ), patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=False,
        ):
            first_result = run_processual_chat_step(
                "Consulte o processo 0011000-82.1981.5.18.0051",
                session_state,
            )
            result = run_processual_chat_step(
                "me diga então o valor causa",
                session_state,
            )

        self.assertIsNone(first_result.response.failed_stage)
        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.response.intent, "process_question")
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "not_needed")
        self.assertEqual(result.analysis["question_focus"], "case_value")
        self.assertIn("R$ 15.430,75", result.response.resposta)
        self.assertNotIn("BAIXADO", result.response.resposta)

    def test_value_described_question_uses_case_value_without_model(self) -> None:
        session_state = self._session_with_active_process()

        with patch(
            "agents.agent1_intent.generate_text",
            side_effect=AssertionError("Agente 1 nao deveria chamar Ollama."),
        ) as agent1_generate, patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=AssertionError("Agente 3 nao deveria chamar Ollama."),
        ) as agent3_generate, patch(
            "agents.agent4_response.generate_text",
            side_effect=AssertionError("Agente 4 nao deveria chamar Ollama."),
        ) as agent4_generate, patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=True,
        ):
            result = run_processual_chat_step(
                "qual o valor descrito nesse processo?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.response.intent, "process_question")
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "not_needed")
        self.assertEqual(result.analysis["question_focus"], "case_value")
        self.assertIn("R$ 15.430,75", result.response.resposta)
        agent1_generate.assert_not_called()
        agent3_generate.assert_not_called()
        agent4_generate.assert_not_called()

    def test_case_value_question_still_works_without_model(self) -> None:
        session_state = self._session_with_active_process()

        with patch(
            "agents.agent1_intent.generate_text",
            side_effect=AssertionError("Agente 1 nao deveria chamar Ollama."),
        ) as agent1_generate, patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=AssertionError("Agente 3 nao deveria chamar Ollama."),
        ) as agent3_generate, patch(
            "agents.agent4_response.generate_text",
            side_effect=AssertionError("Agente 4 nao deveria chamar Ollama."),
        ) as agent4_generate, patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=True,
        ):
            result = run_processual_chat_step(
                "qual o valor da causa?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.analysis["question_focus"], "case_value")
        self.assertIn("R$ 15.430,75", result.response.resposta)
        agent1_generate.assert_not_called()
        agent3_generate.assert_not_called()
        agent4_generate.assert_not_called()

    def test_parties_question_uses_structured_data_without_model(self) -> None:
        session_state = self._session_with_active_process()

        with patch(
            "agents.agent1_intent.generate_text",
            side_effect=AssertionError("Agente 1 nao deveria chamar Ollama."),
        ) as agent1_generate, patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=AssertionError("Agente 3 nao deveria chamar Ollama."),
        ) as agent3_generate, patch(
            "agents.agent4_response.generate_text",
            side_effect=AssertionError("Agente 4 nao deveria chamar Ollama."),
        ) as agent4_generate, patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=True,
        ):
            result = run_processual_chat_step(
                "quais sao as partes interessadas?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "not_needed")
        self.assertEqual(result.analysis["question_focus"], "parties")
        self.assertIn("JO", result.response.resposta)
        self.assertIn("IND", result.response.resposta)
        agent1_generate.assert_not_called()
        agent3_generate.assert_not_called()
        agent4_generate.assert_not_called()

    def test_pending_question_uses_structured_data_without_model(self) -> None:
        session_state = self._session_with_active_process()

        with patch(
            "agents.agent1_intent.generate_text",
            side_effect=AssertionError("Agente 1 nao deveria chamar Ollama."),
        ) as agent1_generate, patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=AssertionError("Agente 3 nao deveria chamar Ollama."),
        ) as agent3_generate, patch(
            "agents.agent4_response.generate_text",
            side_effect=AssertionError("Agente 4 nao deveria chamar Ollama."),
        ) as agent4_generate, patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=True,
        ):
            result = run_processual_chat_step(
                "existe alguma pendencia?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "not_needed")
        self.assertEqual(result.analysis["question_focus"], "pending_issues")
        self.assertIn("pend", result.response.resposta.lower())
        agent1_generate.assert_not_called()
        agent3_generate.assert_not_called()
        agent4_generate.assert_not_called()

    def test_direct_case_value_question_loads_process_and_does_not_summarize(self) -> None:
        ingest_processes(
            self.sample_processes,
            source_name="unit-test",
        )
        session_state = {"conversation": []}

        with patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=OllamaError("offline"),
        ), patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=False,
        ):
            result = run_processual_chat_step(
                "do processo 0011000-82.1981.5.18.0051 qual o valor informado?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.response.intent, "process_question")
        self.assertEqual(result.response.collection_status, "success")
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertEqual(result.analysis["question_focus"], "case_value")
        self.assertIn("O valor da causa informado é R$ 15.430,75.", result.response.resposta)
        self.assertNotIn("Arquivado definitivamente", result.response.resposta)

    def test_case_value_concept_without_active_process_stays_general(self) -> None:
        session_state = {"conversation": []}

        with patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=OllamaError("offline"),
        ), patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=False,
        ):
            result = run_processual_chat_step(
                "o que significa valor da causa?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.response.intent, "legal_general_question")
        self.assertEqual(result.analysis["analysis_type"], "legal_general_explanation")
        self.assertNotEqual(result.analysis["question_focus"], "case_value")
        self.assertIn("valor da causa", result.response.resposta.lower())

    def test_rag_rerank_prioritizes_structured_field_match(self) -> None:
        process_field_payload = {
            "payload": {
                "numero_processo": "00110008219815180051",
                "source_type": "process_field",
                "source_id": "valor_causa",
                "chunk_index": 0,
                "title": "Valor da causa",
                "date": None,
                "content_kind": "structured_field",
                "text_hash": "value-hash",
                "text": "Valor da causa: R$ 15.430,75",
            },
            "score": 0.61,
        }
        movement_payload = {
            "payload": {
                "numero_processo": "00110008219815180051",
                "source_type": "movement",
                "source_id": "4",
                "chunk_index": 0,
                "title": "Arquivado definitivamente",
                "date": "1984-02-05",
                "content_kind": "metadata",
                "text_hash": "movement-hash",
                "text": "Movimentacao: Arquivado definitivamente.",
            },
            "score": 0.89,
        }

        with patch(
            "services.rag_retriever.RAG_ENABLED",
            True,
        ), patch(
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
            return_value=[movement_payload, process_field_payload],
        ):
            context = retrieve_rag_context(
                query="qual o valor da causa?",
                process_number="0011000-82.1981.5.18.0051",
                requires_rag=True,
            )

        self.assertEqual(context["status"], "success")
        self.assertEqual(context["chunks"][0]["source_type"], "process_field")
        self.assertEqual(context["chunks"][0]["source_id"], "valor_causa")

    def test_recent_movement_question_uses_structured_route(self) -> None:
        route = route_process_query(
            "qua a movimentação mais recente?",
            "process_question",
            has_active_process=True,
        )

        self.assertEqual(route.route, "structured")
        self.assertFalse(route.requires_rag)

    def test_document_value_question_keeps_document_route(self) -> None:
        query_spec = resolve_process_query(
            "qual o valor descrito na sentenca?",
            has_active_process=True,
        )
        route = route_process_query(
            "qual o valor descrito na sentenca?",
            "process_question",
            has_active_process=True,
            process_query_spec=query_spec,
        )

        self.assertEqual(query_spec.target, "document_content")
        self.assertTrue(query_spec.requires_rag)
        self.assertEqual(route.route, "rag")
        self.assertTrue(route.requires_rag)

    def test_sentence_decision_question_keeps_rag_route(self) -> None:
        query_spec = resolve_process_query(
            "o que a sentenca decidiu?",
            has_active_process=True,
        )
        route = route_process_query(
            "o que a sentenca decidiu?",
            "process_question",
            has_active_process=True,
            process_query_spec=query_spec,
        )

        self.assertEqual(route.route, "rag")
        self.assertTrue(route.requires_rag)

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

    def test_chat_answers_first_and_latest_movement_without_model(self) -> None:
        session_state = self._session_with_active_process()

        with patch(
            "agents.agent1_intent.generate_text",
            side_effect=AssertionError("Agente 1 nao deveria chamar Ollama."),
        ) as agent1_generate, patch(
            "agents.agent3_process_analysis.generate_text",
            side_effect=AssertionError("Agente 3 nao deveria chamar Ollama."),
        ) as agent3_generate, patch(
            "agents.agent4_response.generate_text",
            side_effect=AssertionError("Agente 4 nao deveria chamar Ollama."),
        ) as agent4_generate, patch(
            "agents.agent4_response._ollama_rewrite_enabled",
            return_value=True,
        ):
            result = run_processual_chat_step(
                "qual a primeira e ultima movimentacao?",
                session_state,
            )

        self.assertIsNone(result.response.failed_stage)
        self.assertEqual(result.context_data["query_route"]["route"], "structured")
        self.assertFalse(result.context_data["query_route"]["requires_rag"])
        self.assertEqual(result.response.rag_status, "not_needed")
        self.assertEqual(result.analysis["question_focus"], "first_and_latest_movement")
        self.assertIn("Distribu", result.response.resposta)
        self.assertIn("12/03/1981", result.response.resposta)
        self.assertIn("Arquivado definitivamente", result.response.resposta)
        self.assertIn("05/02/1984", result.response.resposta)
        agent1_generate.assert_not_called()
        agent3_generate.assert_not_called()
        agent4_generate.assert_not_called()

    def test_chat_answers_latest_movement_without_model(self) -> None:
        result = self._run_active_process_question_without_model(
            "qual foi a ultima movimentacao?"
        )

        self.assertEqual(result.analysis["question_focus"], "latest_movement")
        self.assertEqual(self._movement_fact_count(result), 1)
        self.assertIn("Arquivado definitivamente", result.response.resposta)
        self.assertIn("05/02/1984", result.response.resposta)
        self.assertNotIn("10/10/1983", result.response.resposta)

    def test_chat_answers_default_recent_movements_without_model(self) -> None:
        result = self._run_active_process_question_without_model(
            "quais foram as ultimas movimentacoes?"
        )

        self.assertEqual(result.analysis["question_focus"], "movement_list")
        self.assertEqual(self._movement_fact_count(result), 3)
        self.assertIn("Arquivado definitivamente", result.response.resposta)
        self.assertIn("10/10/1983", result.response.resposta)
        self.assertIn("15/08/1982", result.response.resposta)
        self.assertNotIn("20/05/1981", result.response.resposta)
        self.assertNotIn("12/03/1981", result.response.resposta)

    def test_chat_answers_requested_recent_movement_count_without_model(self) -> None:
        result = self._run_active_process_question_without_model(
            "mostre as 3 movimentacoes mais recentes"
        )

        self.assertEqual(result.analysis["question_focus"], "movement_list")
        self.assertEqual(self._movement_fact_count(result), 3)
        self.assertEqual(result.response.resposta.count("- Movimentacao"), 3)

    def test_chat_answers_all_movements_without_model(self) -> None:
        result = self._run_active_process_question_without_model(
            "liste todas as movimentacoes"
        )

        self.assertEqual(result.analysis["question_focus"], "movement_list")
        self.assertEqual(self._movement_fact_count(result), 5)
        self.assertEqual(result.response.resposta.count("- Movimentacao"), 5)
        self.assertIn("Distribu", result.response.resposta)
        self.assertIn("Arquivado definitivamente", result.response.resposta)

    def test_chat_answers_movement_timeline_without_model(self) -> None:
        result = self._run_active_process_question_without_model(
            "o que aconteceu nesse processo ate agora?"
        )

        self.assertEqual(result.analysis["question_focus"], "movement_timeline")
        self.assertEqual(self._movement_fact_count(result), 5)
        response = result.response.resposta
        self.assertIn("Linha do tempo", response)
        dates = [
            response.find("12/03/1981"),
            response.find("20/05/1981"),
            response.find("15/08/1982"),
            response.find("10/10/1983"),
            response.find("05/02/1984"),
        ]
        self.assertTrue(all(position >= 0 for position in dates))
        self.assertEqual(dates, sorted(dates))


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
