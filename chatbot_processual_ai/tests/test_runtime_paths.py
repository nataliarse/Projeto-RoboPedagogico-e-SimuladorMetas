from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_default_sqlite_path_is_independent_of_current_directory() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    probe = (
        "import sys; "
        f"sys.path.insert(0, {str(backend_dir)!r}); "
        "from services.process_repository import database_path; "
        "assert database_path().resolve() == "
        f"__import__('pathlib').Path({str((backend_dir / 'data' / 'processual.sqlite3').resolve())!r})"
    )
    environment = os.environ.copy()
    environment["LOCAL_DB_PATH"] = "data/processual.sqlite3"
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=Path(sys.executable).anchor,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
