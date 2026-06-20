from flask import Blueprint
from flask_login import login_required

from app.decorators import permission_required
from app.pdf_utils import pdf_or_html
from app.reports.data import (
    _ctx,
    activities_data,
    evolution_data,
    groups_data,
    minutes_data,
    participation_data,
    projects_data,
)

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
@login_required
@permission_required("reports.view")
def index():
    from flask import render_template

    return render_template("reports/index.html")


@reports_bp.route("/projects")
@login_required
@permission_required("reports.view")
def projects():
    items, filter_summary = projects_data()
    ctx = _ctx(projects=items, filter_summary=filter_summary)
    return pdf_or_html(
        "pdf/projects.html",
        "reports/projects.html",
        "relatorio-projetos.pdf",
        **ctx,
    )


@reports_bp.route("/groups")
@login_required
@permission_required("reports.view")
def groups():
    report, filter_summary = groups_data()
    ctx = _ctx(report=report, filter_summary=filter_summary)
    return pdf_or_html(
        "pdf/groups.html",
        "reports/groups.html",
        "relatorio-grupos.pdf",
        **ctx,
    )


@reports_bp.route("/participation")
@login_required
@permission_required("reports.view")
def participation():
    data, filter_summary = participation_data()
    ctx = _ctx(data=data, filter_summary=filter_summary)
    return pdf_or_html(
        "pdf/participation.html",
        "reports/participation.html",
        "relatorio-participacao.pdf",
        **ctx,
    )


@reports_bp.route("/activities")
@login_required
@permission_required("reports.view")
def activities():
    by_group, recent, filter_summary = activities_data()
    ctx = _ctx(by_group=by_group, recent=recent, filter_summary=filter_summary)
    return pdf_or_html(
        "pdf/activities.html",
        "reports/activities.html",
        "relatorio-atividades.pdf",
        **ctx,
    )


@reports_bp.route("/minutes")
@login_required
@permission_required("reports.view")
def minutes():
    items, filter_summary = minutes_data()
    ctx = _ctx(minutes=items, filter_summary=filter_summary)
    return pdf_or_html(
        "pdf/minutes.html",
        "reports/minutes.html",
        "relatorio-atas.pdf",
        **ctx,
    )


@reports_bp.route("/evolution")
@login_required
@permission_required("reports.view")
def evolution():
    data = evolution_data()
    ctx = _ctx(**data)
    return pdf_or_html(
        "pdf/evolution.html",
        "reports/evolution.html",
        "relatorio-evolucao.pdf",
        **ctx,
    )
