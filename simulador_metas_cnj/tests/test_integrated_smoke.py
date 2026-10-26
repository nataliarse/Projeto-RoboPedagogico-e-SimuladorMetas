import unittest

from test_contracts import asgi_request


class IntegratedSmokeTestCase(unittest.TestCase):
    """Smoke inteiramente ASGI/offline; não inicia servidor nem acessa rede."""

    def test_meta1_and_meta2_end_to_end_with_synthetic_changes(self):
        status, base = asgi_request("GET", "/api/base", {})
        self.assertEqual(status, 200)

        changes = {"2026-10": {"julgados": 100}}
        status, simulation = asgi_request("POST", "/api/simular", {"alteracoes": changes})
        self.assertEqual(status, 200)
        self.assertGreater(simulation["meta1_final"], base["meta1_final"])

        status, comparison = asgi_request(
            "POST", "/api/comparar", {"cenarios": [{"nome": "Smoke", "alteracoes": changes}]},
        )
        self.assertEqual(status, 200)
        self.assertEqual(comparison["cenarios"][0]["nome"], "Smoke")

        status, effort = asgi_request(
            "POST", "/api/meta1/quanto-falta", {"meta_alvo": 100, "mes_inicio": "2026-03", "alteracoes": {}},
        )
        self.assertEqual(status, 200)
        self.assertTrue(effort["ok"])
        self.assertEqual(effort["meta_alvo"], 100)

        status, meta2_base = asgi_request("GET", "/api/meta2/base", {})
        self.assertEqual(status, 200)
        status, meta2_simulation = asgi_request(
            "POST", "/api/meta2/simular",
            {"alteracoes_A": {"2026-03": {"julgados": 10}}, "alteracoes_ANT": {}},
        )
        self.assertEqual(status, 200)
        self.assertGreater(
            meta2_simulation["resultado_2026"]["A"]["meta2"],
            meta2_base["resultado_2026"]["A"]["meta2"],
        )


if __name__ == "__main__":
    unittest.main()
