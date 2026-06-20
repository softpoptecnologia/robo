"""Carrega o template IEEE (strict OOXML) para uso com python-docx."""

import os
import shutil
import tempfile
import zipfile

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

_STRICT_TO_TRANSITIONAL = [
    (
        "http://purl.oclc.org/ooxml/officeDocument/relationships/",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/",
    ),
    (
        "http://purl.oclc.org/ooxml/drawingml/wordprocessingDrawing",
        "http://schemas.openxmlformats.org/drawingml/wordprocessingDrawing/2006/main",
    ),
    ("http://purl.oclc.org/ooxml/drawingml/", "http://schemas.openxmlformats.org/drawingml/2006/"),
    (
        "http://purl.oclc.org/ooxml/wordprocessingml/main",
        "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    ),
    (
        "http://purl.oclc.org/ooxml/officeDocument/math",
        "http://schemas.openxmlformats.org/officeDocument/2006/math",
    ),
]


def default_template_path():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base, "arquivos", "conference-template-a4.docx")


def normalize_strict_docx(src_path):
    """Converte strict OOXML (IEEE) para formato compatível com python-docx."""
    tmpdir = tempfile.mkdtemp(prefix="ieee_tpl_")
    fixed = os.path.join(tmpdir, "ieee-template.docx")
    shutil.copy2(src_path, fixed)

    with zipfile.ZipFile(fixed, "r") as zin:
        data = {name: zin.read(name) for name in zin.namelist()}

    for name, content in list(data.items()):
        if not (name.endswith(".xml") or name.endswith(".rels")):
            continue
        text = content.decode("utf-8")
        for old, new in _STRICT_TO_TRANSITIONAL:
            text = text.replace(old, new)
        text = text.replace(' w:conformance="strict"', "")
        data[name] = text.encode("utf-8")

    with zipfile.ZipFile(fixed, "w") as zout:
        for name, content in data.items():
            zout.writestr(name, content)
    return fixed


def set_columns(section, num=2, space_twips=360):
    sect_pr = section._sectPr
    existing = sect_pr.find(qn("w:cols"))
    if existing is not None:
        sect_pr.remove(existing)
    if num > 1:
        cols = OxmlElement("w:cols")
        cols.set(qn("w:num"), str(num))
        cols.set(qn("w:space"), str(space_twips))
        sect_pr.append(cols)


def clear_document_body(doc):
    body = doc.element.body
    sect_pr = body.find(qn("w:sectPr"))
    for child in list(body):
        if child is sect_pr:
            continue
        body.remove(child)


def open_template(template_path=None):
    path = template_path or default_template_path()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Template IEEE não encontrado: {path}")
    normalized = normalize_strict_docx(path)
    return Document(normalized), normalized
