from __future__ import annotations

import asyncio
import json
import unittest
from dataclasses import asdict
from unittest.mock import patch
from uuid import UUID

import api
from schemas.processual_contracts import ProcessualChatResponse, ProcessualChatStepResult


class ASGIResponse:
    def __init__(self, status_code: int, headers: dict[str, str], content: bytes):
        self.status_code = status_code
        self.headers = headers
        self.content = content

    def json(self) -> object:
        return json.loads(self.content)


def asgi_request(
    method: str,
    path: str,
    payload: object,
    *,
    raise_server_exceptions: bool = True,
) -> ASGIResponse:
    body = json.dumps(payload).encode("utf-8")
    messages = [
        {
            "type": "http.request",
            "body": body,
            "more_body": False,
        }
    ]
    response_messages: list[dict] = []

    async def receive() -> dict:
        if messages:
            return messages.pop(0)
        return {"type": "http.disconnect"}

    async def send(message: dict) -> None:
        response_messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"host", b"testserver"),
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode("ascii")),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    try:
        asyncio.run(api.app(scope, receive, send))
    except Exception:
        if raise_server_exceptions:
            raise

    start = next(message for message in response_messages if message["type"] == "http.response.start")
    content = b"".join(
        message.get("body", b"")
        for message in response_messages
        if message["type"] == "http.response.body"
    )
    headers = {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in start["headers"]
    }
    return ASGIResponse(start["status"], headers, content)


def step_result(response: ProcessualChatResponse) -> ProcessualChatStepResult:
    return ProcessualChatStepResult(
        response=response,
        intent_data={},
        context_data={},
        analysis={},
    )


