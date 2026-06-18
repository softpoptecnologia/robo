"""
Dados iniciais de demonstração — Clube de Robótica.

Projetos distintos com estudantes, grupos, cronograma, atividades,
reuniões, atas e evidências de exemplo.
"""

from datetime import date, datetime, time, timedelta

from app.extensions import db
from app.models import (
    ActivityLog,
    Evidence,
    Group,
    Meeting,
    MeetingAttendance,
    MeetingMinute,
    MinuteTask,
    Project,
    ScheduleItem,
    Student,
    User,
)


def seed_all(force=False):
    """
    Popula o banco com dados de demonstração.
    Se force=False, não executa se já existirem projetos cadastrados.
    """
    if not force and Project.query.first():
        print("Banco já possui projetos. Use force=True para recriar.")
        return False

    if force:
        _clear_demo_data()

    students = _seed_students()
    projects = _seed_projects()
    groups = _seed_groups(students, projects)
    _seed_users(students, groups)
    _seed_schedules(groups, students)
    meetings = _seed_meetings(groups)
    _seed_activities(groups, students)
    _seed_evidences(groups, students, meetings)
    _seed_minutes(meetings, students)

    db.session.commit()
    print(f"Seed concluído: {len(projects)} projetos, {len(students)} estudantes, {len(groups)} grupos.")
    return True


def _clear_demo_data():
    """Remove dados de demonstração (mantém admin)."""
    from app.models import EvidenceAttachment

    EvidenceAttachment.query.delete()
    Evidence.query.delete()
    MinuteTask.query.delete()
    MeetingAttendance.query.delete()
    MeetingMinute.query.delete()
    Meeting.query.delete()
    ActivityLog.query.delete()
    ScheduleItem.query.delete()

    for group in Group.query.all():
        group.members = []
    db.session.flush()

    Group.query.delete()
    Project.query.delete()

    User.query.filter(User.username != "admin").delete()
    Student.query.delete()
    db.session.commit()


def _seed_students():
    data = [
        ("Ana Silva", "ana.silva@escola.local", "2ºA", "11999001001"),
        ("Bruno Costa", "bruno.costa@escola.local", "2ºA", "11999001002"),
        ("Carla Mendes", "carla.mendes@escola.local", "2ºB", "11999001003"),
        ("Diego Alves", "diego.alves@escola.local", "2ºB", "11999001004"),
        ("Elena Rocha", "elena.rocha@escola.local", "3ºA", "11999001005"),
        ("Felipe Nunes", "felipe.nunes@escola.local", "3ºA", "11999001006"),
        ("Gabriela Lima", "gabriela.lima@escola.local", "3ºB", "11999001007"),
        ("Henrique Souza", "henrique.souza@escola.local", "3ºB", "11999001008"),
        ("Isabela Torres", "isabela.torres@escola.local", "1ºA", "11999001009"),
        ("João Pedro", "joao.pedro@escola.local", "1ºA", "11999001010"),
    ]
    students = []
    for name, email, turma, phone in data:
        s = Student(name=name, email=email, class_name=turma, phone=phone, status="ativo")
        db.session.add(s)
        students.append(s)
    db.session.flush()
    return students


