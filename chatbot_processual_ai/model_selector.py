from typing import Any


MODEL_PROFILES = [
    {
        "tier": "advanced",
        "candidates": ["qwen3:14b"],
        "min_ram_available_gb": 20.0,
        "preferred_vram_gb": 12.0,
        "num_ctx": 4096,
    },
    {
        "tier": "strong",
        "candidates": ["qwen3:8b"],
        "min_ram_available_gb": 13.0,
        "preferred_vram_gb": 8.0,
        "num_ctx": 4096,
    },
    {
        "tier": "standard",
        "candidates": ["qwen3:4b-instruct"],
        "min_ram_available_gb": 8.0,
        "preferred_vram_gb": 4.0,
        "num_ctx": 4096,
    },
    {
        "tier": "compact",
        "candidates": ["qwen3:1.7b"],
        "min_ram_available_gb": 4.5,
        "preferred_vram_gb": 2.0,
        "num_ctx": 3072,
    },
    {
        "tier": "minimum",
        "candidates": ["llama3.2:1b", "qwen3:0.6b"],
        "min_ram_available_gb": 2.5,
        "preferred_vram_gb": 0.0,
        "num_ctx": 2048,
    },
]

MINIMUM_SAFE_RAM_GB = 2.5
OFFICIAL_MODEL_CATALOG = {
    candidate for profile in MODEL_PROFILES for candidate in profile["candidates"]
}


def select_runtime_model(
    resources: dict,
    installed_models: list[str],
    configured_model: str,
    selection_mode: str = "auto",
) -> dict:
    ram_available_gb = _get_ram_available_gb(resources)
    installed_model_set = _normalize_installed_models(installed_models)
    configured_model_name = _normalize_model_name(configured_model)
    normalized_selection_mode = _normalize_selection_mode(selection_mode)

    if normalized_selection_mode == "force":
        return _select_forced_model(
            configured_model_name,
            installed_model_set,
            resources,
            selection_mode=normalized_selection_mode,
        )

    for profile in MODEL_PROFILES:
        if ram_available_gb < float(profile["min_ram_available_gb"]):
            continue

        selected_model = _first_installed_candidate(profile, installed_model_set)
        if selected_model is None:
            continue

        return _selection_result(
            selected_model=selected_model,
            profile=profile,
            resources=resources,
            configured_model=configured_model_name,
            selection_reason=(
                f"Perfil {profile['tier']} selecionado: RAM disponivel "
                f"atende {float(profile['min_ram_available_gb']):.2f} GB "
                "e o modelo esta instalado no Ollama."
            ),
            safe_mode=False,
            selection_mode=normalized_selection_mode,
            forced_model=False,
        )

    fallback_profile = _configured_model_fallback_profile(
        configured_model_name,
        installed_model_set,
        ram_available_gb,
    )
    if fallback_profile is not None:
        return _selection_result(
            selected_model=configured_model_name,
            profile=fallback_profile,
            resources=resources,
            configured_model=configured_model_name,
            selection_reason=(
                "Modelo configurado usado como fallback seguro: esta instalado, "
                "pertence ao catalogo oficial e atende a politica de RAM."
            ),
            safe_mode=False,
            selection_mode=normalized_selection_mode,
            forced_model=False,
        )

    if ram_available_gb < MINIMUM_SAFE_RAM_GB:
        reason = (
            "RAM disponivel abaixo de 2.50 GB; nenhum modelo local seguro "
            "foi selecionado."
        )
    else:
        reason = (
            "Nenhum modelo instalado do catalogo oficial atende a politica "
            "conservadora de RAM disponivel."
        )

    return {
        "selected_model": None,
        "tier": None,
        "num_ctx": 0,
        "selection_reason": reason,
        "configured_model": configured_model_name,
        "configured_model_used": False,
        "vram_status": "unknown",
        "safe_mode": True,
        "selection_mode": normalized_selection_mode,
        "forced_model": False,
    }


def _selection_result(
    *,
    selected_model: str,
    profile: dict[str, Any],
    resources: dict,
    configured_model: str,
    selection_reason: str,
    safe_mode: bool,
    selection_mode: str,
    forced_model: bool,
) -> dict:
    return {
        "selected_model": selected_model,
        "tier": profile["tier"],
        "num_ctx": int(profile["num_ctx"]),
        "selection_reason": selection_reason,
        "configured_model": configured_model,
        "configured_model_used": selected_model == configured_model,
        "vram_status": _get_vram_status(resources, float(profile["preferred_vram_gb"])),
        "safe_mode": safe_mode,
        "selection_mode": selection_mode,
        "forced_model": forced_model,
    }


