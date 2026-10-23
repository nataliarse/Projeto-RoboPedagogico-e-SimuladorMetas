import unittest

from fastapi import HTTPException
from pydantic import ValidationError

import main


class Meta1EffortTestCase(unittest.TestCase):
    def test_target_already_reached(self):
        result = main.quanto_falta(main.QuantoFaltaRequest(meta_alvo=90))
        self.assertTrue(result["ok"])
        self.assertTrue(result["ja_atingida"])
        self.assertEqual(result["incremento_mensal"], 0)

    def test_required_effort_is_confirmed_by_followup_simulation(self):
        result = main.quanto_falta(main.QuantoFaltaRequest(meta_alvo=100))
        self.assertEqual(result["incremento_mensal"], 387)
        changes = {
            month: {"julgados": result["incremento_mensal"]}
            for month in result["meses"]
        }
        simulated = main.simular_cenario(main.BASE_GLOBAL, changes)
        december = simulated[simulated["ano"] == main.ANO_SIMULACAO].iloc[-1]
        self.assertGreaterEqual(float(december["meta1"]), 100)
        self.assertEqual(float(december["meta1"]), result["meta_resultante"])

    def test_real_start_month_is_reported(self):
        result = main.quanto_falta(
            main.QuantoFaltaRequest(meta_alvo=100, mes_inicio="2026-01")
        )
        self.assertEqual(result["meses_reais"], ["2026-01", "2026-02"])

    def test_invalid_start_month_returns_400(self):
        with self.assertRaises(HTTPException) as raised:
            main.quanto_falta(
                main.QuantoFaltaRequest(meta_alvo=100, mes_inicio="2028-01")
            )
        self.assertEqual(raised.exception.status_code, 400)

    def test_fractional_change_and_out_of_range_target_are_rejected(self):
        with self.assertRaises(ValidationError):
            main.QuantoFaltaRequest.parse_obj(
                {"meta_alvo": 100, "alteracoes": {"2026-10": {"julgados": 1.5}}}
            )
        with self.assertRaises(ValidationError):
            main.QuantoFaltaRequest(meta_alvo=201)

    def test_negative_change_is_clamped_and_extreme_valid_target_is_calculated(self):
        negative = main.quanto_falta(
            main.QuantoFaltaRequest(
                meta_alvo=100,
                alteracoes={"2026-10": main.AlteracaoMes(julgados=-100000)},
            )
        )
        self.assertTrue(negative["ok"])
        extreme = main.quanto_falta(main.QuantoFaltaRequest(meta_alvo=200))
        self.assertTrue(extreme["ok"])
        self.assertGreaterEqual(extreme["meta_resultante"], 200)


if __name__ == "__main__":
    unittest.main()
