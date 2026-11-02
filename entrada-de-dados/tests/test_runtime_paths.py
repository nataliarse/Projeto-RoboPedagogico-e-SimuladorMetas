"""Offline checks for deterministic collector runtime paths."""

from __future__ import annotations

from pathlib import Path
import sys


def test_runtime_artifacts_live_under_collector_data(monkeypatch) -> None:
    import trt18_collector.collector_trt18 as collector

    assert collector.DIR_BRUTOS == collector.RAIZ / "data" / "brutos"
    assert collector.DIR_DEBUG == collector.RAIZ / "data" / "debug"
    assert collector.CAPTCHA_OUTPUT == collector.DIR_DEBUG / "captcha" / "img_captured.png"

    monkeypatch.delenv("TRT18_COLLECTOR_BROWSER_EXECUTABLE", raising=False)
    assert collector.encontrar_navegador_instalado() is None


def test_external_browser_requires_an_explicit_existing_path(monkeypatch) -> None:
    import trt18_collector.collector_trt18 as collector

    executable = Path(sys.executable)
    monkeypatch.setenv("TRT18_COLLECTOR_BROWSER_EXECUTABLE", str(executable))

    assert collector.encontrar_navegador_instalado() == executable
