import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


class Config:
    """Configurações da aplicação Flask."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-clube-robotica-change-in-production")
    DEBUG = _env_bool("FLASK_DEBUG") or _env_bool("DEBUG")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'clube_robotica.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    LOG_FILE = os.environ.get("LOG_FILE", os.path.join(BASE_DIR, "error.log"))

