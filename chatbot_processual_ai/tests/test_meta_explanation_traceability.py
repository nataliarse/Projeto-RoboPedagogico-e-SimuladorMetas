import unittest

from schemas.meta_contracts import MetaSimulationResponse
from services.meta_explanation_service import explain_meta_simulation


class MetaExplanationTraceabilityTestCase(unittest.TestCase):
    def test_explanation_traces_result_target_and_scenario_premises(self):
        response = MetaSimulationResponse(
            tipo="meta_simulation",
            meta_id="meta1",
            ano=2026,
            status="success",
            resultado=109.86,
            meta_alvo=100.0,
            indicadores={
                "cenario": {
                    "alteracoes": {
                        "2026-06": {"julgados": 10, "suspensos": -2}
                    }
                }
            },
            observacoes=[],
        )

        explanation = explain_meta_simulation("simule", response)

        for expected in ("meta1", "2026", "109,86", "100", "2026-06", "julgados 10", "suspensos -2"):
            self.assertIn(expected, explanation)
        self.assertNotIn("preliminar", explanation.casefold())
        self.assertNotIn("regra oficial", explanation.casefold())

    def test_empty_scenario_is_disclosed_without_invented_adjustments(self):
        response = MetaSimulationResponse(
            "meta_simulation", "meta2", 2026, "success", 161.71, 100.0,
            {"cenario": {}}, []
        )
        explanation = explain_meta_simulation("simule", response)
        self.assertIn("nenhuma alteração de cenário informada", explanation)
        self.assertNotIn("julgados", explanation)


if __name__ == "__main__":
    unittest.main()
