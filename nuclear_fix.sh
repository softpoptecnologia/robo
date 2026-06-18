#!/bin/bash
# Corrige 503 no LiteSpeed — NAO sobrescreve .htaccess (cPanel gera isso)
# bash nuclear_fix.sh

set -e
ROBO="/home/ailson/robo.etegaranhuns.com.br"
AULAS="/home/ailson/aulas.etegaranhuns.com.br"
VENV="/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11"

echo "========== NUCLEAR FIX =========="
cd "$ROBO"

echo ""
echo "1. Qual Python tem lswsgi (o binario que o LiteSpeed usa)?"
for v in 38 39 310 311 312 313; do
    if [ -x "/opt/alt/python${v}/bin/lswsgi" ]; then
        echo "   OK  python${v}"
    else
        echo "   --- python${v} (nao existe)"
    fi
done

echo ""
echo "2. Limpando lixo que quebra o Passenger..."
find "$ROBO" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
rm -rf "$ROBO/tmp"
rm -f "$ROBO/passenger_wsgi" "$ROBO/stderr.log" "$ROBO/htaccess"
rm -f "$ROBO/public/.htaccess"
mkdir -p "$ROBO/tmp" "$ROBO/uploads"
chmod 775 "$ROBO/tmp" "$ROBO/uploads" 2>/dev/null || true

echo ""
echo "3. Atualizando codigo (sem mexer no .htaccess)..."
git fetch origin main
git checkout -- passenger_wsgi.py application.py 2>/dev/null || true
git pull origin main

echo ""
echo "4. Dependencias Python 3.11..."
if [ ! -x "$VENV/bin/python" ]; then
    echo "   ERRO: virtualenv 3.11 nao existe em $VENV"
    echo "   Crie o app Python 3.11 no painel PRIMEIRO, depois rode este script de novo."
    exit 1
fi
source "$VENV/bin/activate"
pip install -r requirements.txt -q
python check_server.py

echo ""
echo "5. .htaccess atual (gerado pelo cPanel — NAO editar manualmente):"
if [ -f .htaccess ]; then
    cat .htaccess
else
    echo "   (nao existe — o painel cria ao registrar o app Python)"
fi

echo ""
echo "6. Comparar com AULAS (que funciona):"
if [ -f "$AULAS/.htaccess" ]; then
    echo "   --- AULAS ---"
    cat "$AULAS/.htaccess"
fi

echo ""
echo "7. Registro CloudLinux (se disponivel):"
if command -v cloudlinux-selector >/dev/null 2>&1; then
    cloudlinux-selector get --json --interpreter python --user ailson 2>/dev/null | python3 -m json.tool 2>/dev/null || \
    cloudlinux-selector get --json --interpreter python --user ailson 2>/dev/null || echo "   (sem permissao)"
else
    echo "   cloudlinux-selector nao disponivel"
fi

echo ""
echo "========== FACA NO PAINEL (ordem exata) =========="
echo ""
echo "  A) APAGUE o app Python de robo.etegaranhuns.com.br"
echo "  B) CRIE de novo:"
echo "       Python: 3.11"
echo "       Root:   $ROBO"
echo "       URL:    robo.etegaranhuns.com.br"
echo "       Startup: passenger_wsgi.py"
echo "       Entry:   application"
echo "  C) Clique CREATE — o painel gera o .htaccess"
echo "  D) Clique RESTART"
echo ""
echo "  NAO rode fix_cpanel.sh nem server_update.sh depois disso!"
echo ""
echo "========== TESTE =========="
echo "  https://robo.etegaranhuns.com.br/index.html  -> HTML estatico"
echo "  https://robo.etegaranhuns.com.br/ping          -> pong"
echo ""
echo "Se index.html OK mas /ping 503, mande:"
echo "  tail -10 $ROBO/stderr.log"
echo "  cat $ROBO/.htaccess"
