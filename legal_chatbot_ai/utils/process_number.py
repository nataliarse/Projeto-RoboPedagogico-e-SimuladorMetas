"""Utilitarios para numero de processo.

Este modulo valida e normaliza numeros antes de qualquer coleta mockada. A
decisao do LLM nao e suficiente: a validacao do formato fica no codigo.
"""

import re


def _only_digits(value: str) -> str:
    """Remove tudo que nao for digito."""
    return re.sub(r"\D", "", value)


def _format_process_number(only_digits: str) -> str:
    """Aplica o formato CNJ esperado: 0000000-00.0000.0.00.0000."""
    return (
        f"{only_digits[0:7]}-"
        f"{only_digits[7:9]}."
        f"{only_digits[9:13]}."
        f"{only_digits[13:14]}."
        f"{only_digits[14:16]}."
        f"{only_digits[16:20]}"
    )


def normalize_process_number(raw_number: str) -> dict:
    """Valida e normaliza um numero de processo informado pelo usuario."""
    if raw_number is None or str(raw_number).strip() == "":
        return {
            "is_valid": False,
            "raw": raw_number,
            "normalized": None,
            "only_digits": "",
            "errors": ["Numero de processo nao foi informado."],
        }

    raw = str(raw_number)
    only_digits = _only_digits(raw)

    if len(only_digits) != 20:
        return {
            "is_valid": False,
            "raw": raw,
            "normalized": None,
            "only_digits": only_digits,
            "errors": ["Número de processo deve conter 20 dígitos."],
        }

    return {
        "is_valid": True,
        "raw": raw,
        "normalized": _format_process_number(only_digits),
        "only_digits": only_digits,
        "errors": [],
    }


if __name__ == "__main__":
    examples = [
        "0000000 00 0000 0 00 0000",
        "0000000-00.0000.0.00.0000",
        "abc123",
        "",
        None,
    ]

    for example in examples:
        print(normalize_process_number(example))
