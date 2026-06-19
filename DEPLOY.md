# Deploy — robo.etegaranhuns.com.br

## No servidor

```bash
cd /home/ailson/robo.etegaranhuns.com.br
git pull origin main
bash deploy.sh
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
