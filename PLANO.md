# Plano de Execução — Portal Clube de Robótica

## Visão Geral

Sistema web Flask para gerenciamento escolar do Clube de Robótica, com controle de projetos, grupos, cronogramas, atividades, reuniões, atas, participação e evidências.

---

## Fase 1 — Infraestrutura Base ✅

- [x] Estrutura de pastas (`app/`, `templates/`, `static/`)
- [x] `config.py` com SQLite e uploads
- [x] `requirements.txt`
- [x] Factory Flask (`create_app`)
- [x] SQLAlchemy + Flask-Login
- [x] Layout base com menu lateral
- [x] CSS escolar responsivo
- [x] Usuário admin inicial (`admin` / `admin123`)

---

## Fase 2 — Autenticação e Perfis ✅

- [x] Tela de login
- [x] Sessão Flask-Login
- [x] Logout
- [x] Hash de senha (Werkzeug)
- [x] Decorator `@role_required` (admin, leader, participant)
- [x] Proteção de rotas por perfil

---

## Fase 3 — Cadastros Principais ✅

### Estudantes
- [x] CRUD completo (nome, e-mail, turma, telefone, status, observações)

### Projetos
- [x] CRUD (título, descrição, objetivo, área, datas, status)

### Grupos
- [x] CRUD (nome, projeto, líder, membros, status)
- [x] Tabela associativa `group_students`

---

## Fase 4 — Acompanhamento do Trabalho ✅

### Cronograma
- [x] Etapas por grupo (título, descrição, datas, responsável, status)
- [x] Marcação automática de etapas atrasadas

### Atividades
- [x] Registro por participante (descrição, dificuldades, próximos passos)
- [x] Upload de anexos opcional

### Reuniões
- [x] Agenda (data, horário, local, pauta, status)

### Atas
- [x] Resumo, decisões, presença, tarefas com responsáveis
- [x] Vinculação à reunião realizada

---

## Fase 5 — Participação e Relatórios ✅

### Controle de Participação
- [x] Presença/ausência por reunião
- [x] Percentual de participação
- [x] Identificação de baixa participação (< 70%)
- [x] Histórico de atividades por estudante

### Relatórios
- [x] Projetos cadastrados
- [x] Progresso dos grupos
- [x] Participação dos estudantes
- [x] Atividades por grupo
- [x] Resumo de atas e decisões

---

## Fase 6 — Dashboard ✅

- [x] Total de projetos
- [x] Total de grupos ativos
- [x] Total de estudantes ativos
- [x] Reuniões agendadas
- [x] Etapas atrasadas
- [x] Estudantes com baixa participação
- [x] Atividades e evidências recentes

---

## Fase 7 — Módulo Evidências e Linha do Tempo ✅

### Registro de Evidências
- [x] Campos: projeto, grupo, estudante, título, descrição, tipo
- [x] Tipos: foto, vídeo, documento, link, código, protótipo, teste, apresentação, outro
- [x] Arquivo anexado e link externo
- [x] Etapa do cronograma relacionada
- [x] Snapshot do status do projeto
- [x] Observações

### Timeline do Projeto
- [x] Página por projeto em ordem cronológica
- [x] Exibe data, título, grupo, estudante, descrição, anexos, etapa e status

### Timeline por Grupo
- [x] Evidências, atividades, reuniões, etapas concluídas e atas unificadas

### Relatório de Evolução
- [x] Evidências por grupo
- [x] Últimas evidências
- [x] Grupos sem evidências recentes
- [x] Comparativo cronograma vs evidências
- [x] Top contribuidores

### Interface
- [x] Tela "Linha do Tempo" com filtros (projeto, grupo, estudante, tipo, período)
- [x] Timeline visual em HTML/CSS puro (marcos de evolução)

### Banco de Dados
- [x] Tabela `Evidence` com todos os campos solicitados

---

## Fase 8 — Melhorias Futuras (opcional)

- [ ] Tela admin para criar usuários líder/participante vinculados a estudantes
- [ ] Migração Flask-Migrate (Alembic)
- [ ] Exportação de relatórios em PDF
- [ ] Notificações por e-mail
- [ ] API REST
- [ ] Deploy em produção (Gunicorn + Nginx)
- [ ] Testes automatizados

---

## Como Executar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Login: `admin` / `admin123`

---

## Modelos do Banco

| Tabela              | Descrição                        |
|---------------------|----------------------------------|
| users               | Autenticação e perfis            |
| students            | Estudantes do clube              |
| projects            | Projetos                         |
| groups              | Grupos por projeto               |
| group_students      | Membros dos grupos               |
| schedule_items      | Etapas do cronograma             |
| activity_logs       | Atividades registradas           |
| meetings            | Reuniões agendadas               |
| meeting_minutes     | Atas de reunião                  |
| meeting_attendances | Presença                         |
| minute_tasks        | Tarefas das atas                 |
| evidences           | Evidências da linha do tempo     |
