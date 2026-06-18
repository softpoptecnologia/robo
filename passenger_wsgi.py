import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

try:
    from app import app as application
except Exception:
    import traceback
    with open(os.path.join(BASE, "stderr.log"), "a", encoding="utf-8") as f:
        f.write("=== ERRO ao importar app ===\n")
        f.write(traceback.format_exc())
    raise
