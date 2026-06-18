import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Importa a aplicação corretamente
from app import app as application
