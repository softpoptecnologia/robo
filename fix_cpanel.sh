#!/bin/bash
# Rode no servidor: bash fix_cpanel.sh

set -e
cd /home/ailson/robo.etegaranhuns.com.br

echo "=== 1. Atualizar codigo ==="
git pull origin main || true

echo "=== 2. Criar .htaccess (formato CloudLinux igual app aulas) ==="
cp -f htaccess.example .htaccess
chmod 644 .htaccess
ls -la .htaccess

echo "=== 3. Virtualenv e dependencias ==="
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/activate
pip install -r requirements.txt

echo "=== 4. Testar import Python ==="
python -c "from app import app; print('OK Flask app:', app)"

echo "=== 5. Pastas ==="
mkdir -p uploads tmp
chmod 775 uploads 2>/dev/null || true

echo ""
echo "PRONTO. Agora no cPanel:"
echo "  1. Setup Python App"
echo "  2. REMOVA o app antigo se existir"
echo "  3. CRIE NOVO:"
echo "     - Root: /home/ailson/robo.etegaranhuns.com.br"
echo "     - Startup: passenger_wsgi.py"
echo "     - Entry point: application"
echo "  4. Clique RESTART"
echo ""
echo "Teste: https://robo.etegaranhuns.com.br/login"
