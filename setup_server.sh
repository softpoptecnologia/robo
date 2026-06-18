#!/bin/bash
# Rode no servidor após git pull: bash setup_server.sh

set -e
cd "$(dirname "$0")"

echo "==> Pasta: $(pwd)"

if [ ! -f .htaccess ]; then
    cp htaccess.example .htaccess
    echo "OK: .htaccess criado"
else
    echo "OK: .htaccess já existe"
fi

chmod 644 .htaccess
mkdir -p uploads tmp
chmod 775 uploads 2>/dev/null || true

if [ -f requirements.txt ]; then
    pip install -r requirements.txt -q 2>/dev/null || echo "AVISO: rode pip install manualmente no virtualenv"
fi

if [ ! -f clube_robotica.db ]; then
    python seed.py --force 2>/dev/null || echo "AVISO: rode python seed.py --force manualmente"
fi

echo ""
echo "Pronto! Agora reinicie a aplicacao Python no cPanel."
echo "Teste: https://robo.etegaranhuns.com.br/login"
