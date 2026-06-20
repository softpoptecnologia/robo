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
    BRAND_ASSETS_FOLDER = os.path.join(BASE_DIR, "arquivos")
    BRAND_LOGO_FILE = os.environ.get("BRAND_LOGO_FILE", "logo.enc")
    IEEE_ARTICLE_TEMPLATE = os.environ.get(
        "IEEE_ARTICLE_TEMPLATE",
        os.path.join(BASE_DIR, "arquivos", "conference-template-a4.docx"),
    )
    IEEE_LATEX_TEMPLATE = os.environ.get(
        "IEEE_LATEX_TEMPLATE",
        os.path.join(BASE_DIR, "arquivos", "ieee-template", "conference_101719.tex"),
    )
    IEEE_TEMPLATE_ZIP = os.environ.get(
        "IEEE_TEMPLATE_ZIP",
        os.path.join(BASE_DIR, "arquivos", "IEEE_Conference_Template.zip"),
    )
    IEEE_TEMPLATE_DIR = os.environ.get(
        "IEEE_TEMPLATE_DIR",
        os.path.join(BASE_DIR, "arquivos", "ieee-template"),
    )
    IEEETRAN_CLS = os.environ.get(
        "IEEETRAN_CLS",
        os.path.join(BASE_DIR, "arquivos", "ieee-template", "IEEEtran.cls"),
    )
    LATEX_CACHE_FOLDER = os.environ.get(
        "LATEX_CACHE_FOLDER",
        os.path.join(BASE_DIR, "uploads", "latex-cache"),
    )
    TECTONIC_BIN_DIR = os.environ.get(
        "TECTONIC_BIN_DIR",
        os.path.join(BASE_DIR, "bin"),
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    LOG_FILE = os.environ.get("LOG_FILE", os.path.join(BASE_DIR, "error.log"))

