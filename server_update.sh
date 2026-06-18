#!/bin/bash
# bash server_update.sh
set -e
cd /home/ailson/robo.etegaranhuns.com.br

git fetch origin main
git reset --hard origin/main

# IMPORTANTE: usar Python 3.11 (3.13 nao tem lswsgi neste servidor)
cat > .htaccess << 'EOF'
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
PassengerBaseURI "/"
PassengerPython "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END
EOF
chmod 644 .htaccess
mkdir -p public && cp .htaccess public/.htaccess

echo "=== Instalar deps no Python 3.11 ==="
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
pip install -r requirements.txt -q
python check_server.py

touch tmp/restart.txt 2>/dev/null || mkdir -p tmp && touch tmp/restart.txt
echo ""
echo "PRONTO. No painel: RECRIE o app com Python 3.11 (nao 3.13)"
echo "Startup: passenger_wsgi.py | Entry: application"
