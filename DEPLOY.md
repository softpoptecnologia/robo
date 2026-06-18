# Deploy — robo.etegaranhuns.com.br

Igual a app **aulas** que já funciona no mesmo servidor.

## Painel Python App

| Campo | Valor |
|-------|--------|
| Python | **3.11** |
| Root | `/home/ailson/robo.etegaranhuns.com.br` |
| Startup file | `passenger_wsgi.py` |
| Entry point | `application` |

## No servidor (SSH)

```bash
cd /home/ailson/robo.etegaranhuns.com.br
bash deploy.sh
```

Restart no painel → https://robo.etegaranhuns.com.br/ping

## .htaccess (gerado pelo deploy.sh, igual aulas)

```apache
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
PassengerBaseURI "/"
PassengerPython "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END
```

**Não adicione** `PassengerStartupFile`, `SetEnv`, `PassengerEnabled` — a aulas não tem.

## passenger_wsgi.py

```python
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import app as application
```
