from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Evidence, EvidenceAttachment, Group, Meeting, Project, ScheduleItem, Student
from app.utils import (
    can_access_group,
    delete_upload,
    group_member_students,
    parse_datetime_filter,
    require_group_access,
    resolve_student_id,
    save_uploads,
    user_group_ids,
    user_groups,
)

evidence_bp = Blueprint("evidence", __name__)

TYPES_REQUIRING_FILE = {"foto", "video", "cad", "prototipo", "teste", "documento"}


def _build_query():
    query = Evidence.query

    project_id = request.args.get("project_id")
    group_id = request.args.get("group_id")
    student_id = request.args.get("student_id")
    evidence_type = request.args.get("evidence_type")
    date_from = parse_datetime_filter(request.args.get("date_from"))
    date_to = parse_datetime_filter(request.args.get("date_to"), end_of_day=True)

    if project_id:
        query = query.filter(Evidence.project_id == int(project_id))
    if group_id:
        query = query.filter(Evidence.group_id == int(group_id))
    if student_id:
        query = query.filter(Evidence.student_id == int(student_id))
    if evidence_type:
        query = query.filter(Evidence.evidence_type == evidence_type)
    if date_from:
        query = query.filter(Evidence.created_at >= date_from)
    if date_to:
        query = query.filter(Evidence.created_at <= date_to)

    if not current_user.is_admin:
        group_ids = user_group_ids(current_user)
        if not group_ids:
            return query.filter(False)
        query = query.filter(Evidence.group_id.in_(group_ids))

    return query.order_by(Evidence.created_at.desc())


def _save_attachments(evidence, files, types=None, captions=None):
    """Persiste anexos múltiplos vinculados à evidência."""
    types = types or []
    captions = captions or []
    saved_paths = save_uploads(files)

    if not saved_paths:
        return []

    attachments = []
    for i, path in enumerate(saved_paths):
        att_type = types[i] if i < len(types) and types[i] else "foto"
        caption = captions[i].strip() if i < len(captions) and captions[i] else None
        att = EvidenceAttachment(
            evidence_id=evidence.id,
            file_path=path,
            attachment_type=att_type,
            caption=caption,
            sort_order=i,
        )
        db.session.add(att)
        attachments.append(att)

    if not evidence.file_path and attachments:
        evidence.file_path = attachments[0].file_path

    return attachments


def _delete_evidence_files(evidence):
    for att in evidence.attachments:
        delete_upload(att.file_path)
    if evidence.file_path:
        delete_upload(evidence.file_path)


def _validate_evidence_form(group, evidence_type, external_link, files):
    if evidence_type == "link" and not external_link:
        return "Informe o link externo para evidências do tipo link."
    if evidence_type in TYPES_REQUIRING_FILE and not any(f.filename for f in files):
        return "Anexe pelo menos um arquivo (foto, CAD, vídeo ou documento)."
    return None


def _get_form_context(groups, prefill=None):
    prefill = prefill or {}
    schedule_items = ScheduleItem.query.filter(
        ScheduleItem.group_id.in_([g.id for g in groups])
    ).all()
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()

    selected_group = None
    if prefill.get("group_id"):
        selected_group = db.session.get(Group, int(prefill["group_id"]))

    group_students = group_member_students(selected_group) if selected_group else students

    return {
        "groups": groups,
        "schedule_items": schedule_items,
        "students": students,
        "group_students": group_students,
        "evidence_types": Evidence.EVIDENCE_TYPES,
        "attachment_types": EvidenceAttachment.ATTACHMENT_TYPES,
        "prefill": prefill,
    }


@evidence_bp.route("/")
@login_required
def timeline():
    evidences = _build_query().all()
    projects = Project.query.order_by(Project.title).all()
    groups = user_groups(current_user) if not current_user.is_admin else Group.query.all()
    students = Student.query.filter_by(status="ativo").order_by(Student.name).all()

    return render_template(
        "evidence/timeline.html",
        evidences=evidences,
        projects=projects,
        groups=groups,
        students=students,
        evidence_types=Evidence.EVIDENCE_TYPES,
        filters=request.args,
    )


@evidence_bp.route("/project/<int:project_id>")
@login_required
def project_timeline(project_id):
    project = db.get_or_404(Project, project_id)
    query = Evidence.query.filter_by(project_id=project_id)
    if not current_user.is_admin:
        query = query.filter(Evidence.group_id.in_(user_group_ids(current_user)))
    evidences = query.order_by(Evidence.created_at).all()
    return render_template("evidence/project_timeline.html", project=project, evidences=evidences)