def _seed_projects():
    today = date.today()
    data = [
        {
            "title": "Braço Robótico Articulado",
            "description": "Construção de um braço robótico com 3 graus de liberdade controlado por Arduino.",
            "objective": "Desenvolver um manipulador capaz de pegar objetos leves e demonstrar cinemática básica.",
            "area": "robotica",
            "start_date": today - timedelta(days=60),
            "expected_end_date": today + timedelta(days=30),
            "status": "em andamento",
        },
        {
            "title": "Estufa Inteligente IoT",
            "description": "Monitoramento de temperatura e umidade em mini-estufa com sensores e alertas.",
            "objective": "Automatizar irrigação e registrar dados ambientais em tempo real.",
            "area": "iot",
            "start_date": today - timedelta(days=45),
            "expected_end_date": today + timedelta(days=45),
            "status": "em andamento",
        },
        {
            "title": "Carrinho Seguidor de Linha",
            "description": "Robô móvel que segue fita isolante no chão usando sensores infravermelhos.",
            "objective": "Participar da competição interna de seguidores de linha da escola.",
            "area": "automacao",
            "start_date": today - timedelta(days=30),
            "expected_end_date": today + timedelta(days=20),
            "status": "em andamento",
        },
        {
            "title": "Estação Meteorológica Escolar",
            "description": "Coleta de dados de temperatura, umidade e pressão com display LCD.",
            "objective": "Alimentar um painel com dados climáticos do pátio da escola.",
            "area": "eletronica",
            "start_date": today - timedelta(days=90),
            "expected_end_date": today - timedelta(days=10),
            "status": "concluido",
        },
        {
            "title": "Robô Sumô Autônomo",
            "description": "Robô de combate com sensores ultrassônicos para detectar o oponente.",
            "objective": "Construir um sumôbot competitivo para a OBR regional.",
            "area": "programacao",
            "start_date": today - timedelta(days=15),
            "expected_end_date": today + timedelta(days=60),
            "status": "planejado",
        },
        {
            "title": "Classificador de Lixo com IA",
            "description": "Sistema de visão computacional para separar recicláveis usando câmera e Raspberry Pi.",
            "objective": "Treinar um modelo simples para identificar plástico, metal e papel.",
            "area": "ia",
            "start_date": today - timedelta(days=20),
            "expected_end_date": today + timedelta(days=70),
            "status": "em andamento",
        },
    ]
    projects = []
    for item in data:
        p = Project(**item)
        db.session.add(p)
        projects.append(p)
    db.session.flush()
    return projects


def _seed_groups(students, projects):
    """Um grupo por projeto, com líder e membros distintos."""
    assignments = [
        ("Grupo Atlas", 0, [0, 1, 2]),       # Braço — Ana líder
        ("Grupo Verde", 1, [3, 4, 5]),       # Estufa — Diego líder
        ("Grupo Turbo", 2, [6, 7, 8]),       # Seguidor — Gabriela líder
        ("Grupo Clima", 3, [9, 0, 1]),       # Meteorológica — João líder
        ("Grupo Impacto", 4, [2, 3, 4]),     # Sumô — Carla líder
        ("Grupo Vision", 5, [5, 6, 7]),      # IA — Felipe líder
    ]
    groups = []
    for name, proj_idx, member_idxs in assignments:
        leader = students[member_idxs[0]]
        g = Group(
            name=name,
            project_id=projects[proj_idx].id,
            leader_id=leader.id,
            status="ativo" if projects[proj_idx].status != "concluido" else "concluido",
        )
        g.members = [students[i] for i in member_idxs]
        db.session.add(g)
        groups.append(g)
    db.session.flush()
    return groups


def _seed_users(students, groups):
    """Cria usuários líder e participante para testar perfis."""
    users_data = [
        ("lider_atlas", "lider.atlas@escola.local", "leader", 0),
        ("lider_verde", "lider.verde@escola.local", "leader", 3),
        ("participante1", "participante1@escola.local", "participant", 1),
        ("participante2", "participante2@escola.local", "participant", 4),
    ]
    for username, email, role, student_idx in users_data:
        if User.query.filter_by(username=username).first():
            continue
        u = User(username=username, email=email, role=role, student_id=students[student_idx].id)
        u.set_password("123456")
        db.session.add(u)


