"""
Ponto de entrada WSGI para hospedagem com Passenger (cPanel / pyserver).

O servidor procura a variável: application
"""

import os
import sys

# Pasta do projeto no servidor
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

# Virtualenv do cPanel (ajuste a versão 3.11 se o painel usar outra)
INTERP = os.path.join(
    os.environ.get("HOME", "/home/ailson"),
    "virtualenv",
    "robo.etegaranhuns.com.br",
    "3.11",
    "bin",
    "python3",
)
if os.path.isfile(INTERP) and sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

os.environ.setdefault("SECRET_KEY", "troque-em-producao")

from app import create_app

application = create_app()
