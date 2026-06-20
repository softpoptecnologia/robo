# Deploy — robo.etegaranhuns.com.br

## No servidor

```bash
cd /home/ailson/robo.etegaranhuns.com.br
git pull origin main

source /home/ailson/virtualenv/robo.etegaranhuns.com.br/3.11/bin/activate
pip install -r requirements.txt

mkdir -p bin uploads/latex-cache arquivos/tectonic-cache
chmod 755 bin uploads uploads/latex-cache arquivos/tectonic-cache
```

Reinicie a app Python no cPanel (**RESTART**).

## Compilador LaTeX (PDF do artigo IEEE)

Na **primeira** geração de PDF, o sistema tenta baixar o **Tectonic** para `bin/tectonic` (Linux x86_64).

Se o download automático falhar (firewall do servidor), instale manualmente (**build musl**, compatível com servidores sem OpenSSL 3):

```bash
cd /home/ailson/robo.etegaranhuns.com.br
rm -f bin/tectonic
mkdir -p bin

curl -L -o /tmp/tectonic.tgz \
  https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.16.9/tectonic-0.16.9-x86_64-unknown-linux-musl.tar.gz

tar -xzf /tmp/tectonic.tgz -C bin
chmod +x bin/tectonic
rm /tmp/tectonic.tgz

bin/tectonic --version
```

> **Não use** o build `linux-gnu` em servidores cPanel antigos — ele exige `libssl.so.3`.

Confirme também:

```bash
ls -la arquivos/IEEE_Conference_Template.zip
```

## Cache LaTeX do Tectonic (bundle offline)

Na **primeira** compilação, o Tectonic baixa pacotes LaTeX de `relay.fullyjustified.net`.
Em muitos servidores cPanel essa URL fica bloqueada — o binário roda, mas a compilação falha com:

```text
this bundle isn't cached, and we couldn't get it from the internet
```

### 1. Teste no servidor

```bash
cd /home/ailson/robo.etegaranhuns.com.br
mkdir -p arquivos/tectonic-cache
export TECTONIC_CACHE_DIR=/home/ailson/robo.etegaranhuns.com.br/arquivos/tectonic-cache

curl -I https://relay.fullyjustified.net/default_bundle_v33.tar.index.gz

# Se o curl acima funcionar, popule o cache com:
bash scripts/bootstrap_tectonic_cache.sh
```

### 2. Se o curl falhar (servidor sem saída para relay)

Gere o cache numa máquina **Linux x86_64** com internet (WSL, VPS ou o próprio PC):

```bash
git clone ... # ou copie o projeto
cd clube-robotica
# instale bin/tectonic (musl) como acima
bash scripts/bootstrap_tectonic_cache.sh
tar -czf tectonic-cache.tgz -C arquivos tectonic-cache
```

Envie ao servidor (scp, File Manager do cPanel, etc.):

```bash
# no seu PC
scp tectonic-cache.tgz ailson@br53-cp:/home/ailson/robo.etegaranhuns.com.br/

# no servidor
cd /home/ailson/robo.etegaranhuns.com.br
tar -xzf tectonic-cache.tgz -C arquivos
chmod -R 755 arquivos/tectonic-cache
rm tectonic-cache.tgz
```

Reinicie a app (**RESTART**) e abra o artigo no portal.

> O cache fica em `arquivos/tectonic-cache/` (não vai pro git). Depois de populado, compilações seguintes não precisam de internet.

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
