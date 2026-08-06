# RAG Pipeline Corruption & Repair Comparison Report

## 1. Core Performance Comparison

| Metric | Baseline | Corrupted | Repaired | Impact (Corrupted - Baseline) | Recovery (Repaired - Corrupted) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Retrieval Hit Rate** | `1.0000` | `0.8333` | `1.0000` | `-0.1667` | `+0.1667` |
| **Mean Token F1** | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` |
| **Judge Accuracy** | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` |
| **Mean Judge Score** | `5.0000` | `3.8889` | `5.0000` | `-1.1111` | `+1.1111` |

## 2. Corruption Log Summary

- **Baseline row count:** `24`
- **Corrupted row count:** `24`

| Corruption Type | Records Affected |
| :--- | :---: |
| `blank_summary` | 4 |
| `dropped_latest_record` | 4 |
| `duplicate_row` | 4 |
| `noisy_summary` | 4 |
| `stale_published_date` | 4 |
| `truncated_title` | 4 |

## 3. Data Observability Comparison

| Metric | Baseline | Corrupted | Repaired |
| :--- | :--- | :--- | :--- |
| **Data Quality Checks Passed** | `8 / 9` | `5 / 9` | `8 / 9` |
| **Freshness Status** | `stale` | `stale` | `stale` |

## 4. Analysis & Key Insights
1. **Data Corruption Impact:** Data corruption (dropping records, blanking/noising summary text, truncating titles, staling timestamps, duplicating rows) directly causes measurable degradation in data quality checks, freshness signals, and/or RAG retrieval and answer-quality metrics — see the deltas above and the corruption log summary for which fault types were applied.
2. **Data Repair Effectiveness:** Repairing the dataset by re-cleaning from the authoritative raw Crossref records (not by hand-editing corrupted rows) restores quality/freshness signals and RAG metrics back toward baseline levels — see the recovery deltas above. Any metric that does not fully recover is reported as-is rather than assumed fixed.

---
*Report generated automatically by Data Pipeline Observability Engine.*
