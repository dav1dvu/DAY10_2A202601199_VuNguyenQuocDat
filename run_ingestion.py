import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# pyrefly: ignore [missing-import]
from src.core.config import load_settings
# pyrefly: ignore [missing-import]
from src.ingestion.crossref import fetch_source_records

if __name__ == "__main__":
    print("Loading config...")
    settings = load_settings()
    
    print("Sending request to Crossref API...")
    records = fetch_source_records(settings)
    
    print(f"SUCCESS: Fetched {len(records)} papers!")
    print(f"Raw JSON saved at: {settings.paths.raw_api_response}")
