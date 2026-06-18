from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.models import User

auth_bp = Blueprint("auth", __name__)

# Contas de demonstração — acesso rápido na tela de login
DEMO_ACCOUNTS = [
    {
        "role": "admin",
        "label": "Administrador",
        "description": "Acesso total ao sistema",
        "username": "admin",
        "password": "admin123",
        "css_class": "demo-admin",
    },
    {
        "role": "leader",
        "label": "Líder de Grupo",
        "description": "Grupo Atlas — Braço Robótico",
        "username": "lider_atlas",
        "password": "123456",
        "css_class": "demo-leader",
    },
    {
        "role": "participant",
        "label": "Participante",
        "description": "Grupo Atlas — estudante",
        "username": "participante1",
        "password": "123456",
        "css_class": "demo-participant",
    },
]


def _login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return user
    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Informe usuário e senha.", "error")
            return render_template("auth/login.html", demo_accounts=DEMO_ACCOUNTS)

        if _login_user(username, password):
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        flash("Usuário ou senha inválidos.", "error")

    return render_template("auth/login.html", demo_accounts=DEMO_ACCOUNTS)


@auth_bp.route("/login/demo/<role>")
def login_demo(role):
    """Login rápido para demonstração de cada perfil."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    account = next((a for a in DEMO_ACCOUNTS if a["role"] == role), None)
    if not account:
        flash("Perfil de demonstração inválido.", "error")
        return redirect(url_for("auth.login"))

    user = _login_user(account["username"], account["password"])
    if not user:
        flash(
            f"Conta de demo não encontrada ({account['username']}). Execute: python seed.py --force",
            "warning",
        )
        return redirect(url_for("auth.login"))

    flash(f"Entrou como {account['label']} ({account['username']}).", "success")
    return redirect(url_for("dashboard.index"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for("auth.login"))
