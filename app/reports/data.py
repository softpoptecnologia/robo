from datetime import date, datetime, timedelta

from flask import request
from flask_login import current_user
from sqlalchemy import func

from app.extensions import db
from app.filters import (
    apply_date_range,
    apply_group_id,
    apply_group_scope,
    apply_project_id,
    apply_status,
)
from app.models import (
    ActivityLog,
    Evidence,
    Group,
    Meeting,
    MeetingAttendance,
    MeetingMinute,
    Project,
    ScheduleItem,
    Student,
)


def _filter_summary(parts):
    return " · ".join(parts) if parts else "Nenhum filtro aplicado"


def _ctx(**extra):
    from app.filters import filter_context

    ctx = filter_context()
    ctx["generated_at"] = datetime.now()
    ctx.update(extra)
    return ctx


def projects_data():
    query = Project.query
    query = apply_status(query, Project.status)
    query = apply_project_id(query, Project.id)
    items = query.order_by(Project.status, Project.title).all()

    parts = []
    if request.args.get("status"):
        parts.append(f"Status: {request.args['status']}")
    if request.args.get("project_id"):
        proj = db.session.get(Project, int(request.args["project_id"]))
        if proj:
            parts.append(f"Projeto: {proj.title}")

    return items, _filter_summary(parts)


def groups_data():
    query = Group.query
    query = apply_status(query, Group.status, default="ativo")
    query = apply_group_id(query, Group.id)
    query = apply_project_id(query, Group.project_id)
    query = apply_group_scope(query, Group.id)

    items = query.all()
    report = []
    for group in items:
        total_steps = len(group.schedule_items)
        done = sum(1 for s in group.schedule_items if s.status == "concluida")
        overdue = sum(1 for s in group.schedule_items if s.status == "atrasada")
        report.append({
            "group": group,
            "total_steps": total_steps,
            "done": done,
            "overdue": overdue,
            "progress": round((done / total_steps) * 100, 1) if total_steps else 0,
        })

    parts = [f"Status: {request.args.get('status', 'ativo')}"]
    if request.args.get("project_id"):
        proj = db.session.get(Project, int(request.args["project_id"]))
        if proj:
            parts.append(f"Projeto: {proj.title}")
    if request.args.get("group_id"):
        grp = db.session.get(Group, int(request.args["group_id"]))
        if grp:
            parts.append(f"Grupo: {grp.name}")

    return report, _filter_summary(parts)


def participation_data():
    group_id = request.args.get("group_id")
    below_percent = request.args.get("below_percent")

    students_query = Student.query.filter_by(status="ativo")
    if group_id:
        students_query = students_query.filter(Student.groups.any(id=int(group_id)))
    students = students_query.order_by(Student.name).all()

    data = []
    for student in students:
        meetings_query = MeetingAttendance.query.join(Meeting).filter(
            MeetingAttendance.student_id == student.id,
            Meeting.status == "realizada",
        )
        if group_id:
            meetings_query = meetings_query.filter(Meeting.group_id == int(group_id))

        total = meetings_query.count()
        present = meetings_query.filter(MeetingAttendance.present.is_(True)).count()
        absent = total - present
        pct = round((present / total) * 100, 1) if total else 100

        if below_percent and pct >= float(below_percent):
            continue

        activities_query = ActivityLog.query.filter_by(student_id=student.id)
        if group_id:
            activities_query = activities_query.filter_by(group_id=int(group_id))

        data.append({
            "student": student,
            "total_meetings": total,
            "present": present,
            "absent": absent,
            "percent": pct,
            "activities": activities_query.count(),
        })

    parts = []
    if group_id:
        grp = db.session.get(Group, int(group_id))
        if grp:
            parts.append(f"Grupo: {grp.name}")
    if below_percent:
        parts.append(f"Abaixo de {below_percent}%")

    return data, _filter_summary(parts)


def activities_data():
    group_query = db.session.query(Group.name, func.count(ActivityLog.id)).join(
        ActivityLog, ActivityLog.group_id == Group.id
    )
    group_query = apply_group_id(group_query, Group.id)
    group_query = apply_group_scope(group_query, Group.id)
    by_group = group_query.group_by(Group.id).all()

    recent_query = ActivityLog.query
    recent_query = apply_group_id(recent_query, ActivityLog.group_id)
    recent_query = apply_group_scope(recent_query, ActivityLog.group_id)
    recent_query = apply_date_range(recent_query, ActivityLog.activity_date)

    limit = int(request.args.get("limit", 20))
    recent = recent_query.order_by(ActivityLog.activity_date.desc()).limit(limit).all()

    parts = []
    if request.args.get("group_id"):
        grp = db.session.get(Group, int(request.args["group_id"]))
        if grp:
            parts.append(f"Grupo: {grp.name}")
    if request.args.get("date_from"):
        parts.append(f"De: {request.args['date_from']}")
    if request.args.get("date_to"):
        parts.append(f"Até: {request.args['date_to']}")
    parts.append(f"Limite: {limit}")

    return by_group, recent, _filter_summary(parts)


