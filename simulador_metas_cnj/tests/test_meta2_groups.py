import unittest

from pydantic import ValidationError

import main
from services import meta2_groups


class Meta2GroupsTestCase(unittest.TestCase):
    def test_base_matches_validated_snapshot(self):
        result = main.get_meta2_groups_base()
        self.assertEqual(result["resultado_2026"]["A"]["meta2"], 104.63)
        self.assertIsNone(result["resultado_2026"]["ANT"]["meta2"])
        self.assertEqual(result["serie_A"][12]["tipo"], "real")
        self.assertEqual(result["serie_A"][14]["tipo"], "previsao")

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
        self.assertEqual(result["resultado_2026"]["ANT"]["meta2"], 2200.0)

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


if __name__ == "__main__":
    unittest.main()
