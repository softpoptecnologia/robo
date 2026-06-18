#!/bin/bash
# Copia configuracao da app AULAS (que funciona) para ROBO
# bash fix_from_aulas.sh

set -e
ROBO="/home/ailson/robo.etegaranhuns.com.br"
AULAS="/home/ailson/aulas.etegaranhuns.com.br"

echo "========== FIX FROM AULAS =========="

# 1. Verificar lswsgi (causa do 503)
echo "--- lswsgi no servidor ---"
ls -la /opt/alt/python311/bin/lswsgi 2>&1 || echo "ERRO: lswsgi 3.11 nao existe!"
ls -la /opt/alt/python313/bin/lswsgi 2>&1 || echo "lswsgi 3.13 nao existe (esperado)"
echo ""

# 2. Copiar .htaccess da aulas
echo "--- Copiando .htaccess da aulas ---"
cp "$AULAS/.htaccess" "$ROBO/.htaccess"
sed -i 's/aulas\.etegaranhuns/robo.etegaranhuns/g' "$ROBO/.htaccess"
sed -i 's/aulas/robo/g' "$ROBO/.htaccess"
echo "ROBO .htaccess:"
cat "$ROBO/.htaccess"
echo ""

# 3. Copiar passenger_wsgi stub (sem .py)
if [ -f "$AULAS/passenger_wsgi" ]; then
    echo "--- Copiando passenger_wsgi stub da aulas ---"
    cp "$AULAS/passenger_wsgi" "$ROBO/passenger_wsgi"
else
    echo "--- Usando passenger_wsgi_loader do repo ---"
    cp "$ROBO/passenger_wsgi_loader" "$ROBO/passenger_wsgi"
fi
chmod 755 "$ROBO/passenger_wsgi"
echo "Conteudo passenger_wsgi:"
cat "$ROBO/passenger_wsgi"
echo ""

# 4. Remover public/.htaccess duplicado (pode conflitar)
rm -f "$ROBO/public/.htaccess" 2>/dev/null && echo "Removido public/.htaccess duplicado"

# 5. Instalar deps no venv 3.11
echo "--- Instalando deps Python 3.11 ---"
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
cd "$ROBO"
pip install -r requirements.txt -q
python check_server.py
echo ""

# 6. Restart
touch "$ROBO/tmp/restart.txt"
echo > "$ROBO/stderr.log"

echo "========== CONFERIR NO PAINEL =========="
echo "Python: 3.11 (NAO 3.13)"
echo "Startup file: passenger_wsgi.py"
echo "Entry point: application"
echo ""
echo "Se ainda tiver arquivo 'passenger_wsgi' (sem .py), teste startup: passenger_wsgi"
echo ""
echo "RESTART no painel e teste:"
echo "  https://robo.etegaranhuns.com.br"
echo ""
echo "Se falhar, mande:"
echo "  tail -5 $ROBO/stderr.log"
