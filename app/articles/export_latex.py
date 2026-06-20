"""Exporta artigo no formato LaTeX IEEEtran (conference)."""

import os
import re
import shutil
import tempfile
import zipfile
from io import BytesIO

_AFFILIATION_LINES = (
    r"\textit{Clube de Rob\^{o}tica Escolar, Programa STEM}",
    r"\textit{Escola Estadual de Ensino M\^{e}dio}",
    r"S\~{a}o Paulo, SP, Brasil",
)

_LATEX_PREAMBLE_FALLBACK = r"""\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithmic}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}"""


def _latex_escape(text):
    if not text:
        return ""
    text = (
        text.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("~", r"\textasciitilde{}")
        .replace("^", r"\textasciicircum{}")
        .replace("—", "---")
        .replace("–", "--")
        .replace("−", "-")
        .replace("•", r"\textbullet{}")
        .replace("σ", r"$\sigma$")
        .replace("Δ", r"$\Delta$")
        .replace("≈", r"$\approx$")
        .replace(""", "``")
        .replace(""", "''")
        .replace("\"", "''")
        .replace("«", "``")
        .replace("»", "''")
    )
    return text


def _latex_quotes(text):
    return re.sub(r'"([^"]+)"', r"``\1''", _latex_escape(text))


def _section_name(title):
    name = title.strip().title()
    replacements = {
        " And ": " and ",
        " Of ": " of ",
        " The ": " the ",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def _paragraphs(content):
    blocks = []
    for block in content.split("\n\n"):
        block = block.strip()
        if block:
            blocks.append(block)
    return blocks


def _render_paragraphs(content):
    lines = []
    for block in _paragraphs(content):
        if block.startswith("•") or "\n•" in block:
            items = [item.strip().lstrip("•").strip() for item in block.split("\n") if item.strip()]
            lines.append(r"\begin{itemize}")
            for item in items:
                lines.append(r"\item " + _latex_escape(item))
            lines.append(r"\end{itemize}")
        elif block.startswith("TABELA I"):
            continue
        else:
            lines.append(_latex_escape(block))
            lines.append("")
    return "\n".join(lines)


def _author_names_line(authors):
    names = [_latex_escape(a["name"]) + r"\IEEEauthorrefmark{1}" for a in authors]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return names[0] + " and " + names[1]
    return ", ".join(names[:-1]) + ", and " + names[-1]


def _render_authors(authors, affiliations):
    email = ""
    if affiliations:
        email = affiliations[0]
        if "E-mail:" in email:
            email = email.split("E-mail:", 1)[1].strip()
    elif authors:
        email = authors[0].get("email", "")

    aff_lines = [r"\IEEEauthorrefmark{1}"] + list(_AFFILIATION_LINES)
    if email and "@" in email:
        aff_lines.append("E-mail: " + _latex_escape(email))
    aff_body = r" \\ ".join(aff_lines)

    return (
        r"\author{\IEEEauthorblockN{" + _author_names_line(authors) + "}"
        r"\IEEEauthorblockA{" + aff_body + "}}"
    )


def _render_evidence_table(table_groups):
    if not table_groups:
        return ""

    col_spec = (
        r"|>{\raggedright\arraybackslash}p{0.28\columnwidth}|"
        r">{\raggedright\arraybackslash}p{0.64\columnwidth}|"
    )
    lines = [
        r"\begin{table}[H]",
        r"\caption{Evid\^{e}ncias registradas por fase}",
        r"\label{tab:evidencias}",
        r"\centering",
        r"\renewcommand{\arraystretch}{1.15}",
        r"\begin{tabular}{" + col_spec + "}",
        r"\hline",
        r"\textbf{Fase} & \textbf{Evid\^{e}ncia registrada} \\",
        r"\hline",
    ]
    for group in table_groups:
        phase = _latex_escape(group["phase"])
        for index, row in enumerate(group["rows"]):
            title = _latex_escape(row["title"])
            meta = _latex_escape(f"({row['type']}, {row['date']})")
            detail = _latex_escape(row["summary"])
            phase_cell = r"\textit{" + phase + r"}" if index == 0 else ""
            lines.append(
                phase_cell + r" & \textbf{" + title + r"} " + meta + r" \\"
            )
            lines.append(r" & \small " + detail + r" \\")
        lines.append(r"\hline")
    lines.extend([
        r"\end{tabular}",
        r"\end{table}",
        "",
    ])
    return "\n".join(lines)


def _copy_figure_for_ieee(src_path, dest_path, max_width=720):
    """Redimensiona imagem para caber na coluna IEEE (~3,5 in) sem distorcer."""
    try:
        from PIL import Image

        img = Image.open(src_path)
        if img.mode not in ("RGB", "L"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img)
            img = background
        width, height = img.size
        if width > max_width:
            new_height = max(1, int(height * max_width / width))
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        ext = os.path.splitext(dest_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            img.save(dest_path, "JPEG", quality=92, optimize=True)
        else:
            img.save(dest_path, "PNG", optimize=True)
    except Exception:
        shutil.copy2(src_path, dest_path)


def _prepare_figures(figures, upload_folder):
    figure_map = {}
    latex_figures = []
    for fig in figures:
        src = os.path.join(upload_folder, fig["file_path"])
        if not os.path.isfile(src):
            continue
        ext = os.path.splitext(fig["file_path"])[1].lower() or ".png"
        dest_name = f"fig{fig['num']}{ext}"
        figure_map[dest_name] = src
        latex_figures.append({
            "num": fig["num"],
            "file": dest_name,
            "caption": fig["caption"],
            "label": f"fig:{fig['num']}",
        })
    return figure_map, latex_figures


def _render_participants(participants):
    if not participants:
        return ""
    lines = [
        r"\section*{Authors and Participants}",
        r"\begin{itemize}",
    ]
    for item in participants:
        student = item["student"]
        text = (
            f"{student.name} — {item['role']}, {item['group']}, "
            f"turma {student.class_name} ({student.email})"
        )
        lines.append(r"\item " + _latex_escape(text))
    lines.extend([r"\end{itemize}", ""])
    return "\n".join(lines)


def _render_figures(latex_figures):
    chunks = []
    for fig in latex_figures:
        chunks.extend([
            r"\begin{figure}[H]",
            r"\centering",
            r"\includegraphics[width=\columnwidth,keepaspectratio]{"
            + fig["file"]
            + r"}",
            r"\caption{" + _latex_escape(fig["caption"]) + r"}",
            r"\label{" + fig["label"] + r"}",
            r"\end{figure}",
            "",
        ])
    return "\n".join(chunks)


def build_latex_document(article, latex_figures, preamble=None):
    parts = [
        preamble or _LATEX_PREAMBLE_FALLBACK,
        r"\usepackage{array}",
        r"\usepackage{float}",
        r"\usepackage{placeins}",
        r"\setkeys{Gin}{width=\columnwidth,keepaspectratio}",
        r"\begin{document}",
        "",
        r"\title{" + _latex_escape(article["title"]) + r"}",
        "",
        _render_authors(article["authors"], article["affiliations"]),
        "",
        r"\maketitle",
        "",
        r"\begin{abstract}",
        _latex_escape(article["abstract"]),
        r"\end{abstract}",
        "",
        r"\begin{IEEEkeywords}",
        _latex_escape(article["index_terms"]),
        r"\end{IEEEkeywords}",
        "",
        r"\FloatBarrier",
        "",
    ]

    for sec in article["sections"]:
        parts.append(r"\section{" + _section_name(sec["title"]) + "}")
        parts.append(_render_paragraphs(sec["content"]))
        if sec["id"] == "IV":
            if article.get("evidence_table"):
                parts.append(_render_evidence_table(article["evidence_table"]))
            if latex_figures:
                parts.append(_render_figures(latex_figures))
        parts.append("")

    parts.append(r"\FloatBarrier")
    parts.extend([
        r"\section*{Acknowledgment}",
        _latex_escape(article["acknowledgment"]),
        "",
        r"\begin{thebibliography}{00}",
    ])

    for ref in article["references"]:
        parts.append(r"\bibitem{b" + str(ref["num"]) + r"} " + _latex_quotes(ref["text"]))

    parts.extend([
        r"\end{thebibliography}",
        r"\end{document}",
        "",
    ])
    return "\n".join(parts)


def get_latex_source(article, upload_folder, brand_assets_folder=None):
    from app.articles.ieee_latex_assets import read_latex_preamble

    _, latex_figures = _prepare_figures(article.get("figures") or [], upload_folder)
    preamble = None
    if brand_assets_folder:
        try:
            preamble = read_latex_preamble(brand_assets_folder)
        except (FileNotFoundError, ValueError):
            preamble = None
    return build_latex_document(article, latex_figures, preamble)


def export_article_tex(article, upload_folder, brand_assets_folder=None):
    content = get_latex_source(article, upload_folder, brand_assets_folder)
    buffer = BytesIO()
    buffer.write(content.encode("utf-8"))
    buffer.seek(0)
    return buffer


def export_article_zip(article, project, upload_folder, brand_assets_folder=None):
    from app.articles.ieee_latex_assets import ieee_cls_path, read_latex_preamble

    figure_map, latex_figures = _prepare_figures(article.get("figures") or [], upload_folder)
    preamble = None
    cls_path = None
    if brand_assets_folder:
        try:
            preamble = read_latex_preamble(brand_assets_folder)
            cls_path = ieee_cls_path(brand_assets_folder)
        except (FileNotFoundError, ValueError):
            pass
    tex = build_latex_document(article, latex_figures, preamble)
    slug = re.sub(r"[^\w\-]+", "-", project.title.lower()).strip("-")[:50] or "artigo"

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("main.tex", tex)
        if cls_path and os.path.isfile(cls_path):
            zf.write(cls_path, "IEEEtran.cls")
        zf.writestr(
            "README.txt",
            "Artigo IEEEtran — Clube de Robótica\n\n"
            "Conteúdo:\n"
            "  main.tex       — artigo gerado a partir das evidências\n"
            "  IEEEtran.cls   — classe oficial IEEE\n"
            "  fig*.png/jpg   — figuras do artigo\n\n"
            "Compilar (pdflatex ou tectonic):\n"
            "  pdflatex main.tex\n"
            "  pdflatex main.tex\n\n"
            "Template de referência: arquivos/IEEE_Conference_Template.zip\n",
        )
        for dest_name, src_path in figure_map.items():
            tmp_path = os.path.join(tempfile.gettempdir(), dest_name)
            _copy_figure_for_ieee(src_path, tmp_path)
            zf.write(tmp_path, dest_name)
            if os.path.isfile(tmp_path):
                os.remove(tmp_path)

    buffer.seek(0)
    return buffer, slug
