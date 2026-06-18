from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required

from app.models import (
    ActivityLog,
    Evidence,
    Group,
    Meeting,
    Project,
    ScheduleItem,
    Student,
    MeetingAttendance,
    MeetingMinute,
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    total_projects = Project.query.count()
    total_groups = Group.query.filter_by(status="ativo").count()
    total_students = Student.query.filter_by(status="ativo").count()
    scheduled_meetings = Meeting.query.filter_by(status="agendada").count()
    overdue_items = ScheduleItem.query.filter(
        ScheduleItem.status.in_(["pendente", "em andamento"]),
        ScheduleItem.end_date < date.today(),
    ).count()

    # Estudantes com baixa participação (< 70% em reuniões realizadas)
    low_participation = []
    for student in Student.query.filter_by(status="ativo").all():
        total = MeetingAttendance.query.join(Meeting).filter(
            MeetingAttendance.student_id == student.id,
            Meeting.status == "realizada",
        ).count()
        if total == 0:
            continue
        present = MeetingAttendance.query.join(Meeting).filter(
            MeetingAttendance.student_id == student.id,
            Meeting.status == "realizada",
            MeetingAttendance.present.is_(True),
        ).count()
        pct = round((present / total) * 100, 1)
        if pct < 70:
            low_participation.append({"student": student, "percent": pct})

    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
    recent_evidences = Evidence.query.order_by(Evidence.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard/index.html",
        total_projects=total_projects,
        total_groups=total_groups,
        total_students=total_students,
        scheduled_meetings=scheduled_meetings,
        overdue_items=overdue_items,
        low_participation=low_participation[:5],
        recent_activities=recent_activities,
        recent_evidences=recent_evidences,
    )
