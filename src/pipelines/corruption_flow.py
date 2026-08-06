from __future__ import annotations

import pandas as pd

from core.config import load_settings
from core.utils import now_utc, read_json, write_csv, write_json
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report


def main() -> None:
    """Corruption -> evaluate -> repair -> compare flow (Phase 2 / CP5)."""
    print("=== STARTING CORRUPTION FLOW (PHASE 2) ===")
    settings = load_settings()

    # 1. Baseline must already exist. Never overwrite baseline artifacts below.
    print("1. Loading baseline artifacts...")
    if not settings.paths.baseline_metrics.exists() or not settings.paths.clean_csv.exists():
        raise RuntimeError(
            "Baseline artifacts not found. Run script/run_phase1.py before the corruption flow."
        )
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    baseline_df = pd.read_csv(settings.paths.clean_csv)
    baseline_quality_path = settings.paths.quality_dir / "baseline-quality.json"
    baseline_quality = (
        read_json(baseline_quality_path)
        if baseline_quality_path.exists()
        else run_data_quality_checks(baseline_df, settings, "baseline_quality")
    )
    baseline_freshness = (
        read_json(settings.paths.freshness_report)
        if settings.paths.freshness_report.exists()
        else build_freshness_report(baseline_df, settings, settings.paths.freshness_report)
    )
    print(f"   Baseline: {len(baseline_df)} clean rows, hit_rate={baseline_metrics.get('retrieval_hit_rate', 0.0):.4f}")

    # 2. Corrupt the clean baseline dataframe (in-memory copy only; baseline_df untouched).
    print("2. Corrupting clean dataset...")
    corrupted_df = corrupt_clean_dataframe(baseline_df, settings.paths.corruption_log)
    corruption_log = read_json(settings.paths.corruption_log)
    print(f"   Corrupted dataset: {len(corrupted_df)} rows (baseline had {len(baseline_df)}).")
    print(f"   Corruption types applied: {corruption_log.get('events_by_type')}")

    # 3. Save corrupted artifacts to dedicated corrupted paths (never overwrite baseline paths).
    print("3. Saving corrupted clean data...")
    write_csv(corrupted_df, settings.paths.corrupted_clean_csv)
    write_json(settings.paths.corrupted_clean_json, corrupted_df.to_dict(orient="records"))
    print(f"   Saved to {settings.paths.corrupted_clean_csv} and {settings.paths.corrupted_clean_json}")

    # 4. Rebuild a dedicated corrupted index/collection (papers-corrupted); papers-baseline stays untouched.
    print("4. Building corrupted ChromaDB index...")
    corrupted_index = LocalEmbeddingIndex.build(corrupted_df, settings, settings.paths.corrupted_embeddings_json)
    print(f"   Corrupted collection: {corrupted_index.collection_name} ({len(corrupted_index.documents)} documents)")

    # 5. Evaluate corrupted data with the exact same locked test set used for baseline.
    print("5. Evaluating corrupted pipeline against the locked test set...")
    corrupted_bundle = evaluate_pipeline(
        settings,
        corrupted_index,
        settings.paths.eval_testset,
        settings.paths.corrupted_metrics,
        settings.paths.corrupted_answers,
    )
    print(f"   Corrupted Hit Rate: {corrupted_bundle.summary.get('retrieval_hit_rate', 0.0):.4f}")
    print(f"   Corrupted Token F1: {corrupted_bundle.summary.get('mean_token_f1', 0.0):.4f}")

    # 6. Quality/freshness checks on corrupted data, saved to dedicated corrupted paths.
    print("6. Running quality/freshness checks on corrupted data...")
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(corrupted_df, settings, settings.paths.corrupted_freshness_report)
    print(
        f"   Corrupted Quality Passed: {corrupted_quality.get('summary', {}).get('passed', 0)} "
        f"/ {len(corrupted_quality.get('checks', []))}"
    )
    print(f"   Corrupted Freshness: {corrupted_freshness.get('status', 'unknown')}")

    # 7. Repair: re-clean from the original raw source (never hand-edit corrupted rows/answers/metrics).
    print("7. Repairing dataset from raw source records...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, now_utc())
    write_csv(repaired_df, settings.paths.repaired_clean_csv)
    write_json(settings.paths.repaired_clean_json, repaired_df.to_dict(orient="records"))
    print(f"   Repaired dataset: {len(repaired_df)} rows rebuilt from {len(raw_records)} raw records.")

    # 8. Rebuild a dedicated repaired index/collection and evaluate on the same locked test set.
    print("8. Building repaired ChromaDB index and evaluating...")
    repaired_index = LocalEmbeddingIndex.build(repaired_df, settings, settings.paths.repaired_embeddings_json)
    repaired_bundle = evaluate_pipeline(
        settings,
        repaired_index,
        settings.paths.eval_testset,
        settings.paths.repaired_metrics,
        settings.paths.repaired_answers,
    )
    print(f"   Repaired Hit Rate: {repaired_bundle.summary.get('retrieval_hit_rate', 0.0):.4f}")
    print(f"   Repaired Token F1: {repaired_bundle.summary.get('mean_token_f1', 0.0):.4f}")

    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(repaired_df, settings, settings.paths.repaired_freshness_report)
    print(
        f"   Repaired Quality Passed: {repaired_quality.get('summary', {}).get('passed', 0)} "
        f"/ {len(repaired_quality.get('checks', []))}"
    )
    print(f"   Repaired Freshness: {repaired_freshness.get('status', 'unknown')}")

    # 9. Comparison report: baseline vs corrupted vs repaired, with corruption-log evidence.
    print("9. Generating comparison report...")
    generate_corruption_report(
        settings.paths.comparison_report,
        baseline_metrics,
        corrupted_bundle.summary,
        repaired_bundle.summary,
        baseline_quality,
        corrupted_quality,
        repaired_quality,
        baseline_freshness,
        corrupted_freshness,
        repaired_freshness,
        corruption_log,
    )
    print(f"   Report written to {settings.paths.comparison_report}")
    print("=== CORRUPTION FLOW COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
