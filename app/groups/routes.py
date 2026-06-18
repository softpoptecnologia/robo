from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import role_required
from app.extensions import db
from app.models import Group, Project, Student, User
from app.utils import user_groups

groups_bp = Blueprint("groups", __name__)

STATUSES = ["ativo", "inativo", "concluido"]


@groups_bp.route("/")
@login_required
def index():
    if current_user.is_admin:
        groups = Group.query.order_by(Group.name).all()
    else:
        groups = user_groups(current_user)
    return render_template("groups/index.html", groups=groups)


@groups_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader")
def create():
    projects = Project.query.order_by(Project.title).all()
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        project_id = request.form.get("project_id")

        if not name or not project_id:
            flash("Nome e projeto são obrigatórios.", "error")
            return render_template("groups/form.html", group=None, projects=projects, students=students, statuses=STATUSES)

        group = Group(
            name=name,
            project_id=int(project_id),
            leader_id=request.form.get("leader_id") or None,
            status=request.form.get("status", "ativo"),
        )
        if group.leader_id:
            group.leader_id = int(group.leader_id)

        member_ids = request.form.getlist("member_ids")
        group.members = Student.query.filter(Student.id.in_(member_ids)).all() if member_ids else []

        db.session.add(group)
        db.session.commit()
        flash("Grupo cadastrado.", "success")
        return redirect(url_for("groups.index"))

    return render_template("groups/form.html", group=None, projects=projects, students=students, statuses=STATUSES)


@groups_bp.route("/<int:group_id>")
@login_required
def view(group_id):
    group = db.get_or_404(Group, group_id)
    return render_template("groups/view.html", group=group)


@groups_bp.route("/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader")
def edit(group_id):
    group = db.get_or_404(Group, group_id)
    projects = Project.query.order_by(Project.title).all()
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Nome é obrigatório.", "error")
            return render_template("groups/form.html", group=group, projects=projects, students=students, statuses=STATUSES)

        group.name = name
        group.project_id = int(request.form.get("project_id", group.project_id))
        leader_id = request.form.get("leader_id")
        group.leader_id = int(leader_id) if leader_id else None
        group.status = request.form.get("status", group.status)
        member_ids = request.form.getlist("member_ids")
        group.members = Student.query.filter(Student.id.in_(member_ids)).all() if member_ids else []
        db.session.commit()
        flash("Grupo atualizado.", "success")
        return redirect(url_for("groups.view", group_id=group.id))

    return render_template("groups/form.html", group=group, projects=projects, students=students, statuses=STATUSES)


@groups_bp.route("/<int:group_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete(group_id):
    group = db.get_or_404(Group, group_id)
    db.session.delete(group)
    db.session.commit()
    flash("Grupo removido.", "success")
    return redirect(url_for("groups.index"))
