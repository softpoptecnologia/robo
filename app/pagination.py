"""Utilitários de paginação para listagens."""

from flask import request

DEFAULT_PER_PAGE = 15


def get_page():
    try:
        return max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        return 1


def paginate_query(query, per_page=DEFAULT_PER_PAGE):
    return query.paginate(page=get_page(), per_page=per_page, error_out=False)


def paginate_or_all(query, per_page=DEFAULT_PER_PAGE):
    """HTML paginado; PDF exporta todos os registros filtrados."""
    from app.pdf_utils import wants_pdf

    if wants_pdf():
        return None, query.all()
    pagination = paginate_query(query, per_page)
    return pagination, pagination.items
