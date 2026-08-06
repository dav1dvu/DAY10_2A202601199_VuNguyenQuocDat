# CP2 Audit — Vai trò 4 và 5

## Vai trò 4 — RAG & Agent

### Kiểm tra manifest baseline

| Thuộc tính | Kết quả |
| --- | --- |
| Clean rows | 24 |
| Documents trong manifest | 24 |
| Backend | `chroma` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Collection name | `papers-baseline` |
| Document ID thiếu so với clean data | 0 |
| Document ID trùng trong manifest | 0 |

Manifest có metadata tối thiểu cho RAG: `paper_id`, title, published, authors, categories, summary, abstract URL và PDF URL. `content` có title, authors và cleaned summary; không chứa JATS/HTML.

### Smoke test cần hoàn tất

- Exact lookup theo title và `paper_id` `doi:10.35314/3y9hy151`.
- Semantic query: `Which paper implements a RAG chatbot for campus services?`.
- Agent factual question phải gọi `semantic_search_papers` hoặc `lookup_paper` trước khi trả lời.

**Blocker:** `data/chroma/` hiện chỉ có `.gitkeep`; không có Chroma collection persisted để load/search. Local `.venv` là Python 3.10.11, không tương thích với project Python 3.11–3.13 và chưa có dependencies. Không được ghi nhận smoke test là pass trước khi collection được rebuild trong môi trường hợp lệ.

## Vai trò 5 — Evaluation & Observability

### Kiểm tra test set đã khóa

| Thuộc tính | Kết quả |
| --- | --- |
| Path | `data/eval/test_set.json` |
| Samples | 18 |
| Question types | `summary`, `authors`, `date` |
| Question/ground truth rỗng | 0 |
| `ground_truth_doc_ids` không có trong clean data | 0 |

Không có câu hỏi `categories`, vì `categories_joined` trống trên 24/24 cleaned records. Đây là quyết định bảo toàn ground truth có nguồn.

### Baseline quality/freshness signals

| Signal | Giá trị |
| --- | --- |
| Clean rows | 24 |
| Blank paper ID/title/summary/embedding text | 0 / 0 / 0 / 0 |
| Duplicate paper ID | 0 |
| Duplicate row | 0 |
| `age_days` min/max | 0 / 192 |
| Rows > 180 ngày | 1 |
| Freshness status dự kiến | `stale` |

### Khuôn phase-1 report cần điền ở CP3

1. Source summary: raw/clean count và source snapshot.
2. Index summary: model, collection, manifest document count, smoke-test evidence.
3. Evaluation: `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score` và answers artifact.
4. Quality/freshness: từng check pass/fail; phải nêu 1 stale row nếu kết quả chạy lại vẫn như hiện tại.
5. Kết luận chỉ dùng artifact JSON/Markdown thực tế, không khẳng định RAG chạy trước khi có smoke-test evidence.
