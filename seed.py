"""
Popula o banco com projetos de demonstração.

Uso:
    python seed.py          # só executa se o banco estiver vazio
    python seed.py --force  # apaga dados demo e recria tudo
"""

import sys

from app import create_app
from app.seeds import seed_all

app = create_app()

with app.app_context():
    force = "--force" in sys.argv
    ok = seed_all(force=force)
    if ok:
        print()
        print("Projetos criados:")
        print("  1. Braço Robótico Articulado")
        print("  2. Estufa Inteligente IoT")
        print("  3. Carrinho Seguidor de Linha")
        print("  4. Estação Meteorológica Escolar")
        print("  5. Robô Sumô Autônomo")
        print("  6. Classificador de Lixo com IA")
        print()
        print("Usuários extras (senha: 123456):")
        print("  lider_atlas      — líder do Grupo Atlas")
        print("  lider_verde      — líder do Grupo Verde")
        print("  participante1    — participante")
        print("  participante2    — participante")
        print()
        print("Admin: admin / admin123")
