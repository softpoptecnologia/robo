#!/bin/bash
# Diagnostico completo — bash diagnose.sh
echo "========== DIAGNOSTICO ROBO =========="
echo "Data: $(date)"
echo ""

APP="/home/ailson/robo.etegaranhuns.com.br"
AULAS="/home/ailson/aulas.etegaranhuns.com.br"
VENV311="/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/python"
VENV313="/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/python"

cd "$APP" || exit 1

echo "1. Pasta: $APP"
pwd
echo ""

echo "2. Python virtualenv 3.11 (USE ESTE):"
ls -la "$VENV311" 2>&1 || echo "ERRO: 3.11 nao existe - recrie app no painel com Python 3.11"
echo ""
echo "2b. Python virtualenv 3.13 (NAO USAR - lswsgi quebrado):"
ls -la "$VENV313" 2>&1 || echo "nao existe"
echo ""

echo "3. .htaccess ROBO:"
cat .htaccess 2>/dev/null || echo "ERRO: .htaccess NAO EXISTE na raiz"
echo ""

echo "4. .htaccess AULAS (funciona):"
cat "$AULAS/.htaccess" 2>/dev/null || echo "aulas nao encontrado"
echo ""

echo "5. public/.htaccess:"
cat public/.htaccess 2>/dev/null || echo "nao existe"
echo ""

echo "6. Arquivos WSGI:"
ls -la *wsgi*.py application.py 2>/dev/null
echo ""

echo "7. Teste Flask CLI (3.11):"
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate 2>/dev/null || \
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/activate
python check_server.py 2>&1
echo ""

echo "8. Teste minimal_wsgi:"
python -c "
import sys; sys.path.insert(0,'.')
import minimal_wsgi
s=[]
minimal_wsgi.application({}, lambda st,h: s.append(st))
print('minimal_wsgi:', s)
"
echo ""

echo "9. stderr.log (procure lswsgi):"
tail -5 stderr.log 2>/dev/null || echo "vazio"
echo "   Se aparecer python313/lswsgi: RECRIE app com Python 3.11"
echo ""

echo "10. Subdominio — confira no cPanel se document root e:"
echo "    $APP"
echo "    OU $APP/public"
echo ""
echo "========== PROXIMO PASSO =========="
echo "APAGUE o app Python 3.13 e CRIE NOVO com Python 3.11"
echo "Startup: passenger_wsgi.py | Entry: application"
