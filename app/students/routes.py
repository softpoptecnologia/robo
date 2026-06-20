from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import permission_required
from app.extensions import db
from app.models import Student, User
from app.pagination import paginate_query

students_bp = Blueprint("students", __name__)

STATUSES = ["ativo", "inativo", "removido"]
USER_ROLES = [
    ("participant", "Participante"),
    ("leader", "Gerente"),
]


def _suggest_username(student):
    """Sugere usuário a partir do e-mail do estudante."""
    if not student or not student.email:
        return ""
    local = student.email.split("@")[0].lower()
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in local)


def _save_student_user(student, username, password, role):
    username = (username or "").strip()
    role = (role or "participant").strip()

    if role not in {r[0] for r in USER_ROLES}:
        return None, "Perfil de acesso inválido."

    if not username:
        return None, "Usuário é obrigatório para criar acesso."

    existing = User.query.filter_by(username=username).first()
    if student.user:
        if existing and existing.id != student.user.id:
            return None, "Nome de usuário já em uso."
    elif existing:
        return None, "Nome de usuário já em uso."

    email_taken = User.query.filter(User.email == student.email)
    if student.user:
        email_taken = email_taken.filter(User.id != student.user.id)
    if email_taken.first():
        return None, "E-mail já usado por outra conta de acesso."

    if student.user:
        user = student.user
        user.username = username
        user.email = student.email
        user.role = role
        if password:
            if len(password) < 6:
                return None, "A nova senha deve ter pelo menos 6 caracteres."
            user.set_password(password)
    else:
        if not password or len(password) < 6:
            return None, "Senha deve ter pelo menos 6 caracteres."
        user = User(
            username=username,
            email=student.email,
            role=role,
            student_id=student.id,
        )
        user.set_password(password)
        db.session.add(user)

    return user, None


def _student_form_context(student=None):
    return {
        "student": student,
        "statuses": STATUSES,
        "user_roles": USER_ROLES,
        "suggested_username": _suggest_username(student),
    }


@students_bp.route("/")
@login_required
@permission_required("students.view")
def index():
    query = Student.query.order_by(Student.name)
    pagination = paginate_query(query)
    return render_template("students/index.html", students=pagination.items, pagination=pagination)


@students_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("students.manage")
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        class_name = request.form.get("class_name", "").strip()

        if not name or not email or not class_name:
            flash("Nome, e-mail e turma são obrigatórios.", "error")
            return render_template("students/form.html", **_student_form_context())

        if Student.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "error")
            return render_template("students/form.html", **_student_form_context())

        student = Student(
            name=name,
            email=email,
            class_name=class_name,
            phone=request.form.get("phone", "").strip(),
            status=request.form.get("status", "ativo"),
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(student)
        db.session.flush()

        enable_access = request.form.get("enable_access") == "on"
        if enable_access:
            _, err = _save_student_user(
                student,
                request.form.get("username"),
                request.form.get("password"),
                request.form.get("role"),
            )
            if err:
                db.session.rollback()
                flash(err, "error")
                return render_template(
                    "students/form.html",
                    **_student_form_context(student),
                )

        db.session.commit()
        if enable_access:
            flash("Estudante cadastrado com acesso ao portal.", "success")
        else:
            flash("Estudante cadastrado com sucesso.", "success")
        return redirect(url_for("students.index"))

    return render_template("students/form.html", **_student_form_context())


@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("students.manage")
def edit(student_id):
    student = db.get_or_404(Student, student_id)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        existing = Student.query.filter(Student.email == email, Student.id != student_id).first()
        if existing:
            flash("E-mail já cadastrado.", "error")
            return render_template("students/form.html", **_student_form_context(student))

        student.name = request.form.get("name", "").strip()
        student.email = email
        student.class_name = request.form.get("class_name", "").strip()
        student.phone = request.form.get("phone", "").strip()
        student.status = request.form.get("status", "ativo")
        student.notes = request.form.get("notes", "").strip()

        if student.user:
            _, err = _save_student_user(
                student,
                request.form.get("username"),
                request.form.get("password"),
                request.form.get("role"),
            )
            if err:
                flash(err, "error")
                return render_template("students/form.html", **_student_form_context(student))
        elif request.form.get("enable_access") == "on":
            _, err = _save_student_user(
                student,
                request.form.get("username"),
                request.form.get("password"),
                request.form.get("role"),
            )
            if err:
                flash(err, "error")
                return render_template("students/form.html", **_student_form_context(student))

        db.session.commit()
        flash("Estudante atualizado.", "success")
        return redirect(url_for("students.index"))

    return render_template("students/form.html", **_student_form_context(student))


@students_bp.route("/<int:student_id>")
@login_required
@permission_required("students.view")
def view(student_id):
    student = db.get_or_404(Student, student_id)
    return render_template("students/view.html", student=student, user_roles=USER_ROLES)


@students_bp.route("/<int:student_id>/revoke-access", methods=["POST"])
@login_required
@permission_required("students.manage")
def revoke_access(student_id):
    student = db.get_or_404(Student, student_id)
    if not student.user:
        flash("Este estudante não possui acesso ao portal.", "error")
        return redirect(url_for("students.view", student_id=student_id))

    db.session.delete(student.user)
    db.session.commit()
    flash("Acesso ao portal removido.", "success")
    return redirect(url_for("students.view", student_id=student_id))


@students_bp.route("/<int:student_id>/delete", methods=["POST"])
@login_required
@permission_required("students.manage")
def delete(student_id):
    student = db.get_or_404(Student, student_id)
    if student.user:
        db.session.delete(student.user)
    db.session.delete(student)
    db.session.commit()
    flash("Estudante removido.", "success")
    return redirect(url_for("students.index"))
