"""Compila artigo LaTeX IEEEtran para PDF (Tectonic ou pdflatex)."""

import hashlib
import os
import platform
import shutil
import stat
import subprocess
import tarfile
import tempfile
import zipfile
from urllib.request import urlretrieve

from app.articles.export_latex import _copy_figure_for_ieee, _prepare_figures, build_latex_document
from app.articles.ieee_latex_assets import ieee_cls_path, read_latex_preamble

_TECTONIC_BASE = (
    "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.16.9"
)
_TECTONIC_ASSETS = {
    "Windows": ("tectonic-0.16.9-x86_64-pc-windows-msvc.zip", "zip", "tectonic.exe"),
    "Linux": ("tectonic-0.16.9-x86_64-unknown-linux-musl.tar.gz", "tar.gz", "tectonic"),
    "Darwin": ("tectonic-0.16.9-x86_64-apple-darwin.tar.gz", "tar.gz", "tectonic"),
}


def _build_tex(article, upload_folder, brand_assets_folder):
    figure_map, latex_figures = _prepare_figures(article.get("figures") or [], upload_folder)
    preamble = None
    try:
        preamble = read_latex_preamble(brand_assets_folder)
    except (FileNotFoundError, ValueError):
        pass
    tex = build_latex_document(article, latex_figures, preamble)
    return figure_map, tex


def _content_hash(article, upload_folder, brand_assets_folder):
    figure_map, tex = _build_tex(article, upload_folder, brand_assets_folder)
    digest = hashlib.sha256(tex.encode("utf-8"))
    for dest, src in sorted(figure_map.items()):
        if os.path.isfile(src):
            stat = os.stat(src)
            digest.update(f"{dest}:{stat.st_mtime}:{stat.st_size}".encode())
    return digest.hexdigest()[:16]


def _cache_path(cache_folder, project_id, content_hash):
    os.makedirs(cache_folder, exist_ok=True)
    return os.path.join(cache_folder, f"project-{project_id}-{content_hash}.pdf")


def _find_tectonic(bin_dir):
    for name in ("tectonic.exe", "tectonic"):
        bundled = os.path.join(bin_dir, name)
        if os.path.isfile(bundled):
            return bundled
    return shutil.which("tectonic")


def _tectonic_asset_for_platform():
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Linux" and machine not in ("x86_64", "amd64"):
        return None
    if system == "Darwin" and machine == "arm64":
        return (
            "tectonic-0.16.9-aarch64-apple-darwin.tar.gz",
            "tar.gz",
            "tectonic",
        )
    return _TECTONIC_ASSETS.get(system)


