from __future__ import annotations

import pandas as pd
import json
from pathlib import Path


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """TODO(student): simulate nhieu dang data corruption.

    Pseudo-code:
    1. Drop mot so latest records.
    2. Blank summary o mot so dong.
    3. Inject noise vao text.
    4. Lam title bi truncate.
    5. Lam published date cu di.
    6. Add duplicate rows.
    7. Rebuild `text_for_embedding`.
    8. Ghi corruption log vao output_log_path.
    """
    corrupted = df.copy(deep=True)
    events = []
    if corrupted.empty:
        Path(output_log_path).write_text("[]\n", encoding="utf-8")
        return corrupted
    count = max(1, len(corrupted) // 6)
    for index in corrupted.index[:count]:
        paper_id = corrupted.at[index, "paper_id"]
        corrupted.at[index, "summary"] = ""
        corrupted.at[index, "summary_chars"] = 0
        events.append({"paper_id": paper_id, "type": "missing_summary"})
    for index in corrupted.index[count:count * 2]:
        paper_id = corrupted.at[index, "paper_id"]
        corrupted.at[index, "title"] = str(corrupted.at[index, "title"])[:40]
        events.append({"paper_id": paper_id, "type": "truncated_title"})
    for index in corrupted.index[-count:]:
        paper_id = corrupted.at[index, "paper_id"]
        corrupted.at[index, "published"] = "2000-01-01T00:00:00+00:00"
        corrupted.at[index, "age_days"] = 9999
        events.append({"paper_id": paper_id, "type": "stale_published_date"})
    corrupted["text_for_embedding"] = corrupted.apply(
        lambda row: f"Title: {row['title']}\nAuthors: {row['authors_joined']}\nSummary: {row['summary']}", axis=1
    )
    path = Path(output_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(events, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return corrupted
