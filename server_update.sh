#!/bin/bash
# Atualiza o servidor ignorando alterações locais
# bash server_update.sh

set -e
cd /home/ailson/robo.etegaranhuns.com.br

echo "=== Descartar alterações locais e atualizar ==="
git fetch origin main
git reset --hard origin/main

echo "=== Criar .htaccess ==="
cat > .htaccess << 'EOF'
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
PassengerBaseURI "/"
PassengerPython "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END

SetEnv FLASK_DEBUG "1"
SetEnv DEBUG "1"
PassengerFriendlyErrorPages on
EOF
chmod 644 .htaccess

echo "=== Dependências ==="
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/activate
pip install -r requirements.txt -q

echo "=== Teste ==="
python check_server.py

echo "=== Restart Passenger ==="
mkdir -p tmp uploads
touch tmp/restart.txt
chmod 755 debug_wsgi.py passenger_wsgi.py application.py 2>/dev/null || true

echo ""
echo "PRONTO. Arquivos atualizados."
echo ""
echo "NO PAINEL PYTHON APP configure:"
echo "  Startup file: debug_wsgi.py"
echo "  Entry point:  application"
echo "  RESTART"
echo ""
echo "Abra: https://robo.etegaranhuns.com.br"
echo "Vai mostrar o diagnostico completo na tela."
