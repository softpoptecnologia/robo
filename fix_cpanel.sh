#!/bin/bash
# bash fix_cpanel.sh
set -e
cd /home/ailson/robo.etegaranhuns.com.br

echo "=== git pull ==="
git pull origin main

echo "=== .htaccess (igual app aulas, Python 3.13) ==="
cat > .htaccess << 'EOF'
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
PassengerBaseURI "/"
PassengerPython "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END
EOF
chmod 644 .htaccess
echo "--- conteudo .htaccess ---"
cat .htaccess

echo "=== dependencias ==="
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/activate
pip install -r requirements.txt -q

echo "=== teste python ==="
python check_server.py

echo "=== permissoes ==="
chmod 755 passenger_wsgi.py application.py 2>/dev/null || true
mkdir -p uploads tmp
chmod 775 uploads tmp 2>/dev/null || true
touch tmp/restart.txt

echo ""
echo "=== AGORA NO PAINEL ==="
echo "1. Edite o Python App robo.etegaranhuns.com.br"
echo "2. Startup file: passenger_wsgi.py"
echo "3. Entry point: application"
echo "4. Salve e clique RESTART"
echo ""
echo "Teste: https://robo.etegaranhuns.com.br/ping"
