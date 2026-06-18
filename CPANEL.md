# ERRO 503 RESOLVIDO

## Causa real (stderr.log)

```
/opt/alt/python313/bin/lswsgi: No such file or directory
```

O servidor **LiteSpeed** nao tem WSGI para **Python 3.13** nesta hospedagem.
A app `aulas` funciona porque usa **Python 3.11**.

## Solucao (5 minutos)

### 1. No cPanel → Setup Python App

1. **APAGUE** a aplicacao `robo.etegaranhuns.com.br` (Python 3.13)
2. **CRIE NOVA** com **Python 3.11** (igual aulas)
3. Application root: `/home/ailson/robo.etegaranhuns.com.br`
4. Startup file: `passenger_wsgi.py`
5. Entry point: `application`

### 2. No terminal

```bash
cd /home/ailson/robo.etegaranhuns.com.br
git pull origin main
bash server_update.sh
```

### 3. Restart no painel

Teste: https://robo.etegaranhuns.com.br/login

---

## .htaccess correto (Python 3.11)

```apache
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
PassengerBaseURI "/"
PassengerPython "/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END
```

---

## passenger_wsgi.py

```python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import app as application
```

Nao use Python 3.13 neste servidor ate a hospedagem instalar o lswsgi.
