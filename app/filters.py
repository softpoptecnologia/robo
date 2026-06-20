from flask import request
from flask_login import current_user

from app.utils import parse_date, parse_datetime_filter, user_group_ids, user_groups


def filter_context():
    from app.models import Group, Project, Student

    groups = (
        Group.query.order_by(Group.name).all()
        if current_user.is_admin
        else user_groups(current_user)
    )
    return {
        "groups": groups,
        "projects": Project.query.order_by(Project.title).all(),
        "students": Student.query.filter_by(status="ativo").order_by(Student.name).all(),
        "filters": request.args,
    }


def apply_group_scope(query, group_column):
    if current_user.is_admin:
        return query
    group_ids = user_group_ids(current_user)
    if not group_ids:
        return query.filter(False)
    return query.filter(group_column.in_(group_ids))


def apply_group_id(query, group_column):
    group_id = request.args.get("group_id")
    if group_id:
        query = query.filter(group_column == int(group_id))
    return query


def apply_project_id(query, project_column):
    project_id = request.args.get("project_id")
    if project_id:
        query = query.filter(project_column == int(project_id))
    return query


def apply_student_id(query, student_column):
    student_id = request.args.get("student_id")
    if student_id:
        query = query.filter(student_column == int(student_id))
    return query


def apply_status(query, status_column, default=None):
    if "status" in request.args:
        status = request.args.get("status")
        if status:
            query = query.filter(status_column == status)
        return query
    if default:
        query = query.filter(status_column == default)
    return query


def apply_date_range(query, date_column, use_datetime=False):
    if use_datetime:
        date_from = parse_datetime_filter(request.args.get("date_from"))
        date_to = parse_datetime_filter(request.args.get("date_to"), end_of_day=True)
    else:
        date_from = parse_date(request.args.get("date_from"))
        date_to = parse_date(request.args.get("date_to"))

    if date_from:
        query = query.filter(date_column >= date_from)
    if date_to:
        query = query.filter(date_column <= date_to)
    return query
