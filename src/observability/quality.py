from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import safe_slug, write_json


def _text_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series("", index=df.index, dtype="string")
    return df[column].fillna("").astype(str).str.strip()


def _check(name: str, dimension: str, expected: str, value: Any, passed: bool) -> dict[str, Any]:
    return {
        "name": name,
        "dimension": dimension,
        "expected": expected,
        "value": value,
        "passed": passed,
        "status": "pass" if passed else "fail",
    }


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Run auditable data-quality checks and persist a JSON report."""
    paper_ids = _text_series(df, "paper_id")
    titles = _text_series(df, "title")
    summaries = _text_series(df, "summary")
    embedding_texts = _text_series(df, "text_for_embedding")
    age_days = pd.to_numeric(df.get("age_days"), errors="coerce") if "age_days" in df else pd.Series(float("nan"), index=df.index)

    blank_paper_ids = int((paper_ids == "").sum())
    duplicate_paper_ids = int(paper_ids[paper_ids != ""].duplicated().sum())
    blank_titles = int((titles == "").sum())
    short_summaries = int((summaries.str.len() < 20).sum())
    blank_embedding_texts = int((embedding_texts == "").sum())
    duplicate_rows = int(df.drop(columns=["authors", "categories"], errors="ignore").duplicated().sum())
    invalid_age_days = int(age_days.isna().sum() + (age_days < 0).sum())
    stale_rows = int((age_days > settings.freshness_threshold_days).sum())

    checks = [
        _check("row_count", "completeness", ">= 1", int(len(df)), len(df) > 0),
        _check("paper_id_present", "completeness", "0 blank IDs", blank_paper_ids, blank_paper_ids == 0),
        _check("paper_id_unique", "uniqueness", "0 duplicate IDs", duplicate_paper_ids, duplicate_paper_ids == 0),
        _check("title_present", "completeness", "0 blank titles", blank_titles, blank_titles == 0),
        _check("summary_min_length", "completeness", "0 summaries shorter than 20 characters", short_summaries, short_summaries == 0),
        _check("embedding_text_present", "completeness", "0 blank embedding texts", blank_embedding_texts, blank_embedding_texts == 0),
        _check("duplicate_rows", "uniqueness", "0 duplicate rows", duplicate_rows, duplicate_rows == 0),
        _check("age_days_valid", "validity", "all non-negative numeric values", invalid_age_days, invalid_age_days == 0),
        _check(
            "freshness_threshold",
            "freshness",
            f"0 rows older than {settings.freshness_threshold_days} days",
            stale_rows,
            stale_rows == 0,
        ),
    ]
    payload = {
        "report_name": report_name,
        "total_rows": int(len(df)),
        "freshness_threshold_days": settings.freshness_threshold_days,
        "checks": checks,
        "summary": {
            "passed": sum(check["passed"] for check in checks),
            "failed": sum(not check["passed"] for check in checks),
            "all_passed": all(check["passed"] for check in checks),
        },
    }
    output_path = settings.paths.quality_dir / f"{safe_slug(report_name)}.json"
    write_json(output_path, payload)
    return payload


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """Summarize publication freshness from clean-data timestamps and age fields."""
    published = pd.to_datetime(df.get("published"), errors="coerce", utc=True) if "published" in df else pd.Series(pd.NaT, index=df.index)
    age_days = pd.to_numeric(df.get("age_days"), errors="coerce") if "age_days" in df else pd.Series(float("nan"), index=df.index)
    valid_published = published.dropna()
    invalid_age_days = int(age_days.isna().sum() + (age_days < 0).sum())
    stale_rows = int((age_days > settings.freshness_threshold_days).sum())
    is_fresh = bool(len(df) > 0 and len(valid_published) == len(df) and invalid_age_days == 0 and stale_rows == 0)
    payload = {
        "total_rows": int(len(df)),
        "latest_published": valid_published.max().isoformat() if not valid_published.empty else None,
        "oldest_published": valid_published.min().isoformat() if not valid_published.empty else None,
        "stale_rows": stale_rows,
        "invalid_age_days": invalid_age_days,
        "freshness_threshold_days": settings.freshness_threshold_days,
        "is_fresh": is_fresh,
        "status": "fresh" if is_fresh else "stale" if stale_rows else "unknown",
    }
    write_json(report_path, payload)
    return payload
