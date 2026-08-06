# Phase 1 Baseline Data Pipeline Report

## 1. Source Data Summary
- **Source API:** Crossref REST API
- **Query/Filter:** `query: agentic retrieval augmented generation large language model | filter: from-pub-date:2026-02-07,has-abstract:true`
- **Max Results:** 24
- **Total Records Ingested:** 24
- **Freshness Status:** `stale` (Oldest: `2026-01-25T14:31:54+00:00`, Latest: `2026-08-05T14:17:54+00:00`)

## 2. RAG Evaluation Metrics (Baseline)
- **Retrieval Hit Rate:** `1.0000`
- **Mean Token F1 Score:** `1.0000`
- **Judge Accuracy:** `1.0000`
- **Mean Judge Score:** `5.0000`

## 3. Data Quality Checks
- **Overall Status:** ⚠️ SOME CHECKS FAILED
- **Passed Checks:** 8 / 9

| Check Name | Quality Dimension | Expected | Actual Value | Status |
| :--- | :--- | :--- | :--- | :--- |
| row_count | completeness | `>= 1` | `24` | ✅ PASS |
| paper_id_present | completeness | `0 blank IDs` | `0` | ✅ PASS |
| paper_id_unique | uniqueness | `0 duplicate IDs` | `0` | ✅ PASS |
| title_present | completeness | `0 blank titles` | `0` | ✅ PASS |
| summary_min_length | completeness | `0 summaries shorter than 20 characters` | `0` | ✅ PASS |
| embedding_text_present | completeness | `0 blank embedding texts` | `0` | ✅ PASS |
| duplicate_rows | uniqueness | `0 duplicate rows` | `0` | ✅ PASS |
| age_days_valid | validity | `all non-negative numeric values` | `0` | ✅ PASS |
| freshness_threshold | freshness | `0 rows older than 180 days` | `1` | ❌ FAIL |

---
*Report generated automatically by Data Pipeline Observability Engine.*
