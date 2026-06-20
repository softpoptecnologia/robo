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
    EvidenceAttachment,
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
            "description": "Desenvolvimento de manipulador robótico escolar com três graus de liberdade, controle em Arduino e garra impressa em 3D para manipulação de objetos leves.",
            "objective": "Demonstrar cinemática planar aplicada e controle por servomotores em contexto de educação STEM.",
            "area": "robotica",
            "start_date": today - timedelta(days=60),
            "expected_end_date": today + timedelta(days=30),
            "status": "em andamento",
            "research_question": "É possível construir um braço robótico de baixo custo capaz de posicionar objetos com erro inferior a 2 cm?",
            "hypothesis": "Três servomotores MG996R com controle PWM permitirão alcance de 25 cm com precisão adequada para demonstrações escolares.",
            "keywords": "robótica manipuladora, servomotor, Arduino, educação STEM, cinemática",
            "methodology": "Prototipagem iterativa: levantamento de requisitos, modelagem CAD, montagem mecânica, programação em Arduino IDE e testes de repetibilidade.",
            "scientific_relevance": "Introduz conceitos de engenharia mecânica e programação em projeto interdisciplinar de ensino médio.",
        },
        {
            "title": "Estufa Inteligente IoT",
            "description": "Mini-estufa automatizada com sensores ambientais, atuadores de irrigação e publicação de dados em dashboard web local.",
            "objective": "Automatizar irrigação com base em umidade do solo e registrar séries temporais de temperatura e umidade relativa.",
            "area": "iot",
            "start_date": today - timedelta(days=45),
            "expected_end_date": today + timedelta(days=45),
            "status": "em andamento",
            "research_question": "Sensores de baixo custo podem manter umidade ideal em estufa escolar sem supervisão contínua?",
            "hypothesis": "Um sistema ESP8266 com DHT22 e sensor capacitivo de solo reduzirá em pelo menos 40% a irrigação manual.",
            "keywords": "IoT, agricultura urbana, ESP8266, automação, sensores ambientais",
            "methodology": "Montagem da estufa, calibração de sensores, coleta de dados por 14 dias, comparação com irrigação manual e análise de consumo hídrico.",
            "scientific_relevance": "Relaciona computação, biologia e sustentabilidade em experimento reprodutível.",
        },
        {
            "title": "Carrinho Seguidor de Linha",
            "description": "Robô móvel diferencial com sensores infravermelhos para seguir trajetória demarcada em competição escolar.",
            "objective": "Atingir tempo médio inferior a 12 s em pista padronizada de 4 m com curvas de 90°.",
            "area": "automacao",
            "start_date": today - timedelta(days=30),
            "expected_end_date": today + timedelta(days=20),
            "status": "em andamento",
            "research_question": "Controle proporcional simples melhora desempenho do seguidor de linha frente a lógica bang-bang?",
            "hypothesis": "Implementação de PID básico reduzirá oscilações laterais em pelo menos 30%.",
            "keywords": "seguidor de linha, PID, sensores IR, robótica móvel, competição",
            "methodology": "Construção do chassi, calibração de limiares IR, implementação de controle bang-bang e PID, bateria de 20 voltas cronometradas.",
            "scientific_relevance": "Aplica teoria de controle em hardware acessível para feiras de ciências.",
        },
        {
            "title": "Estação Meteorológica Escolar",
            "description": "Estação automática de monitoramento climático instalada no pátio da escola, com sensor BME280, display LCD e registro horário de temperatura, umidade e pressão atmosférica por 30 dias.",
            "objective": "Validar a correlação entre temperatura externa e umidade relativa no período matutino versus vespertino e publicar dataset aberto para turmas de ciências.",
            "area": "eletronica",
            "start_date": today - timedelta(days=90),
            "expected_end_date": today - timedelta(days=10),
            "status": "concluido",
            "research_question": "Variações térmicas diárias no pátio escolar apresentam padrão estatisticamente significativo entre manhã e tarde?",
            "hypothesis": "A temperatura média matutina será 3 °C inferior à vespertina, com umidade inversamente correlacionada (r < -0,6).",
            "keywords": "meteorologia escolar, BME280, monitoramento ambiental, IoT, ciências da natureza",
            "methodology": "Projeto eletrônico com microcontrolador, encapsulamento estanque IP54, amostragem a cada 5 minutos por 30 dias, exportação CSV e análise descritiva com planilha e gráficos.",
            "scientific_relevance": "Fornece dados locais para estudo de clima urbano e integra física, matemática e tecnologia em produção científica escolar publicável.",
        },
        {
            "title": "Robô Sumô Autônomo",
            "description": "Sumôbot com sensores ultrassônicos HC-SR04, tração diferencial reforçada e estratégia de busca do oponente.",
            "objective": "Desenvolver robô autônomo capaz de detectar oponente em 80 cm e reagir em menos de 500 ms.",
            "area": "programacao",
            "start_date": today - timedelta(days=15),
            "expected_end_date": today + timedelta(days=60),
            "status": "planejado",
            "research_question": "Estratégias de busca espiral superam busca linear em ringue de sumô escolar?",
            "hypothesis": "Busca espiral aumentará taxa de detecção em 25% nos primeiros 5 segundos de combate.",
            "keywords": "robótica competitiva, ultrassom, OBR, estratégia autônoma",
            "methodology": "Design CAD, prototipagem de chassi, implementação de máquina de estados e testes A/B de estratégias em ringue oficial.",
            "scientific_relevance": "Prepara equipe para Olimpíada Brasileira de Robótica com base experimental.",
        },
        {
            "title": "Classificador de Lixo com IA",
            "description": "Sistema embarcado com Raspberry Pi e câmera para classificação visual de resíduos recicláveis em três categorias.",
            "objective": "Alcançar acurácia mínima de 85% em conjunto de teste com 60 imagens locais.",
            "area": "ia",
            "start_date": today - timedelta(days=20),
            "expected_end_date": today + timedelta(days=70),
            "status": "em andamento",
            "research_question": "Modelos leves treinados com Teachable Machine generalizam para resíduos coletados na escola?",
            "hypothesis": "Transfer learning com 120 imagens por classe atingirá acurácia superior a 85% em validação cruzada 5-fold.",
            "keywords": "visão computacional, aprendizado de máquina, sustentabilidade, Raspberry Pi",
            "methodology": "Coleta e rotulação de imagens, treinamento do classificador, implantação em Python/OpenCV e avaliação com matriz de confusão.",
            "scientific_relevance": "Demonstra IA aplicada à educação ambiental com pipeline reprodutível.",
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
            ("Revisão bibliográfica", "Levantamento sobre microclima urbano e sensores BME280", -85, -78, "concluida"),
            ("Esquema elétrico", "Ligação dos sensores BME280, pull-ups I2C e display LCD", -80, -70, "concluida"),
            ("Montagem do protótipo", "Caixa ABS estanque IP54, fixação no pátio e teste de 72 h", -69, -45, "concluida"),
            ("Instalação de campo e coleta", "Logging automático a cada 5 min por 30 dias consecutivos", -44, -20, "concluida"),
            ("Análise estatística", "Médias, correlação Pearson, histogramas e teste de hipótese", -19, -12, "concluida"),
            ("Redação científica e feira", "Poster, apresentação oral e rascunho IEEE", -11, -5, "concluida"),
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
    for i, group in enumerate(groups[:4]):
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

    clima = groups[3]
    m_mid = Meeting(
        group_id=clima.id,
        project_id=clima.project_id,
        meeting_date=today - timedelta(days=35),
        meeting_time=time(14, 0),
        location="Laboratório de Ciências",
        agenda="Validação da calibração do BME280 e início da coleta de 30 dias",
        status="realizada",
    )
    m_final = Meeting(
        group_id=clima.id,
        project_id=clima.project_id,
        meeting_date=today - timedelta(days=20),
        meeting_time=time(10, 0),
        location="Pátio Central",
        agenda="Apresentação final dos dados meteorológicos e fechamento do artigo",
        status="realizada",
    )
    db.session.add(m_mid)
    db.session.add(m_final)
    meetings.append(m_mid)
    meetings.append(m_final)
    db.session.flush()
    return meetings


def _seed_activities(groups, students):
    today = date.today()
    logs = [
        (0, 0, "Soldamos os suportes da base do braço em acrílico 5 mm.", "Dificuldade no alinhamento dos furos.", "Instalar o primeiro servo.", 35),
        (0, 1, "Testamos o movimento do servo com código de exemplo.", None, "Montar o segundo eixo.", 18),
        (0, 2, "Modelamos a garra no Tinkercad e exportamos STL para impressão 3D.", "Impressora com warping na primeira tentativa.", "Montar garra no eixo 3.", 10),
        (1, 3, "Instalamos o sensor DHT22 e validamos leituras no Serial Monitor.", "Fios muito curtos.", "Adicionar sensor de umidade do solo.", 25),
        (1, 4, "Configuramos bomba peristáltica acionada por relé quando umidade < 35%.", None, "Integrar dashboard Node-RED.", 12),
        (2, 6, "Calibramos os 5 sensores IR no piso da sala.", "Reflexo da luz interfere em um sensor.", "Implementar correção no código.", 20),
        (2, 7, "Implementamos PID com Kp=0,8 e reduzimos tempo de volta de 14,3 s para 12,1 s.", None, "Testar em pista oficial.", 5),
        (3, 9, "Levantamos 12 referências sobre microclima escolar e sensores BME280.", None, "Definir protocolo de coleta.", 80),
        (3, 9, "Instalamos a estação no pátio e iniciamos log automático a cada 5 minutos.", "Caixa acumulava condensação interna.", "Adicionar silica gel e fenda de ventilação.", 44),
        (3, 0, "Validamos sensor contra termohigrômetro de referência em 48 pontos.", "Erro máximo de +0,9 °C ao meio-dia.", "Aplicar calibração linear no firmware.", 50),
        (3, 1, "Exportamos 30 dias de CSV (8.640 registros) e calculamos médias por período.", None, "Montar gráficos para apresentação final.", 18),
        (3, 1, "Correlacionamos temperatura e umidade: r = -0,68 (p < 0,01, n = 8.640).", None, "Redigir seção IV do artigo IEEE.", 14),
        (3, 0, "Testamos diferença térmica manhã/tarde: ΔT médio = 3,3 °C (IC 95%: 2,9–3,7).", None, "Confirmar hipótese no manuscrito.", 12),
        (3, 9, "Preparamos poster A0 e roteiro de apresentação de 8 min para feira de ciências.", None, "Submeter rascunho ao orientador.", 8),
        (5, 5, "Coletamos 120 fotos de garrafas PET para o dataset.", None, "Treinar modelo inicial.", 15),
        (5, 6, "Treinamos classificador Teachable Machine: acurácia validação 87,3%.", "Confusão entre alumínio e metal pintado.", "Coletar mais amostras de metal.", 6),
    ]
    for group_idx, student_idx, desc, diff, nxt, days_ago in logs:
        g = groups[group_idx]
        db.session.add(ActivityLog(
            group_id=g.id,
            project_id=g.project_id,
            student_id=students[student_idx].id,
            activity_date=today - timedelta(days=days_ago),
            description=desc,
            difficulties=diff,
            next_steps=nxt,
        ))
    db.session.flush()


def _seed_evidences(groups, students, meetings):
    from flask import current_app

    from app.seed_media import ensure_seed_media

    media = ensure_seed_media(current_app.config["UPLOAD_FOLDER"])
    today = datetime.now()
    evidences_data = [
        # Grupo Atlas — Braço
        {"group_idx": 0, "student_idx": 0, "meeting_idx": 0, "title": "Base em acrílico — protótipo mecânico",
         "description": "Base 5 mm, 3 servos MG996R. Alcance: 24,8 cm. Erro posicionamento: 1,8 cm.",
         "evidence_type": "prototipo", "schedule_title": "Montagem da base e eixo 1",
         "observations": "Dentro da meta de 2 cm.", "days_ago": 35},
        {"group_idx": 0, "student_idx": 1, "meeting_idx": None, "title": "Teste repetibilidade eixo 1",
         "description": "10 ciclos 0°–180°–0°. Desvio padrão angular: 1,2°. Consumo pico: 1,8 A.",
         "evidence_type": "teste", "schedule_title": "Montagem do braço e garra", "days_ago": 18},
        {"group_idx": 0, "student_idx": 2, "meeting_idx": None, "title": "Modelo CAD da garra",
         "description": "Garra 2 dedos, abertura 4 cm, arquivo STEP exportado para impressão 3D.",
         "evidence_type": "cad", "schedule_title": "Montagem do braço e garra",
         "external_link": "https://exemplo.local/garra-atlas.step", "days_ago": 12},
        # Grupo Verde — Estufa
        {"group_idx": 1, "student_idx": 3, "meeting_idx": 1, "title": "Estrutura estufa PVC",
         "description": "Volume 80×50×60 cm. Perda inicial de umidade corrigida com silicone nas juntas.",
         "evidence_type": "foto", "schedule_title": "Montagem da estrutura da estufa",
         "external_link": "https://exemplo.local/estufa-diagrama", "days_ago": 28},
        {"group_idx": 1, "student_idx": 4, "meeting_idx": None, "title": "Leituras DHT22 — 7 dias",
         "description": "Temperatura interna média 26,4 °C. Umidade 58–72%. 168 amostras horárias.",
         "evidence_type": "documento", "schedule_title": "Instalação dos sensores", "days_ago": 14},
        # Grupo Turbo — Seguidor
        {"group_idx": 2, "student_idx": 6, "meeting_idx": 2, "title": "Chassi seguidor de linha",
         "description": "Diferencial 2× TT. Tempo volta pista 4 m: 14,3 s (bang-bang).",
         "evidence_type": "prototipo", "schedule_title": "Chassi e motores", "days_ago": 22},
        {"group_idx": 2, "student_idx": 7, "meeting_idx": None, "title": "PID básico — melhoria 15%",
         "description": "Com Kp=0,8 tempo caiu para 12,1 s. Overshoot em curva 90°: 2,3 cm.",
         "evidence_type": "teste", "schedule_title": "Sensores IR e calibração", "days_ago": 6},
        # Grupo Clima — Estação Meteorológica (artigo IEEE)
        {"group_idx": 3, "student_idx": 9, "meeting_idx": None, "title": "Fichamento bibliográfico — 12 referências",
         "description": "Revisão de microclima urbano, sensores BME280 e projetos escolares similares [1]–[3].",
         "evidence_type": "documento", "schedule_title": "Revisão bibliográfica",
         "observations": "Base para seção II do artigo.", "days_ago": 82},
        {"group_idx": 3, "student_idx": 9, "meeting_idx": None, "title": "Esquema elétrico validado",
         "description": "BME280 I2C 0x76, LCD 16×2, Arduino Nano. Consumo médio 42 mA / pico 68 mA.",
         "evidence_type": "documento", "schedule_title": "Esquema elétrico",
         "observations": "Aprovado pelo professor de física.", "days_ago": 75},
        {"group_idx": 3, "student_idx": 0, "meeting_idx": 4, "title": "Calibração BME280 — 48 pontos",
         "description": "Erro temperatura: +0,4 °C (σ=0,3). Erro umidade: +2,1% UR (σ=1,4). R²=0,97.",
         "evidence_type": "teste", "schedule_title": "Montagem do protótipo",
         "observations": "Offset aplicado no firmware.", "days_ago": 52,
         "attachments": [
             {"file": media["seed_clima_calibracao.jpg"], "type": "foto", "caption": "Tabela de calibração e regressão linear (R²=0,97)."},
         ]},
        {"group_idx": 3, "student_idx": 0, "meeting_idx": None, "title": "Encapsulamento IP54 instalado",
         "description": "Caixa ABS no pátio, orientação norte, altura 1,5 m. Operação contínua 72 h sem falha.",
         "evidence_type": "foto", "schedule_title": "Montagem do protótipo",
         "observations": "Ventilação lateral eliminou condensação.", "days_ago": 48,
         "attachments": [
             {"file": media["seed_clima_estacao.jpg"], "type": "foto", "caption": "Estação meteorológica no pátio central com encapsulamento IP54."},
         ]},
        {"group_idx": 3, "student_idx": 1, "meeting_idx": 4, "title": "Início coleta 30 dias — dia 1",
         "description": "Logging 5 min ativado. Pressão média 1013 hPa. T inicial 21,8 °C, UR 63%.",
         "evidence_type": "documento", "schedule_title": "Instalação de campo e coleta", "days_ago": 40},
        {"group_idx": 3, "student_idx": 1, "meeting_idx": None, "title": "Dataset completo — 8.640 registros",
         "description": "T manhã (6h–12h): 22,1±1,2 °C. T tarde (12h–18h): 25,4±1,5 °C. ΔT=3,3 °C. UR manhã 61%, tarde 48%.",
         "evidence_type": "documento", "schedule_title": "Instalação de campo e coleta",
         "external_link": "https://exemplo.local/dataset-meteorologico-escola.csv",
         "observations": "CSV público para turmas de ciências.", "days_ago": 25,
         "attachments": [
             {"file": media["seed_clima_temp_barras.png"], "type": "documento", "caption": "Comparativo de temperatura média entre período matutino e vespertino."},
         ]},
        {"group_idx": 3, "student_idx": 0, "meeting_idx": None, "title": "Correlação Pearson T × UR",
         "description": "r = -0,68 (n=8.640, p<0,01). Confirma hipótese de correlação inversa significativa.",
         "evidence_type": "documento", "schedule_title": "Análise estatística",
         "observations": "Resultado central do artigo IEEE.", "days_ago": 18,
         "attachments": [
             {"file": media["seed_clima_scatter_t_ur.png"], "type": "documento", "caption": "Dispersão T × UR com reta de tendência (r = −0,68)."},
         ]},
        {"group_idx": 3, "student_idx": 9, "meeting_idx": None, "title": "Teste t pareado manhã vs tarde",
         "description": "t(29)=8,4, p<0,001 para temperatura. Diferença média 3,3 °C (IC95%: 2,9–3,7).",
         "evidence_type": "documento", "schedule_title": "Análise estatística",
         "observations": "Valida hipótese de ΔT ≈ 3 °C.", "days_ago": 16},
        {"group_idx": 3, "student_idx": 0, "meeting_idx": None, "title": "Histogramas e gráficos de dispersão",
         "description": "12 figuras exportadas (Calc): distribuição T, UR e scatter T×UR por semana.",
         "evidence_type": "documento", "schedule_title": "Análise estatística", "days_ago": 14,
         "attachments": [
             {"file": media["seed_clima_temp_barras.png"], "type": "documento", "caption": "Distribuição semanal de temperatura (manhã vs tarde)."},
             {"file": media["seed_clima_scatter_t_ur.png"], "type": "documento", "caption": "Gráfico de dispersão T × UR por semana."},
         ]},
        {"group_idx": 3, "student_idx": 1, "meeting_idx": 5, "title": "Apresentação Feira de Ciências 2025",
         "description": "Poster A0, demo ao vivo, menção honrosa. Nota banca: 9,2/10.",
         "evidence_type": "apresentacao", "schedule_title": "Redação científica e feira",
         "observations": "Material base do manuscrito IEEE.", "days_ago": 10,
         "attachments": [
             {"file": media["seed_clima_poster_feira.jpg"], "type": "foto", "caption": "Poster A0 apresentado na Feira de Ciências 2025."},
         ]},
        {"group_idx": 3, "student_idx": 9, "meeting_idx": None, "title": "Rascunho IEEE v1 — revisão orientador",
         "description": "Manuscrito 6 páginas: Abstract, Index Terms, seções I–V e 8 referências.",
         "evidence_type": "documento", "schedule_title": "Redação científica e feira",
         "external_link": "https://exemplo.local/rascunho-ieee-estacao-meteorologica.docx", "days_ago": 7},
        {"group_idx": 3, "student_idx": 0, "meeting_idx": None, "title": "Pressão atmosférica — série temporal",
         "description": "Média 1012,8 hPa (σ=2,1). Queda de 4 hPa associada a chuva registrada em 2 dias.",
         "evidence_type": "documento", "schedule_title": "Instalação de campo e coleta", "days_ago": 20,
         "attachments": [
             {"file": media["seed_clima_pressao_serie.png"], "type": "documento", "caption": "Série temporal de pressão atmosférica com queda associada a evento de chuva."},
         ]},
        # Grupo Vision — IA
        {"group_idx": 5, "student_idx": 5, "meeting_idx": None, "title": "Dataset 360 imagens — 3 classes",
         "description": "120 img/classe: plástico, metal, papel. Split 80/20. Augmentação horizontal.",
         "evidence_type": "codigo", "schedule_title": "Coleta de imagens",
         "external_link": "https://github.com/exemplo/clube-lixo-ia", "days_ago": 12},
        {"group_idx": 5, "student_idx": 6, "meeting_idx": None, "title": "Matriz confusão — acurácia 87,3%",
         "description": "Precisão: plástico 89%, metal 84%, papel 89%. F1-macro=0,87.",
         "evidence_type": "teste", "schedule_title": "Treinamento do modelo", "days_ago": 5},
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
            created_at=today - timedelta(days=ev_data.get("days_ago", 5)),
        )
        db.session.add(ev)
        db.session.flush()

        attachments = ev_data.get("attachments") or []
        for i, att_data in enumerate(attachments):
            att = EvidenceAttachment(
                evidence_id=ev.id,
                file_path=att_data["file"],
                attachment_type=att_data.get("type", "foto"),
                caption=att_data.get("caption"),
                sort_order=i,
            )
            db.session.add(att)
        if attachments:
            ev.file_path = attachments[0]["file"]
    db.session.flush()


def _seed_minutes(meetings, students):
    """Cria atas para as reuniões realizadas."""
    summaries = {
        4: (
            "Reunião intermediária Grupo Clima: calibração BME280 aprovada (erro < 1 °C). "
            "Iniciada coleta contínua de 30 dias no pátio central.",
            "Manter logging a cada 5 min. Revisar vedação da caixa após chuva prevista.",
        ),
        5: (
            "Reunião final Grupo Clima: apresentados r = -0,68 (T×UR) e ΔT manhã/tarde = 3,3 °C. "
            "Hipótese confirmada estatisticamente (p < 0,01).",
            "Submeter rascunho IEEE à orientadora. Publicar dataset CSV no repositório escolar.",
        ),
    }
    for idx, meeting in enumerate(meetings):
        if idx in summaries:
            summary, decisions = summaries[idx]
        else:
            summary = (
                f"Reunião do {meeting.group.name}: revisamos o progresso do projeto "
                f"{meeting.project.title}."
            )
            decisions = "Manter o cronograma atual. Próxima entrega em duas semanas."

        minute = MeetingMinute(
            meeting_id=meeting.id,
            summary=summary,
            decisions=decisions,
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
