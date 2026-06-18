# CORREÇÃO: "No such application (or application not configured)"

Esse erro **NÃO é do código Flask**. O servidor **não registrou** a aplicação Python.

## Faça EXATAMENTE nesta ordem

### 1. Terminal do cPanel

```bash
cd /home/ailson/robo.etegaranhuns.com.br
git pull origin main
bash fix_cpanel.sh
```

### 2. cPanel → Setup Python App (ou "Aplicação Python")

**APAGUE** a aplicação `robo.etegaranhuns.com.br` se já existir.

**CRIE uma nova:**

| Campo | Valor |
|-------|--------|
| Python version | 3.11 |
| Application root | `/home/ailson/robo.etegaranhuns.com.br` |
| Application URL | `robo.etegaranhuns.com.br` |
| Application startup file | `passenger_wsgi.py` |
| Application Entry point | `application` |

Clique em **Create** e depois **Restart**.

> Ao criar, o cPanel gera o `.htaccess` correto. **Não apague** depois.

### 3. pyserver / painel

- Arquivo: `passenger_wsgi.py`
- Application: `application`

### 4. Teste

https://robo.etegaranhuns.com.br/login

---

## Se ainda falhar

Veja o erro real:

```bash
cat /home/ailson/robo.etegaranhuns.com.br/stderr.log
```

Teste o Python manualmente:

```bash
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
cd /home/ailson/robo.etegaranhuns.com.br
python -c "from app import app; print(app)"
```

Se der erro aqui, rode:

```bash
pip install -r requirements.txt
```

---

## passenger_wsgi.py (não mude)

```python
from app import app as application
```

O `app` é criado em `app/__init__.py`.
