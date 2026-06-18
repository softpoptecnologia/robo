#!/bin/bash
# bash server_update.sh
set -e
cd /home/ailson/robo.etegaranhuns.com.br

git fetch origin main
git reset --hard origin/main

# .htaccess na raiz
cat > .htaccess << 'EOF'
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
PassengerBaseURI "/"
PassengerPython "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END
EOF
chmod 644 .htaccess

# .htaccess em public/ (se document root for public/)
mkdir -p public
cp .htaccess public/.htaccess 2>/dev/null || true

source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/activate
pip install -r requirements.txt -q
touch tmp/restart.txt 2>/dev/null || mkdir -p tmp && touch tmp/restart.txt

echo ""
echo "=== TESTE 1: minimal_wsgi.py no painel ==="
echo "Startup: minimal_wsgi.py | Entry: application | RESTART"
echo "Deve mostrar: PYTHON FUNCIONA - Passenger OK"
echo ""
echo "=== Se ainda 503, rode: bash diagnose.sh ==="
echo "=== E copie .htaccess da app aulas: ==="
echo "cp /home/ailson/aulas.etegaranhuns.com.br/.htaccess .htaccess"
echo "sed -i 's/aulas/robo/g' .htaccess"
