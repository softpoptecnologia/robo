from datetime import datetime, date, time

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


group_students = db.Table(
    "group_students",
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id"), primary_key=True),
    db.Column("student_id", db.Integer, db.ForeignKey("students.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="participant")
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_leader(self):
        return self.role == "leader"

    @property
    def is_participant(self):
        return self.role == "participant"

    def has_permission(self, code):
        from app.permissions import user_has_permission
        return user_has_permission(self, code)

    @property
    def role_label(self):
        from app.permissions import get_role_label
        return get_role_label(self.role)


class RoleProfile(db.Model):
    __tablename__ = "role_profiles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON, nullable=False, default=list)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(30))
    status = db.Column(db.String(20), default="ativo")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="student", uselist=False)
    groups = db.relationship("Group", secondary=group_students, back_populates="members")
    led_groups = db.relationship("Group", back_populates="leader", foreign_keys="Group.leader_id")


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    objective = db.Column(db.Text)
    area = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date)
    expected_end_date = db.Column(db.Date)
    status = db.Column(db.String(30), default="planejado")
    research_question = db.Column(db.Text)
    hypothesis = db.Column(db.Text)
    keywords = db.Column(db.String(500))
    methodology = db.Column(db.Text)
    scientific_relevance = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    groups = db.relationship("Group", back_populates="project", cascade="all, delete-orphan")

    @property
    def all_members(self):
        seen = set()
        members = []
        for group in self.groups:
            if group.leader and group.leader.id not in seen:
                seen.add(group.leader.id)
                members.append(group.leader)
            for member in group.members:
                if member.id not in seen:
                    seen.add(member.id)
                    members.append(member)
        return members


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    status = db.Column(db.String(30), default="ativo")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", back_populates="groups")
    leader = db.relationship("Student", back_populates="led_groups", foreign_keys=[leader_id])
    members = db.relationship("Student", secondary=group_students, back_populates="groups")
    schedule_items = db.relationship("ScheduleItem", back_populates="group", cascade="all, delete-orphan")
    activities = db.relationship("ActivityLog", back_populates="group", cascade="all, delete-orphan")
    meetings = db.relationship("Meeting", back_populates="group", cascade="all, delete-orphan")
    evidences = db.relationship("Evidence", back_populates="group", cascade="all, delete-orphan")


class ScheduleItem(db.Model):
    __tablename__ = "schedule_items"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    responsible_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    status = db.Column(db.String(30), default="pendente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    group = db.relationship("Group", back_populates="schedule_items")
    project = db.relationship("Project")
    responsible = db.relationship("Student")
    evidences = db.relationship("Evidence", back_populates="schedule_item")


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    activity_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.Text, nullable=False)
    difficulties = db.Column(db.Text)
    next_steps = db.Column(db.Text)
    attachment_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    group = db.relationship("Group", back_populates="activities")
    project = db.relationship("Project")
    student = db.relationship("Student")


class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    meeting_time = db.Column(db.Time, default=time(14, 0))
    location = db.Column(db.String(200))
    agenda = db.Column(db.Text)
    status = db.Column(db.String(30), default="agendada")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    group = db.relationship("Group", back_populates="meetings")
    project = db.relationship("Project")
    minute = db.relationship("MeetingMinute", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    attendances = db.relationship("MeetingAttendance", back_populates="meeting", cascade="all, delete-orphan")
    evidences = db.relationship("Evidence", back_populates="meeting")


class MeetingMinute(db.Model):
    __tablename__ = "meeting_minutes"

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=False, unique=True)
    summary = db.Column(db.Text, nullable=False)
    decisions = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meeting = db.relationship("Meeting", back_populates="minute")
    tasks = db.relationship("MinuteTask", back_populates="minute", cascade="all, delete-orphan")


class MeetingAttendance(db.Model):
    __tablename__ = "meeting_attendances"

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    present = db.Column(db.Boolean, default=True)

    meeting = db.relationship("Meeting", back_populates="attendances")
    student = db.relationship("Student")

    __table_args__ = (db.UniqueConstraint("meeting_id", "student_id"),)


class MinuteTask(db.Model):
    __tablename__ = "minute_tasks"

    id = db.Column(db.Integer, primary_key=True)
    minute_id = db.Column(db.Integer, db.ForeignKey("meeting_minutes.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    notes = db.Column(db.Text)

    minute = db.relationship("MeetingMinute", back_populates="tasks")
    responsible = db.relationship("Student")


class Evidence(db.Model):
    __tablename__ = "evidences"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    schedule_item_id = db.Column(db.Integer, db.ForeignKey("schedule_items.id"), nullable=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence_type = db.Column(db.String(30), nullable=False)
    file_path = db.Column(db.String(300))  # legado: primeiro anexo
    external_link = db.Column(db.String(500))
    project_status_snapshot = db.Column(db.String(30))
    observations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship("Project")
    group = db.relationship("Group", back_populates="evidences")
    student = db.relationship("Student")
    schedule_item = db.relationship("ScheduleItem", back_populates="evidences")
    meeting = db.relationship("Meeting", back_populates="evidences")
    attachments = db.relationship(
        "EvidenceAttachment", back_populates="evidence", cascade="all, delete-orphan",
        order_by="EvidenceAttachment.sort_order",
    )

    EVIDENCE_TYPES = [
        "foto", "video", "documento", "cad", "link", "codigo",
        "prototipo", "teste", "apresentacao", "outro",
    ]


class EvidenceAttachment(db.Model):
    """Anexo de evidência — permite várias fotos/CAD por registro."""

    __tablename__ = "evidence_attachments"

    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidences.id"), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    caption = db.Column(db.String(200))
    attachment_type = db.Column(db.String(30), default="foto")
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    evidence = db.relationship("Evidence", back_populates="attachments")

    ATTACHMENT_TYPES = [
        ("foto", "Foto do protótipo"),
        ("cad", "Arquivo CAD / desenho técnico"),
        ("foto_montagem", "Foto da montagem"),
        ("documento", "Documento / relatório"),
        ("video", "Vídeo"),
        ("outro", "Outro"),
    ]
