import json
import unittest
from pathlib import Path

import main


SNAPSHOT = json.loads(
    (Path(__file__).parent / "fixtures" / "numeric_snapshot.json").read_text(encoding="utf-8")
)


class NumericSnapshotTestCase(unittest.TestCase):
    def assert_metric(self, actual, expected):
        self.assertIsNotNone(actual)
        self.assertAlmostEqual(actual, expected, delta=SNAPSHOT["tolerance"])

    def test_base_matches_approved_fixture_snapshot(self):
        response = main.get_base()
        self.assertEqual(len(response["registros"]), SNAPSHOT["records"])
        self.assert_metric(response["meta1_final"], SNAPSHOT["base"]["meta1_final"])
        self.assert_metric(response["meta2_final"], SNAPSHOT["base"]["meta2_final"])

    def test_empty_simulation_is_numerically_identical_to_base(self):
        base = main.get_base()
        simulated = main.simular(main.SimularRequest(alteracoes={}))
        self.assertEqual(simulated["registros"], base["registros"])
        self.assert_metric(simulated["meta1_final"], base["meta1_final"])
        self.assert_metric(simulated["meta2_final"], base["meta2_final"])


if __name__ == "__main__":
    unittest.main()
