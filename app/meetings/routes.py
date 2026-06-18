from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import role_required
from app.extensions import db
from app.models import Group, Meeting
from app.utils import parse_date, parse_time, user_groups

meetings_bp = Blueprint("meetings", __name__)

STATUSES = ["agendada", "realizada", "cancelada"]


@meetings_bp.route("/")
@login_required
def index():
    if current_user.is_admin:
        meetings = Meeting.query.order_by(Meeting.meeting_date.desc()).all()
    else:
        group_ids = [g.id for g in user_groups(current_user)]
        meetings = Meeting.query.filter(Meeting.group_id.in_(group_ids)).order_by(Meeting.meeting_date.desc()).all()
    return render_template("meetings/index.html", meetings=meetings)


@meetings_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader")
def create():
    groups = user_groups(current_user) if not current_user.is_admin else Group.query.all()

    if request.method == "POST":
        group_id = request.form.get("group_id")
        meeting_date = parse_date(request.form.get("meeting_date"))

        if not group_id or not meeting_date:
            flash("Grupo e data são obrigatórios.", "error")
            return render_template("meetings/form.html", meeting=None, groups=groups, statuses=STATUSES)

        group = db.get_or_404(Group, int(group_id))
        meeting = Meeting(
            group_id=group.id,
            project_id=group.project_id,
            meeting_date=meeting_date,
            meeting_time=parse_time(request.form.get("meeting_time")),
            location=request.form.get("location", "").strip(),
            agenda=request.form.get("agenda", "").strip(),
            status=request.form.get("status", "agendada"),
        )
        db.session.add(meeting)
        db.session.commit()
        flash("Reunião agendada.", "success")
        return redirect(url_for("meetings.index"))

    return render_template("meetings/form.html", meeting=None, groups=groups, statuses=STATUSES)


@meetings_bp.route("/<int:meeting_id>")
@login_required
def view(meeting_id):
    meeting = db.get_or_404(Meeting, meeting_id)
    return render_template("meetings/view.html", meeting=meeting)


@meetings_bp.route("/<int:meeting_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader")
def edit(meeting_id):
    meeting = db.get_or_404(Meeting, meeting_id)
    groups = user_groups(current_user) if not current_user.is_admin else Group.query.all()

    if request.method == "POST":
        meeting.meeting_date = parse_date(request.form.get("meeting_date")) or meeting.meeting_date
        meeting.meeting_time = parse_time(request.form.get("meeting_time")) or meeting.meeting_time
        meeting.location = request.form.get("location", "").strip()
        meeting.agenda = request.form.get("agenda", "").strip()
        meeting.status = request.form.get("status", meeting.status)
        db.session.commit()
        flash("Reunião atualizada.", "success")
        return redirect(url_for("meetings.view", meeting_id=meeting.id))

    return render_template("meetings/form.html", meeting=meeting, groups=groups, statuses=STATUSES)


@meetings_bp.route("/<int:meeting_id>/delete", methods=["POST"])
@login_required
@role_required("admin", "leader")
def delete(meeting_id):
    meeting = db.get_or_404(Meeting, meeting_id)
    db.session.delete(meeting)
    db.session.commit()
    flash("Reunião removida.", "success")
    return redirect(url_for("meetings.index"))
