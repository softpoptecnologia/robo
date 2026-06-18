from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import ActivityLog, Group, Student
from app.utils import (
    group_member_students,
    parse_date,
    require_group_access,
    resolve_student_id,
    save_upload,
    user_groups,
)

activities_bp = Blueprint("activities", __name__)


@activities_bp.route("/")
@login_required
def index():
    if current_user.is_admin:
        activities = ActivityLog.query.order_by(ActivityLog.activity_date.desc()).all()
    elif current_user.student_id or user_groups(current_user):
        group_ids = [g.id for g in user_groups(current_user)]
        activities = ActivityLog.query.filter(
            ActivityLog.group_id.in_(group_ids)
        ).order_by(ActivityLog.activity_date.desc()).all()
    else:
        activities = []
    return render_template("activities/index.html", activities=activities)


def _form_context(groups):
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()
    return {"activity": None, "groups": groups, "students": students}


@activities_bp.route("/new", methods=["GET", "POST"])
@login_required
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
def view(activity_id):
    activity = db.get_or_404(ActivityLog, activity_id)
    require_group_access(current_user, activity.group_id)
    return render_template("activities/view.html", activity=activity)


@activities_bp.route("/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete(activity_id):
    activity = db.get_or_404(ActivityLog, activity_id)
    if not current_user.is_admin and activity.student_id != current_user.student_id:
        flash("Sem permissão.", "error")
        return redirect(url_for("activities.index"))
    db.session.delete(activity)
    db.session.commit()
    flash("Atividade removida.", "success")
    return redirect(url_for("activities.index"))
