from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import permission_required
from app.extensions import db
from app.models import RoleProfile
from app.permissions import (
    MODULE_LABELS,
    PERMISSIONS,
    REQUIRED_PERMISSIONS,
    get_role_label,
    normalize_permissions,
    permissions_by_module,
    restore_role_defaults,
)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/roles")
@login_required
@permission_required("settings.roles")
def roles_index():
    profiles = RoleProfile.query.order_by(RoleProfile.slug).all()
    return render_template("admin/roles_index.html", profiles=profiles)


@admin_bp.route("/roles/<slug>", methods=["GET", "POST"])
@login_required
@permission_required("settings.roles")
def roles_edit(slug):
    profile = RoleProfile.query.filter_by(slug=slug).first_or_404()

    if slug == "admin":
        flash("O perfil Administrador possui acesso total e não pode ser restringido.", "warning")
        return redirect(url_for("admin.roles_index"))

    if request.method == "POST":
        selected = request.form.getlist("permissions")
        invalid = [c for c in selected if c not in PERMISSIONS]
        if invalid:
            flash("Permissão inválida detectada.", "error")
        else:
            permissions, missing_required = normalize_permissions(selected)
            if missing_required:
                labels = ", ".join(PERMISSIONS[code][0] for code in sorted(missing_required))
                flash(
                    f"As permissões obrigatórias foram mantidas automaticamente: {labels}.",
                    "warning",
                )
            profile.permissions = permissions
            profile.name = request.form.get("name", profile.name).strip() or profile.name
            profile.description = request.form.get("description", "").strip()
            db.session.commit()
            flash(f"Permissões do perfil {profile.name} atualizadas.", "success")
            return redirect(url_for("admin.roles_index"))

    grouped = permissions_by_module()
    active = set(profile.permissions or [])
    return render_template(
        "admin/roles_edit.html",
        profile=profile,
        grouped=grouped,
        active=active,
        role_label=get_role_label(slug),
        module_labels=MODULE_LABELS,
        required_permissions=REQUIRED_PERMISSIONS,
    )


@admin_bp.route("/roles/<slug>/reset", methods=["POST"])
@login_required
@permission_required("settings.roles")
def roles_reset(slug):
    if slug == "admin":
        flash("O perfil Administrador possui acesso total e não pode ser alterado.", "warning")
        return redirect(url_for("admin.roles_index"))

    profile = restore_role_defaults(slug)
    if not profile:
        flash("Perfil não encontrado.", "error")
        return redirect(url_for("admin.roles_index"))

    flash(f"Permissões padrão restauradas para {profile.name}.", "success")
    return redirect(url_for("admin.roles_edit", slug=slug))
