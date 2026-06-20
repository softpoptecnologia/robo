# Deploy — robo.etegaranhuns.com.br

## No servidor

```bash
cd /home/ailson/robo.etegaranhuns.com.br
git pull origin main

source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
pip install -r requirements.txt

mkdir -p bin uploads/latex-cache
chmod 755 bin uploads uploads/latex-cache
```

Reinicie a app Python no cPanel (**RESTART**).

## Compilador LaTeX (PDF do artigo IEEE)

Na **primeira** geração de PDF, o sistema tenta baixar o **Tectonic** para `bin/tectonic` (Linux x86_64).

Se o download automático falhar (firewall do servidor), instale manualmente:

```bash
cd /home/ailson/robo.etegaranhuns.com.br
mkdir -p bin
curl -L -o /tmp/tectonic.tgz \
  https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.16.9/tectonic-0.16.9-x86_64-unknown-linux-gnu.tar.gz
tar -xzf /tmp/tectonic.tgz -C bin
chmod +x bin/tectonic
rm /tmp/tectonic.tgz
bin/tectonic --version
```

Confirme também:

```bash
ls -la arquivos/IEEE_Conference_Template.zip
```

## No painel Python App

Se existir arquivo `passenger_wsgi` (sem .py) na pasta:

| Campo | Valor |
|-------|--------|
| Startup file | **`passenger_wsgi`** |
| Entry point | `application` |

Se não existir, use:

| Campo | Valor |
|-------|--------|
| Startup file | `passenger_wsgi.py` |
| Entry point | `application` |

**RESTART** → https://robo.etegaranhuns.com.br/ping

## Se ainda falhar

```bash
bash compare_aulas.sh
```

Mande a saída completa + qual startup file a app **aulas** usa no painel.
