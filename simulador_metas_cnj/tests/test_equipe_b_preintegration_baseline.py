import json
import unittest
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

import main


FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "equipe_b_preintegration_snapshot.json").read_text(
        encoding="utf-8"
    )
)


class EquipeBPreIntegrationBaselineTestCase(unittest.TestCase):
    def test_scenarios_match_snapshot_without_mutating_global_base(self):
        original = main.BASE_GLOBAL.copy(deep=True)

        for name, scenario in FIXTURE["scenarios"].items():
            with self.subTest(scenario=name):
                result = main.simular_cenario(main.BASE_GLOBAL, scenario["changes"])
                december = result[result["ano"] == main.ANO_SIMULACAO].iloc[-1]
                self.assertAlmostEqual(
                    float(december["meta1"]),
                    scenario["meta1_final"],
                    delta=FIXTURE["tolerance"],
                )
                self.assertAlmostEqual(
                    float(december["meta2"]),
                    scenario["meta2_final"],
                    delta=FIXTURE["tolerance"],
                )
                self.assertEqual(len(result), FIXTURE["records"])

                october = result[result["data"] == pd.Timestamp("2026-10-01")].iloc[0]
                if "oct_julgados" in scenario:
                    self.assertAlmostEqual(
                        float(october["julgados"]), scenario["oct_julgados"], places=6
                    )
                if "oct_suspensos" in scenario:
                    self.assertAlmostEqual(
                        float(october["suspensos"]), scenario["oct_suspensos"], places=6
                    )

                assert_frame_equal(main.BASE_GLOBAL, original, check_exact=True)


if __name__ == "__main__":
    unittest.main()
