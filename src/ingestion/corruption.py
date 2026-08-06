from __future__ import annotations

import pandas as pd
import json
from pathlib import Path

_NOISE_TEXT = (
    " ##CORRUPTED-NOISE## asdkjqwe lorem ipsum garbled-token-9931 "
    "xzxzxz injected-noise !!! qweqweqwe"
)
_STALE_PUBLISHED = "2000-01-01T00:00:00+00:00"
_STALE_AGE_DAYS = 9999
_TITLE_TRUNCATE_LEN = 40


def _rebuild_embedding_text(row: pd.Series) -> str:
    sections = [f"Title: {row['title']}"]
    authors_joined = row.get("authors_joined") or ""
    categories_joined = row.get("categories_joined") or ""
    if authors_joined:
        sections.append(f"Authors: {authors_joined}")
    if categories_joined:
        sections.append(f"Categories: {categories_joined}")
    sections.append(f"Summary: {row['summary']}")
    return "\n".join(sections)


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """Simulate intentional, logged data corruption on a cleaned dataframe.

    Applies six distinct, non-overlapping corruption types across disjoint
    row slices so each affected record only carries one fault (keeps the
    impact of each fault type separately measurable):
    1. Drop some of the most recently published records (missing data).
    2. Blank out summary text.
    3. Inject noise into summary text.
    4. Truncate title.
    5. Make the publication date stale (far in the past).
    6. Duplicate rows.

    A JSON log with per-record before/after evidence and row-count deltas
    is written to `output_log_path` so the impact is auditable.
    """
    baseline_row_count = len(df)
    corrupted = df.copy(deep=True)
    events: list[dict] = []

    if corrupted.empty:
        Path(output_log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_log_path).write_text(
            json.dumps({"baseline_row_count": 0, "corrupted_row_count": 0, "events": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        return corrupted

    # 1. Drop some of the latest-published records (simulates missing/lost data).
    published_dt = pd.to_datetime(corrupted["published"], errors="coerce", utc=True)
    drop_count = max(1, baseline_row_count // 6)
    latest_index = published_dt.sort_values(ascending=False).index[:drop_count]
    for index in latest_index:
        events.append(
            {
                "paper_id": corrupted.at[index, "paper_id"],
                "type": "dropped_latest_record",
                "parameter": {"published": corrupted.at[index, "published"]},
            }
        )
    corrupted = corrupted.drop(index=latest_index)

    # Partition the remaining rows into disjoint slices for the other fault types.
    remaining_index = list(corrupted.index)
    remaining_count = len(remaining_index)
    slice_size = max(1, remaining_count // 5)

    def _take(offset: int) -> list:
        start = offset * slice_size
        end = start + slice_size if offset < 4 else remaining_count
        return remaining_index[start:end]

    blank_summary_idx = _take(0)
    noisy_summary_idx = _take(1)
    truncated_title_idx = _take(2)
    stale_date_idx = _take(3)
    duplicate_source_idx = _take(4)

    # 2. Blank summary.
    for index in blank_summary_idx:
        before = corrupted.at[index, "summary"]
        corrupted.at[index, "summary"] = ""
        corrupted.at[index, "summary_chars"] = 0
        events.append(
            {
                "paper_id": corrupted.at[index, "paper_id"],
                "type": "blank_summary",
                "parameter": {"before_chars": len(str(before))},
            }
        )

    # 3. Inject noise into summary.
    for index in noisy_summary_idx:
        before = str(corrupted.at[index, "summary"])
        after = before + _NOISE_TEXT
        corrupted.at[index, "summary"] = after
        corrupted.at[index, "summary_chars"] = len(after)
        events.append(
            {
                "paper_id": corrupted.at[index, "paper_id"],
                "type": "noisy_summary",
                "parameter": {"before_chars": len(before), "after_chars": len(after)},
            }
        )

    # 4. Truncate title.
    for index in truncated_title_idx:
        before = str(corrupted.at[index, "title"])
        after = before[:_TITLE_TRUNCATE_LEN]
        corrupted.at[index, "title"] = after
        events.append(
            {
                "paper_id": corrupted.at[index, "paper_id"],
                "type": "truncated_title",
                "parameter": {"before_len": len(before), "after_len": len(after)},
            }
        )

    # 5. Stale publication date.
    for index in stale_date_idx:
        before_published = corrupted.at[index, "published"]
        before_age_days = corrupted.at[index, "age_days"]
        corrupted.at[index, "published"] = _STALE_PUBLISHED
        corrupted.at[index, "age_days"] = _STALE_AGE_DAYS
        events.append(
            {
                "paper_id": corrupted.at[index, "paper_id"],
                "type": "stale_published_date",
                "parameter": {
                    "before_published": before_published,
                    "before_age_days": int(before_age_days) if pd.notna(before_age_days) else None,
                    "after_published": _STALE_PUBLISHED,
                    "after_age_days": _STALE_AGE_DAYS,
                },
            }
        )

    # 6. Duplicate rows (append copies with the same paper_id -> breaks uniqueness).
    duplicate_rows = corrupted.loc[duplicate_source_idx].copy()
    if not duplicate_rows.empty:
        corrupted = pd.concat([corrupted, duplicate_rows], ignore_index=True)
        for _, row in duplicate_rows.iterrows():
            events.append(
                {
                    "paper_id": row["paper_id"],
                    "type": "duplicate_row",
                    "parameter": {"duplicated_from_paper_id": row["paper_id"]},
                }
            )
    else:
        corrupted = corrupted.reset_index(drop=True)

    corrupted["text_for_embedding"] = corrupted.apply(_rebuild_embedding_text, axis=1)

    events_by_type: dict[str, int] = {}
    for event in events:
        events_by_type[event["type"]] = events_by_type.get(event["type"], 0) + 1

    log_payload = {
        "baseline_row_count": baseline_row_count,
        "corrupted_row_count": len(corrupted),
        "events_by_type": events_by_type,
        "events": events,
    }
    path = Path(output_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log_payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return corrupted