def _select_forced_model(
    configured_model: str,
    installed_models: set[str],
    resources: dict,
    *,
    selection_mode: str,
) -> dict:
    if not configured_model:
        return _forced_model_safe_mode(
            configured_model,
            selection_mode,
            "Modo force ativo, mas OLLAMA_MODEL nao foi configurado.",
        )

    if configured_model not in installed_models:
        return _forced_model_safe_mode(
            configured_model,
            selection_mode,
            (
                "Modo force ativo, mas o modelo configurado nao esta instalado "
                "no Ollama."
            ),
        )

    profile = _profile_for_model(configured_model)
    if profile is None:
        return {
            "selected_model": configured_model,
            "tier": "forced",
            "num_ctx": 0,
            "selection_reason": (
                "Modelo configurado forcado pelo .env; politica de RAM e "
                "catalogo oficial foram ignorados."
            ),
            "configured_model": configured_model,
            "configured_model_used": True,
            "vram_status": "unknown",
            "safe_mode": False,
            "selection_mode": selection_mode,
            "forced_model": True,
        }

    return _selection_result(
        selected_model=configured_model,
        profile=profile,
        resources=resources,
        configured_model=configured_model,
        selection_reason=(
            "Modelo configurado forcado pelo .env; politica de RAM foi ignorada."
        ),
        safe_mode=False,
        selection_mode=selection_mode,
        forced_model=True,
    )


def _forced_model_safe_mode(
    configured_model: str,
    selection_mode: str,
    selection_reason: str,
) -> dict:
    return {
        "selected_model": None,
        "tier": None,
        "num_ctx": 0,
        "selection_reason": selection_reason,
        "configured_model": configured_model,
        "configured_model_used": False,
        "vram_status": "unknown",
        "safe_mode": True,
        "selection_mode": selection_mode,
        "forced_model": True,
    }


def _configured_model_fallback_profile(
    configured_model: str,
    installed_models: set[str],
    ram_available_gb: float,
) -> dict[str, Any] | None:
    if configured_model not in installed_models:
        return None
    if configured_model not in OFFICIAL_MODEL_CATALOG:
        return None

    profile = _profile_for_model(configured_model)
    if profile is None:
        return None
    if ram_available_gb < float(profile["min_ram_available_gb"]):
        return None

    return profile


def _profile_for_model(model_name: str) -> dict[str, Any] | None:
    for profile in MODEL_PROFILES:
        if model_name in profile["candidates"]:
            return profile
    return None


def _first_installed_candidate(
    profile: dict[str, Any],
    installed_models: set[str],
) -> str | None:
    for candidate in profile["candidates"]:
        if candidate in installed_models:
            return candidate
    return None


def _normalize_installed_models(installed_models: list[str]) -> set[str]:
    return {
        normalized
        for normalized in (_normalize_model_name(model) for model in installed_models)
        if normalized
    }


def _normalize_model_name(model_name: object) -> str:
    if not isinstance(model_name, str):
        return ""
    return model_name.strip()


def _normalize_selection_mode(selection_mode: object) -> str:
    if not isinstance(selection_mode, str):
        return "auto"

    normalized = selection_mode.strip().lower()
    if normalized == "force":
        return "force"
    return "auto"


def _get_ram_available_gb(resources: dict) -> float:
    if not isinstance(resources, dict):
        return 0.0

    ram_available = resources.get("ram_available_gb")
    if isinstance(ram_available, (int, float)):
        return float(ram_available)

    return 0.0


def _get_vram_available_gb(resources: dict) -> float | None:
    if not isinstance(resources, dict):
        return None

    gpu = resources.get("gpu")
    if isinstance(gpu, dict):
        vram_available = gpu.get("vram_available_gb")
        if isinstance(vram_available, (int, float)):
            return float(vram_available)
        return None

    vram_available = resources.get("vram_available_gb")
    if isinstance(vram_available, (int, float)):
        return float(vram_available)

    return None


def _get_vram_status(resources: dict, preferred_vram_gb: float) -> str:
    if preferred_vram_gb <= 0:
        return "not_required"

    vram_available_gb = _get_vram_available_gb(resources)
    if vram_available_gb is None:
        return "unknown"
    if vram_available_gb >= preferred_vram_gb:
        return "sufficient"
    return "insufficient"
