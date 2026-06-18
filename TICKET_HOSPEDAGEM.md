# Abrir ticket na hospedagem — 503 LiteSpeed

O Flask funciona no terminal (`check_server.py` OK) e arquivos estaticos carregam (`/index.html` OK), mas rotas Python retornam **503**.

Isso indica falha no **lswsgi** (conector LiteSpeed + Python), nao no codigo.

## Texto para o ticket

```
Assunto: Python app 503 — lswsgi ausente / dominio robo nao registrado no LiteSpeed

Dominio: robo.etegaranhuns.com.br
Usuario: ailson
Pasta: /home/ailson/robo.etegaranhuns.com.br

Sintoma:
- https://robo.etegaranhuns.com.br/index.html funciona (HTML estatico)
- https://robo.etegaranhuns.com.br/ retorna 503
- stderr.log mostra: /opt/alt/pythonXXX/bin/lswsgi: No such file or directory

A app aulas.etegaranhuns.com.br funciona com Python 3.11 no mesmo servidor.
A app robo foi recriada com Python 3.11 e mesmo formato de .htaccess.

Solicito:
1. Verificar se alt-python311-wsgi-lsapi esta instalado
2. Executar: /usr/local/lsws/admin/misc/enable_ruby_python_selector.sh
3. Verificar registro do dominio robo.etegaranhuns.com.br no CloudLinux Python Selector
```

## Versoes Python com lswsgi

Rode no SSH:

```bash
for v in 38 39 310 311 312 313; do
  [ -x "/opt/alt/python${v}/bin/lswsgi" ] && echo "OK python${v}" || echo "-- python${v}"
done
```

Use no painel **somente** uma versao que apareca como OK.
