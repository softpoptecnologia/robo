from flask import Blueprint, current_app, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.articles.export import export_article_docx
from app.articles.export_latex import export_article_tex, export_article_zip, get_latex_source
from app.articles.generator import build_article_mvp
from app.articles.render import enrich_article_for_view
from app.articles.compile_latex import compile_article_pdf
from app.decorators import permission_required
from app.extensions import db
from app.models import Evidence, Project
from app.pagination import paginate_query
from app.utils import parse_date

projects_bp = Blueprint("projects", __name__)

AREAS = ["robotica", "iot", "automacao", "programacao", "eletronica", "ia", "outra"]
STATUSES = ["planejado", "em andamento", "concluido", "cancelado"]

SCIENCE_FIELDS = [
    "research_question",
    "hypothesis",
    "keywords",
    "methodology",
    "scientific_relevance",
]


def _project_form_data():
    return {f: request.form.get(f, "").strip() for f in SCIENCE_FIELDS}


def _apply_science_fields(project):
    for field in SCIENCE_FIELDS:
        setattr(project, field, request.form.get(field, "").strip() or None)


def _slug_filename(title):
    safe = "".join(c if c.isalnum() or c in " -_" else "" for c in title)
    return safe.strip().replace(" ", "-")[:60] or "artigo"


@projects_bp.route("/")
@login_required
@permission_required("projects.view")
def index():
    query = Project.query.order_by(Project.created_at.desc())
    pagination = paginate_query(query)
    return render_template("projects/index.html", projects=pagination.items, pagination=pagination)


@projects_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("projects.manage")
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
            **_project_form_data(),
        )
        db.session.add(project)
        db.session.commit()
        flash("Projeto cadastrado.", "success")
        return redirect(url_for("projects.index"))

    return render_template("projects/form.html", project=None, areas=AREAS, statuses=STATUSES)


def _ieee_portal_context(cfg):
    from app.articles.ieee_latex_assets import template_status

    status = template_status(cfg["BRAND_ASSETS_FOLDER"], cfg.get("IEEE_ARTICLE_TEMPLATE"))
    status["example_pdf_url"] = (
        url_for("ieee_brand_file", filename="conference_101719.pdf")
        if status["example_pdf_ready"]
        else None
    )
    return status


def _article_view_context(article_data, project_id):
    cfg = current_app.config
    return enrich_article_for_view(
        article_data,
        cfg["UPLOAD_FOLDER"],
        cfg["LATEX_CACHE_FOLDER"],
        cfg["BRAND_ASSETS_FOLDER"],
        cfg["TECTONIC_BIN_DIR"],
        project_id,
        url_for("projects.article", project_id=project_id, format="pdf"),
    )


@projects_bp.route("/<int:project_id>")
@login_required
@permission_required("projects.view")
def view(project_id):
    project = db.get_or_404(Project, project_id)
    article_preview = None
    if current_user.has_permission("projects.article"):
        article_data = build_article_mvp(project)
        if article_data["can_export"]:
            article_preview = _article_view_context(article_data, project.id)
    return render_template(
        "projects/view.html",
        project=project,
        article_preview=article_preview,
    )


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("projects.manage")
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
        _apply_science_fields(project)
        db.session.commit()
        flash("Projeto atualizado.", "success")
        return redirect(url_for("projects.view", project_id=project.id))

    return render_template("projects/form.html", project=project, areas=AREAS, statuses=STATUSES)


@projects_bp.route("/<int:project_id>/article")
@login_required
@permission_required("projects.article")
def article(project_id):
    project = db.get_or_404(Project, project_id)
    article_data = build_article_mvp(project)

    if not article_data["can_export"]:
        if not article_data["participants"]:
            flash("Cadastre grupos com participantes no projeto para gerar o artigo.", "warning")
        else:
            flash("Registre ao menos uma evidência para gerar o rascunho do artigo.", "warning")
        return redirect(url_for("projects.view", project_id=project.id))

    if request.args.get("format") == "docx":
        try:
            buffer = export_article_docx(
                article_data,
                project,
                current_app.config["UPLOAD_FOLDER"],
            )
        except FileNotFoundError as exc:
            flash(str(exc), "error")
            return redirect(url_for("projects.article", project_id=project.id))
        filename = f"artigo-{_slug_filename(project.title)}.docx"
        response = make_response(buffer.read())
        response.headers["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    if request.args.get("format") == "tex":
        buffer = export_article_tex(
            article_data,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["BRAND_ASSETS_FOLDER"],
        )
        filename = f"artigo-{_slug_filename(project.title)}.tex"
        response = make_response(buffer.read())
        response.headers["Content-Type"] = "application/x-tex; charset=utf-8"
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    if request.args.get("format") == "zip":
        buffer, slug = export_article_zip(
            article_data,
            project,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["BRAND_ASSETS_FOLDER"],
        )
        filename = f"artigo-{slug}.zip"
        response = make_response(buffer.read())
        response.headers["Content-Type"] = "application/zip"
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    if request.args.get("format") == "pdf":
        article_view = _article_view_context(article_data, project.id)
        if not article_view["pdf_available"]:
            flash(article_view["compile_error"] or "Não foi possível compilar o PDF.", "error")
            return redirect(url_for("projects.article", project_id=project.id))

        pdf_bytes, _ = compile_article_pdf(
            article_data,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["LATEX_CACHE_FOLDER"],
            current_app.config["BRAND_ASSETS_FOLDER"],
            current_app.config["TECTONIC_BIN_DIR"],
            project.id,
        )
        filename = f"artigo-{_slug_filename(project.title)}.pdf"
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        disposition = "attachment" if request.args.get("download") else "inline"
        response.headers["Content-Disposition"] = f'{disposition}; filename="{filename}"'
        return response

    evidences = (
        Evidence.query.filter_by(project_id=project.id)
        .order_by(Evidence.created_at.desc())
        .all()
    )
    latex_source = get_latex_source(
        article_data,
        current_app.config["UPLOAD_FOLDER"],
        current_app.config["BRAND_ASSETS_FOLDER"],
    )
    article_view = _article_view_context(article_data, project.id)
    ieee = _ieee_portal_context(current_app.config)

    return render_template(
        "projects/article.html",
        project=project,
        article=article_view,
        evidences=evidences,
        latex_source=latex_source,
        ieee=ieee,
    )


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
@permission_required("projects.delete")
def delete(project_id):
    project = db.get_or_404(Project, project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Projeto removido.", "success")
    return redirect(url_for("projects.index"))
