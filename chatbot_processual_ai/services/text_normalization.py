from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parents[1]


def resolve_project_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_DIR / path


def normalize_process_number(value: str | None) -> str | None:
    normalized = re.sub(r"\D", "", value or "")
    if len(normalized) != 20:
        return None
    return normalized


def normalize_text_for_match(value: Any) -> str:
    lowered = str(value or "").lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


def clean_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
