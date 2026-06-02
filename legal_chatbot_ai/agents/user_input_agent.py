"""Agente de entrada do usuario.

Este agente prepara a mensagem antes do contexto. Ele nao chama Ollama, nao
decide intencao juridica e nao define se sera feita coleta.
"""

import re


# Formato CNJ mais comum com pontuacao.
CNJ_FORMATTED_PATTERN = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")

# Candidato com digitos e separadores simples. A validacao real fica em utils.
LOOSE_PROCESS_PATTERN = re.compile(r"\b[\d\s.-]{20,}\b")


def _normalize_text(raw_message: str) -> str:
    """Remove espacos duplicados e bordas desnecessarias."""
    return " ".join(str(raw_message).strip().split())


def _extract_possible_process_number(message: str) -> str | None:
    """Identifica um possivel numero de processo, sem validar completamente."""
    formatted_match = CNJ_FORMATTED_PATTERN.search(message)
    if formatted_match:
        return formatted_match.group(0)

    for candidate_match in LOOSE_PROCESS_PATTERN.finditer(message):
        candidate = candidate_match.group(0).strip()
        only_digits = re.sub(r"\D", "", candidate)

        if len(only_digits) == 20:
            return " ".join(candidate.split())

    return None


def run_user_input_agent(raw_message: str) -> dict:
    """Monta o primeiro contrato JSON a partir da mensagem do usuario."""
    notes = []

    if raw_message is None or str(raw_message).strip() == "":
        notes.append("Mensagem do usuario esta vazia.")

    normalized_message = _normalize_text(raw_message or "")
    possible_process_number = _extract_possible_process_number(normalized_message)

    return {
        "raw_message": raw_message or "",
        "normalized_message": normalized_message,
        "possible_process_number": possible_process_number,
        "notes": notes,
    }


if __name__ == "__main__":
    examples = [
        "Quero saber o andamento do processo 0000000-00.0000.0.00.0000",
        "Consultar processo 0000000 00 0000 0 00 0000 por favor",
        "   Tenho uma duvida sobre pensao alimenticia   ",
        "",
        None,
    ]

    for example in examples:
        print(run_user_input_agent(example))
