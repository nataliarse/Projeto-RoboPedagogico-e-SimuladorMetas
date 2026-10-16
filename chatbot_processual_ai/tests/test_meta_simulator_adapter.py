import unittest

from schemas.meta_contracts import MetaSimulationRequest, MetaSimulationResponse
from services.meta_simulator_adapter import SimulatorUnavailableError, simulate_meta


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

    def test_missing_gateway_is_transparent_instead_of_not_integrated_result(self):
        request = MetaSimulationRequest("meta1", 2026, None, {})
        with self.assertRaises(SimulatorUnavailableError):
            simulate_meta(request)


if __name__ == "__main__":
    unittest.main()
