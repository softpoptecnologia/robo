import html
import os
from io import BytesIO

from docx import Document
from docx.oxml.ns import qn

from app.articles.export import build_article_document

SINGLE_COL_STYLES = {"paper title", "Author", "Abstract", "Keywords"}


def _style_class(style_name):
    key = (style_name or "Normal").strip().lower()
    return {
        "paper title": "ieee-s-title",
        "author": "ieee-s-author",
        "abstract": "ieee-s-abstract",
        "keywords": "ieee-s-keywords",
        "heading 1": "ieee-s-h1",
        "heading 5": "ieee-s-h5",
        "body text": "ieee-s-body",
        "figure caption": "ieee-s-figcaption",
        "references": "ieee-s-ref",
    }.get(key, "ieee-s-body")


def _runs_html(para):
    chunks = []
    for run in para.runs:
        text = html.escape(run.text)
        if not text:
            continue
        if run.bold and run.italic:
            text = f"<strong><em>{text}</em></strong>"
        elif run.bold:
            text = f"<strong>{text}</strong>"
        elif run.italic:
            text = f"<em>{text}</em>"
        if run.font.superscript:
            text = f"<sup>{text}</sup>"
        chunks.append(text)
    if chunks:
        return "".join(chunks)
    return html.escape(para.text)


def _paragraph_has_image(para):
    for run in para.runs:
        if run._element.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
            return True
    return False


def _figure_html(fig, image_url_builder):
    url = image_url_builder(fig["file_path"])
    cap = html.escape(fig.get("caption") or "")
    num = fig.get("num", "")
    return (
        f'<figure class="ieee-s-fig">'
        f'<img src="{html.escape(url)}" alt="{cap}">'
        f'<figcaption class="ieee-s-figcaption">Fig. {num}. {cap}</figcaption>'
        f"</figure>"
    )


def build_ieee_preview_html(article, upload_folder, template_path, image_url_builder):
    """
    Gera HTML idêntico ao Word exportado (conference-template-a4.docx).
    image_url_builder: callable(file_path) -> url
    """
    doc = build_article_document(article, upload_folder, template_path)

    single_parts = []
    body_parts = []
    figures = list(article.get("figures") or [])
    fig_i = 0
    skip_caption = False

    for para in doc.paragraphs:
        style_name = para.style.name if para.style else "Normal"

        if skip_caption:
            skip_caption = False
            continue

        if _paragraph_has_image(para):
            if fig_i < len(figures):
                body_parts.append(_figure_html(figures[fig_i], image_url_builder))
                fig_i += 1
                skip_caption = True
            continue

        text = _runs_html(para).strip()
        if not text:
            continue

        cls = _style_class(style_name)
        block = f'<p class="{cls}">{text}</p>'

        if style_name in SINGLE_COL_STYLES:
            single_parts.append(block)
        else:
            body_parts.append(block)

    return (
        '<div class="ieee-doc">'
        f'<div class="ieee-single">{"".join(single_parts)}</div>'
        f'<div class="ieee-body-flow">{"".join(body_parts)}</div>'
        "</div>"
    )


def build_article_document_bytes(article, upload_folder, template_path):
    doc = build_article_document(article, upload_folder, template_path)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
