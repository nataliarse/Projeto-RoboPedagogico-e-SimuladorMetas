import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_MODEL_SELECTION = os.getenv("OLLAMA_MODEL_SELECTION", "auto")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "sim"}


# Provedor do modelo de linguagem: "ollama" (local) ou "bedrock" (Amazon Bedrock).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
# Com o Bedrock como provedor, recorre ao Ollama local se o Bedrock falhar.
LLM_FALLBACK_OLLAMA = _flag("LLM_FALLBACK_OLLAMA", "true")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
BEDROCK_TEMPERATURE = float(os.getenv("BEDROCK_TEMPERATURE", "0.2"))
BEDROCK_MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", "1024"))
BEDROCK_TIMEOUT_SECONDS = float(os.getenv("BEDROCK_TIMEOUT_SECONDS", "60"))
BEDROCK_EMBED_MODEL_ID = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
BEDROCK_EMBED_DIMENSIONS = int(os.getenv("BEDROCK_EMBED_DIMENSIONS", "1024"))

# Busca nas normas (glossário das metas): "qdrant" (local) ou "pgvector" (banco da IESB).
NORMAS_BACKEND = os.getenv("NORMAS_BACKEND", "qdrant").strip().lower()
# Conexão do pgvector: URL explícita (uso local) ou secret do Secrets Manager (EC2).
NORMAS_PG_URL = os.getenv("NORMAS_PG_URL", "").strip()
TCC_SECRET_ID = os.getenv("TCC_SECRET_ID", "tcc/leonardo-a-pereira/db").strip()
NORMAS_PG_SCHEMA = os.getenv("NORMAS_PG_SCHEMA", "tcc_leonardo_a_pereira").strip()
# Similaridade mínima no pgvector (Titan v2): trechos pertinentes ficaram entre 0,43 e 0,67
# e um texto sem relação, abaixo de 0,15, na calibração com o glossário de 2026.
NORMAS_MIN_SCORE = float(os.getenv("NORMAS_MIN_SCORE", "0.30"))

# Registro de auditoria das chamadas ao modelo (JSON Lines); vazio desativa.
LLM_AUDIT_LOG = os.getenv("LLM_AUDIT_LOG", "data/logs/llm_auditoria.jsonl").strip()
LLM_AUDIT_FULL_TEXT = _flag("LLM_AUDIT_FULL_TEXT", "false")

# Paths relativos são resolvidos pelo repositório em relação a este módulo,
# nunca ao diretório corrente do processo (ver process_repository.database_path).
LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "data/processual.sqlite3")
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "sim",
}
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "processual_chunks")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.35"))