@evidence_bp.route("/group/<int:group_id>")
@login_required
def group_timeline(group_id):
    from app.models import ActivityLog, Meeting, MeetingMinute

    group = db.get_or_404(Group, group_id)
    require_group_access(current_user, group_id)

    evidences = Evidence.query.filter_by(group_id=group_id).order_by(Evidence.created_at).all()
    activities = ActivityLog.query.filter_by(group_id=group_id).order_by(ActivityLog.activity_date).all()
    meetings = Meeting.query.filter_by(group_id=group_id).order_by(Meeting.meeting_date).all()
    completed_steps = [s for s in group.schedule_items if s.status == "concluida"]

    events = []
    for ev in evidences:
        events.append({"date": ev.created_at, "type": "evidencia", "obj": ev})
    for act in activities:
        events.append({"date": datetime.combine(act.activity_date, datetime.min.time()), "type": "atividade", "obj": act})
    for mt in meetings:
        if mt.status == "realizada" and not mt.minute:
            events.append({"date": datetime.combine(mt.meeting_date, datetime.min.time()), "type": "reuniao", "obj": mt})
        if mt.minute:
            events.append({"date": mt.minute.created_at, "type": "ata", "obj": mt.minute})
            for ev in mt.evidences:
                events.append({"date": ev.created_at, "type": "evidencia_reuniao", "obj": ev})
    for step in completed_steps:
        if step.end_date:
            events.append({"date": datetime.combine(step.end_date, datetime.min.time()), "type": "etapa", "obj": step})

    events.sort(key=lambda e: e["date"])

    return render_template("evidence/group_timeline.html", group=group, events=events)


@evidence_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    groups = user_groups(current_user) if not current_user.is_admin else Group.query.all()

    prefill = {
        "group_id": request.args.get("group_id") or request.form.get("group_id"),
        "schedule_item_id": request.args.get("schedule_item_id") or request.form.get("schedule_item_id"),
        "meeting_id": request.args.get("meeting_id") or request.form.get("meeting_id"),
        "project_id": request.args.get("project_id"),
    }

    if request.method == "POST":
        group_id = request.form.get("group_id")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        evidence_type = request.form.get("evidence_type", "").strip()
        external_link = request.form.get("external_link", "").strip() or None
        files = request.files.getlist("files")

        if not group_id or not title or not description or not evidence_type:
            flash("Grupo, título, descrição e tipo são obrigatórios.", "error")
            return render_template("evidence/form.html", evidence=None, **_get_form_context(groups, prefill))

        group = db.get_or_404(Group, int(group_id))
        require_group_access(current_user, group.id)

        err = _validate_evidence_form(group, evidence_type, external_link, files)
        if err:
            flash(err, "error")
            return render_template("evidence/form.html", evidence=None, **_get_form_context(groups, prefill))

        student_id = resolve_student_id(current_user, request.form.get("student_id"), group)
        if not student_id:
            flash("Selecione o estudante responsável pelo registro.", "error")
            return render_template("evidence/form.html", evidence=None, **_get_form_context(groups, prefill))

        schedule_item_id = request.form.get("schedule_item_id")
        meeting_id = request.form.get("meeting_id")

        if schedule_item_id:
            item = db.session.get(ScheduleItem, int(schedule_item_id))
            if not item or item.group_id != group.id:
                flash("Etapa do cronograma inválida para este grupo.", "error")
                return render_template("evidence/form.html", evidence=None, **_get_form_context(groups, prefill))

        if meeting_id:
            meeting = db.session.get(Meeting, int(meeting_id))
            if not meeting or meeting.group_id != group.id:
                flash("Reunião inválida para este grupo.", "error")
                return render_template("evidence/form.html", evidence=None, **_get_form_context(groups, prefill))

        evidence = Evidence(
            project_id=group.project_id,
            group_id=group.id,
            student_id=student_id,
            schedule_item_id=int(schedule_item_id) if schedule_item_id else None,
            meeting_id=int(meeting_id) if meeting_id else None,
            title=title,
            description=description,
            evidence_type=evidence_type,
            external_link=external_link,
            project_status_snapshot=group.project.status,
            observations=request.form.get("observations", "").strip(),
        )
        db.session.add(evidence)
        db.session.flush()

        att_types = request.form.getlist("attachment_type")
        captions = request.form.getlist("attachment_caption")
        _save_attachments(evidence, files, att_types, captions)

        db.session.commit()
        flash("Evidência registrada com sucesso.", "success")

        if meeting_id:
            return redirect(url_for("meetings.view", meeting_id=meeting_id))
        if prefill.get("project_id"):
            return redirect(url_for("evidence.project_timeline", project_id=prefill["project_id"]))
        return redirect(url_for("evidence.timeline"))

    return render_template("evidence/form.html", evidence=None, **_get_form_context(groups, prefill))


@evidence_bp.route("/<int:evidence_id>")
@login_required
def view(evidence_id):
    evidence = db.get_or_404(Evidence, evidence_id)
    require_group_access(current_user, evidence.group_id)
    can_delete = current_user.is_admin or evidence.student_id == current_user.student_id
    return render_template("evidence/view.html", evidence=evidence, can_delete=can_delete)


@evidence_bp.route("/<int:evidence_id>/delete", methods=["POST"])
@login_required
def delete(evidence_id):
    evidence = db.get_or_404(Evidence, evidence_id)
    require_group_access(current_user, evidence.group_id)
    if not current_user.is_admin and evidence.student_id != current_user.student_id:
        flash("Sem permissão.", "error")
        return redirect(url_for("evidence.view", evidence_id=evidence_id))

    _delete_evidence_files(evidence)
    db.session.delete(evidence)
    db.session.commit()
    flash("Evidência removida.", "success")
    return redirect(url_for("evidence.timeline"))
