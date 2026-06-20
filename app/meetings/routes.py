from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import permission_required
from app.extensions import db
from app.filters import (
    apply_date_range,
    apply_group_id,
    apply_group_scope,
    apply_status,
    filter_context,
)
from app.models import Group, Meeting
from app.pagination import paginate_or_all
from app.pdf_utils import pdf_or_html
from app.utils import parse_date, parse_time, user_groups

meetings_bp = Blueprint("meetings", __name__)

STATUSES = ["agendada", "realizada", "cancelada"]


def _filter_summary():
    parts = []
    if request.args.get("group_id"):
        group = db.session.get(Group, int(request.args["group_id"]))
        if group:
            parts.append(f"Grupo: {group.name}")
    if request.args.get("status"):
        parts.append(f"Status: {request.args['status']}")
    if request.args.get("date_from"):
        parts.append(f"De: {request.args['date_from']}")
    if request.args.get("date_to"):
        parts.append(f"Até: {request.args['date_to']}")
    return " · ".join(parts) if parts else "Nenhum filtro aplicado"


@meetings_bp.route("/")
@login_required
@permission_required("meetings.view")
def index():
    query = Meeting.query
    query = apply_group_scope(query, Meeting.group_id)
    query = apply_group_id(query, Meeting.group_id)
    query = apply_status(query, Meeting.status)
    query = apply_date_range(query, Meeting.meeting_date)
    query = query.order_by(Meeting.meeting_date.desc())
    pagination, meetings = paginate_or_all(query)

    ctx = filter_context()
    ctx.update({
        "meetings": meetings,
        "pagination": pagination,
        "statuses": STATUSES,
        "filter_summary": _filter_summary(),
        "generated_at": datetime.now(),
    })
    return pdf_or_html(
        "pdf/meetings_list.html",
        "meetings/index.html",
        "reunioes.pdf",
        **ctx,
    )


@meetings_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("meetings.manage")
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
@permission_required("meetings.view")
def view(meeting_id):
    meeting = db.get_or_404(Meeting, meeting_id)
    return render_template("meetings/view.html", meeting=meeting)


@meetings_bp.route("/<int:meeting_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("meetings.manage")
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
@permission_required("meetings.manage")
def delete(meeting_id):
    meeting = db.get_or_404(Meeting, meeting_id)
    db.session.delete(meeting)
    db.session.commit()
    flash("Reunião removida.", "success")
    return redirect(url_for("meetings.index"))
