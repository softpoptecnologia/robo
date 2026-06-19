#!/bin/bash
# Deploy final — bash deploy.sh
set -e

APP="/home/ailson/robo.etegaranhuns.com.br"
AULAS="/home/ailson/aulas.etegaranhuns.com.br"
VENV="/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11"

cd "$APP"
git pull origin main

# Remove conflitos
rm -rf public
rm -f passenger_wsgi htaccess

# .htaccess = copia exata da aulas
cp "$AULAS/.htaccess" .htaccess
sed -i 's/aulas\.etegaranhuns\.com\.br/robo.etegaranhuns.com.br/g' .htaccess
chmod 644 .htaccess

# Se aulas tem passenger_wsgi (sem .py), copia tambem
if [ -f "$AULAS/passenger_wsgi" ]; then
    cp "$AULAS/passenger_wsgi" passenger_wsgi
    sed -i 's/aulas\.etegaranhuns\.com\.br/robo.etegaranhuns.com.br/g' passenger_wsgi
    sed -i 's/aulas/robo/g' passenger_wsgi
    chmod 755 passenger_wsgi
    echo "Copiado passenger_wsgi da aulas"
fi

mkdir -p tmp uploads
chmod 775 tmp uploads
chmod 755 passenger_wsgi.py

source "$VENV/bin/activate"
pip install -r requirements.txt -q
python check_server.py

touch tmp/restart.txt
echo > stderr.log

echo ""
echo "=== PRONTO ==="
echo ""
echo "No painel, teste ESTA ORDEM:"
echo ""
if [ -f passenger_wsgi ]; then
    echo "  1) Startup: passenger_wsgi  | Entry: application"
    echo "  2) Se falhar: Startup: passenger_wsgi.py | Entry: application"
else
    echo "  Startup: passenger_wsgi.py | Entry: application"
fi
echo ""
echo "RESTART e teste /ping"
echo ""
echo "Se falhar: bash compare_aulas.sh"
