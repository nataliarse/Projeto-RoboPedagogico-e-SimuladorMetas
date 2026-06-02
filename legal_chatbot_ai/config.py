"""Configuracao central da PoC.

Este modulo carrega variaveis do arquivo .env usando python-dotenv. Assim, o
modelo do Ollama pode ser trocado sem alterar os agentes.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# OLLAMA_MODEL define qual modelo local sera usado pelo Ollama.
DEFAULT_OLLAMA_MODEL = "llama3.2:1b"

# OLLAMA_BASE_URL define o endereco da API local do Ollama.
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"

# OLLAMA_TEMPERATURE controla a variacao das respostas do modelo.
DEFAULT_OLLAMA_TEMPERATURE = "0.2"

# DEBUG_MODE mostra os contratos JSON entre agentes durante a demonstracao.
DEFAULT_DEBUG_MODE = "false"

# O arquivo .env oficial fica na raiz do projeto, ao lado de main.py.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


def _to_bool(value: str) -> bool:
    """Converte texto simples de .env para booleano."""
    return str(value).strip().lower() in {"1", "true", "yes", "sim", "on"}


def _to_float(value: str, default: float) -> float:
    """Converte texto de .env para float com fallback seguro."""
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def get_settings() -> dict:
    """Carrega e retorna as configuracoes simples da aplicacao."""
    load_dotenv(ENV_PATH)

    return {
        "ollama_model": os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
        "ollama_temperature": _to_float(
            os.getenv("OLLAMA_TEMPERATURE", DEFAULT_OLLAMA_TEMPERATURE),
            float(DEFAULT_OLLAMA_TEMPERATURE),
        ),
        "debug_mode": _to_bool(os.getenv("DEBUG_MODE", DEFAULT_DEBUG_MODE)),
    }
