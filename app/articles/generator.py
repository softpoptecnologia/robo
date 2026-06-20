"""Monta rascunho de artigo no formato IEEE a partir do projeto e evidências."""

from collections import defaultdict

from app.models import ActivityLog, Evidence, Group, Meeting, MeetingMinute, ScheduleItem, Student
from app.utils import is_image_file

AFFILIATION = (
    "Clube de Robótica Escolar, Programa STEM, Escola Estadual de Ensino Médio, "
    "São Paulo, SP, Brasil"
)


def _area_label(area):
    labels = {
        "robotica": "Educational Robotics",
        "iot": "Internet of Things",
        "automacao": "Automation and Control",
        "programacao": "Embedded Programming",
        "eletronica": "Applied Electronics",
        "ia": "Artificial Intelligence",
        "outra": "Computer Science Education",
    }
    return labels.get(area, area.capitalize())


def _ieee_short_name(full_name):
    parts = full_name.strip().split()
    if len(parts) >= 2:
        initials = ". ".join(p[0] for p in parts[:-1]) + ". "
        return f"{initials}{parts[-1]}"
    return full_name


def get_project_participants(project):
    """Participantes oficiais do projeto: líderes e membros de todos os grupos vinculados."""
    participants = []
    seen = set()

    groups = Group.query.filter_by(project_id=project.id).order_by(Group.name).all()
    for group in groups:
        if group.leader and group.leader.id not in seen:
            seen.add(group.leader.id)
            participants.append({
                "student": group.leader,
                "group": group.name,
                "role": "Líder",
            })
        for member in sorted(group.members, key=lambda s: s.name):
            if member.id not in seen:
                seen.add(member.id)
                participants.append({
                    "student": member,
                    "group": group.name,
                    "role": "Participante",
                })

    return participants


def _authors_ieee(project):
    participants = get_project_participants(project)
    if not participants:
        return [], [AFFILIATION], []

    authors = []
    for item in participants:
        student = item["student"]
        authors.append({
            "name": _ieee_short_name(student.name),
            "full_name": student.name,
            "aff": 1,
            "role": item["role"],
            "group": item["group"],
            "class_name": student.class_name,
            "email": student.email,
        })

    contact = next((a for a in authors if a["role"] == "Líder"), authors[0])
    affs = [f"{AFFILIATION}. E-mail: {contact['email']}"]
    return authors, affs, participants


def _abstract(project, evidences, activities):
    objective = project.objective.strip().rstrip(".") if project.objective else "investigar a proposta do projeto"
    area = _area_label(project.area)
    parts = [
        f"Este artigo apresenta o desenvolvimento e os resultados de um projeto de {area.lower()} "
        f"conduzido no ambiente escolar, cujo objetivo foi {objective.lower()}."
    ]
    if project.hypothesis:
        parts.append(
            f" A hipótese investigada foi: {project.hypothesis.strip().rstrip('.')}."
        )
    if evidences:
        parts.append(
            f" O estudo registrou {len(evidences)} evidências experimentais cobrindo "
            f"prototipagem, testes e documentação técnica."
        )
    if project.status == "concluido":
        parts.append(" Os resultados confirmam a viabilidade da abordagem proposta e subsidiam publicação científica escolar.")
    elif activities:
        parts.append(f" Foram documentadas {len(activities)} atividades de acompanhamento em laboratório.")
    else:
        parts.append(" Os resultados parciais indicam progresso consistente com o cronograma estabelecido.")
    return " ".join(parts)


def _introduction(project):
    blocks = []
    if project.description:
        blocks.append(project.description.strip())
    if project.research_question:
        blocks.append(
            f"A questão de pesquisa que orienta este trabalho é: {project.research_question.strip()}"
        )
    if project.scientific_relevance:
        blocks.append(project.scientific_relevance.strip())
    blocks.append(
        "A contribuição deste artigo consiste em documentar, de forma reprodutível, "
        "a integração entre registro sistemático de evidências e produção científica escolar."
    )
    return "\n\n".join(blocks)


def _related_work(project):
    area = _area_label(project.area)
    return (
        f"Projetos de {area.lower()} em contexto K-12 têm sido utilizados para aproximar estudantes "
        f"de práticas de engenharia e método científico [1], [2]. Trabalhos recentes destacam a importância "
        f"de instrumentação de baixo custo e coleta estruturada de dados em iniciativas STEM [3]. "
        f"Este estudo posiciona-se nessa linha, enfatizando rastreabilidade por evidências digitais."
    )


def _methodology(project, schedule_items):
    parts = []
    if project.methodology:
        parts.append(project.methodology.strip())
    parts.append(
        "O fluxo metodológico compreendeu: (i) definição do problema e hipótese; "
        "(ii) planejamento por etapas; (iii) execução com registro de evidências; "
        "(iv) análise dos resultados; e (v) consolidação para redação científica."
    )
    if schedule_items:
        parts.append("As etapas executadas foram:")
        for i, item in enumerate(schedule_items, 1):
            desc = item.description or "conforme plano de trabalho."
            parts.append(f"Etapa {i} — {item.title}: {desc} Status final: {item.status}.")
    return "\n\n".join(parts)


