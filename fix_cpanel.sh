#!/bin/bash
# DEPRECADO — use nuclear_fix.sh
# Este script NAO sobrescreve mais o .htaccess (causava 503 com Python 3.13)
echo "AVISO: fix_cpanel.sh esta obsoleto."
echo "Rode: bash nuclear_fix.sh"
exec bash "$(dirname "$0")/nuclear_fix.sh"
