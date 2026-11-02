import unittest
from unittest.mock import Mock

import requests

from schemas.meta_contracts import MetaSimulationRequest, MetaSimulationResponse
from services.meta_simulator_adapter import (
    HttpSimulatorGateway,
    InvalidSimulatorSchemaError,
    SimulatorUnavailableError,
    simulate_meta,
)


class FakeGateway:
    def __init__(self, response):
        self.response = response
        self.requests = []

    def simulate(self, request):
        self.requests.append(request)
        return self.response


class MetaSimulatorAdapterTestCase(unittest.TestCase):
    def test_delegates_exact_request_to_testable_gateway(self):
        request = MetaSimulationRequest("meta1", 2026, "VT-1", {"alteracoes": {}})
        response = MetaSimulationResponse(
            "meta_simulation", "meta1", 2026, "success", 109.86, 100.0, {}, []
        )
        gateway = FakeGateway(response)

        self.assertIs(simulate_meta(request, gateway), response)
        self.assertEqual(gateway.requests, [request])

    def test_http_gateway_sends_scenario_with_timeout_and_maps_numeric_result(self):
        http_response = Mock()
        http_response.raise_for_status.return_value = None
        http_response.json.return_value = {
            "registros": [{"data": "2026-01"}],
            "meta1_final": 109.86,
            "meta2_final": 161.71,
        }
        session = Mock()
        session.post.return_value = http_response
        gateway = HttpSimulatorGateway("http://simulator.local", 7.5, session)
        request = MetaSimulationRequest(
            "meta1", 2026, "VT-1", {"alteracoes": {"2026-06": {"julgados": 10}}}
        )

        result = gateway.simulate(request)

        session.post.assert_called_once_with(
            "http://simulator.local/api/simular",
            json={"alteracoes": {"2026-06": {"julgados": 10}}},
            timeout=7.5,
        )
        self.assertEqual(result.status, "success")
        self.assertEqual(result.resultado, 109.86)
        self.assertEqual(result.indicadores["registros"], 1)

    def test_http_gateway_translates_timeout_without_inventing_result(self):
        session = Mock()
        session.post.side_effect = requests.Timeout("controlled")
        gateway = HttpSimulatorGateway("http://simulator.local", 1, session)
        with self.assertRaises(SimulatorUnavailableError):
            gateway.simulate(MetaSimulationRequest("meta1", 2026, None, {}))

    def test_http_gateway_rejects_non_numeric_schema(self):
        http_response = Mock()
        http_response.raise_for_status.return_value = None
        http_response.json.return_value = {
            "registros": [], "meta1_final": "109.86", "meta2_final": 161.71
        }
        session = Mock()
        session.post.return_value = http_response
        gateway = HttpSimulatorGateway("http://simulator.local", 1, session)
        with self.assertRaises(InvalidSimulatorSchemaError):
            gateway.simulate(MetaSimulationRequest("meta1", 2026, None, {}))


if __name__ == "__main__":
    unittest.main()
