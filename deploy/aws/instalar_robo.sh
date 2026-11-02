#!/usr/bin/env bash
# Instala o Robô Orientador na instância (Ubuntu 22.04): backend em 127.0.0.1:8000 (systemd),
# interface servida pelo nginx na porta 7860, que também encaminha /api para o backend.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
APP=/home/ubuntu/robo
BACK=$APP/chatbot_processual_ai

echo "== pacotes do sistema"
sudo apt-get update -qq
sudo apt-get install -y -qq python3.10-venv nginx xvfb libgl1 libglib2.0-0 >/dev/null

echo "== ambiente Python"
python3 -m venv "$BACK/.venv"
"$BACK/.venv/bin/pip" install -q --upgrade pip
"$BACK/.venv/bin/pip" install -q -r "$BACK/requirements.txt"
"$BACK/.venv/bin/pip" install -q -e "$APP/entrada-de-dados[collect]"

echo "== navegador do coletor (Chromium do Playwright)"
sudo "$BACK/.venv/bin/python" -m playwright install-deps chromium >/dev/null
"$BACK/.venv/bin/python" -m playwright install chromium >/dev/null

echo "== configuração (.env)"
if [ ! -f "$BACK/.env" ]; then
  sed -e 's#^OLLAMA_BASE_URL=.*#OLLAMA_BASE_URL=http://127.0.0.1:11434#' \
      -e 's#^QDRANT_URL=.*#QDRANT_URL=http://127.0.0.1:6333#' \
      -e 's#^RAG_ENABLED=.*#RAG_ENABLED=false#' "$BACK/.env.example" > "$BACK/.env"
fi

echo "== serviço do backend"
sudo tee /etc/systemd/system/robo-backend.service >/dev/null <<EOF
[Unit]
Description=Robo Orientador - backend FastAPI
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=$BACK
# xvfb-run dá ao coletor uma tela virtual: ele abre o navegador com janela, e o servidor não tem tela
ExecStart=/usr/bin/xvfb-run -a $BACK/.venv/bin/python -m uvicorn api:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "== nginx na porta 7860"
sudo tee /etc/nginx/sites-available/robo >/dev/null <<'EOF'
server {
    listen 7860 default_server;
    root /home/ubuntu/robo/web;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF
sudo ln -sf /etc/nginx/sites-available/robo /etc/nginx/sites-enabled/robo
sudo rm -f /etc/nginx/sites-enabled/default
chmod o+x /home/ubuntu
sudo nginx -t

sudo systemctl daemon-reload
sudo systemctl enable -q --now robo-backend
sudo systemctl restart robo-backend nginx
sleep 6
echo "== verificação"
systemctl is-active robo-backend nginx
curl -s -m 10 http://127.0.0.1:8000/api/health; echo
curl -s -m 10 -o /dev/null -w "interface via 7860: %{http_code}\n" http://127.0.0.1:7860/
curl -s -m 10 http://127.0.0.1:7860/api/health; echo
free -h | head -2
