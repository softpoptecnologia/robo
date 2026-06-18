"""
Ponto de entrada WSGI para hospedagem com Passenger (cPanel / pyserver).

O servidor procura a variável: application
"""

import os
import sys
import traceback
from datetime import datetime

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(APP_ROOT, "error.log")

if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)


def _log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except OSError:
        pass


# Virtualenv do cPanel — tenta 3.11, 3.10 e 3.9
_home = os.environ.get("HOME", "/home/ailson")
_app_name = "robo.etegaranhuns.com.br"
for _ver in ("3.11", "3.10", "3.9", "3.8"):
    INTERP = os.path.join(_home, "virtualenv", _app_name, _ver, "bin", "python3")
    if os.path.isfile(INTERP):
        if sys.executable != INTERP:
            os.execl(INTERP, INTERP, *sys.argv)
        break

os.environ.setdefault("SECRET_KEY", "troque-em-producao")
os.environ.setdefault("FLASK_DEBUG", "1")

_log(f"Starting app — Python {sys.version} — cwd={os.getcwd()} — app_root={APP_ROOT}")

try:
    from app import create_app

    application = create_app()
    _log("Application loaded OK")
except Exception:
    _err = traceback.format_exc()
    _log(f"FAILED to load application:\n{_err}")

    def application(environ, start_response):
        start_response("500 Internal Server Error", [("Content-Type", "text/plain; charset=utf-8")])
        body = (
            "ERRO AO INICIAR A APLICACAO (modo debug)\n"
            "=====================================\n\n"
            + _err
            + f"\n\nLog salvo em: {LOG_FILE}\n"
            + f"Python: {sys.version}\n"
            + f"App root: {APP_ROOT}\n"
        )
        return [body.encode("utf-8")]
