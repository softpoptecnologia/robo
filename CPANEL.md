# CORREÇÃO: "No such application (or application not configured)"

## .htaccess — copie EXATAMENTE este formato (igual sua app aulas)

```apache
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
PassengerBaseURI "/"
PassengerPython "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END
```

No terminal:

```bash
cd /home/ailson/robo.etegaranhuns.com.br
cp htaccess.example .htaccess
```

Ou deixe o cPanel gerar ao criar o Python App.

---

## pyserver / Setup Python App

| Campo | Valor |
|-------|--------|
| Application root | `/home/ailson/robo.etegaranhuns.com.br` |
| Startup file | `passenger_wsgi.py` |
| Entry point | `application` |

## passenger_wsgi.py

```python
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
```

## Dependências

```bash
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.13/bin/activate
pip install -r requirements.txt
```

Restart no painel.

## Teste

https://robo.etegaranhuns.com.br/login
