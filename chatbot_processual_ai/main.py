import argparse
import json

from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text

import agents.agent1_intent as agent1_intent_module
import agents.agent3_process_analysis as agent3_process_analysis_module
from agents.agent1_intent import interpret_user_message
from agents.agent2_context_collection import (
    MAX_CONVERSATION_ENTRIES,
    build_context_and_collect,
)
from agents.agent3_process_analysis import (
    analyze_process_context,
    cpf_cnpj_removed_from_model_context,
)
from agents.agent4_response import create_user_response
from ollama_client import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaInvalidJSONError,
    OllamaMissingFieldError,
    OllamaTimeoutError,
    check_ollama_availability,
    generate_text,
)
from session_state import create_session_state


CHAT_EXIT_COMMANDS = {"sair", "exit", "quit"}
SAFE_CHAT_ERROR_RESPONSE = (
    "Não consegui processar essa mensagem agora. Tente reformular a pergunta."
)

AGENT2_SEQUENCE_MESSAGES = [
    "Consulte o processo 0011000-82.1981.5.18.0051",
    "Esse processo ainda está aberto?",
    "O que aconteceu antes do arquivamento?",
    "O que quer dizer trânsito em julgado nesse caso?",
    "Consulte outro processo",
]

AGENT3_SEQUENCE_MESSAGES = [
    "Consulte o processo 0011000-82.1981.5.18.0051",
    "Qual é a situação atual do processo?",
    "Quem são as partes?",
    "Quando ele foi arquivado?",
    "Existem pendências?",
    "O que a sentença decidiu?",
    "O que significa trânsito em julgado?",
]


AGENT4_SEQUENCE_MESSAGES = [
    "Oi",
    "Consulte o processo 0011000-82.1981.5.18.0051",
    "Quem são as partes?",
    "Quando ele foi arquivado?",
    "Existem pendências?",
    "O que a sentença decidiu?",
    "O que significa trânsito em julgado?",
    "Me ajuda a escolher uma placa de vídeo",
    "me fala disso",
]


console = Console()
error_console = Console(stderr=True)

USER_LABEL_STYLE = "bold cyan"
USER_TEXT_STYLE = "cyan"
AGENT_LABEL_STYLE = "bold green"
AGENT_TEXT_STYLE = "green"
ERROR_STYLE = "bold red"
INFO_STYLE = "cyan"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "yellow"
TRACE_STYLE = "magenta"


def _print_plain(message: str, style: str, *, stderr: bool = False) -> None:
    target_console = error_console if stderr else console
    target_console.print(str(message), style=style, markup=False)


def _print_prefixed(
    label: str,
    message: str,
    label_style: str,
    message_style: str,
) -> None:
    text = Text()
    text.append(f"{label}: ", style=label_style)
    text.append(str(message), style=message_style)
    console.print(text)


def _print_error(message: str) -> None:
    _print_plain(message, ERROR_STYLE, stderr=True)


def _print_info(message: str) -> None:
    _print_plain(message, INFO_STYLE)


def _print_success(message: str) -> None:
    _print_plain(message, SUCCESS_STYLE)


def _print_warning(message: str) -> None:
    _print_plain(message, WARNING_STYLE)


def _print_trace(message: str) -> None:
    _print_plain(message, TRACE_STYLE)


def _print_agent(message: str) -> None:
    _print_prefixed("Assistente", message, AGENT_LABEL_STYLE, AGENT_TEXT_STYLE)


def _print_user(message: str) -> None:
    _print_prefixed("Você", message, USER_LABEL_STYLE, USER_TEXT_STYLE)


def _read_user_message() -> str:
    return console.input("[bold cyan]Você:[/] ")


def _print_json(data: object) -> None:
    json_text = json.dumps(data, ensure_ascii=False, indent=2)
    console.print(Syntax(json_text, "json", theme="ansi_dark", word_wrap=True))


def _print_connection_error() -> None:
    _print_error("Não foi possível conectar ao Ollama local.")
    _print_error(
        "Verifique se o Ollama está em execução e se a URL configurada está correta."
    )


