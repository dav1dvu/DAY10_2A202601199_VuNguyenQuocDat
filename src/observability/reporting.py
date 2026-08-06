from __future__ import annotations

from typing import Any
from pathlib import Path


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Viet markdown report cho baseline phase."""
    checks_rows = []
    for check in quality.get("checks", []):
        status_emoji = "✅ PASS" if check["passed"] else "❌ FAIL"
        checks_rows.append(
            f"| {check['name']} | {check['dimension']} | `{check['expected']}` | `{check['value']}` | {status_emoji} |"
        )
    checks_table = "\n".join(checks_rows)

    md = f"""# Phase 1 Baseline Data Pipeline Report

## 1. Source Data Summary
- **Source API:** {source_summary.get("source", "N/A")}
- **Query/Filter:** `{source_summary.get("query_filter", "N/A")}`
- **Max Results:** {source_summary.get("max_results", "N/A")}
- **Total Records Ingested:** {source_summary.get("total_rows", "N/A")}
- **Freshness Status:** `{freshness.get("status", "N/A")}` (Oldest: `{freshness.get("oldest_published", "N/A")}`, Latest: `{freshness.get("latest_published", "N/A")}`)

## 2. RAG Evaluation Metrics (Baseline)
- **Retrieval Hit Rate:** `{metrics.get("retrieval_hit_rate", 0.0):.4f}`
- **Mean Token F1 Score:** `{metrics.get("mean_token_f1", 0.0):.4f}`
- **Judge Accuracy:** `{metrics.get("judge_accuracy", 0.0):.4f}`
- **Mean Judge Score:** `{metrics.get("mean_judge_score", 0.0):.4f}`

## 3. Data Quality Checks
- **Overall Status:** {"✅ ALL PASSED" if quality.get("summary", {}).get("all_passed") else "⚠️ SOME CHECKS FAILED"}
- **Passed Checks:** {quality.get("summary", {}).get("passed", 0)} / {len(quality.get("checks", []))}

| Check Name | Quality Dimension | Expected | Actual Value | Status |
| :--- | :--- | :--- | :--- | :--- |
{checks_table}

---
*Report generated automatically by Data Pipeline Observability Engine.*
"""
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(md, encoding="utf-8")


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    baseline_quality: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    baseline_freshness: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
    corruption_log: dict[str, Any] | None = None,
) -> None:
    """Viet markdown report so sanh baseline/corrupted/repaired."""
    b_hr = baseline_metrics.get("retrieval_hit_rate", 0.0)
    c_hr = corrupted_metrics.get("retrieval_hit_rate", 0.0)
    r_hr = repaired_metrics.get("retrieval_hit_rate", 0.0)

    b_f1 = baseline_metrics.get("mean_token_f1", 0.0)
    c_f1 = corrupted_metrics.get("mean_token_f1", 0.0)
    r_f1 = repaired_metrics.get("mean_token_f1", 0.0)

    b_acc = baseline_metrics.get("judge_accuracy", 0.0)
    c_acc = corrupted_metrics.get("judge_accuracy", 0.0)
    r_acc = repaired_metrics.get("judge_accuracy", 0.0)

    b_score = baseline_metrics.get("mean_judge_score", 0.0)
    c_score = corrupted_metrics.get("mean_judge_score", 0.0)
    r_score = repaired_metrics.get("mean_judge_score", 0.0)

    hr_delta = c_hr - b_hr
    hr_recovery = r_hr - c_hr
    f1_delta = c_f1 - b_f1
    f1_recovery = r_f1 - c_f1
    acc_delta = c_acc - b_acc
    acc_recovery = r_acc - c_acc
    score_delta = c_score - b_score
    score_recovery = r_score - c_score

    b_passed = baseline_quality.get("summary", {}).get("passed", 0)
    b_total = len(baseline_quality.get("checks", []))
    c_passed = corrupted_quality.get("summary", {}).get("passed", 0)
    c_total = len(corrupted_quality.get("checks", []))
    r_passed = repaired_quality.get("summary", {}).get("passed", 0)
    r_total = len(repaired_quality.get("checks", []))

    row_count_rows = ""
    events_by_type = (corruption_log or {}).get("events_by_type")
    if events_by_type:
        b_rows = (corruption_log or {}).get("baseline_row_count", "N/A")
        c_rows = (corruption_log or {}).get("corrupted_row_count", "N/A")
        type_lines = "\n".join(f"| `{name}` | {count} |" for name, count in sorted(events_by_type.items()))
        row_count_rows = f"""
## 2. Corruption Log Summary

- **Baseline row count:** `{b_rows}`
- **Corrupted row count:** `{c_rows}`

| Corruption Type | Records Affected |
| :--- | :---: |
{type_lines}
"""

    md = f"""# RAG Pipeline Corruption & Repair Comparison Report

## 1. Core Performance Comparison

| Metric | Baseline | Corrupted | Repaired | Impact (Corrupted - Baseline) | Recovery (Repaired - Corrupted) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Retrieval Hit Rate** | `{b_hr:.4f}` | `{c_hr:.4f}` | `{r_hr:.4f}` | `{hr_delta:+.4f}` | `{hr_recovery:+.4f}` |
| **Mean Token F1** | `{b_f1:.4f}` | `{c_f1:.4f}` | `{r_f1:.4f}` | `{f1_delta:+.4f}` | `{f1_recovery:+.4f}` |
| **Judge Accuracy** | `{b_acc:.4f}` | `{c_acc:.4f}` | `{r_acc:.4f}` | `{acc_delta:+.4f}` | `{acc_recovery:+.4f}` |
| **Mean Judge Score** | `{b_score:.4f}` | `{c_score:.4f}` | `{r_score:.4f}` | `{score_delta:+.4f}` | `{score_recovery:+.4f}` |
{row_count_rows}
## 3. Data Observability Comparison

| Metric | Baseline | Corrupted | Repaired |
| :--- | :--- | :--- | :--- |
| **Data Quality Checks Passed** | `{b_passed} / {b_total}` | `{c_passed} / {c_total}` | `{r_passed} / {r_total}` |
| **Freshness Status** | `{baseline_freshness.get("status", "N/A")}` | `{corrupted_freshness.get("status", "N/A")}` | `{repaired_freshness.get("status", "N/A")}` |

## 4. Analysis & Key Insights
1. **Data Corruption Impact:** Data corruption (dropping records, blanking/noising summary text, truncating titles, staling timestamps, duplicating rows) directly causes measurable degradation in data quality checks, freshness signals, and/or RAG retrieval and answer-quality metrics — see the deltas above and the corruption log summary for which fault types were applied.
2. **Data Repair Effectiveness:** Repairing the dataset by re-cleaning from the authoritative raw Crossref records (not by hand-editing corrupted rows) restores quality/freshness signals and RAG metrics back toward baseline levels — see the recovery deltas above. Any metric that does not fully recover is reported as-is rather than assumed fixed.

---
*Report generated automatically by Data Pipeline Observability Engine.*
"""
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(md, encoding="utf-8")
