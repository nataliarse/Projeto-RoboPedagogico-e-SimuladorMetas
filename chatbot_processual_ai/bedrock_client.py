"""Cliente do Amazon Bedrock (API Converse) para a redação das respostas.

O modelo de linguagem apenas redige: os fatos (situação do processo, metas, movimento
determinante) chegam prontos no prompt, calculados pelas regras determinísticas.

Credenciais: cadeia padrão do boto3. Na EC2, o instance profile da instância; localmente,
o perfil configurado com ``aws configure``. Nenhuma chave fica no código.

Auditoria: cada chamada registra, em JSON Lines, o modelo, a latência, os tokens e o hash
SHA-256 do prompt e da resposta. O texto integral só é gravado com
``LLM_AUDIT_FULL_TEXT=true``, porque os prompts podem conter dados pessoais dos processos.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import (
    BEDROCK_EMBED_DIMENSIONS,
    BEDROCK_EMBED_MODEL_ID,
    BEDROCK_MAX_TOKENS,
    BEDROCK_MODEL_ID,
    BEDROCK_REGION,
    BEDROCK_TEMPERATURE,
    BEDROCK_TIMEOUT_SECONDS,
    LLM_AUDIT_FULL_TEXT,
    LLM_AUDIT_LOG,
)


class BedrockError(Exception):
    """Falha ao gerar texto no Bedrock (credencial, permissão, rede, limite ou resposta)."""


_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            import boto3
            from botocore.config import Config
        except ImportError as exc:  # pragma: no cover - depende do ambiente
            raise BedrockError("boto3 não está instalado.") from exc
        _client = boto3.client(
            "bedrock-runtime",
            region_name=BEDROCK_REGION,
            config=Config(
                connect_timeout=10,
                read_timeout=BEDROCK_TIMEOUT_SECONDS,
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )
    return _client


def generate_text(prompt: str, system_prompt: str | None = None) -> str:
    request: dict[str, Any] = {
        "modelId": BEDROCK_MODEL_ID,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": BEDROCK_MAX_TOKENS, "temperature": BEDROCK_TEMPERATURE},
    }
    if system_prompt:
        request["system"] = [{"text": system_prompt}]

    inicio = time.perf_counter()
    try:
        response = _get_client().converse(**request)
    except BedrockError:
        raise
    except Exception as exc:  # botocore: ClientError, EndpointConnectionError, ReadTimeout...
        _audit(prompt, system_prompt, None, inicio, status=f"erro: {type(exc).__name__}")
        raise BedrockError(f"Falha ao chamar o Bedrock ({type(exc).__name__}).") from exc

    text = _extract_text(response)
    _audit(prompt, system_prompt, text, inicio, status="ok", usage=response.get("usage"))
    return text


def embed_text(text: str) -> list[float]:
    """Vetor do texto pelo modelo de embeddings do Bedrock (Titan v2, normalizado)."""
    body = json.dumps({
        "inputText": text,
        "dimensions": BEDROCK_EMBED_DIMENSIONS,
        "normalize": True,
    })
    try:
        response = _get_client().invoke_model(
            modelId=BEDROCK_EMBED_MODEL_ID, body=body,
            contentType="application/json", accept="application/json",
        )
        data = json.loads(response["body"].read())
    except BedrockError:
        raise
    except Exception as exc:
        raise BedrockError(f"Falha ao gerar embedding no Bedrock ({type(exc).__name__}).") from exc
    vector = data.get("embedding") if isinstance(data, dict) else None
    if not isinstance(vector, list) or not vector:
        raise BedrockError("Resposta de embedding do Bedrock sem vetor.")
    return [float(v) for v in vector]


def _extract_text(response: dict[str, Any]) -> str:
    try:
        content = response["output"]["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise BedrockError("Resposta do Bedrock sem conteúdo.") from exc
    parts = [block["text"] for block in content if isinstance(block, dict) and isinstance(block.get("text"), str)]
    text = "".join(parts).strip()
    if not text:
        raise BedrockError("Resposta do Bedrock sem texto.")
    return text


def _sha256(text: str | None) -> str | None:
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text is not None else None


def _audit(prompt: str, system_prompt: str | None, text: str | None, inicio: float,
           status: str, usage: dict[str, Any] | None = None) -> None:
    if not LLM_AUDIT_LOG:
        return
    registro: dict[str, Any] = {
        "momento": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "provedor": "bedrock",
        "modelo": BEDROCK_MODEL_ID,
        "status": status,
        "latencia_ms": round((time.perf_counter() - inicio) * 1000),
        "tokens_entrada": (usage or {}).get("inputTokens"),
        "tokens_saida": (usage or {}).get("outputTokens"),
        "sha256_prompt": _sha256((system_prompt or "") + "\n" + prompt),
        "sha256_resposta": _sha256(text),
    }
    if LLM_AUDIT_FULL_TEXT:
        registro.update({"system": system_prompt, "prompt": prompt, "resposta": text})
    try:
        caminho = Path(LLM_AUDIT_LOG)
        if not caminho.is_absolute():
            caminho = Path(__file__).resolve().parent / caminho
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except OSError:
        pass  # a auditoria nunca derruba a resposta
