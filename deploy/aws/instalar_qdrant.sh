#!/usr/bin/env bash
# Instala o Qdrant (banco vetorial) como serviço e indexa o Glossário das Metas.
# Usa o binário estático (musl): o binário padrão exige glibc mais nova que a do Ubuntu 22.04.
set -euo pipefail
BACK=/home/ubuntu/robo/chatbot_processual_ai

if [ ! -x /opt/qdrant/qdrant ]; then
  cd /tmp
  curl -fsSL -o qdrant.tgz \
    https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-musl.tar.gz
  sudo mkdir -p /opt/qdrant /var/lib/qdrant
  sudo tar -xzf qdrant.tgz -C /opt/qdrant
  sudo chown -R ubuntu:ubuntu /var/lib/qdrant
  rm qdrant.tgz
fi

sudo tee /etc/systemd/system/qdrant.service >/dev/null <<'UNIT'
[Unit]
Description=Qdrant (banco vetorial do Robo Orientador)
After=network-online.target

[Service]
User=ubuntu
WorkingDirectory=/var/lib/qdrant
Environment=QDRANT__SERVICE__HOST=127.0.0.1
Environment=QDRANT__STORAGE__STORAGE_PATH=/var/lib/qdrant/storage
Environment=QDRANT__TELEMETRY_DISABLED=true
ExecStart=/opt/qdrant/qdrant
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable -q --now qdrant
sleep 5
systemctl is-active qdrant

# indexa as normas (exige o Ollama no ar, para gerar os embeddings)
cd "$BACK"
.venv/bin/python -m services.norma_rag
sudo systemctl restart robo-backend
