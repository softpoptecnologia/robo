import os

from flask import Flask
from flask_login import login_required

from app.extensions import db, login_manager
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.students.routes import students_bp
    from app.projects.routes import projects_bp
    from app.groups.routes import groups_bp
    from app.schedule.routes import schedule_bp
    from app.activities.routes import activities_bp
    from app.meetings.routes import meetings_bp
    from app.minutes.routes import minutes_bp
    from app.reports.routes import reports_bp
    from app.evidence.routes import evidence_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(groups_bp, url_prefix="/groups")
    app.register_blueprint(schedule_bp, url_prefix="/schedule")
    app.register_blueprint(activities_bp, url_prefix="/activities")
    app.register_blueprint(meetings_bp, url_prefix="/meetings")
    app.register_blueprint(minutes_bp, url_prefix="/minutes")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(evidence_bp, url_prefix="/evidence")

    @app.route("/uploads/<path:filename>")
    @login_required
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    with app.app_context():
        db.create_all()
        _migrate_db()
        _seed_admin()

    return app


def _migrate_db():
    """Adiciona colunas novas em bancos SQLite já existentes."""
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    if "evidences" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("evidences")}
        if "meeting_id" not in cols:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE evidences ADD COLUMN meeting_id INTEGER"))
                conn.commit()


def _seed_admin():
    from app.models import User

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@clube.local",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
