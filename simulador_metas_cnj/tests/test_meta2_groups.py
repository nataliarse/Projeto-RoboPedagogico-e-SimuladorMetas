import unittest

from pydantic import ValidationError

import main
from services import meta2_groups


class Meta2GroupsTestCase(unittest.TestCase):
    def test_base_preserves_a_and_marks_ant_as_pending_validation(self):
        result = main.get_meta2_groups_base()
        self.assertEqual(result["resultado_2026"]["A"]["meta2"], 104.63)
        self.assertIsNone(result["resultado_2026"]["ANT"]["meta2"])
        self.assertFalse(result["resultado_2026"]["A"]["homologado"])
        self.assertEqual(result["resultado_2026"]["A"]["status_validacao"], "demonstrativo")
        self.assertFalse(result["resultado_2026"]["ANT"]["homologado"])
        self.assertEqual(result["resultado_2026"]["ANT"]["status_validacao"], "pendente_validacao")
        self.assertEqual(result["serie_A"][12]["tipo"], "real")
        self.assertEqual(result["serie_A"][14]["tipo"], "previsao")

    def test_historical_110_case_is_reproducible_but_not_the_2026_rule(self):
        historical = meta2_groups.calculate_ant_percentage(22, 72, 28, 24, 100)
        official_2026 = meta2_groups.calculate_meta_ant_2026(22, 72, 28, 24)

        self.assertEqual(round(historical, 2), 110.0)
        self.assertEqual(round(official_2026, 2), 111.11)

    def test_zero_denominator_returns_none(self):
        self.assertIsNone(meta2_groups.calculate_meta_ant_2026(22, 72, 28, 44))

    def test_consolidated_loads_are_not_summed_again(self):
        records = [
            self._ant_record("2026-01", 5, 1, 2),
            self._ant_record("2026-02", 7, 2, 4),
        ]
        series = meta2_groups.build_ant_series(
            records,
            72,
            self._metadata(meta2_groups.CONSOLIDATED_LOAD),
        )

        february = series[-1]
        self.assertEqual(february["julgados_acum_2026"], 12)
        self.assertEqual(february["julgados_calculo"], 7)
        self.assertEqual(february["suspensos_calculo"], 2)
        self.assertEqual(february["dessobrestados_calculo"], 4)
        self.assertEqual(february["denominador"], 66)
        self.assertEqual(february["meta2"], 10.71)

    def test_monthly_flows_are_accumulated_only_when_explicit(self):
        records = [
            self._ant_record("2026-01", 5, 1, 2),
            self._ant_record("2026-02", 2, 1, 2),
        ]
        series = meta2_groups.build_ant_series(
            records,
            72,
            self._metadata(meta2_groups.MONTHLY_FLOW),
        )

        february = series[-1]
        self.assertEqual(february["julgados_acum_2026"], 7)
        self.assertEqual(february["julgados_calculo"], 7)
        self.assertEqual(february["suspensos_calculo"], 2)
        self.assertEqual(february["dessobrestados_calculo"], 4)
        self.assertEqual(february["denominador"], 66)
        self.assertEqual(february["meta2"], 10.71)

    def test_undefined_semantics_prevent_a_calculated_or_homologated_result(self):
        series = meta2_groups.build_ant_series(
            [self._ant_record("2026-12", 22, 28, 24)],
            72,
            self._metadata(meta2_groups.UNDEFINED_SEMANTICS),
        )

        self.assertIsNone(series[0]["meta2"])
        self.assertIsNone(series[0]["denominador"])
        self.assertEqual(series[0]["status_validacao"], "pendente_validacao")

    def test_missing_provenance_prevents_homologated_classification(self):
        metadata = self._metadata(meta2_groups.CONSOLIDATED_LOAD)
        metadata["proveniencia"] = {
            "fonte": "",
            "versao": None,
            "referencia": "2026",
            "homologada": True,
        }

        status, message, homologated = meta2_groups.classify_dataset(metadata)

        self.assertEqual(status, "demonstrativo")
        self.assertEqual(message, "Simulação com dados não homologados")
        self.assertFalse(homologated)

    def test_empty_scenario_matches_base(self):
        base = main.get_meta2_groups_base()
        simulated = main.simulate_meta2_groups_endpoint(main.SimularMeta2Request())
        self.assertEqual(simulated, base)

    def test_groups_are_independent_and_simultaneous_changes_are_supported(self):
        result = main.simulate_meta2_groups_endpoint(
            main.SimularMeta2Request.parse_obj({
                "alteracoes_A": {"2026-03": {"julgados": 10}},
                "alteracoes_ANT": {"2026-03": {"dessobrestados": -1}},
            })
        )
        self.assertEqual(result["resultado_2026"]["A"]["meta2"], 104.67)
        self.assertIsNone(result["resultado_2026"]["ANT"]["meta2"])
        self.assertEqual(result["resultado_2026"]["ANT"]["status_validacao"], "pendente_validacao")

    def test_real_month_can_be_changed_as_validated(self):
        result = main.simulate_meta2_groups_endpoint(
            main.SimularMeta2Request.parse_obj(
                {"alteracoes_A": {"2026-01": {"julgados": 10}}}
            )
        )
        january = next(row for row in result["serie_A"] if row["data"] == "2026-01")
        self.assertEqual(january["tipo"], "real")
        self.assertEqual(january["julgados"], 190)

    def test_nonpositive_denominators_return_null_without_nan(self):
        result = meta2_groups.simulate(
            {"2026-12": {"suspensos": 30000}},
            {"2026-12": {"suspensos": 1000}},
        )
        self.assertIsNone(result["resultado_2026"]["A"]["meta2"])
        self.assertIsNone(result["resultado_2026"]["ANT"]["meta2"])

    def test_invalid_group_month_fraction_and_extra_field_are_rejected(self):
        invalid_payloads = (
            {"alteracoes_A": {"2028-01": {"julgados": 1}}},
            {"alteracoes_A": {"2026-03": {"julgados": 1.5}}},
            {"alteracoes_A": {}, "desconhecido": True},
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                main.SimularMeta2Request.parse_obj(payload)

    def test_sequential_requests_do_not_mutate_constants(self):
        before = main.get_meta2_groups_base()
        main.simulate_meta2_groups_endpoint(
            main.SimularMeta2Request.parse_obj(
                {"alteracoes_A": {"2026-03": {"julgados": 999}}}
            )
        )
        after = main.get_meta2_groups_base()
        self.assertEqual(after, before)

    @staticmethod
    def _ant_record(month, judgments, suspended, reopened):
        return {
            "data": month,
            "tipo": "real",
            "julgados": judgments,
            "suspensos": suspended,
            "dessobrestados": reopened,
        }

    @staticmethod
    def _metadata(semantics):
        return {
            "proveniencia": {
                "fonte": "fixture sintética",
                "versao": "teste-1",
                "referencia": "2026",
                "homologada": False,
            },
            "semantica_temporal": {
                "julgados": semantics,
                "suspensos": semantics,
                "dessobrestados": semantics,
            },
        }


if __name__ == "__main__":
    unittest.main()
