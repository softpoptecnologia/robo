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

---

## Erro: `git pull` — conflito no `.htaccess`

O cPanel modifica o `.htaccess` automaticamente. O Git bloqueia o pull com:

```
Your local changes to the following files would be overwritten by merge: .htaccess
```

### Solução no Terminal do cPanel (SSH)

```bash
cd /home/ailson/robo.etegaranhuns.com.br

# 1. Guardar cópia do .htaccess que o cPanel gerou
cp .htaccess .htaccess.cpanel.bak

# 2. Descartar alteração local só no Git (mantém o arquivo no disco)
git checkout -- .htaccess

# 3. Atualizar o projeto
git pull origin main
```

Se `git checkout -- .htaccess` não funcionar, use:

```bash
git stash push -m "htaccess cpanel" -- .htaccess
git pull origin main
```

### Após o pull — garantir variáveis de debug no `.htaccess`

Edite `.htaccess` e confira se existem estas linhas (adicione se faltarem):

```apache
SetEnv FLASK_DEBUG "1"
SetEnv DEBUG "1"
SetEnv SECRET_KEY "sua-chave-secreta"
```

O bloco `Passenger...` gerado pelo cPanel deve permanecer. Use `htaccess.example` como referência.

Depois: **Restart** da aplicação Python no painel.

> O `.htaccess` não é mais versionado no Git para evitar este conflito no futuro.
