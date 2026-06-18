# Deploy — robo.etegaranhuns.com.br

## Erro: `.htaccess` não encontrado

O painel tenta gravar variáveis em:

```
/home/ailson/robo.etegaranhuns.com.br/.htaccess
```

**Causa:** a pasta do subdomínio não existe ou o `.htaccess` não foi criado.

### Correção rápida (SSH ou Gerenciador de Arquivos)

```bash
mkdir -p /home/ailson/robo.etegaranhuns.com.br
cd /home/ailson/robo.etegaranhuns.com.br
git clone https://github.com/softpoptecnologia/robo.git .
# ou: git pull se já clonou em outro lugar

# Garantir que .htaccess existe
touch .htaccess
chmod 644 .htaccess
```

Se clonou do GitHub, o `.htaccess` e o `passenger_wsgi.py` já vêm no repositório.

---

## Ordem correta no cPanel

1. **Criar a pasta** `robo.etegaranhuns.com.br` (subdomínio apontando para ela)
2. **Enviar/clonar** os arquivos do projeto para essa pasta
3. **Confirmar** que existem:
   - `.htaccess`
   - `passenger_wsgi.py`
   - `app/`, `config.py`, `requirements.txt`
4. **Setup Python App** no cPanel:
   - Python version: 3.11
   - Application root: `/home/ailson/robo.etegaranhuns.com.br`
   - Application URL: `robo.etegaranhuns.com.br`
   - Application startup file: `passenger_wsgi.py`
   - Application entry point: `application`
5. **Instalar dependências** (botão no painel ou terminal):

```bash
source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
pip install -r requirements.txt
```

6. **Popular banco** (uma vez):

```bash
python seed.py --force
```

7. **Restart** da aplicação Python no painel

---

## Ajustar caminhos

No `.htaccess`, confira:

```
PassengerAppRoot "/home/ailson/robo.etegaranhuns.com.br"
```

No `passenger_wsgi.py`, confira o caminho do virtualenv (o cPanel mostra no Setup Python App):

```
/home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/python3
```

---

## Variáveis de ambiente

No `.htaccess`:

```apache
SetEnv SECRET_KEY "sua-chave-secreta-aqui"
```

Ou defina no painel **Setup Python App → Environment variables**.

---

## Permissões

```bash
chmod 755 /home/ailson/robo.etegaranhuns.com.br
chmod 644 /home/ailson/robo.etegaranhuns.com.br/.htaccess
mkdir -p uploads
chmod 775 uploads
```

---

## Teste

Acesse: https://robo.etegaranhuns.com.br/login

Login demo: `/login/demo/admin`
