# ERRO 503 — LiteSpeed lswsgi

## Erro real (stderr.log)

```
/opt/alt/python313/bin/lswsgi: No such file or directory
```

Python **3.13 nao funciona** neste servidor. Use **3.11** (igual aulas).

Se ainda da 503 com 3.11, rode:

```bash
cd /home/ailson/robo.etegaranhuns.com.br
git pull origin main
bash fix_from_aulas.sh
```

Isso copia o `.htaccess` e o `passenger_wsgi` da app **aulas** que funciona.

## No painel Python App

1. **APAGUE** o app robo
2. **CRIE** com **Python 3.11**
3. Root: `/home/ailson/robo.etegaranhuns.com.br`
4. Teste startup file nesta ordem:
   - `passenger_wsgi.py` + entry `application`
   - Se falhar: `passenger_wsgi` (sem .py) + entry `application`
5. **RESTART**

## Verificar lswsgi

```bash
ls -la /opt/alt/python311/bin/lswsgi
```

Se nao existir, abra ticket na hospedagem.

## passenger_wsgi.py

```python
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import app as application
```

## Mande se falhar

```bash
tail -5 stderr.log
cat .htaccess
ls -la /opt/alt/python311/bin/lswsgi
```
