from __future__ import annotations

import logging
from core.config import load_settings
from core.utils import now_utc, write_csv, write_json, read_json
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.testset import build_test_set
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_phase1_report

logger = logging.getLogger(__name__)


def main() -> None:
    """Baseline pipeline end-to-end."""
    print("=== STARTING PHASE 1 BASELINE PIPELINE ===")
    
    # 1. Load settings
    print("1. Loading settings...")
    settings = load_settings()
    
    # 2. Load or fetch raw records
    print("2. Ingesting raw Crossref records...")
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        print("   Fetching fresh records from Crossref API...")
        records = fetch_source_records(settings)
    else:
        print("   Loading cached raw records from local JSON...")
        records = load_raw_records(settings.paths.raw_records_json)
    print(f"   Ingested {len(records)} raw records.")
    
    # 3. Clean data
    print("3. Cleaning and modeling data...")
    run_date = now_utc()
    df = build_clean_dataframe(records, run_date)
    print(f"   Cleaned records count: {len(df)}")
    
    # 4. Save clean CSV/JSON
    print(f"   Saving cleaned data to CSV ({settings.paths.clean_csv}) and JSON ({settings.paths.clean_json})...")
    write_csv(df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, df.to_dict(orient="records"))
    
    # 5. Build Chroma index
    print("4. Building ChromaDB vector index...")
    index = LocalEmbeddingIndex.build(df, settings, settings.paths.embeddings_json)
    print(f"   Chroma index collection '{index.collection_name}' built successfully.")
    
    # 6. Create or load evaluation set
    print("5. Preparing test set...")
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        print("   Generating a fresh test set from cleaned data...")
        test_set = build_test_set(df, settings.paths.eval_testset)
    else:
        print("   Loading existing test set from JSON...")
        test_set = read_json(settings.paths.eval_testset)
    print(f"   Test set loaded with {len(test_set)} questions.")
    
    # 7. Evaluate
    print("6. Evaluating pipeline performance...")
    bundle = evaluate_pipeline(
        settings,
        index,
        settings.paths.eval_testset,
        settings.paths.baseline_metrics,
        settings.paths.baseline_answers
    )
    print(f"   Baseline Hit Rate: {bundle.summary.get('retrieval_hit_rate', 0.0):.4f}")
    print(f"   Baseline Token F1: {bundle.summary.get('mean_token_f1', 0.0):.4f}")
    
    # 8. Run quality checks and freshness report
    print("7. Running observability quality and freshness checks...")
    quality_report = run_data_quality_checks(df, settings, "baseline_quality")
    freshness_report = build_freshness_report(df, settings, settings.paths.freshness_report)
    print(f"   Quality Checks Passed: {quality_report.get('summary', {}).get('passed', 0)} / {len(quality_report.get('checks', []))}")
    print(f"   Freshness status: {freshness_report.get('status', 'unknown')}")
    
    # 9. Generate markdown report
    print("8. Generating phase 1 baseline markdown report...")
    source_summary = {
        "source": settings.source_api,
        "query_filter": f"query: {settings.source_query} | filter: {settings.source_filter}",
        "max_results": settings.max_results,
        "total_rows": len(records),
    }
    generate_phase1_report(
        settings.paths.baseline_report,
        source_summary,
        bundle.summary,
        quality_report,
        freshness_report
    )
    print(f"   Report successfully written to {settings.paths.baseline_report}")
    print("=== PHASE 1 BASELINE PIPELINE COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