class ProcessualChatHTTPTestCase(unittest.TestCase):
    def setUp(self) -> None:
        api._SESSIONS.clear()

    def tearDown(self) -> None:
        api._SESSIONS.clear()

    def test_health_reports_only_api_availability_without_touching_sessions(self) -> None:
        existing_state = api._get_session_state("sessao-existente")
        sessions_before = dict(api._SESSIONS)

        response = asgi_request("GET", "/api/health", {})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(api._SESSIONS, sessions_before)
        self.assertIs(api._SESSIONS["sessao-existente"], existing_state)

    def test_processual_chat_returns_contract_response(self) -> None:
        process_number = "0011000-82.1981.5.18.0051"
        controlled_result = step_result(
            ProcessualChatResponse(
                tipo="processual_chat",
                intent="process_lookup",
                resposta="Processo localizado com sucesso.",
                processo_ativo=process_number,
                collection_status="success",
                failed_stage=None,
                rag_status="not_needed",
                fontes=[],
            )
        )

        with patch("api.run_processual_chat_step", return_value=controlled_result):
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": " teste-sessao-a ", "mensagem": "Consulte o processo"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        payload = response.json()
        self.assertEqual(payload["session_id"], "teste-sessao-a")
        result = payload["resultado"]
        self.assertEqual(
            set(asdict(controlled_result.response)),
            set(result),
        )
        self.assertEqual(result["tipo"], "processual_chat")
        self.assertIsInstance(result["resposta"], str)
        self.assertTrue(result["resposta"].strip())
        self.assertEqual(result["processo_ativo"], process_number)
        self.assertIsNone(result["failed_stage"])
        self.assertIsInstance(result["fontes"], list)

    def test_processual_chat_preserves_explicit_session_context(self) -> None:
        process_number = "0011000-82.1981.5.18.0051"
        received_states: list[dict] = []

        def controlled_step(message: str, session_state: dict) -> ProcessualChatStepResult:
            received_states.append(session_state)
            if message == "Consulte o processo":
                session_state["active_process"] = {
                    "processo": {"numero": process_number}
                }
            active_process = session_state.get("active_process")
            active_number = (
                active_process.get("processo", {}).get("numero")
                if isinstance(active_process, dict)
                else None
            )
            return step_result(
                ProcessualChatResponse(
                    tipo="processual_chat",
                    intent="process_question",
                    resposta="Contexto da sessão preservado.",
                    processo_ativo=active_number,
                    collection_status="not_needed",
                    failed_stage=None,
                    rag_status="not_needed",
                    fontes=[],
                )
            )

        with patch("api.run_processual_chat_step", side_effect=controlled_step):
            first = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": "teste-sessao-a", "mensagem": "Consulte o processo"},
            )
            second = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": "teste-sessao-a", "mensagem": "Qual foi a movimentação?"},
            )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertIs(received_states[0], received_states[1])
        self.assertEqual(second.json()["session_id"], "teste-sessao-a")
        self.assertEqual(second.json()["resultado"]["processo_ativo"], process_number)

    def test_processual_chat_without_session_id_creates_independent_contexts(self) -> None:
        processes = {
            "Consulte A": "0011000-82.1981.5.18.0051",
            "Consulte B": "0000001-02.2003.5.10.0001",
        }

        def controlled_step(message: str, session_state: dict) -> ProcessualChatStepResult:
            if message in processes:
                session_state["active_process"] = {
                    "processo": {"numero": processes[message]}
                }
            active_process = session_state.get("active_process")
            active_number = (
                active_process.get("processo", {}).get("numero")
                if isinstance(active_process, dict)
                else None
            )
            return step_result(
                ProcessualChatResponse(
                    tipo="processual_chat",
                    intent="process_question",
                    resposta="Contexto isolado.",
                    processo_ativo=active_number,
                    collection_status="not_needed",
                    failed_stage=None,
                    rag_status="not_needed",
                    fontes=[],
                )
            )

        with patch("api.run_processual_chat_step", side_effect=controlled_step):
            first_a = asgi_request(
                "POST", "/api/processos/chat", {"mensagem": "Consulte A"}
            )
            first_b = asgi_request(
                "POST", "/api/processos/chat", {"mensagem": "Consulte B"}
            )
            session_a = first_a.json()["session_id"]
            session_b = first_b.json()["session_id"]
            second_a = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": session_a, "mensagem": "Continue A"},
            )
            second_b = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": session_b, "mensagem": "Continue B"},
            )

        self.assertEqual(UUID(session_a).version, 4)
        self.assertEqual(UUID(session_b).version, 4)
        self.assertNotEqual(session_a, session_b)
        self.assertIsNot(api._SESSIONS[session_a], api._SESSIONS[session_b])
        self.assertEqual(
            second_a.json()["resultado"]["processo_ativo"], processes["Consulte A"]
        )
        self.assertEqual(
            second_b.json()["resultado"]["processo_ativo"], processes["Consulte B"]
        )

    def test_processual_chat_generates_session_for_each_unusable_id_form(self) -> None:
        controlled_result = step_result(
            ProcessualChatResponse(
                tipo="processual_chat",
                intent="general_question",
                resposta="Sessão criada.",
                processo_ativo=None,
                collection_status="not_needed",
                failed_stage=None,
                rag_status="not_needed",
                fontes=[],
            )
        )
        payloads = (
            {"mensagem": "Sem ID"},
            {"session_id": None, "mensagem": "ID nulo"},
            {"session_id": "", "mensagem": "ID vazio"},
            {"session_id": "   ", "mensagem": "ID com espaços"},
        )

        with patch("api.run_processual_chat_step", return_value=controlled_result):
            session_ids = [
                asgi_request("POST", "/api/processos/chat", payload).json()["session_id"]
                for payload in payloads
            ]

        self.assertEqual(len(set(session_ids)), len(payloads))
        for session_id in session_ids:
            self.assertEqual(UUID(session_id).version, 4)

    def test_processual_chat_preserves_unknown_explicit_id_after_state_loss(self) -> None:
        session_id = "session-explicita-apos-restart"
        stale_state = api._get_session_state(session_id)
        stale_state["active_process"] = {
            "processo": {"numero": "0011000-82.1981.5.18.0051"}
        }
        api._SESSIONS.clear()
        received_states: list[dict] = []

        def controlled_step(message: str, session_state: dict) -> ProcessualChatStepResult:
            received_states.append(session_state)
            return step_result(
                ProcessualChatResponse(
                    tipo="processual_chat",
                    intent="process_question",
                    resposta="Novo contexto vazio.",
                    processo_ativo=None,
                    collection_status="not_needed",
                    failed_stage=None,
                    rag_status="not_needed",
                    fontes=[],
                )
            )

        with patch("api.run_processual_chat_step", side_effect=controlled_step):
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": session_id, "mensagem": "Continue"},
            )

        self.assertEqual(response.json()["session_id"], session_id)
        self.assertIn(session_id, api._SESSIONS)
        self.assertIs(received_states[0], api._SESSIONS[session_id])
        self.assertIsNot(received_states[0], stale_state)
        self.assertIsNone(received_states[0]["active_process"])
        self.assertEqual(received_states[0]["last_intent"], None)

    def test_processual_chat_rejects_structurally_invalid_payload(self) -> None:
        response = asgi_request(
            "POST",
            "/api/processos/chat",
            {"session_id": "teste-sessao-a"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        payload = response.json()
        self.assertIsInstance(payload["detail"], list)
        self.assertNotIn("resultado", payload)

    def test_processual_chat_rejects_null_message_without_creating_session(self) -> None:
        sessions_before = dict(api._SESSIONS)

        response = asgi_request(
            "POST",
            "/api/processos/chat",
            {"session_id": "teste-sessao-null", "mensagem": None},
        )

        self.assertEqual(response.status_code, 422)
        self.assertNotIn("resultado", response.json())
        self.assertEqual(api._SESSIONS, sessions_before)

    def test_processual_chat_rejects_empty_message_without_calling_orchestrator(self) -> None:
        sessions_before = dict(api._SESSIONS)

        with patch("api.run_processual_chat_step") as orchestrator:
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": "teste-sessao-vazia", "mensagem": ""},
            )

        self.assertEqual(response.status_code, 422)
        self.assertNotIn("resultado", response.json())
        orchestrator.assert_not_called()
        self.assertEqual(api._SESSIONS, sessions_before)

    def test_processual_chat_rejects_whitespace_only_message(self) -> None:
        with patch("api.run_processual_chat_step") as orchestrator:
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"mensagem": "   \t\n\r"},
            )

        self.assertEqual(response.status_code, 422)
        orchestrator.assert_not_called()

    def test_processual_chat_preserves_valid_message_whitespace(self) -> None:
        controlled_result = step_result(
            ProcessualChatResponse(
                tipo="processual_chat",
                intent="general_question",
                resposta="Mensagem recebida.",
                processo_ativo=None,
                collection_status="not_needed",
                failed_stage=None,
                rag_status="not_needed",
                fontes=[],
            )
        )
        message = "  explique este processo  "

        with patch(
            "api.run_processual_chat_step", return_value=controlled_result
        ) as orchestrator:
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": "teste-sessao-valida", "mensagem": message},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(orchestrator.call_args.args[0], message)

    def test_processual_chat_missing_number_remains_functional_result(self) -> None:
        controlled_result = step_result(
            ProcessualChatResponse(
                tipo="processual_chat",
                intent="process_lookup",
                resposta="Informe o número do processo.",
                processo_ativo=None,
                collection_status="missing_number",
                failed_stage=None,
                rag_status="not_needed",
                fontes=[],
            )
        )

        with patch("api.run_processual_chat_step", return_value=controlled_result):
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"mensagem": "Consulte um processo"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["resultado"]["collection_status"], "missing_number"
        )
        self.assertTrue(response.json()["resultado"]["resposta"].strip())

    def test_processual_chat_controlled_failure_is_safe(self) -> None:
        technical_marker = (
            "SECRET_TEST_VALUE token-test-value Traceback "
            "C:\\Users\\test-user\\private /home/test-user/private"
        )

        with patch(
            "orchestrators.processual_chat_orchestrator.interpret_user_message",
            side_effect=RuntimeError(technical_marker),
        ):
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"session_id": "teste-sessao-falha", "mensagem": "Teste controlado"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["session_id"], "teste-sessao-falha")
        result = payload["resultado"]
        self.assertEqual(result["failed_stage"], "Agente 1")
        self.assertIsInstance(result["resposta"], str)
        self.assertTrue(result["resposta"].strip())
        public_response = response.content.decode("utf-8")
        for forbidden in (
            "SECRET_TEST_VALUE",
            "token-test-value",
            "Traceback",
            "C:\\Users\\test-user\\private",
            "/home/test-user/private",
        ):
            self.assertNotIn(forbidden, public_response)

    def test_processual_chat_unexpected_failure_returns_safe_500(self) -> None:
        technical_marker = "INTERNAL_TEST_MARKER"

        with patch(
            "api.run_processual_chat_step",
            side_effect=RuntimeError(technical_marker),
        ):
            response = asgi_request(
                "POST",
                "/api/processos/chat",
                {"mensagem": "Mensagem válida"},
                raise_server_exceptions=False,
            )

        self.assertEqual(response.status_code, 500)
        self.assertNotIn(technical_marker, response.content.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
