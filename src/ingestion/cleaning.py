from __future__ import annotations

from datetime import datetime

import pandas as pd

from ingestion.crossref import PaperRecord
from core.utils import normalize_whitespace


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Normalize raw records into the stable clean/index schema."""
    rows = []
    for record in records:
        title = normalize_whitespace(record.title or "")
        summary = normalize_whitespace(record.summary or "")
        paper_id = normalize_whitespace(record.paper_id or "").lower()
        authors = [normalize_whitespace(str(value)) for value in (record.authors or []) if normalize_whitespace(str(value))]
        categories = [normalize_whitespace(str(value)) for value in (record.categories or []) if normalize_whitespace(str(value))]
        published = pd.to_datetime(record.published, errors="coerce", utc=True)
        if not paper_id or not title or not summary or pd.isna(published):
            continue
        run_timestamp = pd.Timestamp(run_date)
        if run_timestamp.tzinfo is None:
            run_timestamp = run_timestamp.tz_localize("UTC")
        else:
            run_timestamp = run_timestamp.tz_convert("UTC")
        age_days = max(0, (run_timestamp - published).days)
        rows.append({
            "paper_id": paper_id, "title": title, "summary": summary,
            "authors": authors, "categories": categories,
            "primary_category": normalize_whitespace(record.primary_category or ""),
            "published": published.isoformat(), "updated": normalize_whitespace(record.updated or ""),
            "abs_url": normalize_whitespace(record.abs_url or ""), "pdf_url": normalize_whitespace(record.pdf_url or ""),
            "comment": normalize_whitespace(record.comment or ""),
            "authors_joined": ", ".join(dict.fromkeys(authors)),
            "categories_joined": ", ".join(dict.fromkeys(categories)),
            "summary_chars": len(summary), "age_days": int(age_days),
            "text_for_embedding": f"Title: {title}\nAuthors: {', '.join(dict.fromkeys(authors))}\nSummary: {summary}",
        })
    columns = ["paper_id", "title", "summary", "authors", "categories", "primary_category", "published", "updated", "abs_url", "pdf_url", "comment", "authors_joined", "categories_joined", "summary_chars", "age_days", "text_for_embedding"]
    return pd.DataFrame(rows, columns=columns).drop_duplicates("paper_id", keep="first").sort_values("published").reset_index(drop=True)
