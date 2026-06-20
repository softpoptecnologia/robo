"""Prepara dados do artigo para visualização no portal (PDF LaTeX)."""

from app.articles.compile_latex import compile_article_pdf


def enrich_article_for_view(
    article,
    upload_folder,
    cache_folder,
    brand_assets_folder,
    bin_dir,
    project_id,
    pdf_url,
    tectonic_cache_dir=None,
):
    pdf_bytes, compile_error = compile_article_pdf(
        article,
        upload_folder,
        cache_folder,
        brand_assets_folder,
        bin_dir,
        project_id,
        tectonic_cache_dir,
    )
    enriched = dict(article)
    enriched["pdf_available"] = pdf_bytes is not None
    enriched["compile_error"] = compile_error
    enriched["pdf_url"] = pdf_url if pdf_bytes else None
    return enriched
