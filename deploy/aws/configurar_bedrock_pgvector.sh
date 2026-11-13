#!/usr/bin/env bash
# Passa o Robô Orientador a usar o Amazon Bedrock para redigir as respostas e o pgvector do
# banco da IESB para a busca no Glossário das Metas. Retira o Simulador de Metas da instância.
#
# Pré-requisitos (provisionados pela instituição):
#   - a role da instância pode chamar o Bedrock e ler o secret do banco (TCC_SECRET_ID);
#   - o egress da instância libera 443 (Bedrock e Secrets Manager) e 5432 (PostgreSQL).
# Nenhuma credencial é gravada: o boto3 usa o instance profile.
set -euo pipefail
APP=/home/ubuntu/robo
BACK=$APP/chatbot_processual_ai
ENV=$BACK/.env

definir() {  # definir CHAVE VALOR: troca a linha da chave no .env ou a acrescenta
  if grep -q "^$1=" "$ENV"; then sed -i "s#^$1=.*#$1=$2#" "$ENV"; else echo "$1=$2" >> "$ENV"; fi
}

echo "== dependências (boto3, psycopg)"
"$BACK/.venv/bin/pip" install -q -r "$BACK/requirements.txt"

echo "== configuração do modelo e da busca"
definir LLM_PROVIDER bedrock
definir LLM_FALLBACK_OLLAMA true
definir BEDROCK_MODEL_ID us.anthropic.claude-haiku-4-5-20251001-v1:0
definir BEDROCK_REGION us-east-1
definir LLM_AUDIT_LOG data/logs/llm_auditoria.jsonl
definir NORMAS_BACKEND pgvector
definir TCC_SECRET_ID tcc/leonardo-a-pereira/db
definir NORMAS_PG_SCHEMA tcc_leonardo_a_pereira
definir NORMAS_MIN_SCORE 0.30
# o fallback para o Ollama não deve segurar a resposta por minutos
definir OLLAMA_TIMEOUT_SECONDS 90
sed -i '/^SIMULATOR_API_URL=/d;/^SIMULATOR_TIMEOUT_SECONDS=/d;/simulador de metas/d' "$ENV"

echo "== teste do Bedrock com a role da instância"
cd "$BACK"
.venv/bin/python - <<'PY'
import bedrock_client
print("Bedrock:", bedrock_client.generate_text("Responda apenas: ok")[:40])
print("Embedding:", len(bedrock_client.embed_text("teste")), "dimensões")
PY

echo "== indexação do glossário no pgvector"
.venv/bin/python -m services.norma_rag

echo "== retirada do simulador de metas"
if systemctl list-unit-files robo-simulador.service >/dev/null 2>&1; then
  sudo systemctl disable -q --now robo-simulador || true
  sudo rm -f /etc/systemd/system/robo-simulador.service
  sudo systemctl daemon-reload
fi

echo "== nginx sem as rotas do simulador"
sudo tee /etc/nginx/sites-available/robo >/dev/null <<'EOF'
server {
    listen 7860 default_server;
    root /home/ubuntu/robo/web;
    index index.html;

    proxy_read_timeout 300s;
    proxy_send_timeout 300s;

    # mesmas rotas do proxy do Angular (frontend/proxy.conf.json)
    location = /api/processos/health {
        proxy_pass http://127.0.0.1:8000/api/health;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF
sudo nginx -t
sudo systemctl restart robo-backend nginx
sleep 6

echo "== verificação"
systemctl is-active robo-backend nginx
curl -s -m 10 http://127.0.0.1:7860/api/processos/health; echo
curl -s -m 10 -o /dev/null -w "simulador (esperado 404 ou 405): %{http_code}\n" http://127.0.0.1:7860/api/simulador/health
