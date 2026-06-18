import os
import sys
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

try:
    from app import create_app

    application = create_app()
except Exception:
    _error = traceback.format_exc()

    def application(environ, start_response):
        start_response("500 Internal Server Error", [("Content-Type", "text/plain; charset=utf-8")])
        return [_error.encode("utf-8")]
