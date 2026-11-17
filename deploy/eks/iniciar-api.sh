#!/bin/sh
# Inicia a tela virtual (o coletor abre o navegador com janela) e, em seguida, a API.
# Substitui o xvfb-run, que trava quando é o primeiro processo do container (PID 1).
set -e
Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp >/tmp/xvfb.log 2>&1 &
export DISPLAY=:99
for i in 1 2 3 4 5 6 7 8 9 10; do
  [ -e /tmp/.X11-unix/X99 ] && break
  sleep 0.5
done
exec python -m uvicorn api:app --host 127.0.0.1 --port 8000
