import unittest
from unittest.mock import patch

from orchestrators.processual_chat_orchestrator import run_processual_chat_step
from services.meta_diagnosis_service import is_process_meta_impact_question
from session_state import create_session_state


class MetaIntentRoutingTestCase(unittest.TestCase):
    def test_only_explicit_process_impact_language_matches(self):
        self.assertTrue(is_process_meta_impact_question("Este processo pesa na Meta 1?"))
        self.assertTrue(is_process_meta_impact_question("Qual o impacto desse processo nas metas?"))
        self.assertFalse(is_process_meta_impact_question("Qual a última movimentação do processo?"))
        self.assertFalse(is_process_meta_impact_question("Explique a Meta 1"))
        self.assertFalse(is_process_meta_impact_question("Simule um cenário da Meta 1"))
        self.assertFalse(is_process_meta_impact_question("O que conta como julgado na Meta 1?"))

    def test_server_questions_about_leaving_the_goal_match(self):
        self.assertTrue(is_process_meta_impact_question(
            "Qual movimento está impactando na meta 1 ou 2 do CNJ?"))
        self.assertTrue(is_process_meta_impact_question(
            "O que preciso fazer para parar de constar na meta?"))
        self.assertTrue(is_process_meta_impact_question("Como tirar o processo da Meta 2?"))

    def test_ordinary_process_question_is_not_diverted_to_meta_diagnosis(self):
        state = create_session_state()
        state["active_process"] = {"processo": {"numero": "001"}}
        with (
            patch(
                "orchestrators.processual_chat_orchestrator.answer_meta_question"
            ) as meta_answer,
            patch(
                "orchestrators.processual_chat_orchestrator.interpret_user_message",
                side_effect=RuntimeError("intent reached"),
            ) as intent,
        ):
            result = run_processual_chat_step("Qual a movimentação deste processo?", state)

        intent.assert_called_once()
        meta_answer.assert_not_called()
        self.assertEqual(result.response.failed_stage, "Agente 1")

    def test_explicit_process_meta_question_uses_deterministic_route(self):
        state = create_session_state()
        state["active_process"] = {"processo": {"numero": "001"}}
        with (
            patch(
                "orchestrators.processual_chat_orchestrator.answer_meta_question",
                return_value="Diagnóstico calculado.",
            ) as meta_answer,
            patch("orchestrators.processual_chat_orchestrator.interpret_user_message") as intent,
        ):
            result = run_processual_chat_step("Este processo pesa na Meta 1?", state)

        meta_answer.assert_called_once()
        intent.assert_not_called()
        self.assertEqual(result.response.intent, "meta_impact")
        self.assertEqual(result.response.resposta, "Diagnóstico calculado.")


if __name__ == "__main__":
    unittest.main()
