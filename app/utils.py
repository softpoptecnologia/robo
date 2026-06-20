import os
import uuid
from datetime import datetime

from flask import abort, current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp", "bmp",
    "pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx",
    "stl", "step", "stp", "iges", "igs", "dxf", "dwg",
    "zip", "rar", "7z",
    "mp4", "webm", "mov", "avi",
    "txt", "py", "ino", "cpp", "c", "h",
}

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "bmp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image_file(filename):
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in IMAGE_EXTENSIONS


def save_upload(file):
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, unique_name)
    file.save(filepath)
    return unique_name


def save_uploads(files, max_files=10):
    """Salva vários arquivos e retorna lista de nomes salvos."""
    saved = []
    for file in files[:max_files]:
        path = save_upload(file)
        if path:
            saved.append(path)
    return saved


def delete_upload(filename):
    if not filename:
        return
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(filepath):
        os.remove(filepath)


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_time(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None


def parse_datetime_filter(value, end_of_day=False):
    if not value:
        return None
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        if end_of_day:
            return dt.replace(hour=23, minute=59, second=59)
        return dt
    except ValueError:
        return None


def user_groups(user):
    from app.models import Group

    if user.is_admin:
        return Group.query.all()
    if user.student_id:
        if user.is_leader:
            return Group.query.filter(
                (Group.leader_id == user.student_id)
                | Group.members.any(id=user.student_id)
            ).all()
        return Group.query.filter(Group.members.any(id=user.student_id)).all()
    return []


def user_group_ids(user):
    return [g.id for g in user_groups(user)]


def groups_scoped_query(user):
    """Query de grupos visíveis ao usuário, ordenada por nome."""
    from app.models import Group

    query = Group.query
    if user.is_admin:
        return query.order_by(Group.name)
    if not user.student_id:
        return query.filter(False).order_by(Group.name)
    if user.is_leader:
        query = query.filter(
            (Group.leader_id == user.student_id)
            | Group.members.any(id=user.student_id)
        )
    else:
        query = query.filter(Group.members.any(id=user.student_id))
    return query.order_by(Group.name)


def can_access_group(user, group_id):
    if user.is_admin:
        return True
    return group_id in user_group_ids(user)


def require_group_access(user, group_id):
    if not can_access_group(user, group_id):
        abort(403)


def resolve_student_id(user, form_student_id=None, group=None):
    """Define o estudante autor: usuário logado, seleção do form ou líder do grupo."""
    if user.student_id:
        return user.student_id
    if form_student_id:
        return int(form_student_id)
    if group and group.leader_id:
        return group.leader_id
    if group and group.members:
        return group.members[0].id
    return None


def group_member_students(group):
    """Estudantes elegíveis como autor em um grupo."""
    members = list(group.members)
    if group.leader and group.leader not in members:
        members.insert(0, group.leader)
    return members
