from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import role_required
from app.extensions import db
from app.models import Project
from app.utils import parse_date

projects_bp = Blueprint("projects", __name__)

AREAS = ["robotica", "iot", "automacao", "programacao", "eletronica", "ia", "outra"]
STATUSES = ["planejado", "em andamento", "concluido", "cancelado"]


@projects_bp.route("/")
@login_required
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects/index.html", projects=projects)


@projects_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader")
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        area = request.form.get("area", "").strip()

        if not title or not area:
            flash("Título e área são obrigatórios.", "error")
            return render_template("projects/form.html", project=None, areas=AREAS, statuses=STATUSES)

        project = Project(
            title=title,
            description=request.form.get("description", "").strip(),
            objective=request.form.get("objective", "").strip(),
            area=area,
            start_date=parse_date(request.form.get("start_date")),
            expected_end_date=parse_date(request.form.get("expected_end_date")),
            status=request.form.get("status", "planejado"),
        )
        db.session.add(project)
        db.session.commit()
        flash("Projeto cadastrado.", "success")
        return redirect(url_for("projects.index"))

    return render_template("projects/form.html", project=None, areas=AREAS, statuses=STATUSES)


@projects_bp.route("/<int:project_id>")
@login_required
def view(project_id):
    project = db.get_or_404(Project, project_id)
    return render_template("projects/view.html", project=project)


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "leader")
def edit(project_id):
    project = db.get_or_404(Project, project_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Título é obrigatório.", "error")
            return render_template("projects/form.html", project=project, areas=AREAS, statuses=STATUSES)

        project.title = title
        project.description = request.form.get("description", "").strip()
        project.objective = request.form.get("objective", "").strip()
        project.area = request.form.get("area", project.area)
        project.start_date = parse_date(request.form.get("start_date"))
        project.expected_end_date = parse_date(request.form.get("expected_end_date"))
        project.status = request.form.get("status", project.status)
        db.session.commit()
        flash("Projeto atualizado.", "success")
        return redirect(url_for("projects.view", project_id=project.id))

    return render_template("projects/form.html", project=project, areas=AREAS, statuses=STATUSES)


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete(project_id):
    project = db.get_or_404(Project, project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Projeto removido.", "success")
    return redirect(url_for("projects.index"))
