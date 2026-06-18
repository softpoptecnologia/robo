#!/bin/bash
# Diagnostico completo — bash diagnose.sh
echo "========== DIAGNOSTICO ROBO =========="
echo "Data: $(date)"
echo ""

APP="/home/ailson/robo.etegaranhuns.com.br"
AULAS="/home/ailson/aulas.etegaranhuns.com.br"
VENV="/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/python"

cd "$APP" 2>/dev/null || { echo "ERRO: pasta $APP nao existe"; exit 1; }

echo "1. Pasta atual:"
pwd
ls -la
echo ""

echo "2. Python virtualenv:"
ls -la "$VENV" 2>&1 || echo "ERRO: python nao encontrado em $VENV"
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

echo "7. Teste Flask CLI:"
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

echo "9. stderr.log:"
tail -20 stderr.log 2>/dev/null || echo "vazio"
echo ""

echo "10. Subdominio — confira no cPanel se document root e:"
echo "    $APP"
echo "    OU $APP/public"
echo ""
echo "========== PROXIMO PASSO =========="
echo "No painel Python App:"
echo "  Startup file: minimal_wsgi.py"
echo "  Entry point:  application"
echo "  RESTART"
echo ""
echo "Se minimal_wsgi ainda der 503, o problema e 100% painel/htaccess."
echo "Copie o .htaccess da app AULAS:"
echo "  cp $AULAS/.htaccess $APP/.htaccess"
echo "  sed -i 's/aulas/robo/g' $APP/.htaccess"
