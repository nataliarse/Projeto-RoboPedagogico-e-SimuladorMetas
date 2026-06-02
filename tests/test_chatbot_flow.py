import unittest
from contextlib import ExitStack
from unittest.mock import patch

from legal_chatbot_ai.collection.collection_router import (
    run_collection_router as real_collection_router,
)
from legal_chatbot_ai.orchestrator import run_chatbot_flow


def _blocked_llm_stack() -> ExitStack:
    """Bloqueia chamadas ao Ollama em fluxos que devem ser deterministicos."""
    stack = ExitStack()
    targets = [
        "legal_chatbot_ai.agents.context_agent.call_ollama",
        "legal_chatbot_ai.agents.legal_reasoning_agent.call_ollama",
        "legal_chatbot_ai.agents.response_agent.call_ollama",
    ]

    for target in targets:
        stack.enter_context(
            patch(target, side_effect=AssertionError(f"LLM chamado: {target}"))
        )
    return stack


class ChatbotFlowTests(unittest.TestCase):
    def test_greeting_is_no_collection_and_does_not_ask_for_cnj(self):
        with _blocked_llm_stack():
            result = run_chatbot_flow("oi, tudo bem?")

        context = result["debug"]["context_decision"]
        self.assertEqual(context["intent"], "greeting")
        self.assertEqual(context["next_action"], "NO_COLLECTION")
        self.assertFalse(context["needs_collection"])
        self.assertIsNone(result["debug"]["collected_data"])
        self.assertIn("Tudo certo", result["answer"])
        self.assertNotIn("preciso que voce informe", result["answer"])
        self.assertNotIn("Informacao geral", result["answer"])

    def test_user_feedback_is_no_collection_and_does_not_ask_for_cnj(self):
        with _blocked_llm_stack():
            result = run_chatbot_flow("uau, incrivel")

        context = result["debug"]["context_decision"]
        self.assertEqual(context["intent"], "user_feedback")
        self.assertEqual(context["next_action"], "NO_COLLECTION")
        self.assertFalse(context["needs_collection"])
        self.assertIsNone(result["debug"]["collected_data"])
        self.assertNotIn("preciso que voce informe", result["answer"])
        self.assertNotIn("Informacao geral", result["answer"])

    def test_process_lookup_validates_normalizes_and_calls_collection(self):
        with (
            _blocked_llm_stack(),
            patch(
                "legal_chatbot_ai.orchestrator.run_collection_router",
                wraps=real_collection_router,
            ) as collection_router_mock,
        ):
            result = run_chatbot_flow(
                "consulte o processo 0000000-00.0000.0.00.0000"
            )

        context = result["debug"]["context_decision"]
        self.assertEqual(context["intent"], "process_lookup_request")
        self.assertEqual(context["next_action"], "REQUEST_COLLECTION")
        self.assertTrue(context["needs_collection"])
        self.assertEqual(
            result["debug"]["process_number_result"]["normalized"],
            "0000000-00.0000.0.00.0000",
        )
        self.assertIsNotNone(result["debug"]["collected_data"])
        collection_router_mock.assert_called_once()
        self.assertIn("consulta simulada", result["answer"])
        self.assertIn("em andamento", result["answer"])
        self.assertIn("Informacao geral", result["answer"])

    def test_follow_up_uses_last_collection_memory_without_new_collection(self):
        with (
            _blocked_llm_stack(),
            patch(
                "legal_chatbot_ai.orchestrator.run_collection_router",
                wraps=real_collection_router,
            ) as collection_router_mock,
        ):
            first_result = run_chatbot_flow(
                "consulte o processo 0000000-00.0000.0.00.0000"
            )
            second_result = run_chatbot_flow(
                "sobre o que voce acabou de coletar, explica melhor?",
                session_state=first_result["state"],
            )

        context = second_result["debug"]["context_decision"]
        self.assertEqual(context["intent"], "process_follow_up")
        self.assertEqual(context["next_action"], "NO_COLLECTION")
        self.assertTrue(context["should_use_memory"])
        self.assertEqual(context["memory_target"], "last_collection")
        self.assertEqual(second_result["debug"]["memory_used"], "last_collection")
        self.assertIsNone(second_result["debug"]["collected_data"])
        self.assertEqual(collection_router_mock.call_count, 1)
        self.assertIn("coleta simulada", second_result["answer"])
        self.assertIn("movimentacoes", second_result["answer"])

    def test_legal_general_question_does_not_collect(self):
        with _blocked_llm_stack():
            result = run_chatbot_flow("o que significa juntada de peticao?")

        context = result["debug"]["context_decision"]
        self.assertEqual(context["intent"], "legal_general_question")
        self.assertEqual(context["next_action"], "NO_COLLECTION")
        self.assertFalse(context["needs_collection"])
        self.assertIsNone(result["debug"]["collected_data"])
        self.assertIn("Juntada de peticao", result["answer"])
        self.assertIn("Informacao geral", result["answer"])

    def test_out_of_scope_request_redirects_without_collection(self):
        with _blocked_llm_stack():
            result = run_chatbot_flow("me conte uma piada")

        context = result["debug"]["context_decision"]
        self.assertEqual(context["intent"], "out_of_scope_request")
        self.assertEqual(context["next_action"], "NO_COLLECTION")
        self.assertFalse(context["needs_collection"])
        self.assertIsNone(result["debug"]["collected_data"])
        self.assertIn("foge um pouco do meu papel", result["answer"])
        self.assertNotIn("preciso que voce informe", result["answer"])
        self.assertNotIn("Informacao geral", result["answer"])

    def test_process_lookup_without_number_asks_for_cnj(self):
        with _blocked_llm_stack():
            result = run_chatbot_flow("quero ver o andamento do meu processo")

        context = result["debug"]["context_decision"]
        self.assertEqual(context["intent"], "process_lookup_request")
        self.assertEqual(context["next_action"], "ASK_CLARIFICATION")
        self.assertFalse(context["needs_collection"])
        self.assertIsNone(result["debug"]["collected_data"])
        self.assertIn("formato CNJ", result["answer"])


if __name__ == "__main__":
    unittest.main()
