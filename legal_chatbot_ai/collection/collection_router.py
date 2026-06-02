"""Roteador de coleta simulada.

Recebe um numero ja validado e escolhe a fonte mockada. Futuramente, se a PoC
evoluir, o ponto de entrada para Playwright ficaria aqui, mas nesta versao nao
ha acesso externo.
"""

from .mock_process_tree import get_mock_process_tree


def _invalid_process_response(process_number_result: dict) -> dict:
    """Retorno seguro quando o numero ainda nao foi validado."""
    return {
        "source": "mock",
        "error": True,
        "message": "Coleta mockada nao executada: numero de processo invalido.",
        "process_number_result": process_number_result,
        "data": None,
    }


def run_collection_router(process_number_result: dict) -> dict:
    """Executa a coleta mockada somente para numero previamente validado."""
    if process_number_result.get("is_valid") is not True:
        return _invalid_process_response(process_number_result)

    normalized_process_number = process_number_result.get("normalized")
    if not normalized_process_number:
        return _invalid_process_response(process_number_result)

    return get_mock_process_tree(normalized_process_number)


if __name__ == "__main__":
    valid_example = {
        "is_valid": True,
        "raw": "0000000 00 0000 0 00 0000",
        "normalized": "0000000-00.0000.0.00.0000",
        "only_digits": "00000000000000000000",
        "errors": [],
    }
    invalid_example = {
        "is_valid": False,
        "raw": "abc123",
        "normalized": None,
        "only_digits": "123",
        "errors": ["Número de processo deve conter 20 dígitos."],
    }

    print(run_collection_router(valid_example))
    print(run_collection_router(invalid_example))
