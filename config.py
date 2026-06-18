import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configurações da aplicação Flask."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-clube-robotica-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'clube_robotica.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