def _extract_tectonic(archive_path, archive_type, bin_dir, binary_name):
    if archive_type == "zip":
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(bin_dir)
    else:
        with tarfile.open(archive_path, "r:gz") as tf:
            tf.extractall(bin_dir)
    binary_path = os.path.join(bin_dir, binary_name)
    if os.path.isfile(binary_path):
        os.chmod(binary_path, os.stat(binary_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _download_tectonic(bin_dir):
    asset = _tectonic_asset_for_platform()
    if not asset:
        return None

    filename, archive_type, _binary_name = asset
    url = f"{_TECTONIC_BASE}/{filename}"
    os.makedirs(bin_dir, exist_ok=True)
    archive_path = os.path.join(bin_dir, filename)

    try:
        urlretrieve(url, archive_path)
        _extract_tectonic(archive_path, archive_type, bin_dir, _binary_name)
    except OSError:
        return None
    finally:
        if os.path.isfile(archive_path):
            os.remove(archive_path)

    return _find_tectonic(bin_dir)


def _ensure_tectonic(bin_dir):
    exe = _find_tectonic(bin_dir)
    if exe:
        return exe
    return _download_tectonic(bin_dir)


def _tectonic_subprocess_env(tectonic_cache_dir):
    env = os.environ.copy()
    if tectonic_cache_dir:
        os.makedirs(tectonic_cache_dir, exist_ok=True)
        env["TECTONIC_CACHE_DIR"] = tectonic_cache_dir
    return env


def _find_pdflatex():
    candidates = [
        shutil.which("pdflatex"),
        os.path.join(os.environ.get("ProgramFiles", ""), "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe"),
        os.path.join(
            os.environ.get("LocalAppData", ""),
            "Programs",
            "MiKTeX",
            "miktex",
            "bin",
            "x64",
            "pdflatex.exe",
        ),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _run_compile(work_dir, main_tex, bin_dir, tectonic_cache_dir=None):
    tectonic = _ensure_tectonic(bin_dir)
    if tectonic:
        return subprocess.run(
            [tectonic, "-X", "compile", "--outdir", work_dir, main_tex],
            capture_output=True,
            text=True,
            cwd=work_dir,
            timeout=300,
            env=_tectonic_subprocess_env(tectonic_cache_dir),
        )

    pdflatex = _find_pdflatex()
    if not pdflatex:
        return None

    last = None
    for _ in range(2):
        last = subprocess.run(
            [
                pdflatex,
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={work_dir}",
                main_tex,
            ],
            capture_output=True,
            text=True,
            cwd=work_dir,
            timeout=300,
        )
        if last.returncode != 0:
            break
    return last


_BUNDLE_NETWORK_HINT = (
    "O Tectonic precisa baixar pacotes LaTeX na primeira compilação, "
    "mas o servidor não acessa relay.fullyjustified.net. "
    "Rode scripts/bootstrap_tectonic_cache.sh numa máquina Linux com internet, "
    "compacte arquivos/tectonic-cache/ e envie ao servidor — veja DEPLOY.md."
)


def _compile_error_message(result):
    parts = []
    if result.stdout:
        parts.append(result.stdout.strip())
    if result.stderr:
        parts.append(result.stderr.strip())
    message = "\n".join(parts) or "Falha desconhecida na compilação LaTeX."
    lowered = message.lower()
    if "couldn't get it from the internet" in lowered or "isn't cached" in lowered:
        return f"{message}\n\n{_BUNDLE_NETWORK_HINT}"
    return message


def compile_tex_file(work_dir, tex_filename, bin_dir, tectonic_cache_dir=None):
    """Compila um .tex já presente em work_dir. Retorna caminho do PDF ou None."""
    main_tex = os.path.join(work_dir, tex_filename)
    if not os.path.isfile(main_tex):
        return None

    result = _run_compile(work_dir, main_tex, bin_dir, tectonic_cache_dir)
    if result is None or result.returncode != 0:
        return None

    pdf_name = os.path.splitext(tex_filename)[0] + ".pdf"
    pdf_path = os.path.join(work_dir, pdf_name)
    return pdf_path if os.path.isfile(pdf_path) else None


def ensure_reference_pdf(brand_assets_folder, bin_dir, tectonic_cache_dir=None):
    """Garante conference_101719.pdf no template (usa o do zip ou compila)."""
    from app.articles.ieee_latex_assets import (
        REFERENCE_PDF,
        REFERENCE_TEX,
        ensure_template_dir,
        reference_pdf_path,
    )

    template_dir = ensure_template_dir(brand_assets_folder)
    existing = reference_pdf_path(brand_assets_folder)
    if existing:
        return existing

    pdf_path = compile_tex_file(template_dir, REFERENCE_TEX, bin_dir, tectonic_cache_dir)
    if pdf_path:
        dest = os.path.join(template_dir, REFERENCE_PDF)
        if pdf_path != dest:
            shutil.copy2(pdf_path, dest)
        return dest
    return None


def compile_article_pdf(
    article,
    upload_folder,
    cache_folder,
    brand_assets_folder,
    bin_dir,
    project_id,
    tectonic_cache_dir=None,
):
    """Retorna (pdf_bytes, error_message). error_message é None em sucesso."""
    try:
        cls_path = ieee_cls_path(brand_assets_folder)
    except FileNotFoundError as exc:
        return None, str(exc)

    content_hash = _content_hash(article, upload_folder, brand_assets_folder)
    cached = _cache_path(cache_folder, project_id, content_hash)
    if os.path.isfile(cached):
        with open(cached, "rb") as handle:
            return handle.read(), None

    figure_map, tex = _build_tex(article, upload_folder, brand_assets_folder)
    work_dir = tempfile.mkdtemp(prefix="latex-build-")
    try:
        for dest_name, src_path in figure_map.items():
            dest = os.path.join(work_dir, dest_name)
            _copy_figure_for_ieee(src_path, dest)
        shutil.copy2(cls_path, os.path.join(work_dir, "IEEEtran.cls"))

        main_tex = os.path.join(work_dir, "main.tex")
        with open(main_tex, "w", encoding="utf-8") as handle:
            handle.write(tex)

        result = _run_compile(work_dir, main_tex, bin_dir, tectonic_cache_dir)
        if result is None:
            return None, (
                "Compilador LaTeX não encontrado. "
                "O Tectonic é baixado automaticamente em bin/ na primeira compilação "
                "(Linux/Windows). Se falhar, instale manualmente — veja DEPLOY.md."
            )
        if result.returncode != 0:
            return None, _compile_error_message(result)

        out_pdf = os.path.join(work_dir, "main.pdf")
        if not os.path.isfile(out_pdf):
            return None, "Compilação concluída, mas main.pdf não foi gerado."

        shutil.copy2(out_pdf, cached)
        with open(cached, "rb") as handle:
            return handle.read(), None
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
