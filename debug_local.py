#!/usr/bin/env python3
"""Rode: python debug_local.py — simula o que o Passenger faz"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

print("Importando debug_wsgi...")
import debug_wsgi

environ = {
    "REQUEST_METHOD": "GET",
    "PATH_INFO": "/",
    "SERVER_NAME": "localhost",
    "wsgi.version": (1, 0),
    "wsgi.input": None,
    "wsgi.errors": sys.stderr,
    "wsgi.multithread": False,
    "wsgi.multiprocess": True,
    "wsgi.run_once": False,
}

status = []
def start_response(s, headers):
    status.append(s)
    print("STATUS:", s)

body = b"".join(debug_wsgi.application(environ, start_response))
print(body.decode("utf-8", errors="replace"))
