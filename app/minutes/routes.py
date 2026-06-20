from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import permission_required
from app.extensions import db
from app.filters import (
    apply_date_range,
    apply_group_id,
    apply_group_scope,
    filter_context,
)
from app.models import Group, Meeting, MeetingAttendance, MeetingMinute, MinuteTask, Student
from app.pagination import paginate_or_all
from app.pdf_utils import pdf_or_html

minutes_bp = Blueprint("minutes", __name__)


def _filter_summary():
    parts = []
    if request.args.get("group_id"):
        group = db.session.get(Group, int(request.args["group_id"]))
        if group:
            parts.append(f"Grupo: {group.name}")
    if request.args.get("date_from"):
        parts.append(f"De: {request.args['date_from']}")
    if request.args.get("date_to"):
        parts.append(f"Até: {request.args['date_to']}")
    return " · ".join(parts) if parts else "Nenhum filtro aplicado"


@minutes_bp.route("/")
@login_required
@permission_required("minutes.view")
def index():
    query = MeetingMinute.query.join(Meeting)
    query = apply_group_scope(query, Meeting.group_id)
    query = apply_group_id(query, Meeting.group_id)
    query = apply_date_range(query, Meeting.meeting_date)
    query = query.order_by(MeetingMinute.created_at.desc())
    pagination, minutes = paginate_or_all(query)

    ctx = filter_context()
    ctx.update({
        "minutes": minutes,
        "pagination": pagination,
        "filter_summary": _filter_summary(),
        "generated_at": datetime.now(),
    })
    return pdf_or_html(
        "pdf/minutes_list.html",
        "minutes/index.html",
        "atas.pdf",
        **ctx,
    )


@minutes_bp.route("/new/<int:meeting_id>", methods=["GET", "POST"])
@login_required
@permission_required("minutes.manage")
def create(meeting_id):
    meeting = db.get_or_404(Meeting, meeting_id)
    students = meeting.group.members

    if meeting.minute:
        flash("Esta reunião já possui ata.", "warning")
        return redirect(url_for("minutes.view", minute_id=meeting.minute.id))

    if request.method == "POST":
        summary = request.form.get("summary", "").strip()
        if not summary:
            flash("Resumo é obrigatório.", "error")
            return render_template("minutes/form.html", meeting=meeting, students=students)

        minute = MeetingMinute(
            meeting_id=meeting.id,
            summary=summary,
            decisions=request.form.get("decisions", "").strip(),
            notes=request.form.get("notes", "").strip(),
        )
        meeting.status = "realizada"
        db.session.add(minute)
        db.session.flush()

        for student in students:
            present = request.form.get(f"present_{student.id}") == "on"
            attendance = MeetingAttendance(
                meeting_id=meeting.id,
                student_id=student.id,
                present=present,
            )
            db.session.add(attendance)

        task_descriptions = request.form.getlist("task_description")
        task_responsibles = request.form.getlist("task_responsible")
        for desc, resp in zip(task_descriptions, task_responsibles):
            if desc.strip():
                task = MinuteTask(
                    minute_id=minute.id,
                    description=desc.strip(),
                    responsible_id=int(resp) if resp else None,
                )
                db.session.add(task)

        db.session.commit()
        flash("Ata registrada.", "success")
        return redirect(url_for("minutes.view", minute_id=minute.id))

    return render_template("minutes/form.html", meeting=meeting, students=students)


@minutes_bp.route("/<int:minute_id>")
@login_required
@permission_required("minutes.view")
def view(minute_id):
    minute = db.get_or_404(MeetingMinute, minute_id)
    return render_template("minutes/view.html", minute=minute)
