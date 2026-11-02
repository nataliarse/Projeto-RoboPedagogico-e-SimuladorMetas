import subprocess
from typing import Any

import psutil

from config import OLLAMA_MODEL, OLLAMA_MODEL_SELECTION
from ollama_client import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaInvalidJSONError,
    OllamaMissingFieldError,
    OllamaTimeoutError,
    check_ollama_availability,
)


BYTES_PER_GB = 1024**3
MIB_PER_GB = 1024


def _round_gb(value: float) -> float:
    return round(value, 2)


def _bytes_to_gb(value: int) -> float:
    return _round_gb(value / BYTES_PER_GB)


def _mib_to_gb(value: float) -> float:
    return _round_gb(value / MIB_PER_GB)


def _gpu_not_detected(note: str | None = None) -> dict[str, Any]:
    return {
        "detected": False,
        "name": None,
        "vram_total_gb": None,
        "vram_available_gb": None,
        "detection_method": "none",
        "note": note,
    }


def _parse_memory_mib(value: str) -> float | None:
    cleaned = value.strip()
    if not cleaned or cleaned.upper() in {"N/A", "[N/A]"}:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_nvidia_smi_line(line: str) -> dict[str, Any] | None:
    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 3:
        return None

    name = parts[0]
    if not name:
        return None

    total_mib = _parse_memory_mib(parts[1])
    free_mib = _parse_memory_mib(parts[2])
    note = None
    if total_mib is None or free_mib is None:
        note = "VRAM nao pode ser detectada de forma confiavel via nvidia-smi."

    return {
        "detected": True,
        "name": name,
        "vram_total_gb": _mib_to_gb(total_mib) if total_mib is not None else None,
        "vram_available_gb": _mib_to_gb(free_mib) if free_mib is not None else None,
        "detection_method": "nvidia-smi",
        "note": note,
    }


def _detect_nvidia_gpu() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.free",
        "--format=csv,noheader,nounits",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except FileNotFoundError:
        return _gpu_not_detected(
            "VRAM nao pode ser detectada porque nvidia-smi nao esta disponivel."
        )
    except subprocess.TimeoutExpired:
        return _gpu_not_detected(
            "VRAM nao pode ser detectada porque nvidia-smi excedeu o tempo limite."
        )
    except OSError:
        return _gpu_not_detected(
            "VRAM nao pode ser detectada por falha ao executar nvidia-smi."
        )

    if result.returncode != 0:
        return _gpu_not_detected(
            "VRAM nao pode ser detectada porque nvidia-smi nao retornou dados validos."
        )

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    for line in lines:
        gpu = _parse_nvidia_smi_line(line)
        if gpu is not None:
            if len(lines) > 1 and gpu["note"] is None:
                gpu["note"] = "Mais de uma GPU detectada; exibindo a primeira."
            return gpu

    return _gpu_not_detected(
        "VRAM nao pode ser detectada porque nvidia-smi nao retornou GPUs validas."
    )


def get_system_resources() -> dict[str, Any]:
    memory = psutil.virtual_memory()

    return {
        "ram_total_gb": _bytes_to_gb(memory.total),
        "ram_available_gb": _bytes_to_gb(memory.available),
        "gpu": _detect_nvidia_gpu(),
    }


def get_runtime_diagnostics() -> dict[str, Any]:
    ollama = {
        "reachable": False,
        "configured_model": OLLAMA_MODEL,
        "model_selection": OLLAMA_MODEL_SELECTION,
        "configured_model_available": False,
    }

    try:
        availability = check_ollama_availability()
    except (
        OllamaConnectionError,
        OllamaTimeoutError,
        OllamaHTTPError,
        OllamaInvalidJSONError,
        OllamaMissingFieldError,
    ):
        pass
    else:
        ollama = {
            "reachable": True,
            "configured_model": availability.configured_model,
            "model_selection": OLLAMA_MODEL_SELECTION,
            "configured_model_available": availability.model_available,
        }

    return {
        "resources": get_system_resources(),
        "ollama": ollama,
    }
