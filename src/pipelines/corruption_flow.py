from __future__ import annotations

import logging
import pandas as pd
from core.config import load_settings
from core.utils import read_json, write_csv, write_json, now_utc
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report

logger = logging.getLogger(__name__)


def main() -> None:
    """Orchestrate corruption, re-evaluation, repair, and comparison reporting."""
    print("=== STARTING PHA 2 CORRUPTION & REPAIR FLOW ===")
    
    # 1. Load settings, baseline metrics, and baseline clean data
    print("1. Loading settings and baseline metrics...")
    settings = load_settings()
    if not settings.paths.baseline_metrics.exists() or not settings.paths.clean_json.exists():
        raise RuntimeError("Baseline artifacts are missing. Run Phase 1 baseline pipeline first.")
        
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    baseline_df = pd.read_json(settings.paths.clean_json)
    print(f"   Loaded baseline metrics and {len(baseline_df)} clean papers.")
    
    # 2. Create corrupted dataframe
    print("2. Simulating intentional data corruption on baseline data...")
    corrupted_df = corrupt_clean_dataframe(baseline_df, settings.paths.corruption_log)
    print(f"   Corrupted records count: {len(corrupted_df)}")
    
    # 3. Save corrupted clean dataset
    print(f"   Saving corrupted clean data to CSV ({settings.paths.corrupted_clean_csv}) and JSON ({settings.paths.corrupted_clean_json})...")
    write_csv(corrupted_df, settings.paths.corrupted_clean_csv)
    write_json(settings.paths.corrupted_clean_json, corrupted_df.to_dict(orient="records"))
    
    # 4. Rebuild index on corrupted data
    print("3. Building ChromaDB vector index for corrupted data...")
    corrupted_index = LocalEmbeddingIndex.build(
        df=corrupted_df,
        settings=settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json
    )
    print(f"   Corrupted index collection '{corrupted_index.collection_name}' built successfully.")
    
    # 5. Evaluate corrupted index on locked test set
    print("4. Evaluating RAG agent on corrupted data...")
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers
    )
    print(f"   Corrupted Hit Rate: {corrupted_bundle.summary.get('retrieval_hit_rate', 0.0):.4f}")
    print(f"   Corrupted Token F1: {corrupted_bundle.summary.get('mean_token_f1', 0.0):.4f}")
    
    # 6. Run quality and freshness checks on corrupted data
    print("5. Running observability quality and freshness checks on corrupted data...")
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
    corrupted_freshness_report_path = settings.paths.quality_dir / "corrupted_freshness_report.json"
    corrupted_freshness = build_freshness_report(corrupted_df, settings, corrupted_freshness_report_path)
    print(f"   Quality Checks Passed: {corrupted_quality.get('summary', {}).get('passed', 0)} / {len(corrupted_quality.get('checks', []))}")
    print(f"   Freshness status: {corrupted_freshness.get('status', 'unknown')}")
    
    # 7. Repair data from raw records
    print("6. Repairing dataset from raw source records...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    run_date = now_utc()
    repaired_df = build_clean_dataframe(raw_records, run_date)
    print(f"   Repaired records count (lineage recovery): {len(repaired_df)}")
    
    # 8. Save repaired clean dataset
    print(f"   Saving repaired data to CSV ({settings.paths.repaired_clean_csv}) and JSON ({settings.paths.repaired_clean_json})...")
    write_csv(repaired_df, settings.paths.repaired_clean_csv)
    write_json(settings.paths.repaired_clean_json, repaired_df.to_dict(orient="records"))
    
    # 9. Rebuild index on repaired data
    print("7. Building ChromaDB vector index for repaired data...")
    repaired_index = LocalEmbeddingIndex.build(
        df=repaired_df,
        settings=settings,
        embeddings_output_path=settings.paths.repaired_embeddings_json
    )
    print(f"   Repaired index collection '{repaired_index.collection_name}' built successfully.")
    
    # 10. Evaluate repaired index on locked test set
    print("8. Evaluating RAG agent on repaired data...")
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers
    )
    print(f"   Repaired Hit Rate: {repaired_bundle.summary.get('retrieval_hit_rate', 0.0):.4f}")
    print(f"   Repaired Token F1: {repaired_bundle.summary.get('mean_token_f1', 0.0):.4f}")
    
    # 11. Run quality and freshness checks on repaired data
    print("9. Running observability quality and freshness checks on repaired data...")
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness_report_path = settings.paths.quality_dir / "repaired_freshness_report.json"
    repaired_freshness = build_freshness_report(repaired_df, settings, repaired_freshness_report_path)
    print(f"   Quality Checks Passed: {repaired_quality.get('summary', {}).get('passed', 0)} / {len(repaired_quality.get('checks', []))}")
    print(f"   Freshness status: {repaired_freshness.get('status', 'unknown')}")
    
    # 12. Generate comparison report
    print("10. Generating RAG pipeline comparison report...")
    baseline_quality_path = settings.paths.quality_dir / "baseline-quality.json"
    baseline_quality = read_json(baseline_quality_path) if baseline_quality_path.exists() else {}
    baseline_freshness = read_json(settings.paths.freshness_report) if settings.paths.freshness_report.exists() else {}
    corruption_log = read_json(settings.paths.corruption_log) if settings.paths.corruption_log.exists() else {}

    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        baseline_quality=baseline_quality,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        baseline_freshness=baseline_freshness,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
        corruption_log=corruption_log,
    )
    print(f"    Comparison report successfully written to {settings.paths.comparison_report}")
    print("=== PHA 2 CORRUPTION & REPAIR FLOW COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
