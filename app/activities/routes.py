from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import permission_required
from app.extensions import db
from app.filters import (
    apply_date_range,
    apply_group_id,
    apply_group_scope,
    apply_student_id,
    filter_context,
)
from app.models import ActivityLog, Group, Student
from app.pagination import paginate_or_all
from app.pdf_utils import pdf_or_html
from app.utils import (
    group_member_students,
    parse_date,
    require_group_access,
    resolve_student_id,
    save_upload,
    user_groups,
)

activities_bp = Blueprint("activities", __name__)


def _filter_summary():
    parts = []
    if request.args.get("group_id"):
        group = db.session.get(Group, int(request.args["group_id"]))
        if group:
            parts.append(f"Grupo: {group.name}")
    if request.args.get("student_id"):
        student = db.session.get(Student, int(request.args["student_id"]))
        if student:
            parts.append(f"Estudante: {student.name}")
    if request.args.get("date_from"):
        parts.append(f"De: {request.args['date_from']}")
    if request.args.get("date_to"):
        parts.append(f"Até: {request.args['date_to']}")
    return " · ".join(parts) if parts else "Nenhum filtro aplicado"


@activities_bp.route("/")
@login_required
@permission_required("activities.view")
def index():
    query = ActivityLog.query
    query = apply_group_scope(query, ActivityLog.group_id)
    query = apply_group_id(query, ActivityLog.group_id)
    query = apply_student_id(query, ActivityLog.student_id)
    query = apply_date_range(query, ActivityLog.activity_date)
    query = query.order_by(ActivityLog.activity_date.desc())
    pagination, activities = paginate_or_all(query)

    ctx = filter_context()
    ctx.update({
        "activities": activities,
        "pagination": pagination,
        "filter_summary": _filter_summary(),
        "generated_at": datetime.now(),
    })
    return pdf_or_html(
        "pdf/activities_list.html",
        "activities/index.html",
        "atividades.pdf",
        **ctx,
    )


def _form_context(groups):
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()
    return {"activity": None, "groups": groups, "students": students}


@activities_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("activities.manage")
def create():
    groups = user_groups(current_user) if not current_user.is_admin else Group.query.all()

    if request.method == "POST":
        group_id = request.form.get("group_id")
        description = request.form.get("description", "").strip()

        if not group_id or not description:
            flash("Grupo e descrição são obrigatórios.", "error")
            return render_template("activities/form.html", **_form_context(groups))

        group = db.get_or_404(Group, int(group_id))
        require_group_access(current_user, group.id)

        student_id = resolve_student_id(current_user, request.form.get("student_id"), group)
        if not student_id:
            flash("Selecione o estudante responsável.", "error")
            return render_template("activities/form.html", **_form_context(groups))

        attachment = save_upload(request.files.get("attachment"))

        activity = ActivityLog(
            group_id=group.id,
            project_id=group.project_id,
            student_id=student_id,
            activity_date=parse_date(request.form.get("activity_date")) or date.today(),
            description=description,
            difficulties=request.form.get("difficulties", "").strip(),
            next_steps=request.form.get("next_steps", "").strip(),
            attachment_path=attachment,
        )
        db.session.add(activity)
        db.session.commit()
        flash("Atividade registrada.", "success")
        return redirect(url_for("activities.index"))

    return render_template("activities/form.html", **_form_context(groups))


@activities_bp.route("/<int:activity_id>")
@login_required
@permission_required("activities.view")
def view(activity_id):
    activity = db.get_or_404(ActivityLog, activity_id)
    require_group_access(current_user, activity.group_id)
    return render_template("activities/view.html", activity=activity)


@activities_bp.route("/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete(activity_id):
    activity = db.get_or_404(ActivityLog, activity_id)
    can_delete = (
        current_user.has_permission("activities.manage")
        or activity.student_id == current_user.student_id
    )
    if not can_delete:
        flash("Sem permissão.", "error")
        return redirect(url_for("activities.index"))
    db.session.delete(activity)
    db.session.commit()
    flash("Atividade removida.", "success")
    return redirect(url_for("activities.index"))
