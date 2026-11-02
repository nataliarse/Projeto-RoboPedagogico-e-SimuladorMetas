#!/usr/bin/env bash
# Instala o Ollama na instância e baixa os modelos usados pelo chatbot.
# A instância t3.medium tem 3,7 GB de RAM: cria-se 2 GB de swap como margem.
set -euo pipefail
BACK=/home/ubuntu/robo/chatbot_processual_ai

if ! command -v ollama >/dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
if [ ! -f /swapfile ]; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile >/dev/null
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi
sudo systemctl enable -q --now ollama
sleep 3
for modelo in llama3.2:1b llama3.2:3b nomic-embed-text; do
  ollama pull "$modelo" >/dev/null 2>&1 && echo "baixado: $modelo"
done

# o backend passa a usar o modelo de 3B e aguarda mais pela resposta (CPU de uso geral)
sed -i -e 's#^OLLAMA_MODEL=.*#OLLAMA_MODEL=llama3.2:3b#' \
       -e 's#^OLLAMA_TIMEOUT_SECONDS=.*#OLLAMA_TIMEOUT_SECONDS=240#' "$BACK/.env"
sudo systemctl restart robo-backend
ollama list
