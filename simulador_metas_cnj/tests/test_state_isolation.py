import json
import unittest

import main
from test_contracts import asgi_request


class StateIsolationHTTPTestCase(unittest.TestCase):
    def test_two_meta2_scenarios_and_reload_leave_base_unchanged(self):
        status, base_before = asgi_request("GET", "/api/meta2/base", {})
        self.assertEqual(status, 200)

        status, first = asgi_request(
            "POST", "/api/meta2/simular",
            {"alteracoes_A": {"2026-03": {"julgados": 10}}, "alteracoes_ANT": {}},
        )
        self.assertEqual(status, 200)
        status, second = asgi_request(
            "POST", "/api/meta2/simular",
            {"alteracoes_A": {}, "alteracoes_ANT": {"2026-03": {"julgados": 5}}},
        )
        self.assertEqual(status, 200)
        self.assertNotEqual(first, second)

        status, base_after = asgi_request("GET", "/api/meta2/base", {})
        self.assertEqual(status, 200)
        self.assertEqual(base_after, base_before)

    def test_meta2_invalid_payload_is_structured_422(self):
        status, payload = asgi_request(
            "POST", "/api/meta2/simular",
            {"alteracoes_A": {"2026-99": {"julgados": 1}}},
        )
        self.assertEqual(status, 422)
        self.assertIsInstance(payload["detail"], list)

    def test_responses_never_emit_nonstandard_nan_json(self):
        for method, path, payload in (
            ("GET", "/api/base", {}),
            ("POST", "/api/meta1/quanto-falta", {"meta_alvo": 100}),
            ("GET", "/api/meta2/base", {}),
            ("POST", "/api/meta2/simular", {}),
        ):
            with self.subTest(path=path):
                status, response = asgi_request(method, path, payload)
                self.assertEqual(status, 200)
                json.dumps(response, allow_nan=False)

    def test_unexpected_meta2_failure_returns_sanitized_500(self):
        original = main.simulate_meta2_groups
        try:
            main.simulate_meta2_groups = lambda *_: (_ for _ in ()).throw(
                RuntimeError("PRIVATE_META2_DETAIL")
            )
            status, payload = asgi_request(
                "GET", "/api/meta2/base", {}, raise_server_exceptions=False
            )
        finally:
            main.simulate_meta2_groups = original
        self.assertEqual(status, 500)
        self.assertNotIn("PRIVATE_META2_DETAIL", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
