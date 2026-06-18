# Deploy — robo.etegaranhuns.com.br

## Configuração no pyserver (cPanel)

No painel **Python App / pyserver**, use apenas:

| Campo | Valor |
|-------|--------|
| **Arquivo de entrada** | `passenger_wsgi.py` |
| **Application / callable** | `application` |

Só isso. O arquivo `passenger_wsgi.py` tem 6 linhas:

```python
from app import create_app
application = create_app()
```

Alternativa: arquivo `run.py`, callable `application`.

Depois clique em **Restart**.

---

## Se mostrar "Index of /" (lista de arquivos)

Falta o `.htaccess`. No terminal:

```bash
cd /home/ailson/robo.etegaranhuns.com.br
cp htaccess.example .htaccess
```

Ou rode: `bash setup_server.sh`

Marque **mostrar arquivos ocultos** no Gerenciador de Arquivos.

---

## Instalar dependências (uma vez)

```bash
cd /home/ailson/robo.etegaranhuns.com.br
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
pip install -r requirements.txt
python seed.py --force
```

---

## Atualizar código

```bash
cd /home/ailson/robo.etegaranhuns.com.br
git pull origin main
```

Se der erro no `.htaccess`:

```bash
git checkout -- .htaccess
git pull origin main
```

Restart no painel.

---

## Teste

https://robo.etegaranhuns.com.br/login
