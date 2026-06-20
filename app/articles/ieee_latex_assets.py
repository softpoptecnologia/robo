"""Extração e leitura do template LaTeX IEEE oficial (IEEE_Conference_Template.zip)."""

import os
import shutil
import zipfile

TEMPLATE_ZIP_NAME = "IEEE_Conference_Template.zip"
TEMPLATE_DIR_NAME = "ieee-template"
REFERENCE_TEX = "conference_101719.tex"
REFERENCE_PDF = "conference_101719.pdf"
IEEE_CLS = "IEEEtran.cls"
_REQUIRED = (IEEE_CLS, REFERENCE_TEX)


def template_zip_path(brand_assets_folder):
    return os.path.join(brand_assets_folder, TEMPLATE_ZIP_NAME)


def template_dir_path(brand_assets_folder):
    return os.path.join(brand_assets_folder, TEMPLATE_DIR_NAME)


def _is_ready(template_dir):
    return all(os.path.isfile(os.path.join(template_dir, name)) for name in _REQUIRED)


def _flatten_template_dir(template_dir):
    """Copia arquivos de subpastas do zip para a raiz de ieee-template/."""
    for root, _, files in os.walk(template_dir):
        for fname in files:
            src = os.path.join(root, fname)
            dest = os.path.join(template_dir, fname)
            if src == dest:
                continue
            if not os.path.isfile(dest):
                shutil.copy2(src, dest)


def ensure_template_dir(brand_assets_folder):
    """Descompacta IEEE_Conference_Template.zip em arquivos/ieee-template/ se necessário."""
    template_dir = template_dir_path(brand_assets_folder)
    if _is_ready(template_dir):
        return template_dir

    zip_path = template_zip_path(brand_assets_folder)
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(
            f"Template IEEE LaTeX não encontrado. Coloque {TEMPLATE_ZIP_NAME} em arquivos/."
        )

    os.makedirs(template_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(template_dir)

    _flatten_template_dir(template_dir)

    if not _is_ready(template_dir):
        raise FileNotFoundError(
            f"O zip {TEMPLATE_ZIP_NAME} não contém {IEEE_CLS} e {REFERENCE_TEX}."
        )
    return template_dir


def ieee_cls_path(brand_assets_folder):
    return os.path.join(ensure_template_dir(brand_assets_folder), IEEE_CLS)


def reference_tex_path(brand_assets_folder):
    return os.path.join(ensure_template_dir(brand_assets_folder), REFERENCE_TEX)


def reference_pdf_path(brand_assets_folder):
    path = os.path.join(ensure_template_dir(brand_assets_folder), REFERENCE_PDF)
    return path if os.path.isfile(path) else None


def read_latex_preamble(brand_assets_folder):
    """Retorna o preâmbulo oficial (até \\begin{document}) de conference_101719.tex."""
    ref_path = reference_tex_path(brand_assets_folder)
    with open(ref_path, encoding="utf-8") as handle:
        content = handle.read()
    marker = r"\begin{document}"
    idx = content.find(marker)
    if idx == -1:
        raise ValueError(f"{REFERENCE_TEX} não contém \\begin{{document}}.")
    return content[:idx].rstrip()


def template_status(brand_assets_folder, docx_template_path=None):
    """Retorna flags usadas no portal do artigo."""
    try:
        ensure_template_dir(brand_assets_folder)
        latex_ready = True
        example_pdf = reference_pdf_path(brand_assets_folder) is not None
    except (FileNotFoundError, ValueError):
        latex_ready = False
        example_pdf = False

    return {
        "latex_ready": latex_ready,
        "docx_ready": bool(docx_template_path and os.path.isfile(docx_template_path)),
        "example_pdf_ready": example_pdf,
    }