def _seed_schedules(groups, students):
    today = date.today()
    schedules = [
        # Grupo Atlas — Braço Robótico
        [
            ("Planejamento e lista de materiais", "Definir servos, estrutura e ferramentas", -50, -40, "concluida"),
            ("Montagem da base e eixo 1", "Fixar base em acrílico e instalar primeiro servo", -39, -25, "concluida"),
            ("Montagem do braço e garra", "Instalar eixos 2 e 3 com garra impressa em 3D", -24, -5, "em andamento"),
            ("Programação e calibração", "Código Arduino e testes de movimento", -4, 20, "pendente"),
        ],
        # Grupo Verde — Estufa IoT
        [
            ("Montagem da estrutura da estufa", "Armação em PVC e cobertura", -35, -20, "concluida"),
            ("Instalação dos sensores", "DHT22, umidade do solo e relé da bomba", -19, -5, "em andamento"),
            ("Dashboard e alertas", "Interface web simples com gráficos", -4, 30, "pendente"),
        ],
        # Grupo Turbo — Seguidor de linha
        [
            ("Chassi e motores", "Montagem do carrinho diferencial", -25, -15, "concluida"),
            ("Sensores IR e calibração", "Ajuste de limiar para fita preta", -14, 0, "em andamento"),
            ("Otimização de curvas", "PID básico para competição", 1, 15, "pendente"),
        ],
        # Grupo Clima — Meteorológica (concluído)
        [
            ("Esquema elétrico", "Ligação dos sensores BME280", -80, -70, "concluida"),
            ("Montagem do protótipo", "Caixa estanque e display", -69, -40, "concluida"),
            ("Coleta e apresentação", "Relatório final e demo", -39, -15, "concluida"),
        ],
        # Grupo Impacto — Sumô
        [
            ("Design do robô", "Desenho CAD e escolha de motores", -10, 0, "em andamento"),
            ("Chassi reforçado", "Estrutura em alumínio", 1, 20, "pendente"),
        ],
        # Grupo Vision — IA
        [
            ("Coleta de imagens", "Fotografar amostras de lixo", -15, -5, "concluida"),
            ("Treinamento do modelo", "Classificador com Teachable Machine", -4, 25, "em andamento"),
            ("Integração com atuador", "Servo para desviar itens", 26, 50, "pendente"),
        ],
    ]

    for group, steps in zip(groups, schedules):
        for title, desc, start_off, end_off, status in steps:
            item = ScheduleItem(
                group_id=group.id,
                project_id=group.project_id,
                title=title,
                description=desc,
                start_date=today + timedelta(days=start_off),
                end_date=today + timedelta(days=end_off),
                responsible_id=group.leader_id,
                status=status,
            )
            db.session.add(item)
    db.session.flush()


def _seed_meetings(groups):
    today = date.today()
    meetings = []
    for i, group in enumerate(groups[:4]):  # reuniões nos 4 primeiros grupos
        m1 = Meeting(
            group_id=group.id,
            project_id=group.project_id,
            meeting_date=today - timedelta(days=14 - i),
            meeting_time=time(14, 0),
            location="Sala de Robótica",
            agenda="Revisão do cronograma e divisão de tarefas",
            status="realizada",
        )
        m2 = Meeting(
            group_id=group.id,
            project_id=group.project_id,
            meeting_date=today + timedelta(days=7 + i),
            meeting_time=time(15, 30),
            location="Laboratório Maker",
            agenda="Demonstração parcial do protótipo",
            status="agendada",
        )
        db.session.add(m1)
        db.session.add(m2)
        meetings.append(m1)
    db.session.flush()
    return meetings


def _seed_activities(groups, students):
    today = date.today()
    logs = [
        (0, 0, "Soldamos os suportes da base do braço em acrílico 5 mm.", "Dificuldade no alinhamento dos furos.", "Instalar o primeiro servo."),
        (0, 1, "Testamos o movimento do servo com código de exemplo.", None, "Montar o segundo eixo."),
        (1, 3, "Instalamos o sensor DHT22 e validamos leituras no Serial Monitor.", "Fios muito curtos.", "Adicionar sensor de umidade do solo."),
        (2, 6, "Calibramos os 5 sensores IR no piso da sala.", "Reflexo da luz interfere em um sensor.", "Implementar correção no código."),
        (5, 5, "Coletamos 120 fotos de garrafas PET para o dataset.", None, "Treinar modelo inicial."),
    ]
    for group_idx, student_idx, desc, diff, nxt in logs:
        g = groups[group_idx]
        db.session.add(ActivityLog(
            group_id=g.id,
            project_id=g.project_id,
            student_id=students[student_idx].id,
            activity_date=today - timedelta(days=3),
            description=desc,
            difficulties=diff,
            next_steps=nxt,
        ))
    db.session.flush()


