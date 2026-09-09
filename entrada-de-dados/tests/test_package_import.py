"""Probes offline da fronteira instalável do coletor."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class _FixtureCache:
    def __init__(self, fixture: Path) -> None:
        self.fixture = fixture

    def __truediv__(self, _name: str) -> Path:
        return self.fixture


def test_public_api_is_lightweight() -> None:
    from trt18_collector import obter_processo

    assert callable(obter_processo)
    assert not {"playwright", "cv2", "ddddocr"}.intersection(sys.modules)


def test_public_api_imports_outside_repository() -> None:
    probe = (
        "import sys; "
        "from trt18_collector import obter_processo; "
        "assert callable(obter_processo); "
        "assert not {'playwright', 'cv2', 'ddddocr'}.intersection(sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=Path(sys.executable).anchor,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_cache_only_keeps_working_with_sanitized_fixture(monkeypatch) -> None:
    import trt18_collector.service as service

    fixture = Path(__file__).parents[1] / "exemplos" / "exemplo_bruto.json"
    monkeypatch.setattr(service, "DIR_BRUTOS", _FixtureCache(fixture))

    result = service.obter_processo("00110008219815180051", coletar=False)

    assert result["processo"]["numero_normalizado"] == "00110008219815180051"
