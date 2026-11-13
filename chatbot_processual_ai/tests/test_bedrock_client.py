import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bedrock_client
import ollama_client


class _FakeBedrock:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


def _resposta(texto="Texto redigido.", entrada=12, saida=5):
    return {
        "output": {"message": {"role": "assistant", "content": [{"text": texto}]}},
        "usage": {"inputTokens": entrada, "outputTokens": saida},
    }


class BedrockClientTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = Path(self.tmp.name) / "auditoria.jsonl"
        patcher = patch.object(bedrock_client, "LLM_AUDIT_LOG", str(self.log))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_envia_system_prompt_e_parametros_de_inferencia(self):
        fake = _FakeBedrock(_resposta())
        with patch.object(bedrock_client, "_get_client", return_value=fake):
            texto = bedrock_client.generate_text("FATOS: ...", system_prompt="Use apenas os fatos.")

        self.assertEqual(texto, "Texto redigido.")
        chamada = fake.calls[0]
        self.assertEqual(chamada["modelId"], bedrock_client.BEDROCK_MODEL_ID)
        self.assertEqual(chamada["system"], [{"text": "Use apenas os fatos."}])
        self.assertEqual(chamada["messages"][0]["content"][0]["text"], "FATOS: ...")
        self.assertLessEqual(chamada["inferenceConfig"]["temperature"], 0.2)

    def test_auditoria_registra_hash_e_nao_o_texto_por_padrao(self):
        fake = _FakeBedrock(_resposta("Resposta com NOME DA PARTE"))
        with patch.object(bedrock_client, "_get_client", return_value=fake):
            bedrock_client.generate_text("prompt com NOME DA PARTE")

        registro = json.loads(self.log.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(registro["status"], "ok")
        self.assertEqual(registro["tokens_entrada"], 12)
        self.assertEqual(len(registro["sha256_prompt"]), 64)
        self.assertNotIn("NOME DA PARTE", self.log.read_text(encoding="utf-8"))

    def test_falha_do_servico_vira_bedrock_error_e_e_auditada(self):
        fake = _FakeBedrock(error=RuntimeError("AccessDeniedException"))
        with patch.object(bedrock_client, "_get_client", return_value=fake):
            with self.assertRaises(bedrock_client.BedrockError):
                bedrock_client.generate_text("prompt")

        registro = json.loads(self.log.read_text(encoding="utf-8").splitlines()[0])
        self.assertTrue(registro["status"].startswith("erro"))

    def test_resposta_sem_texto_e_erro(self):
        fake = _FakeBedrock({"output": {"message": {"content": []}}})
        with patch.object(bedrock_client, "_get_client", return_value=fake):
            with self.assertRaises(bedrock_client.BedrockError):
                bedrock_client.generate_text("prompt")


class ProvedorDoModeloTestCase(unittest.TestCase):
    def test_bedrock_e_usado_quando_configurado(self):
        with patch.object(ollama_client, "LLM_PROVIDER", "bedrock"), \
                patch.object(bedrock_client, "generate_text", return_value="do bedrock") as bedrock, \
                patch.object(ollama_client, "_generate_with_ollama") as ollama:
            self.assertEqual(ollama_client.generate_text("p", system_prompt="s"), "do bedrock")
        bedrock.assert_called_once_with("p", system_prompt="s")
        ollama.assert_not_called()

    def test_falha_do_bedrock_recorre_ao_ollama(self):
        with patch.object(ollama_client, "LLM_PROVIDER", "bedrock"), \
                patch.object(ollama_client, "LLM_FALLBACK_OLLAMA", True), \
                patch.object(bedrock_client, "generate_text", side_effect=bedrock_client.BedrockError("x")), \
                patch.object(ollama_client, "_generate_with_ollama", return_value="do ollama"):
            self.assertEqual(ollama_client.generate_text("p"), "do ollama")

    def test_sem_fallback_a_falha_vira_ollama_error_para_a_resposta_deterministica(self):
        with patch.object(ollama_client, "LLM_PROVIDER", "bedrock"), \
                patch.object(ollama_client, "LLM_FALLBACK_OLLAMA", False), \
                patch.object(bedrock_client, "generate_text", side_effect=bedrock_client.BedrockError("x")), \
                patch.object(ollama_client, "_generate_with_ollama") as ollama:
            with self.assertRaises(ollama_client.OllamaError):
                ollama_client.generate_text("p")
        ollama.assert_not_called()

    def test_ollama_continua_sendo_o_padrao(self):
        with patch.object(ollama_client, "LLM_PROVIDER", "ollama"), \
                patch.object(bedrock_client, "generate_text") as bedrock, \
                patch.object(ollama_client, "_generate_with_ollama", return_value="local"):
            self.assertEqual(ollama_client.generate_text("p"), "local")
        bedrock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