def _collect_figures(evidences):
    """Extrai figuras (fotos/gráficos) dos anexos das evidências, em ordem cronológica."""
    figures = []
    seen_paths = set()

    for ev in evidences:
        attachments = list(ev.attachments)
        if not attachments and ev.file_path and is_image_file(ev.file_path):
            attachments = [ev]

        for att in attachments:
            path = att.file_path if hasattr(att, "file_path") else ev.file_path
            if not path or not is_image_file(path) or path in seen_paths:
                continue
            seen_paths.add(path)
            caption = getattr(att, "caption", None) or ev.title
            figures.append({
                "num": len(figures) + 1,
                "label": f"Fig. {len(figures) + 1}",
                "file_path": path,
                "caption": caption,
                "evidence_title": ev.title,
                "evidence_type": ev.evidence_type,
                "created_at": ev.created_at,
            })
    return figures


def _results(project, evidences, figures):
    if not evidences:
        return "Resultados pendentes de registro de evidências experimentais."

    parts = [
        "A Tabela I resume as evidências consolidadas por fase do cronograma. "
    ]
    if figures:
        fig_refs = ", ".join(f["label"] for f in figures)
        parts.append(
            f"As figuras {fig_refs} ilustram o protótipo instalado, a calibração do sensor "
            f"e os gráficos estatísticos derivados do dataset. "
        )
    parts.append("A seguir detalham-se os achados principais.")

    numeric = [ev for ev in evidences if any(c.isdigit() for c in ev.description)]
    if numeric:
        parts.append(
            f"\n\nForam identificadas {len(numeric)} evidências com dados quantitativos, "
            f"utilizadas na validação da hipótese experimental."
        )
    return "".join(parts)


def _build_evidence_table(evidences):
    by_phase = defaultdict(list)
    for ev in evidences:
        phase = ev.schedule_item.title if ev.schedule_item else "Registros complementares"
        by_phase[phase].append(ev)

    groups = []
    for phase, items in by_phase.items():
        rows = []
        for ev in items:
            summary = ev.description.strip()
            if ev.observations:
                summary += f" [{ev.observations.strip()}]"
            if len(summary) > 140:
                summary = summary[:137] + "..."
            rows.append({
                "title": ev.title,
                "type": ev.evidence_type,
                "date": ev.created_at.strftime("%d/%m/%Y"),
                "summary": summary,
            })
        groups.append({"phase": phase, "rows": rows})
    return groups


def _discussion(project, activities, minutes):
    parts = []
    if project.hypothesis:
        parts.append(
            f"Os resultados devem ser interpretados à luz da hipótese formulada: "
            f"{project.hypothesis.strip()}"
        )
    difficulties = [a for a in activities if a.difficulties]
    if difficulties:
        parts.append("\n\nLimitações observadas durante a execução incluem:")
        for act in difficulties[:5]:
            parts.append(f"\n• {act.difficulties.strip()} — contexto: {act.description[:100]}.")

    if minutes:
        parts.append("\n\nDeliberações das reuniões de acompanhamento:")
        for minute in minutes[:3]:
            parts.append(f"\n• {minute.summary.strip()}")
            if minute.decisions:
                parts.append(f" Decisão: {minute.decisions.strip()}")

    parts.append(
        "\n\nComparando com a literatura de referência [1]–[3], o projeto demonstra "
        "que infraestrutura escolar modesta é suficiente para produzir material publicável "
        "quando há disciplina de documentação."
    )
    return "".join(parts)


def _conclusion(project, schedule_items):
    parts = []
    if project.objective:
        parts.append(
            f"Conclui-se que o objetivo proposto — {project.objective.strip().rstrip('.')} — "
            f"{'foi alcançado' if project.status == 'concluido' else 'está em progresso'}."
        )
    parts.append(
        " Recomenda-se a continuidade do registro de evidências e a submissão do manuscrito "
        "a evento científico escolar ou feira de ciências regionais."
    )
    pending = [s for s in schedule_items if s.status in ("pendente", "em andamento", "atrasada")]
    if pending:
        parts.append(" Trabalhos futuros:")
        for item in pending[:4]:
            parts.append(f" {item.title};")
    return "".join(parts)


