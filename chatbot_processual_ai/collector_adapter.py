from services.process_repository import find_process_by_number as _find_process_by_number


def find_process_by_number(process_number: str) -> dict | None:
    return _find_process_by_number(process_number)
