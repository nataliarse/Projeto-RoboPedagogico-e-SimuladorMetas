import json
import asyncio
import unittest
from pathlib import Path

from pydantic import ValidationError

import main


FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "contracts.json").read_text(encoding="utf-8")
)


def asgi_request(method, path, payload, *, raise_server_exceptions=True):
    body = json.dumps(payload).encode()
    received = [{"type": "http.request", "body": body, "more_body": False}]
    sent = []

    async def receive():
        return received.pop(0) if received else {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": method, "scheme": "http", "path": path,
        "raw_path": path.encode(), "query_string": b"", "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 1), "server": ("test", 80),
    }
    try:
        asyncio.run(main.app(scope, receive, send))
    except Exception:
        if raise_server_exceptions:
            raise
    status = next(item["status"] for item in sent if item["type"] == "http.response.start")
    content = b"".join(item.get("body", b"") for item in sent if item["type"] == "http.response.body")
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        payload = {"detail": content.decode("utf-8", errors="replace")}
    return status, payload


class SimulatorContractTestCase(unittest.TestCase):
    def test_valid_request_fixtures_match_all_post_endpoints(self):
        self.assertIsInstance(main.SimularRequest.parse_obj(FIXTURES["valid"]["simular"]), main.SimularRequest)
        self.assertIsInstance(main.CompararRequest.parse_obj(FIXTURES["valid"]["comparar"]), main.CompararRequest)
        self.assertIsInstance(main.OtimizadorRequest.parse_obj(FIXTURES["valid"]["otimizador"]), main.OtimizadorRequest)

    def test_invalid_request_fixtures_are_rejected(self):
        cases = (
            (main.SimularRequest, FIXTURES["invalid"]["simular"]),
            (main.CompararRequest, FIXTURES["invalid"]["comparar"]),
            (main.OtimizadorRequest, FIXTURES["invalid"]["otimizador"]),
        )
        for model, fixture in cases:
            with self.subTest(model=model.__name__), self.assertRaises(ValidationError):
                model.parse_obj(fixture)

    def test_openapi_declares_four_endpoint_response_schemas(self):
        paths = main.app.openapi()["paths"]
        expected = {
            ("/api/base", "get"): "ResultadoMetasResponse",
            ("/api/simular", "post"): "ResultadoMetasResponse",
            ("/api/comparar", "post"): "CompararResponse",
            ("/api/otimizador", "post"): "OtimizadorResponse",
        }
        for (path, method), schema in expected.items():
            with self.subTest(path=path):
                response = paths[path][method]["responses"]["200"]
                reference = response["content"]["application/json"]["schema"]["$ref"]
                self.assertEqual(reference, f"#/components/schemas/{schema}")

    def test_invalid_http_payload_returns_structured_422(self):
        status, payload = asgi_request("POST", "/api/simular", FIXTURES["invalid"]["simular"])
        self.assertEqual(status, 422)
        self.assertIsInstance(payload["detail"], list)

    def test_unexpected_failure_returns_500_without_internal_detail(self):
        original = main.calcular_metas
        try:
            main.calcular_metas = lambda *_: (_ for _ in ()).throw(RuntimeError("PRIVATE"))
            status, payload = asgi_request("GET", "/api/base", {}, raise_server_exceptions=False)
        finally:
            main.calcular_metas = original
        self.assertEqual(status, 500)
        self.assertNotIn("PRIVATE", json.dumps(payload))

    def test_numeric_response_fields_are_json_numbers(self):
        status, payload = asgi_request("GET", "/api/base", {})
        self.assertEqual(status, 200)
        self.assertIsInstance(payload["meta1_final"], (int, float))
        self.assertIsInstance(payload["meta2_final"], (int, float))
        self.assertNotIsInstance(payload["meta1_final"], bool)


if __name__ == "__main__":
    unittest.main()
