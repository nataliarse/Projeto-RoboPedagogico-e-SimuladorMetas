"""Utilitarios para contratos JSON.

Agentes podem pedir JSON ao LLM, mas o modelo pode devolver texto antes ou
depois do objeto. Este arquivo oferece uma extracao simples e segura.
"""

import json


def _fallback(raw_response: str) -> dict:
    """Retorno padrao quando nao for possivel interpretar o JSON."""
    return {
        "error": True,
        "message": "Não foi possível interpretar a resposta do agente.",
        "raw_response": raw_response,
    }


def _find_json_object(text: str) -> str | None:
    """Encontra o primeiro objeto JSON delimitado por chaves balanceadas."""
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def extract_json_from_text(text: str) -> dict:
    """Extrai um dict de uma resposta textual que deveria conter JSON."""
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else _fallback(text)
    except json.JSONDecodeError:
        pass

    json_block = _find_json_object(text)
    if not json_block:
        return _fallback(text)

    try:
        data = json.loads(json_block)
    except json.JSONDecodeError:
        return _fallback(text)

    return data if isinstance(data, dict) else _fallback(text)


if __name__ == "__main__":
    examples = [
        '{"intent": "GENERAL_INFORMATION"}',
        'Resposta do agente:\n{"intent": "REQUEST_COLLECTION", "ok": true}\nFim.',
        "texto sem json",
    ]

    for example in examples:
        print(extract_json_from_text(example))
