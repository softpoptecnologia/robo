"""
USE NO PAINEL AGORA:
  Startup file: debug_wsgi.py
  Entry point: application

Abra o site — vai mostrar o erro REAL na tela.
Depois volte para passenger_wsgi.py
"""
import os
import sys
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "stderr.log")


def _write_log(text):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except OSError:
        pass


def application(environ, start_response):
    lines = []
    lines.append("=" * 60)
    lines.append("DEBUG WSGI — Clube de Robótica")
    lines.append("=" * 60)
    lines.append(f"Python: {sys.version}")
    lines.append(f"Executable: {sys.executable}")
    lines.append(f"BASE: {BASE}")
    lines.append(f"cwd: {os.getcwd()}")
    lines.append(f"sys.path: {sys.path[:5]}")
    lines.append("")

    # Variáveis WSGI importantes
    lines.append("--- WSGI ENV ---")
    for key in sorted(environ):
        if any(x in key.upper() for x in ("PASSENGER", "WSGI", "PYTHON", "HOME", "PATH", "SCRIPT")):
            lines.append(f"  {key} = {environ[key]}")
    lines.append("")

    os.chdir(BASE)
    if BASE not in sys.path:
        sys.path.insert(0, BASE)

    lines.append("--- TESTE IMPORTS ---")
    for mod in ("flask", "flask_login", "flask_sqlalchemy", "sqlalchemy", "werkzeug"):
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "ok")
            lines.append(f"  OK  {mod}: {ver}")
        except Exception as e:
            lines.append(f"  FALHA {mod}: {e}")
    lines.append("")

    lines.append("--- TESTE config.py ---")
    try:
        import config
        lines.append(f"  OK  BASE_DIR={config.BASE_DIR}")
        lines.append(f"  OK  DB={config.Config.SQLALCHEMY_DATABASE_URI}")
    except Exception:
        lines.append(traceback.format_exc())
    lines.append("")

    lines.append("--- TESTE from app import app ---")
    try:
        from app import app
        lines.append(f"  OK  Flask app: {app}")
        lines.append(f"  OK  Rotas: {len(list(app.url_map.iter_rules()))}")
        for rule in list(app.url_map.iter_rules())[:8]:
            lines.append(f"       {rule}")
        lines.append("")
        lines.append(">>> APP CARREGOU COM SUCESSO <<<")
        lines.append("Troque startup file para: passenger_wsgi.py")
    except Exception:
        lines.append("  FALHA:")
        lines.append(traceback.format_exc())
        lines.append("")
        lines.append(">>> ESTE E O ERRO REAL <<<")

    lines.append("")
    lines.append(f"Log: {LOG}")

    body = "\n".join(lines)
    _write_log(body)

    start_response("200 OK", [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Cache-Control", "no-store"),
    ])
    return [body.encode("utf-8")]