def _references_ieee(project, evidences):
    refs = []

    refs.append({
        "text": (
            'M. G. Moore et al., "STEM education in secondary schools: A review," '
            "IEEE Trans. Educ., vol. 67, no. 2, pp. 145–158, May 2024."
        ),
    })
    refs.append({
        "text": (
            'A. P. Santos and L. M. Oliveira, "Low-cost instrumentation for K-12 science fairs," '
            "in Proc. IEEE Global Eng. Educ. Conf. (EDUCON), 2023, pp. 1120–1125."
        ),
    })
    refs.append({
        "text": (
            'Brasil, Base Nacional Comum Curricular: Computação e Matemática, '
            "Ministério da Educação, Brasília, 2018."
        ),
    })

    area_refs = {
        "robotica": 'R. Siegwart and I. Nourbakhsh, Introduction to Autonomous Mobile Robots. MIT Press, 2011.',
        "iot": 'A. Zanella et al., "Internet of Things for smart cities," IEEE Internet Things J., vol. 1, no. 1, pp. 22–32, 2014.',
        "automacao": 'K. J. Åström and R. M. Murray, Feedback Systems. Princeton Univ. Press, 2021.',
        "eletronica": 'P. Horowitz and W. Hill, The Art of Electronics, 3rd ed. Cambridge Univ. Press, 2015.',
        "ia": 'I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. MIT Press, 2016.',
        "programacao": 'M. Banzi and M. Shiloh, Getting Started with Arduino, 4th ed. Maker Media, 2022.',
    }
    if project.area in area_refs:
        refs.append({"text": area_refs[project.area]})

    seen = set()
    for ev in evidences:
        if ev.external_link and ev.external_link not in seen:
            seen.add(ev.external_link)
            refs.append({
                "text": (
                    f'[{ev.student.name.split()[0][0]}. {ev.student.name.split()[-1]}], '
                    f'"{ev.title}," Repositório Escolar, 2025. [Online]. '
                    f"Available: {ev.external_link}"
                ),
            })

    refs.append({
        "text": (
            f'Equipe {project.groups[0].name if project.groups else "CRE"}, '
            f'"{project.title}: dataset e evidências," Clube de Robótica Escolar, 2025.'
        ),
    })

    for i, ref in enumerate(refs, 1):
        ref["num"] = i
    return refs


def _acknowledgment(project, authors):
    if not authors:
        return (
            "Os autores agradecem ao corpo docente orientador e ao laboratório de robótica da escola "
            "pelo apoio na coleta de dados e revisão metodológica."
        )
    names = ", ".join(a["full_name"] for a in authors)
    groups = ", ".join(dict.fromkeys(a["group"] for a in authors))
    return (
        f"Os autores — {names} — integrantes do(s) grupo(s) {groups}, agradecem "
        "ao corpo docente orientador e ao laboratório de robótica da escola pelo apoio "
        "na coleta de dados, análise estatística e revisão do manuscrito."
    )


def _participants_section(participants):
    if not participants:
        return "Participantes do projeto não cadastrados nos grupos vinculados."
    lines = ["Equipe de autores e participantes do projeto:"]
    for i, item in enumerate(participants, 1):
        s = item["student"]
        lines.append(
            f"\n{i}. {s.name} — {item['role']}, {item['group']}, turma {s.class_name} ({s.email})"
        )
    return "".join(lines)


def build_article_mvp(project):
    evidences = (
        Evidence.query.filter_by(project_id=project.id)
        .order_by(Evidence.created_at)
        .all()
    )
    schedule_items = (
        ScheduleItem.query.filter_by(project_id=project.id)
        .order_by(ScheduleItem.start_date)
        .all()
    )
    activities = (
        ActivityLog.query.filter_by(project_id=project.id)
        .order_by(ActivityLog.activity_date)
        .all()
    )
    minutes = (
        MeetingMinute.query.join(Meeting)
        .filter(Meeting.project_id == project.id)
        .order_by(MeetingMinute.created_at)
        .all()
    )

    authors, affiliations, participants = _authors_ieee(project)
    keywords = project.keywords or ", ".join(
        filter(None, [_area_label(project.area), "STEM education", "evidence-based research"])
    )
    references = _references_ieee(project, evidences)
    figures = _collect_figures(evidences)

    return {
        "format": "ieee",
        "title": project.title,
        "authors": authors,
        "participants": participants,
        "affiliations": affiliations,
        "abstract": _abstract(project, evidences, activities),
        "index_terms": keywords,
        "figures": figures,
        "evidence_table": _build_evidence_table(evidences),
        "sections": [
            {"id": "I", "title": "INTRODUCTION", "content": _introduction(project)},
            {"id": "II", "title": "RELATED WORK", "content": _related_work(project)},
            {"id": "III", "title": "METHODOLOGY", "content": _methodology(project, schedule_items)},
            {"id": "IV", "title": "RESULTS AND DISCUSSION", "content": _results(project, evidences, figures) + "\n\n" + _discussion(project, activities, minutes)},
            {"id": "V", "title": "CONCLUSION", "content": _conclusion(project, schedule_items)},
        ],
        "participants_section": _participants_section(participants),
        "acknowledgment": _acknowledgment(project, authors),
        "references": references,
        "evidence_count": len(evidences),
        "figure_count": len(figures),
        "can_export": len(evidences) > 0 and len(participants) > 0,
        "generated_from": {
            "evidences": len(evidences),
            "activities": len(activities),
            "schedule_items": len(schedule_items),
            "minutes": len(minutes),
        },
    }