def _check_ollama(verbose: bool = True) -> bool:
    try:
        availability = check_ollama_availability()
    except (OllamaConnectionError, OllamaTimeoutError):
        _print_connection_error()
        return False
    except (OllamaHTTPError, OllamaInvalidJSONError, OllamaMissingFieldError) as exc:
        _print_error("Não foi possível validar o Ollama local.")
        _print_error(str(exc))
        return False

    if not availability.model_available:
        _print_warning(
            "O Ollama está acessível, mas o modelo configurado não foi encontrado."
        )
        _print_info(f"Modelo esperado: {availability.configured_model}")
        return False

    if verbose:
        _print_info(f"Ollama acessível em: {availability.base_url}")
        _print_info(f"Modelo configurado: {availability.configured_model}")
        _print_success("Status do modelo: disponível")
    return True


def _smoke_ollama() -> None:
    if not _check_ollama(verbose=False):
        return

    try:
        response = generate_text("Responda somente com a palavra: OK")
    except (OllamaConnectionError, OllamaTimeoutError):
        _print_connection_error()
        return
    except (OllamaHTTPError, OllamaInvalidJSONError, OllamaMissingFieldError) as exc:
        _print_error("Não foi possível concluir o teste do Ollama.")
        _print_error(str(exc))
        return

    _print_success("Teste do Ollama concluído.")
    _print_agent(f"Resposta do modelo: {response}")


def _run_agent2_test(message: str, session_state: dict) -> dict:
    intent_data = interpret_user_message(message)
    return build_context_and_collect(message, intent_data, session_state)


def _run_agent2_sequence_step(
    message: str,
    session_state: dict,
) -> dict:
    active_process_before = _active_process_normalized_number(session_state)
    intent_data = interpret_user_message(message)
    context_data = build_context_and_collect(message, intent_data, session_state)
    active_process_after = _active_process_normalized_number(session_state)

    return {
        "mensagem": message,
        "intent_original_agente1": intent_data.get("intent"),
        "intent_transportado_agente2": context_data.get("intent_data", {}).get(
            "intent"
        ),
        "collection_status": context_data.get("collection_status"),
        "processo_ativo": _active_process_status(
            active_process_before,
            active_process_after,
        ),
    }


def _run_agent3_test_step(message: str, session_state: dict) -> tuple[dict, dict]:
    intent_data = interpret_user_message(message)
    context_data = build_context_and_collect(message, intent_data, session_state)
    analysis = analyze_process_context(message, context_data)
    return context_data, analysis


def _run_agent4_test_step(
    message: str,
    session_state: dict,
) -> tuple[dict, dict, dict, str]:
    intent_data = interpret_user_message(message)
    context_data = build_context_and_collect(message, intent_data, session_state)
    analysis = analyze_process_context(message, context_data)
    response = create_user_response(message, analysis)
    return intent_data, context_data, analysis, response


def _run_chat() -> None:
    session_state = create_session_state()
    trace_enabled = False

    _print_success("Assistente Processual iniciado.")
    _print_info("Digite 'sair' para encerrar.")
    _print_info("Digite '--trace' para ligar ou desligar o modo de depuração.")

    while True:
        try:
            raw_message = _read_user_message()
        except EOFError:
            _print_agent("Encerrando a conversa. Até mais.")
            return

        message = raw_message.strip()
        command = message.lower()

        if not message:
            _print_agent("Digite uma pergunta ou informe o número de um processo.")
            continue

        if command in CHAT_EXIT_COMMANDS:
            _print_agent("Encerrando a conversa. Até mais.")
            return

        if command == "--trace":
            trace_enabled = not trace_enabled
            status = "ativado" if trace_enabled else "desativado"
            _print_success(f"Modo trace {status}.")
            continue

        intent_data, context_data, analysis, response, failed_stage = _run_chat_step(
            message,
            session_state,
        )
        _print_agent(response)
        _register_assistant_message(response, session_state)

        if trace_enabled:
            _print_chat_trace(
                intent_data,
                context_data,
                analysis,
                session_state,
                failed_stage,
            )


