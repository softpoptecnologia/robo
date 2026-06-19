#!/bin/bash
# Compara ROBO com AULAS (que funciona) e corrige
# bash compare_aulas.sh

ROBO="/home/ailson/robo.etegaranhuns.com.br"
AULAS="/home/ailson/aulas.etegaranhuns.com.br"

echo "========== COMPARAR COM AULAS =========="
echo ""

echo "--- Arquivos WSGI na AULAS ---"
ls -la "$AULAS"/passenger* "$AULAS"/application* 2>/dev/null || true
echo ""
echo "--- Conteudo AULAS passenger_wsgi* ---"
for f in "$AULAS"/passenger_wsgi "$AULAS"/passenger_wsgi.py; do
    if [ -f "$f" ]; then
        echo ">>> $f"
        head -20 "$f"
        echo ""
    fi
done

echo "--- Arquivos WSGI no ROBO ---"
ls -la "$ROBO"/passenger* "$ROBO"/application* 2>/dev/null || true
echo ""
echo "--- Conteudo ROBO passenger_wsgi.py ---"
head -20 "$ROBO/passenger_wsgi.py" 2>/dev/null || echo "nao existe"
echo ""

echo "--- .htaccess ---"
echo "AULAS:"; cat "$AULAS/.htaccess" 2>/dev/null
echo ""
echo "ROBO:"; cat "$ROBO/.htaccess" 2>/dev/null
echo ""

echo "--- stderr.log ROBO (ultimas 20 linhas) ---"
tail -20 "$ROBO/stderr.log" 2>/dev/null || echo "vazio"
echo ""

echo "--- Teste import no venv ROBO ---"
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
cd "$ROBO"
python -c "
import sys, os
sys.path.insert(0, '.')
print('executable:', sys.executable)
import passenger_wsgi
print('application:', passenger_wsgi.application)
print('OK')
"
echo ""

echo "========== COPIE E MANDE =========="
echo "1. Saida completa deste script"
echo "2. No painel AULAS: qual Startup file? (passenger_wsgi ou passenger_wsgi.py)"
echo "3. No painel ROBO: qual Startup file esta configurado?"
