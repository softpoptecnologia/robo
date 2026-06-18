from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import role_required
from app.extensions import db
from app.models import Student

students_bp = Blueprint("students", __name__)

STATUSES = ["ativo", "inativo", "removido"]


@students_bp.route("/")
@login_required
@role_required("admin")
def index():
    students = Student.query.order_by(Student.name).all()
    return render_template("students/index.html", students=students)


@students_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        class_name = request.form.get("class_name", "").strip()

        if not name or not email or not class_name:
            flash("Nome, e-mail e turma são obrigatórios.", "error")
            return render_template("students/form.html", student=None, statuses=STATUSES)

        if Student.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "error")
            return render_template("students/form.html", student=None, statuses=STATUSES)

        student = Student(
            name=name,
            email=email,
            class_name=class_name,
            phone=request.form.get("phone", "").strip(),
            status=request.form.get("status", "ativo"),
            notes=request.form.get("notes", "").strip(),
        )
        db.session.add(student)
        db.session.commit()
        flash("Estudante cadastrado com sucesso.", "success")
        return redirect(url_for("students.index"))

    return render_template("students/form.html", student=None, statuses=STATUSES)


@students_bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit(student_id):
    student = db.get_or_404(Student, student_id)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        existing = Student.query.filter(Student.email == email, Student.id != student_id).first()
        if existing:
            flash("E-mail já cadastrado.", "error")
            return render_template("students/form.html", student=student, statuses=STATUSES)

        student.name = request.form.get("name", "").strip()
        student.email = email
        student.class_name = request.form.get("class_name", "").strip()
        student.phone = request.form.get("phone", "").strip()
        student.status = request.form.get("status", "ativo")
        student.notes = request.form.get("notes", "").strip()
        db.session.commit()
        flash("Estudante atualizado.", "success")
        return redirect(url_for("students.index"))

    return render_template("students/form.html", student=student, statuses=STATUSES)


@students_bp.route("/<int:student_id>")
@login_required
@role_required("admin")
def view(student_id):
    student = db.get_or_404(Student, student_id)
    return render_template("students/view.html", student=student)


@students_bp.route("/<int:student_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete(student_id):
    student = db.get_or_404(Student, student_id)
    db.session.delete(student)
    db.session.commit()
    flash("Estudante removido.", "success")
    return redirect(url_for("students.index"))
