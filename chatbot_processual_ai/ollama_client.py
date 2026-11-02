from dataclasses import dataclass
from typing import Any

import requests

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE,
    OLLAMA_TIMEOUT_SECONDS,
)


class OllamaError(Exception):
    """Base exception for local Ollama client errors."""


class OllamaConnectionError(OllamaError):
    pass


class OllamaTimeoutError(OllamaError):
    pass


class OllamaHTTPError(OllamaError):
    pass


class OllamaInvalidJSONError(OllamaError):
    pass


class OllamaMissingFieldError(OllamaError):
    pass


@dataclass(frozen=True)
class OllamaAvailability:
    base_url: str
    configured_model: str
    installed_models: list[str]
    model_available: bool


_runtime_model: str | None = None
_runtime_num_ctx: int | None = None


def _base_url() -> str:
    return OLLAMA_BASE_URL.rstrip("/")


def set_runtime_model(model_name: str | None, num_ctx: int | None = None) -> None:
    global _runtime_model, _runtime_num_ctx

    if isinstance(model_name, str) and model_name.strip():
        _runtime_model = model_name.strip()
    else:
        _runtime_model = None

    if isinstance(num_ctx, int) and num_ctx > 0:
        _runtime_num_ctx = num_ctx
    else:
        _runtime_num_ctx = None


def get_runtime_model() -> str:
    return _runtime_model or OLLAMA_MODEL


def _get_runtime_num_ctx() -> int | None:
    return _runtime_num_ctx


def _request_json(method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
    url = f"{_base_url()}{endpoint}"

    try:
        response = requests.request(
            method,
            url,
            timeout=OLLAMA_TIMEOUT_SECONDS,
            **kwargs,
        )
    except requests.exceptions.Timeout as exc:
        raise OllamaTimeoutError("Tempo limite excedido ao chamar o Ollama.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise OllamaConnectionError("Falha de conexao com o Ollama local.") from exc
    except requests.exceptions.RequestException as exc:
        raise OllamaConnectionError("Falha ao chamar o Ollama local.") from exc

    if not response.ok:
        raise OllamaHTTPError(
            f"Ollama retornou HTTP {response.status_code}: {response.text}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise OllamaInvalidJSONError("Ollama retornou JSON invalido.") from exc

    if not isinstance(data, dict):
        raise OllamaInvalidJSONError("Ollama retornou um JSON inesperado.")

    return data


def _extract_model_name(model: Any) -> str | None:
    if isinstance(model, str):
        return model

    if not isinstance(model, dict):
        return None

    name = model.get("name") or model.get("model")
    if isinstance(name, str):
        return name

    return None


def check_ollama_availability() -> OllamaAvailability:
    data = _request_json("GET", "/api/tags")

    if "models" not in data:
        raise OllamaMissingFieldError("Resposta do Ollama sem o campo 'models'.")

    models = data["models"]
    if not isinstance(models, list):
        raise OllamaInvalidJSONError("Campo 'models' do Ollama nao e uma lista.")

    installed_models = [
        model_name
        for model_name in (_extract_model_name(model) for model in models)
        if model_name
    ]

    return OllamaAvailability(
        base_url=_base_url(),
        configured_model=OLLAMA_MODEL,
        installed_models=installed_models,
        model_available=OLLAMA_MODEL in installed_models,
    )


def generate_text(prompt: str, system_prompt: str | None = None) -> str:
    options: dict[str, Any] = {
        "temperature": OLLAMA_TEMPERATURE,
    }
    runtime_num_ctx = _get_runtime_num_ctx()
    if runtime_num_ctx is not None:
        options["num_ctx"] = runtime_num_ctx

    payload: dict[str, Any] = {
        "model": get_runtime_model(),
        "prompt": prompt,
        "stream": False,
        "options": options,
    }

    if system_prompt is not None:
        payload["system"] = system_prompt

    data = _request_json("POST", "/api/generate", json=payload)

    if "response" not in data:
        raise OllamaMissingFieldError("Resposta do Ollama sem o campo 'response'.")

    response_text = data["response"]
    if not isinstance(response_text, str):
        raise OllamaInvalidJSONError("Campo 'response' do Ollama nao e texto.")

    return response_text