def _run_chat_step(
    message: str,
    session_state: dict,
) -> tuple[dict, dict, dict, str, str | None]:
    intent_data: dict = {}
    context_data: dict = {}
    analysis: dict = {}
    stage = "Agente 1"

    try:
        intent_data = interpret_user_message(message)
        stage = "Agente 2"
        context_data = build_context_and_collect(message, intent_data, session_state)
        stage = "Agente 3"
        analysis = analyze_process_context(message, context_data)
        stage = "Agente 4"
        response = create_user_response(message, analysis)
    except Exception:
        return intent_data, context_data, analysis, SAFE_CHAT_ERROR_RESPONSE, stage

    return intent_data, context_data, analysis, response, None


def _register_assistant_message(response: str, session_state: dict) -> None:
    conversation = session_state.setdefault("conversation", [])
    conversation.append(
        {
            "role": "assistant",
            "message": response,
        }
    )
    del conversation[:-MAX_CONVERSATION_ENTRIES]


def _print_chat_trace(
    intent_data: dict,
    context_data: dict,
    analysis: dict,
    session_state: dict,
    failed_stage: str | None,
) -> None:
    _print_trace("[Trace]")
    if failed_stage is not None:
        _print_error(f"Falha: {failed_stage}")
    _print_trace(f"Intent: {_safe_trace_text(intent_data.get('intent'))}")
    _print_trace(
        f"Collection status: {_safe_trace_text(context_data.get('collection_status'))}"
    )
    _print_trace(
        f"Processo ativo: {_active_process_number_for_trace(context_data, session_state)}"
    )
    _print_trace(f"Analysis type: {_safe_trace_text(analysis.get('analysis_type'))}")


def _active_process_number_for_trace(context_data: dict, session_state: dict) -> str:
    active_process = context_data.get("active_process")
    if not isinstance(active_process, dict) or not active_process:
        active_process = session_state.get("active_process")

    if not isinstance(active_process, dict):
        return "nenhum"

    process_data = active_process.get("processo")
    if not isinstance(process_data, dict):
        return "nenhum"

    process_number = process_data.get("numero")
    if not isinstance(process_number, str) or not process_number.strip():
        return "nenhum"

    return process_number.strip()


def _active_process_normalized_number(session_state: dict) -> str | None:
    active_process = session_state.get("active_process")
    if not isinstance(active_process, dict):
        return None

    process_data = active_process.get("processo")
    if not isinstance(process_data, dict):
        return None

    process_number = process_data.get("numero_normalizado")
    if not isinstance(process_number, str) or not process_number.strip():
        return None

    return process_number.strip()


def _active_process_status(
    active_process_before: str | None,
    active_process_after: str | None,
) -> str:
    if active_process_before is None and active_process_after is None:
        return "ausente"
    if active_process_before is None:
        return "carregado"
    if active_process_before == active_process_after:
        return "preservado"
    if active_process_after is None:
        return "removido"
    return "substituido"


def _safe_trace_text(value: object) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "unknown"


def _force_deterministic_model_fallbacks() -> None:
    def _raise_unavailable(*_args, **_kwargs) -> None:
        raise OllamaConnectionError("Geracao local desativada nesta validacao.")

    agent1_intent_module.generate_text = _raise_unavailable
    agent3_process_analysis_module.generate_text = _raise_unavailable


