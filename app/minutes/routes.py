from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import role_required
from app.extensions import db
from app.models import Meeting, MeetingAttendance, MeetingMinute, MinuteTask, Student

minutes_bp = Blueprint("minutes", __name__)


@minutes_bp.route("/")
@login_required
def index():
    minutes = MeetingMinute.query.order_by(MeetingMinute.created_at.desc()).all()
    return render_template("minutes/index.html", minutes=minutes)


@minutes_bp.route("/new/<int:meeting_id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader")
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
def view(minute_id):
    minute = db.get_or_404(MeetingMinute, minute_id)
    return render_template("minutes/view.html", minute=minute)
