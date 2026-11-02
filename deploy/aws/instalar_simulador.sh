#!/usr/bin/env bash
# Instala o Simulador de Metas na instância e atualiza o nginx para as rotas da integração.
#
# O simulador fixa pandas 3 e numpy 2.4, que exigem Python 3.11 ou mais novo; o Ubuntu 22.04
# traz o 3.10. Por isso o Python 3.12 é instalado pelo uv, só para o ambiente do simulador.
# O simulador também fixa Pydantic 1, incompatível com o chatbot: os ambientes são separados.
set -euo pipefail
APP=/home/ubuntu/robo
SIM=$APP/simulador_metas_cnj
BACK=$APP/chatbot_processual_ai

echo "== Python 3.12 (uv)"
if ! command -v uv >/dev/null && [ ! -x "$HOME/.local/bin/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null
fi
UV="$(command -v uv || echo "$HOME/.local/bin/uv")"
"$UV" python install 3.12 >/dev/null

echo "== ambiente do simulador"
rm -rf "$SIM/.venv"
"$UV" venv --python 3.12 "$SIM/.venv" >/dev/null
"$UV" pip install --python "$SIM/.venv/bin/python" -q -r "$SIM/requirements.txt"
[ -f "$SIM/.env" ] || cp "$SIM/.env.example" "$SIM/.env"
sed -i 's#^SIMULADOR_RELOAD=.*#SIMULADOR_RELOAD=false#' "$SIM/.env"

echo "== chatbot aponta para o simulador local"
grep -q '^SIMULATOR_API_URL=' "$BACK/.env" || cat >> "$BACK/.env" <<'EOF'

# Backend do simulador de metas, na própria instância
SIMULATOR_API_URL=http://127.0.0.1:8001
SIMULATOR_TIMEOUT_SECONDS=20
EOF

echo "== serviço do simulador"
sudo tee /etc/systemd/system/robo-simulador.service >/dev/null <<EOF
[Unit]
Description=Robo Orientador - simulador de metas (FastAPI)
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=$SIM
ExecStart=$SIM/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8001
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "== nginx: mesmas rotas do proxy do Angular (frontend/proxy.conf.json)"
sudo tee /etc/nginx/sites-available/robo >/dev/null <<'EOF'
server {
    listen 7860 default_server;
    root /home/ubuntu/robo/web;
    index index.html;

    proxy_read_timeout 300s;
    proxy_send_timeout 300s;

    # healthcheck do chatbot: /api/processos/health -> /api/health
    location = /api/processos/health {
        proxy_pass http://127.0.0.1:8000/api/health;
    }
    location /api/processos/ {
        proxy_pass http://127.0.0.1:8000;
    }
    location /api/metas/ {
        proxy_pass http://127.0.0.1:8000;
    }
    # simulador: remove o prefixo /api/simulador e entrega /api/... na porta 8001
    location /api/simulador/ {
        proxy_pass http://127.0.0.1:8001/api/;
    }
    location = /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
    }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF
sudo nginx -t

sudo systemctl daemon-reload
sudo systemctl enable -q --now robo-simulador
sudo systemctl restart robo-simulador robo-backend nginx
sleep 6
echo "== verificação"
systemctl is-active robo-backend robo-simulador nginx ollama qdrant | tr '\n' ' '; echo
curl -s -m 10 http://127.0.0.1:7860/api/processos/health; echo
curl -s -m 10 http://127.0.0.1:7860/api/simulador/health; echo
