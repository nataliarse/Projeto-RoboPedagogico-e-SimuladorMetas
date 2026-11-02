from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any

from schemas.processual_contracts import ProcessProgressEvent


ProgressReporter = Callable[[ProcessProgressEvent], None]


def progress_clock() -> float:
    return perf_counter()


def report_progress(
    progress_reporter: ProgressReporter | None,
    *,
    code: str,
    level: str,
    message: str,
    details: dict[str, Any] | None = None,
    started_at: float | None = None,
) -> None:
    if progress_reporter is None:
        return

    elapsed_ms = None
    if started_at is not None:
        elapsed_ms = max(0, int((perf_counter() - started_at) * 1000))

    event = ProcessProgressEvent(
        code=code,
        level=level,
        message=message,
        details=dict(details or {}),
        elapsed_ms=elapsed_ms,
    )

    try:
        progress_reporter(event)
    except Exception:
        return
