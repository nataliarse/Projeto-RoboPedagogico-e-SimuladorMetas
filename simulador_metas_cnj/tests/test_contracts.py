import json
import unittest
from pathlib import Path

from pydantic import ValidationError

import main


FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "contracts.json").read_text(encoding="utf-8")
)


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


if __name__ == "__main__":
    unittest.main()
