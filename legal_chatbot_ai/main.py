"""Ponto principal da PoC pelo terminal.

Mantem a versao principal por `python main.py`. A orquestracao fica em
`orchestrator.py` para tambem ser reutilizada pela API opcional.
"""

from .config import get_settings
from .orchestrator import run_chatbot_flow


EXIT_COMMANDS = {"sair", "exit", "quit"}


def main() -> None:
    """Loop simples de terminal usando input() e print()."""
    settings = get_settings()
    debug_mode = settings["debug_mode"]

    print("legal_chatbot_ai - chatbot juridico informativo")
    print("Digite sua mensagem ou use 'sair', 'exit' ou 'quit' para encerrar.\n")

    session_state = {}

    while True:
        raw_message = input("Voce: ").strip()

        if raw_message.lower() in EXIT_COMMANDS:
            print("Encerrando.")
            break

        if not raw_message:
            print("Assistente: Digite uma mensagem para eu analisar.\n")
            continue

        try:
            result = run_chatbot_flow(
                raw_message,
                debug_mode=debug_mode,
                session_state=session_state,
            )
            session_state = result.get("state", session_state)
            final_response = result["answer"]
        except RuntimeError as exc:
            final_response = (
                "Nao foi possivel concluir a resposta agora. "
                f"Detalhe: {exc}"
            )
        except Exception as exc:
            final_response = (
                "Ocorreu um erro inesperado nesta prova de conceito. "
                f"Detalhe: {exc}"
            )

        print(f"\nAssistente: {final_response}\n")


if __name__ == "__main__":
    main()