def _seed_evidences(groups, students, meetings):
    today = datetime.now()
    evidences_data = [
        {
            "group_idx": 0,
            "student_idx": 0,
            "meeting_idx": 0,
            "title": "Braço robótico — base montada",
            "description": "Construímos a base em acrílico 5 mm com 3 furos para servos MG996R. Alcance previsto: 25 cm.",
            "evidence_type": "prototipo",
            "schedule_title": "Montagem da base e eixo 1",
            "observations": "Fotos do protótipo e modelo CAD serão anexadas na próxima reunião.",
        },
        {
            "group_idx": 0,
            "student_idx": 1,
            "meeting_idx": None,
            "title": "Teste do servo eixo 1",
            "description": "Servo responde de 0° a 180° com alimentação 5V/2A. Código de calibração funcionando.",
            "evidence_type": "teste",
            "schedule_title": "Montagem do braço e garra",
            "observations": None,
        },
        {
            "group_idx": 1,
            "student_idx": 3,
            "meeting_idx": 1,
            "title": "Estrutura da estufa concluída",
            "description": "Armazém PVC ¾ montado com cobertura transparente. Dimensões: 80×50×60 cm.",
            "evidence_type": "foto",
            "schedule_title": "Montagem da estrutura da estufa",
            "observations": "Link do diagrama: https://exemplo.local/estufa-diagrama",
            "external_link": "https://exemplo.local/estufa-diagrama",
        },
        {
            "group_idx": 2,
            "student_idx": 6,
            "meeting_idx": None,
            "title": "Chassi do seguidor de linha",
            "description": "Carrinho diferencial com 2 motores TT e castor frontal. Velocidade base calibrada.",
            "evidence_type": "prototipo",
            "schedule_title": "Chassi e motores",
            "observations": None,
        },
        {
            "group_idx": 3,
            "student_idx": 9,
            "meeting_idx": None,
            "title": "Estação meteorológica em operação",
            "description": "Sensores BME280 e display LCD 16x2 exibindo temperatura e umidade a cada 5 segundos.",
            "evidence_type": "apresentacao",
            "schedule_title": "Coleta e apresentação",
            "observations": "Projeto apresentado na feira de ciências.",
        },
        {
            "group_idx": 5,
            "student_idx": 5,
            "meeting_idx": None,
            "title": "Dataset de imagens para classificador",
            "description": "120 imagens rotuladas em 3 categorias: plástico, metal e papel.",
            "evidence_type": "codigo",
            "schedule_title": "Coleta de imagens",
            "observations": "Repositório no GitHub da escola.",
            "external_link": "https://github.com/exemplo/clube-lixo-ia",
        },
    ]

    schedule_map = {}
    for g in groups:
        for item in g.schedule_items:
            schedule_map[(g.id, item.title)] = item

    for ev_data in evidences_data:
        g = groups[ev_data["group_idx"]]
        schedule_item = schedule_map.get((g.id, ev_data["schedule_title"]))
        meeting = meetings[ev_data["meeting_idx"]] if ev_data["meeting_idx"] is not None else None

        ev = Evidence(
            project_id=g.project_id,
            group_id=g.id,
            student_id=students[ev_data["student_idx"]].id,
            schedule_item_id=schedule_item.id if schedule_item else None,
            meeting_id=meeting.id if meeting else None,
            title=ev_data["title"],
            description=ev_data["description"],
            evidence_type=ev_data["evidence_type"],
            external_link=ev_data.get("external_link"),
            project_status_snapshot=g.project.status,
            observations=ev_data.get("observations"),
            created_at=today - timedelta(days=5),
        )
        db.session.add(ev)
    db.session.flush()


def _seed_minutes(meetings, students):
    """Cria atas para as reuniões realizadas."""
    for meeting in meetings:
        minute = MeetingMinute(
            meeting_id=meeting.id,
            summary=f"Reunião do {meeting.group.name}: revisamos o progresso do projeto {meeting.project.title}.",
            decisions="Manter o cronograma atual. Próxima entrega em duas semanas.",
            notes="Todos participaram ativamente.",
        )
        db.session.add(minute)
        db.session.flush()

        for member in meeting.group.members:
            db.session.add(MeetingAttendance(
                meeting_id=meeting.id,
                student_id=member.id,
                present=True,
            ))

        db.session.add(MinuteTask(
            minute_id=minute.id,
            description="Finalizar etapa em andamento e registrar evidências",
            responsible_id=meeting.group.leader_id,
        ))
    db.session.flush()
