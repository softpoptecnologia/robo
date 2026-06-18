from datetime import date, timedelta

from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
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

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
@login_required
def index():
    return render_template("reports/index.html")


@reports_bp.route("/projects")
@login_required
def projects():
    items = Project.query.order_by(Project.status, Project.title).all()
    return render_template("reports/projects.html", projects=items)


@reports_bp.route("/groups")
@login_required
def groups():
    items = Group.query.filter_by(status="ativo").all()
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
    return render_template("reports/groups.html", report=report)


@reports_bp.route("/participation")
@login_required
def participation():
    data = []
    for student in Student.query.filter_by(status="ativo").order_by(Student.name).all():
        total = MeetingAttendance.query.join(Meeting).filter(
            MeetingAttendance.student_id == student.id,
            Meeting.status == "realizada",
        ).count()
        present = MeetingAttendance.query.join(Meeting).filter(
            MeetingAttendance.student_id == student.id,
            Meeting.status == "realizada",
            MeetingAttendance.present.is_(True),
        ).count()
        absent = total - present
        pct = round((present / total) * 100, 1) if total else 100
        activities_count = ActivityLog.query.filter_by(student_id=student.id).count()
        data.append({
            "student": student,
            "total_meetings": total,
            "present": present,
            "absent": absent,
            "percent": pct,
            "activities": activities_count,
        })
    return render_template("reports/participation.html", data=data)


@reports_bp.route("/activities")
@login_required
def activities():
    by_group = (
        db.session.query(Group.name, func.count(ActivityLog.id))
        .join(ActivityLog, ActivityLog.group_id == Group.id)
        .group_by(Group.id)
        .all()
    )
    recent = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(20).all()
    return render_template("reports/activities.html", by_group=by_group, recent=recent)


@reports_bp.route("/minutes")
@login_required
def minutes():
    items = MeetingMinute.query.order_by(MeetingMinute.created_at.desc()).all()
    return render_template("reports/minutes.html", minutes=items)


@reports_bp.route("/evolution")
@login_required
def evolution():
    """Relatório de evolução do módulo de evidências."""
    days = int(request.args.get("days", 30))
    since = date.today() - timedelta(days=days)

    by_group = (
        db.session.query(Group.name, func.count(Evidence.id))
        .join(Evidence, Evidence.group_id == Group.id)
        .group_by(Group.id)
        .all()
    )

    recent = Evidence.query.order_by(Evidence.created_at.desc()).limit(15).all()

    inactive_groups = []
    for group in Group.query.filter_by(status="ativo").all():
        last = Evidence.query.filter_by(group_id=group.id).order_by(Evidence.created_at.desc()).first()
        if not last or last.created_at.date() < since:
            inactive_groups.append(group)

    top_contributors = (
        db.session.query(Student.name, func.count(Evidence.id).label("total"))
        .join(Evidence, Evidence.student_id == Student.id)
        .group_by(Student.id)
        .order_by(func.count(Evidence.id).desc())
        .limit(10)
        .all()
    )

    schedule_vs_evidence = []
    for item in ScheduleItem.query.order_by(ScheduleItem.end_date).limit(20).all():
        ev_count = Evidence.query.filter_by(schedule_item_id=item.id).count()
        schedule_vs_evidence.append({"item": item, "evidence_count": ev_count})

    return render_template(
        "reports/evolution.html",
        by_group=by_group,
        recent=recent,
        inactive_groups=inactive_groups,
        top_contributors=top_contributors,
        schedule_vs_evidence=schedule_vs_evidence,
        days=days,
    )
