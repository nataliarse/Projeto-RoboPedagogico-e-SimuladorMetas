import json
import unittest
from pathlib import Path

from pydantic import ValidationError

import main
from services import meta2_groups


SERIES_FIXTURE = json.loads(
    (
        Path(__file__).parents[2]
        / "docs"
        / "integracao_equipe_b"
        / "fixtures"
        / "meta2_original_series.json"
    ).read_text(encoding="utf-8")
)


class Meta2GroupsTestCase(unittest.TestCase):
    def test_base_separates_official_v3_from_original_non_homologated_result(self):
        result = main.get_meta2_groups_base()
        self.assertEqual(result["resultado_2026"]["A"]["meta2"], 105.32)
        self.assertEqual(result["resultado_2026"]["ANT"]["meta2"], 111.11)
        self.assertEqual(result["reproducao_original_2026"]["A"]["meta2"], 104.63)
        self.assertEqual(result["reproducao_original_2026"]["ANT"]["meta2"], 110.0)
        self.assertFalse(result["resultado_2026"]["A"]["homologado"])
        self.assertEqual(result["resultado_2026"]["A"]["status_validacao"], "demonstrativo")
        self.assertFalse(result["resultado_2026"]["ANT"]["homologado"])
        self.assertEqual(result["resultado_2026"]["ANT"]["status_validacao"], "demonstrativo")
        self.assertFalse(result["reproducao_original_2026"]["ANT"]["homologado"])
        self.assertEqual(result["serie_A"][12]["tipo"], "real")
        self.assertEqual(result["serie_A"][14]["tipo"], "previsao")

    def test_all_original_historical_and_forecast_values_match_audited_fixture(self):
        for group in ("A", "ANT"):
            self.assertEqual(
                meta2_groups.DATASET_METADATA[group]["proveniencia"]["versao"],
                f"sha256:{SERIES_FIXTURE['evidencia']['zip_processual_sha256']}",
            )
            self.assertEqual(meta2_groups.HISTORY[group]["months"], SERIES_FIXTURE["meses_historicos"])
            self.assertEqual(meta2_groups.FORECAST[group]["months"], SERIES_FIXTURE["meses_projetados"])
            for field in ("julgados", "suspensos", "dessobrestados"):
                self.assertEqual(meta2_groups.HISTORY[group][field], SERIES_FIXTURE[group]["historico"][field])
                self.assertEqual(meta2_groups.FORECAST[group][field], SERIES_FIXTURE[group]["projecao"][field])

    def test_historical_110_case_is_reproducible_but_not_the_2026_rule(self):
        historical = meta2_groups.calculate_ant_percentage(22, 72, 28, 24, 100)
        official_2026 = meta2_groups.calculate_meta_ant_2026(22, 72, 28, 24)

        self.assertEqual(round(historical, 2), 110.0)
        self.assertEqual(round(official_2026, 2), 111.11)

    def test_ant_24_reopened_is_6_observed_plus_18_forecast_not_december_flow(self):
        result = main.get_meta2_groups_base()
        december = result["serie_ANT"][-1]
        self.assertEqual(sum(meta2_groups.HISTORY["ANT"]["dessobrestados"][-2:]), 6)
        self.assertEqual(sum(meta2_groups.FORECAST["ANT"]["dessobrestados"]), 18)
        self.assertEqual(december["dessobrestados"], 2)
        self.assertEqual(december["dessobrestados_acum_2026"], 24)

    def test_meta_a_v3_denominator_deducts_reopened_while_original_does_not(self):
        december = main.get_meta2_groups_base()["serie_A"][-1]
        self.assertEqual(december["julgados_calculo"], 26907)
        self.assertEqual(december["suspensos_calculo"], 190)
        self.assertEqual(december["dessobrestados_calculo"], 180)
        self.assertEqual(december["denominador"], 27178)
        self.assertEqual(december["denominador_original"], 27358)
        self.assertEqual(december["meta2"], 105.32)
        self.assertEqual(december["meta2_original"], 104.63)

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
        self.assertEqual(result["resultado_2026"]["A"]["meta2"], 105.36)
        self.assertEqual(result["resultado_2026"]["ANT"]["meta2"], 105.82)
        self.assertEqual(result["reproducao_original_2026"]["A"]["meta2"], 104.67)
        self.assertEqual(result["reproducao_original_2026"]["ANT"]["meta2"], 104.76)

    def test_real_month_can_be_changed_as_validated(self):
        result = main.simulate_meta2_groups_endpoint(
            main.SimularMeta2Request.parse_obj(
                {"alteracoes_A": {"2026-01": {"julgados": 10}}}
            )
        )
        january = next(row for row in result["serie_A"] if row["data"] == "2026-01")
        self.assertEqual(january["tipo"], "real")
        self.assertEqual(january["julgados"], 137)

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
