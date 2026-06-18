#!/usr/bin/env python3
"""Diagnóstico no servidor: python check_server.py"""
import os
import sys
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

print("Python:", sys.version)
print("Pasta:", BASE)
print("-" * 40)

try:
    import flask
    print("Flask OK:", flask.__version__)
except ImportError as e:
    print("ERRO Flask:", e)
    print("Rode: pip install -r requirements.txt")
    sys.exit(1)

try:
    from app import create_app

    app = create_app()
    print("App OK:", app)
    print("URL map (primeiras rotas):")
    for rule in list(app.url_map.iter_rules())[:5]:
        print(" ", rule)
    print("-" * 40)
    print("TUDO OK — problema pode ser .htaccess ou pyserver")
except Exception:
    print("ERRO ao carregar app:")
    traceback.print_exc()
    sys.exit(1)
