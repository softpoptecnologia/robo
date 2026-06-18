import os
import sys
import traceback

# FORÇA DEBUG
os.environ["FLASK_DEBUG"] = "1"
os.environ["DEBUG"] = "1"

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

LOG = os.path.join(BASE, "stderr.log")


def _log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except OSError:
        pass


_err_html = None

try:
    from app import app as application
    application.config["DEBUG"] = True
    application.config["PROPAGATE_EXCEPTIONS"] = True
    application.config["TRAP_HTTP_EXCEPTIONS"] = True
    _log("OK passenger_wsgi carregou app")

    @application.errorhandler(Exception)
    def _show_all_errors(e):
        from flask import Response
        tb = traceback.format_exc()
        _log("REQUEST ERROR:\n" + tb)
        return Response(
            f"<h1>ERRO DEBUG</h1><pre>{tb}</pre>",
            status=500,
            mimetype="text/html",
        )

except Exception:
    _tb = traceback.format_exc()
    _log("FALHA IMPORT:\n" + _tb)
    _err_html = _tb

    def application(environ, start_response):
        start_response("500 Internal Server Error", [("Content-Type", "text/html; charset=utf-8")])
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>ERRO DEBUG</title></head><body style="background:#111;color:#0f0;font-family:monospace;padding:20px">
        <h1 style="color:red">ERRO AO INICIAR FLASK</h1>
        <pre style="white-space:pre-wrap;font-size:14px">{_err_html}</pre>
        <hr>
        <p>Python: {sys.version}</p>
        <p>BASE: {BASE}</p>
        <p>Log: {LOG}</p>
        <p><b>Troque startup para debug_wsgi.py para mais detalhes</b></p>
        </body></html>"""
        return [html.encode("utf-8")]
