from io import BytesIO

from flask import abort, make_response, render_template, request
from flask_login import current_user


def wants_pdf():
    return request.args.get("format") == "pdf"


def _pdf_context(context):
    ctx = dict(context)
    ctx.setdefault("org_name", "Clube de Robótica Escolar")
    ctx.setdefault("org_subtitle", "Sistema de Gestão de Projetos")
    if current_user.is_authenticated:
        ctx.setdefault("issued_by", current_user.username)
        ctx.setdefault("issued_role", current_user.role_label)
    return ctx


def render_pdf(template_name, filename, **context):
    from xhtml2pdf import pisa

    html = render_template(template_name, **_pdf_context(context))
    buffer = BytesIO()
    status = pisa.CreatePDF(html, dest=buffer, encoding="utf-8")
    if status.err:
        raise RuntimeError("Erro ao gerar PDF")

    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def pdf_or_html(pdf_template, html_template, filename, **context):
    if wants_pdf():
        if not current_user.is_authenticated or not current_user.has_permission("reports.export"):
            abort(403)
        return render_pdf(pdf_template, filename, **context)
    return render_template(html_template, **context)