def _print_agent4_trace(
    index: int,
    intent_data: dict,
    context_data: dict,
    analysis: dict,
) -> None:
    facts = analysis.get("facts")
    if not isinstance(facts, list):
        facts = []

    limitations = analysis.get("limitations")
    if not isinstance(limitations, list):
        limitations = []

    fact_labels = [
        str(fact.get("label")).strip()
        for fact in facts
        if isinstance(fact, dict) and str(fact.get("label")).strip()
    ]
    privacy_status = (
        "sim" if cpf_cnpj_removed_from_model_context(context_data) else "não"
    )
    active_process_status = "sim" if context_data.get("active_process") else "não"

    _print_trace(f"Trace etapa {index}:")
    _print_trace(
        "  Intenção: "
        f"{intent_data.get('intent')} | confiança: {intent_data.get('confidence')}"
    )
    _print_trace(
        "  Coleta: "
        f"{context_data.get('collection_status')} | processo ativo: {active_process_status}"
    )
    _print_trace(
        "  Análise: "
        f"{analysis.get('analysis_type')} | fatos: {len(facts)} | limitações: {len(limitations)}"
    )
    if fact_labels:
        _print_trace(f"  Rótulos dos fatos: {', '.join(fact_labels)}")
    _print_trace(f"  Privacidade: documentos pessoais removidos: {privacy_status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot processual local.")
    parser.add_argument(
        "--check-ollama",
        action="store_true",
        help="Verifica a disponibilidade do Ollama local e do modelo configurado.",
    )
    parser.add_argument(
        "--smoke-ollama",
        action="store_true",
        help="Executa uma geração mínima usando o Ollama local.",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Inicia uma conversa contínua no terminal.",
    )
    parser.add_argument(
        "--test-agent1",
        metavar="MENSAGEM",
        help="Executa uma interpretacao isolada da mensagem pelo Agente 1.",
    )
    parser.add_argument(
        "--test-agent2",
        metavar="MENSAGEM",
        help="Executa Agente 1 e Agente 2 para uma mensagem isolada.",
    )
    parser.add_argument(
        "--test-agent2-sequence",
        action="store_true",
        help="Executa uma sequencia fixa de validacao do Agente 2 na mesma sessao.",
    )
    parser.add_argument(
        "--test-agent3-sequence",
        action="store_true",
        help="Executa Agente 1, Agente 2 e Agente 3 em uma sequencia fixa na mesma sessao.",
    )
    parser.add_argument(
        "--test-agent4-sequence",
        action="store_true",
        help="Executa Agente 1, Agente 2, Agente 3 e Agente 4 em uma sequencia fixa na mesma sessao.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Exibe um resumo legivel dos agentes no teste do Agente 4.",
    )
    args = parser.parse_args()

    if args.check_ollama:
        _check_ollama()
        return

    if args.smoke_ollama:
        _smoke_ollama()
        return

    if args.chat:
        _run_chat()
        return

    if args.test_agent1 is not None:
        result = interpret_user_message(args.test_agent1)
        _print_json(result)
        return

    if args.test_agent2 is not None:
        session_state = create_session_state()
        result = _run_agent2_test(args.test_agent2, session_state)
        _print_json(result)
        return

    if args.test_agent2_sequence:
        session_state = create_session_state()
        results = [
            _run_agent2_sequence_step(message, session_state)
            for message in AGENT2_SEQUENCE_MESSAGES
        ]
        _print_json(results)
        return

    if args.test_agent3_sequence:
        session_state = create_session_state()
        results = []
        privacy_checks = []

        for index, message in enumerate(AGENT3_SEQUENCE_MESSAGES, start=1):
            context_data, analysis = _run_agent3_test_step(message, session_state)
            privacy_checks.append(cpf_cnpj_removed_from_model_context(context_data))
            results.append(
                {
                    "passo": index,
                    "mensagem": message,
                    "fluxo": "Agente 1 -> Agente 2 -> Agente 3",
                    "analise_agente3": analysis,
                }
            )

        _print_json(results)
        privacy_status = "sim" if all(privacy_checks) else "nao"
        _print_info(
            f"CPF/CNPJ removidos do contexto enviado ao modelo: {privacy_status}"
        )
        return

    if args.test_agent4_sequence:
        _force_deterministic_model_fallbacks()
        session_state = create_session_state()

        for index, message in enumerate(AGENT4_SEQUENCE_MESSAGES, start=1):
            intent_data, context_data, analysis, response = _run_agent4_test_step(
                message,
                session_state,
            )
            _print_user(message)
            _print_agent(response)
            if args.trace:
                _print_agent4_trace(index, intent_data, context_data, analysis)

        return

    create_session_state()
    _print_success("Base do chatbot processual inicializada.")


if __name__ == "__main__":
    main()
