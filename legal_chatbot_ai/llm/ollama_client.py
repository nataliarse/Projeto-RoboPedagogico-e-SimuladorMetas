"""Cliente do Ollama local.

Este e o unico ponto da PoC que deve chamar o Ollama diretamente. Os agentes
devem usar este modulo, sem conhecer URL, modelo ou detalhes da API.
"""

import requests

from ..config import get_settings


def call_ollama(prompt: str) -> str:
    """Envia um prompt ao Ollama local e retorna apenas o texto gerado."""
    settings = get_settings()
    model = settings["ollama_model"]
    base_url = settings["ollama_base_url"].rstrip("/")
    url = f"{base_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": settings["ollama_temperature"],
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Nao foi possivel conectar ao Ollama local. "
            "Verifique se o Ollama esta rodando em OLLAMA_BASE_URL."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "A chamada ao Ollama demorou demais. "
            "Verifique se o modelo local esta carregando corretamente."
        ) from exc

    if response.status_code == 404:
        raise RuntimeError(
            f"O modelo configurado '{model}' nao foi encontrado no Ollama. "
            "Confira OLLAMA_MODEL no .env ou baixe o modelo com ollama pull."
        )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Ollama retornou erro HTTP {response.status_code}: {response.text}"
        ) from exc

    data = response.json()
    return data.get("response", "").strip()


if __name__ == "__main__":
    test_prompt = "Responda em uma frase: o que e um chatbot juridico informativo?"
    print(call_ollama(test_prompt))
