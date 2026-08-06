from __future__ import annotations

from typing import Any

import pandas as pd

from core.utils import first_sentence, normalize_whitespace, safe_slug, write_json


def _normalized_cell(value: object) -> str:
    """Convert a scalar dataframe cell to text without turning NaN into `nan`."""
    if value is None or pd.isna(value):
        return ""
    return normalize_whitespace(str(value))


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """Build a deterministic test set from available clean-data fields.

    Categories are optional in Crossref.  A category question is therefore only
    emitted for rows with a source-backed ``categories_joined`` value; the
    function never invents a category merely to satisfy a question type.
    """
    required_columns = {"paper_id", "title", "summary", "authors_joined", "published"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Clean dataset is missing required test-set columns: {missing}")

    candidates: list[dict[str, str]] = []
    for row in df.to_dict(orient="records"):
        paper_id = _normalized_cell(row.get("paper_id"))
        title = _normalized_cell(row.get("title"))
        summary = _normalized_cell(row.get("summary"))
        authors = _normalized_cell(row.get("authors_joined"))
        published = _normalized_cell(row.get("published"))
        categories = _normalized_cell(row.get("categories_joined"))
        if paper_id and title and summary and published:
            candidates.append(
                {
                    "paper_id": paper_id,
                    "title": title,
                    "summary": summary,
                    "authors": authors,
                    "published": published,
                    "categories": categories,
                }
            )

    if not candidates:
        raise ValueError("No clean records contain the fields required to build an evaluation set.")

    sample_count = min(6, len(candidates))
    if sample_count == len(candidates):
        selected = candidates
    else:
        selected_indices = {
            round(position * (len(candidates) - 1) / (sample_count - 1))
            for position in range(sample_count)
        }
        selected = [candidate for index, candidate in enumerate(candidates) if index in selected_indices]

    test_set: list[dict[str, Any]] = []
    for candidate in selected:
        title = candidate["title"]
        paper_id = candidate["paper_id"]
        base_id = safe_slug(paper_id)
        common = {"ground_truth_doc_ids": [paper_id]}
        test_set.extend(
            [
                {
                    "id": f"{base_id}-summary",
                    "question_type": "summary",
                    "question": f"What is the main topic of '{title}'?",
                    "ground_truth": first_sentence(candidate["summary"]),
                    **common,
                },
                {
                    "id": f"{base_id}-date",
                    "question_type": "date",
                    "question": f"When was '{title}' published?",
                    "ground_truth": candidate["published"],
                    **common,
                },
            ]
        )
        if candidate["authors"]:
            test_set.append(
                {
                    "id": f"{base_id}-authors",
                    "question_type": "authors",
                    "question": f"Who authored '{title}'?",
                    "ground_truth": candidate["authors"],
                    **common,
                }
            )
        if candidate["categories"]:
            test_set.append(
                {
                    "id": f"{base_id}-categories",
                    "question_type": "categories",
                    "question": f"What categories are assigned to '{title}'?",
                    "ground_truth": candidate["categories"],
                    **common,
                }
            )

    write_json(output_path, test_set)
    return test_set
