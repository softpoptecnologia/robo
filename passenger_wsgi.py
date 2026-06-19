import os
import sys

# Forca o Python do virtualenv (padrao cPanel que funciona)
INTERP = "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/python"
if sys.executable != INTERP and os.path.isfile(INTERP):
    os.execl(INTERP, INTERP, *sys.argv)

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

# Garante que o venv esta no path (Flask instalado la)
SITE = "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/lib/python3.11/site-packages"
if os.path.isdir(SITE):
    sys.path.insert(0, SITE)

_app = None


def application(environ, start_response):
    global _app
    if _app is None:
        from app import create_app
        _app = create_app()
    return _app(environ, start_response)
