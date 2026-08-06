from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import logging
from pathlib import Path
import time
import requests

from core.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def generate_stable_id(item: dict) -> str:
    doi = item.get("DOI", "").strip().lower()
    if doi:
        return f"doi:{doi}"
        
    url = item.get("URL", "").strip().lower()
    if url:
        return f"url:{url}"
        
    title = item.get("title", [""])[0] if item.get("title") else ""
    title_norm = title.strip().lower()
    
    # Hash fallback if no DOI or URL
    raw_str = f"{title_norm}"
    return f"hash:{hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:12]}"


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload thanh list PaperRecord.
    
    - Tao paper_id on dinh tu DOI, URL, hoac Hash.
    - Bo qua record loi khong de loi toan bo batch.
    """
    records = []
    items = payload.get("message", {}).get("items", [])
    
    for item in items:
        try:
            paper_id = generate_stable_id(item)
                
            title = item.get("title", [""])[0] if item.get("title") else ""
            summary = item.get("abstract", "")
            
            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip()
                if name:
                    authors.append(name)
                    
            categories = item.get("subject", [])
            primary_category = categories[0] if categories else ""
            
            # Crossref dates
            created_obj = item.get("created", {})
            created = created_obj.get("date-time", "")
            published = created
            updated = created
            
            abs_url = item.get("URL", "")
            
            pdf_url = ""
            links = item.get("link", [])
            for link in links:
                if link.get("content-type") == "application/pdf":
                    pdf_url = link.get("URL", "")
                    break
                    
            records.append(PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=""
            ))
        except Exception as e:
            logger.warning(f"Skipping a bad record due to error: {e}")
            continue
        
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Goi source API, luu raw response, parse thanh records."""
    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results
    }
    
    headers = {
        "User-Agent": "Day10Agent/1.0 (mailto:student@vinuni.edu.vn)"
    }
    
    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            if response.status_code in (429, 503):
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise RuntimeError(f"Lỗi khi gọi Crossref API sau {max_retries} lần thử. Status: {response.status_code}")
            
            response.raise_for_status()
            break
        except requests.HTTPError as e:
            raise RuntimeError(f"Lỗi khi gọi Crossref API. Status: {response.status_code}") from e
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Lỗi khi gọi Crossref API sau {max_retries} lần thử: {e}") from e
            time.sleep(2 ** attempt)
        
    payload = response.json()
    
    settings.paths.raw_api_response.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.paths.raw_api_response, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        
    records = parse_crossref_payload(payload)
    
    settings.paths.raw_records_json.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.paths.raw_records_json, "w", encoding="utf-8") as f:
        json.dump([vars(r) for r in records], f, ensure_ascii=False, indent=2)
        
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Doc JSON snapshot va map thanh list `PaperRecord`."""
    if not path.exists():
        return []
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return [PaperRecord(**record) for record in data]
