#!/bin/bash
# Atualiza codigo — NAO mexe no .htaccess (cPanel gerencia)
set -e
cd /home/ailson/robo.etegaranhuns.com.br

git fetch origin main
git reset --hard origin/main

VENV="/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11"
if [ ! -x "$VENV/bin/python" ]; then
    echo "ERRO: virtualenv 3.11 nao existe. Crie o app Python 3.11 no painel."
    exit 1
fi

source "$VENV/bin/activate"
pip install -r requirements.txt -q
python check_server.py

mkdir -p tmp uploads
touch tmp/restart.txt 2>/dev/null || true

echo ""
echo "Codigo atualizado. Restart no painel Python App."
echo "Se der 503: bash nuclear_fix.sh"
