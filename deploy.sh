#!/bin/bash
# Deploy — copia config da app AULAS que funciona no mesmo servidor
# bash deploy.sh

set -e
APP="/home/ailson/robo.etegaranhuns.com.br"
AULAS="/home/ailson/aulas.etegaranhuns.com.br"
VENV="/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11"

echo "=== deploy robo ==="
cd "$APP"

echo "1. Atualizar codigo"
git pull origin main

echo "2. Remover arquivos que quebram o Passenger"
rm -rf public
rm -f passenger_wsgi htaccess

echo "3. .htaccess = copia da aulas (so troca o dominio)"
cp "$AULAS/.htaccess" .htaccess
sed -i 's/aulas\.etegaranhuns\.com\.br/robo.etegaranhuns.com.br/g' .htaccess
chmod 644 .htaccess

if [ -f "$AULAS/passenger_wsgi" ]; then
    echo "4. passenger_wsgi stub = copia da aulas"
    cp "$AULAS/passenger_wsgi" passenger_wsgi
    sed -i 's/aulas\.etegaranhuns\.com\.br/robo.etegaranhuns.com.br/g' passenger_wsgi
    chmod 755 passenger_wsgi
else
    echo "4. Sem stub passenger_wsgi na aulas (ok)"
fi

echo "5. Dependencias Python 3.11"
if [ ! -x "$VENV/bin/python" ]; then
    echo "ERRO: virtualenv 3.11 nao existe em $VENV"
    echo "No painel: crie app Python 3.11 para robo.etegaranhuns.com.br"
    exit 1
fi
source "$VENV/bin/activate"
pip install -r requirements.txt -q
python check_server.py

mkdir -p tmp uploads
touch tmp/restart.txt

echo ""
echo "=== .htaccess ==="
cat .htaccess
echo ""
echo "=== PRONTO ==="
echo "Painel: Startup passenger_wsgi.py | Entry application | RESTART"
echo "Teste: https://robo.etegaranhuns.com.br/ping"
