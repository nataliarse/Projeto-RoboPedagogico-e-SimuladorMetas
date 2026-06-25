import json
import re
from pathlib import Path


_DATA_FILE = Path(__file__).resolve().parent / "data" / "sample_processes.json"


def find_process_by_number(process_number: str) -> dict | None:
    normalized_number = re.sub(r"\D", "", process_number or "")
    if len(normalized_number) != 20:
        return None

    with _DATA_FILE.open("r", encoding="utf-8") as file:
        processes = json.load(file)

    for process in processes:
        process_data = process.get("processo", {})
        if process_data.get("numero_normalizado") == normalized_number:
            return process

    return None
