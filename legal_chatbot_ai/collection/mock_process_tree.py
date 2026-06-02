"""Arvore processual simulada.

Este arquivo retorna dados ficticios para validar o fluxo sem site real,
scraping, Playwright ou qualquer consulta externa.
"""


def get_mock_process_tree(process_number: str) -> dict:
    """Retorna uma arvore JSON mockada para um numero de processo validado."""
    return {
        "source": "mock",
        "process_number": process_number,
        "collected_at": "2026-06-02T10:00:00",
        "court": "Tribunal de exemplo",
        "process_class": "Procedimento comum mockado",
        "status": "em andamento",
        "parties": [
            {
                "role": "autor",
                "name": "Nome ocultado",
            },
            {
                "role": "réu",
                "name": "Nome ocultado",
            },
        ],
        "movements": [
            {
                "date": "2026-05-28",
                "description": "Movimentação processual simulada para teste.",
            },
            {
                "date": "2026-05-10",
                "description": "Conclusão simulada para análise interna.",
            },
        ],
        "warnings": [
            "Dados simulados. Não representam consulta oficial.",
        ],
    }


if __name__ == "__main__":
    print(get_mock_process_tree("0000000-00.0000.0.00.0000"))
