from __future__ import annotations

from datetime import datetime
from html import unescape
import re

import pandas as pd

from ingestion.crossref import PaperRecord
from core.utils import normalize_whitespace


def _clean_source_text(value: object) -> str:
    """Remove Crossref JATS/HTML markup while preserving readable text."""
    text = unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return normalize_whitespace(text)


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Normalize raw records into the stable clean/index schema."""
    rows = []
    for record in records:
        title = _clean_source_text(record.title)
        summary = _clean_source_text(record.summary)
        paper_id = normalize_whitespace(record.paper_id or "").lower()
        authors = [_clean_source_text(value) for value in (record.authors or [])]
        authors = [value for value in authors if value]
        categories = [_clean_source_text(value) for value in (record.categories or [])]
        categories = [value for value in categories if value]
        published = pd.to_datetime(record.published, errors="coerce", utc=True)
        if not paper_id or not title or not summary or pd.isna(published):
            continue
        run_timestamp = pd.Timestamp(run_date)
        if run_timestamp.tzinfo is None:
            run_timestamp = run_timestamp.tz_localize("UTC")
        else:
            run_timestamp = run_timestamp.tz_convert("UTC")
        age_days = max(0, (run_timestamp - published).days)
        authors_joined = ", ".join(dict.fromkeys(authors))
        categories_joined = ", ".join(dict.fromkeys(categories))
        embedding_sections = [f"Title: {title}"]
        if authors_joined:
            embedding_sections.append(f"Authors: {authors_joined}")
        if categories_joined:
            embedding_sections.append(f"Categories: {categories_joined}")
        embedding_sections.append(f"Summary: {summary}")

        rows.append({
            "paper_id": paper_id, "title": title, "summary": summary,
            "authors": authors, "categories": categories,
            "primary_category": _clean_source_text(record.primary_category),
            "published": published.isoformat(), "updated": _clean_source_text(record.updated),
            "abs_url": normalize_whitespace(record.abs_url or ""), "pdf_url": normalize_whitespace(record.pdf_url or ""),
            "comment": _clean_source_text(record.comment),
            "authors_joined": authors_joined,
            "categories_joined": categories_joined,
            "summary_chars": len(summary), "age_days": int(age_days),
            "text_for_embedding": "\n".join(embedding_sections),
        })
    columns = ["paper_id", "title", "summary", "authors", "categories", "primary_category", "published", "updated", "abs_url", "pdf_url", "comment", "authors_joined", "categories_joined", "summary_chars", "age_days", "text_for_embedding"]
    return pd.DataFrame(rows, columns=columns).drop_duplicates("paper_id", keep="first").sort_values("published").reset_index(drop=True)
