# robo

# Clube de Robótica — Portal Web

Portal Flask para gerenciamento de projetos, grupos, cronogramas, atividades, reuniões, atas e evidências do Clube de Robótica escolar.

## Requisitos

- Python 3.11+
- pip

## Instalação

```bash
cd clube-robotica
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Executar

```bash
python run.py
```

### Popular com dados de demonstração

```bash
python seed.py          # cria 6 projetos distintos (só se o banco estiver vazio)
python seed.py --force  # recria todos os dados de demo
```

Projetos incluídos no seed: Braço Robótico, Estufa IoT, Seguidor de Linha, Estação Meteorológica, Robô Sumô e Classificador de Lixo com IA — cada um com grupo, cronograma, atividades, reuniões e evidências.

Acesse: http://localhost:5000

**Login inicial:**
- Usuário: `admin`
- Senha: `admin123`

> Altere a senha e a `SECRET_KEY` em produção.

## Estrutura do Projeto

```
clube-robotica/
├── app/
│   ├── __init__.py          # Factory da aplicação
│   ├── models.py            # Modelos SQLAlchemy
│   ├── extensions.py        # db e login_manager
│   ├── decorators.py        # Controle de perfil
│   ├── utils.py             # Uploads e helpers
│   ├── auth/                # Login e logout
│   ├── dashboard/           # Painel inicial
│   ├── students/            # CRUD estudantes
│   ├── projects/            # CRUD projetos
│   ├── groups/              # CRUD grupos
│   ├── schedule/            # Cronograma
│   ├── activities/          # Registro de atividades
│   ├── meetings/            # Agenda de reuniões
│   ├── minutes/             # Atas de reunião
│   ├── reports/             # Relatórios
│   ├── evidence/            # Evidências e Linha do Tempo
│   ├── templates/           # HTML Jinja2
│   └── static/css/          # Estilos
├── config.py                # Configurações
├── run.py                   # Entrada da aplicação
├── requirements.txt
└── uploads/                 # Arquivos anexados (criado automaticamente)
```

## Perfis de Usuário

| Perfil        | Acesso                                              |
|---------------|-----------------------------------------------------|
| admin         | Acesso total                                        |
| leader        | Projetos, grupos, cronograma, reuniões, atas        |
| participant   | Atividades, evidências do próprio grupo             |

Para vincular líderes e participantes, crie o estudante e depois um usuário com `student_id` correspondente (via banco ou script futuro).

## Banco de Dados

SQLite em desenvolvimento (`clube_robotica.db` na raiz).

Para migrar para PostgreSQL ou MySQL, altere `DATABASE_URL`:

```bash
set DATABASE_URL=postgresql://user:pass@localhost/clube_robotica
```

## Módulos

- **Dashboard** — cards com totais e alertas
- **Estudantes** — cadastro completo
- **Projetos** — áreas, status e datas
- **Grupos** — líder e membros
- **Cronograma** — etapas com status automático de atraso
- **Atividades** — registro diário com anexos
- **Reuniões** — agenda e status
- **Atas** — presença, decisões e tarefas
- **Linha do Tempo** — evidências visuais do progresso
- **Relatórios** — participação, progresso e evolução

## Licença

Uso educacional.
