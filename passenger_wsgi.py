import sys
import os
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

LOG = os.path.join(BASE, "stderr.log")


def _log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except OSError:
        pass


try:
    from app import app as application
    _log("OK: app carregado")
except Exception:
    _err = traceback.format_exc()
    _log("ERRO ao importar app:\n" + _err)

    def application(environ, start_response):
        start_response("500 Internal Server Error", [("Content-Type", "text/html; charset=utf-8")])
        html = f"""<!DOCTYPE html><html><body style="font-family:monospace;padding:20px">
        <h1>Erro ao iniciar o Clube de Robótica</h1>
        <pre>{_err}</pre>
        <p>Log: {LOG}</p>
        <p>Rode no terminal: <code>python check_server.py</code></p>
        </body></html>"""
        return [html.encode("utf-8")]