def minutes_data():
    query = MeetingMinute.query.join(Meeting)
    query = apply_group_id(query, Meeting.group_id)
    query = apply_group_scope(query, Meeting.group_id)
    query = apply_date_range(query, Meeting.meeting_date)
    items = query.order_by(MeetingMinute.created_at.desc()).all()

    parts = []
    if request.args.get("group_id"):
        grp = db.session.get(Group, int(request.args["group_id"]))
        if grp:
            parts.append(f"Grupo: {grp.name}")
    if request.args.get("date_from"):
        parts.append(f"De: {request.args['date_from']}")
    if request.args.get("date_to"):
        parts.append(f"Até: {request.args['date_to']}")

    return items, _filter_summary(parts)


def _evidence_query(project_id, group_id):
    query = Evidence.query
    if project_id:
        query = query.filter(Evidence.project_id == int(project_id))
    if group_id:
        query = query.filter(Evidence.group_id == int(group_id))
    if not current_user.is_admin:
        from app.utils import user_group_ids

        group_ids = user_group_ids(current_user)
        if group_ids:
            query = query.filter(Evidence.group_id.in_(group_ids))
        else:
            query = query.filter(False)
    return query


def evolution_data():
    days = int(request.args.get("days", 30))
    since = date.today() - timedelta(days=days)
    project_id = request.args.get("project_id")
    group_id = request.args.get("group_id")

    evidence_query = _evidence_query(project_id, group_id)

    by_group = (
        db.session.query(Group.name, func.count(Evidence.id))
        .join(Evidence, Evidence.group_id == Group.id)
    )
    if project_id:
        by_group = by_group.filter(Evidence.project_id == int(project_id))
    if group_id:
        by_group = by_group.filter(Evidence.group_id == int(group_id))
    if not current_user.is_admin:
        from app.utils import user_group_ids

        group_ids = user_group_ids(current_user)
        if group_ids:
            by_group = by_group.filter(Evidence.group_id.in_(group_ids))
        else:
            by_group = by_group.filter(False)
    by_group = by_group.group_by(Group.id).all()

    recent = evidence_query.order_by(Evidence.created_at.desc()).limit(15).all()

    groups_query = Group.query.filter_by(status="ativo")
    groups_query = apply_project_id(groups_query, Group.project_id)
    groups_query = apply_group_id(groups_query, Group.id)
    groups_query = apply_group_scope(groups_query, Group.id)

    inactive_groups = []
    for group in groups_query.all():
        last = (
            evidence_query.filter(Evidence.group_id == group.id)
            .order_by(Evidence.created_at.desc())
            .first()
        )
        if not last or last.created_at.date() < since:
            inactive_groups.append(group)

    top_query = (
        db.session.query(Student.name, func.count(Evidence.id).label("total"))
        .join(Evidence, Evidence.student_id == Student.id)
    )
    if project_id:
        top_query = top_query.filter(Evidence.project_id == int(project_id))
    if group_id:
        top_query = top_query.filter(Evidence.group_id == int(group_id))
    if not current_user.is_admin:
        from app.utils import user_group_ids

        group_ids = user_group_ids(current_user)
        if group_ids:
            top_query = top_query.filter(Evidence.group_id.in_(group_ids))
        else:
            top_query = top_query.filter(False)
    top_contributors = top_query.group_by(Student.id).order_by(func.count(Evidence.id).desc()).limit(10).all()

    schedule_query = ScheduleItem.query
    schedule_query = apply_group_id(schedule_query, ScheduleItem.group_id)
    schedule_query = apply_project_id(schedule_query, ScheduleItem.project_id)
    schedule_query = apply_group_scope(schedule_query, ScheduleItem.group_id)

    schedule_vs_evidence = []
    for item in schedule_query.order_by(ScheduleItem.end_date).limit(20).all():
        ev_count = evidence_query.filter(Evidence.schedule_item_id == item.id).count()
        schedule_vs_evidence.append({"item": item, "evidence_count": ev_count})

    parts = [f"Período: últimos {days} dias"]
    if project_id:
        proj = db.session.get(Project, int(project_id))
        if proj:
            parts.append(f"Projeto: {proj.title}")
    if group_id:
        grp = db.session.get(Group, int(group_id))
        if grp:
            parts.append(f"Grupo: {grp.name}")

    return {
        "by_group": by_group,
        "recent": recent,
        "inactive_groups": inactive_groups,
        "top_contributors": top_contributors,
        "schedule_vs_evidence": schedule_vs_evidence,
        "days": days,
        "filter_summary": _filter_summary(parts),
    }
