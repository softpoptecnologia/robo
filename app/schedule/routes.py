from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import role_required
from app.extensions import db
from app.models import Group, ScheduleItem, Student
from app.utils import parse_date, user_groups

schedule_bp = Blueprint("schedule", __name__)

STATUSES = ["pendente", "em andamento", "concluida", "atrasada"]


def _update_overdue_status():
    """Marca etapas vencidas como atrasadas."""
    overdue = ScheduleItem.query.filter(
        ScheduleItem.status.in_(["pendente", "em andamento"]),
        ScheduleItem.end_date < date.today(),
    ).all()
    for item in overdue:
        item.status = "atrasada"
    if overdue:
        db.session.commit()


@schedule_bp.route("/")
@login_required
def index():
    _update_overdue_status()
    if current_user.is_admin:
        items = ScheduleItem.query.order_by(ScheduleItem.end_date).all()
    else:
        group_ids = [g.id for g in user_groups(current_user)]
        items = ScheduleItem.query.filter(ScheduleItem.group_id.in_(group_ids)).order_by(ScheduleItem.end_date).all()
    return render_template("schedule/index.html", items=items)


@schedule_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader", "participant")
def create():
    groups = user_groups(current_user) if not current_user.is_admin else Group.query.all()
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()

    if request.method == "POST":
        group_id = request.form.get("group_id")
        title = request.form.get("title", "").strip()

        if not group_id or not title:
            flash("Grupo e título são obrigatórios.", "error")
            return render_template("schedule/form.html", item=None, groups=groups, students=students, statuses=STATUSES)

        group = db.get_or_404(Group, int(group_id))
        responsible_id = request.form.get("responsible_id")

        item = ScheduleItem(
            group_id=group.id,
            project_id=group.project_id,
            title=title,
            description=request.form.get("description", "").strip(),
            start_date=parse_date(request.form.get("start_date")),
            end_date=parse_date(request.form.get("end_date")),
            responsible_id=int(responsible_id) if responsible_id else None,
            status=request.form.get("status", "pendente"),
        )
        db.session.add(item)
        db.session.commit()
        flash("Etapa cadastrada.", "success")
        return redirect(url_for("schedule.index"))

    return render_template("schedule/form.html", item=None, groups=groups, students=students, statuses=STATUSES)


@schedule_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader", "participant")
def edit(item_id):
    item = db.get_or_404(ScheduleItem, item_id)
    groups = user_groups(current_user) if not current_user.is_admin else Group.query.all()
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()

    if request.method == "POST":
        item.title = request.form.get("title", "").strip()
        item.description = request.form.get("description", "").strip()
        item.start_date = parse_date(request.form.get("start_date"))
        item.end_date = parse_date(request.form.get("end_date"))
        responsible_id = request.form.get("responsible_id")
        item.responsible_id = int(responsible_id) if responsible_id else None
        item.status = request.form.get("status", item.status)
        db.session.commit()
        flash("Etapa atualizada.", "success")
        return redirect(url_for("schedule.index"))

    return render_template("schedule/form.html", item=item, groups=groups, students=students, statuses=STATUSES)


@schedule_bp.route("/<int:item_id>/delete", methods=["POST"])
@login_required
@role_required("admin", "leader")
def delete(item_id):
    item = db.get_or_404(ScheduleItem, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Etapa removida.", "success")
    return redirect(url_for("schedule.index"))
