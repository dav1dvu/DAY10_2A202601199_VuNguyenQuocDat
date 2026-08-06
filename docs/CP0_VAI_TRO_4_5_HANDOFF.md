# CP0 Handoff — Vai trò 4 và 5

Tài liệu này chốt contract trước khi build baseline. Snapshot raw đã được kiểm tra ngày 2026-08-06; pipeline vẫn chưa chạy và chưa có clean/index/evaluation artifacts được ghi ra `data/`.

## Kết quả kiểm tra snapshot Crossref

| Kiểm tra | Kết quả |
| --- | --- |
| Raw records | 24 trong `data/raw/crossref_records.json` |
| Có `paper_id`, title, summary, published | 24/24 |
| `paper_id` unique | Có |
| Categories từ Crossref | 0/24 records có categories |
| Abstract | Có, nhưng đang chứa JATS/HTML như `<jats:p>` |

### Blocker cần xử lý trước CP1/CP2

1. **Categories không có dữ liệu:** không thể tạo câu hỏi `categories` có ground truth trung thực. Vai trò 2/3 cần chốt một trong hai hướng: bổ sung/enrich categories từ nguồn đáng tin cậy hoặc bỏ chính thức loại câu hỏi `categories` khỏi test set và báo cáo.
2. **Abstract còn JATS/HTML:** Vai trò 3 cần strip markup trước khi tạo `summary` và `text_for_embedding`; nếu không semantic retrieval, ground truth summary và agent answer sẽ chứa tag thay vì văn bản sạch.
3. **Môi trường hiện tại không thể chạy pipeline:** `.venv` là Python 3.10.11, trong khi project yêu cầu Python 3.11–3.13 và code dùng `datetime.UTC`; dependencies chưa được cài (`pandas` không import được), `uv` chưa có trên PATH. Vai trò 1 cần dựng lại môi trường phù hợp trước khi chạy smoke test/baseline.

## Vai trò 4 — RAG & Agent

### Contract đầu vào cho index

`LocalEmbeddingIndex.build()` nhận một cleaned `DataFrame` có tối thiểu các cột:

- `paper_id`: định danh ổn định, không rỗng và unique.
- `title`
- `text_for_embedding`: nội dung dùng để embedding, không rỗng.
- `published`
- `authors_joined`
- `categories_joined`
- `summary`
- `abs_url`
- `pdf_url`

Mỗi document trong manifest có `record_id` theo dạng `<paper_id>::<row_index>`, nhưng retrieval/evaluation dùng `paper_id` làm ground-truth document ID.

### Cấu hình đã chốt từ `src/core/config.py`

| Thành phần | Giá trị |
| --- | --- |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Baseline collection | `papers-baseline` |
| Corrupted collection | `papers-corrupted` |
| Repaired collection | `papers-repaired` |
| Persist path | `data/chroma/` |
| Retrieval top-k | `4` |

Ba collection và ba embedding manifest phải tách biệt để corruption/repaired không ghi đè baseline.

### Metadata tối thiểu cần audit

Metadata của mỗi document phải giữ được các trường sau:

- `paper_id`, `title`, `published`
- `authors_joined`, `categories_joined`, `summary`
- `abs_url`, `pdf_url`

### Smoke test đã chuẩn bị, sẽ chạy sau khi có clean data/index

1. Build baseline index từ `data/clean/papers_clean.csv`.
2. Dùng title thật `A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models` và `paper_id` `doi:10.36227/techrxiv.177272838.89432844/v1`; exact lookup theo cả hai cách phải trả đúng cùng document.
3. Dùng semantic query `Which survey reviews Deep RAG and reasoning in large language models?`; top-k phải chứa `doi:10.36227/techrxiv.177272838.89432844/v1`.
4. Gọi agent với câu hỏi factual; agent phải dùng `semantic_search_papers` hoặc `lookup_paper` trước khi trả lời.

Không dùng query, title hoặc `paper_id` bịa. Vai trò 3 bàn giao ít nhất một record clean hợp lệ để Vai trò 4 điền vào smoke-test log.

## Vai trò 5 — Evaluation & Observability

### Contract evaluation set

Mỗi sample trong `data/eval/test_set.json` có:

```json
{
  "id": "<stable-test-id>",
  "question_type": "summary|authors|date|categories",
  "question": "<question based on a cleaned paper>",
  "ground_truth": "<answer supported by that paper>",
  "ground_truth_doc_ids": ["<paper_id from cleaned data>"]
}
```

`ground_truth_doc_ids` bắt buộc lấy từ `paper_id` clean/index. Không tự sinh hoặc đổi ID giữa baseline, corrupted và repaired. Test set được tạo một lần sau khi clean schema ổn định và tái dùng nguyên vẹn cho cả ba trạng thái.

`build_test_set()` chỉ tạo question type `categories` khi `categories_joined` có giá trị từ nguồn. Với snapshot hiện tại, test set sẽ gồm `summary`, `authors` và `date`.

### Mẫu câu hỏi cần tạo khi nhận clean data

Với mỗi paper thật được chọn:

- `summary`: `What does '<title>' describe?`
- `authors`: `Who authored '<title>'?`
- `date`: `When was '<title>' published?`
- `categories`: `What categories are assigned to '<title>'?`

Ground truth lần lượt lấy từ `summary`, `authors_joined`, `published`, `categories_joined` của chính row đó.

Candidate đã xác minh từ raw snapshot:

| Loại | Câu hỏi/ground truth dự kiến |
| --- | --- |
| Summary | `What does 'A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models' describe?` — lấy câu trả lời từ `summary` đã bỏ JATS/HTML. |
| Authors | `Who authored 'A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models'?` — `Lihui Liu`. |
| Date | `When was 'A Survey of (Deep RAG) Deep Retrieval Augmented Generation and Reasoning in Large Language Models' published?` — `2026-03-05T16:33:10Z` (cần thống nhất định dạng output khi clean). |
| Categories | Chưa tạo được: snapshot hiện không có category cho bất cứ record nào. |

### Format answer và metrics đã xác nhận

`evaluate_pipeline()` ghi mỗi answer với các trường: `id`, `question_type`, `question`, `ground_truth`, `ground_truth_doc_ids`, `answer`, `retrieved_doc_ids`, `retrieved_contexts`, `retrieval_hit`, `token_f1`, `judge`.

Metrics summary cần theo dõi:

- `retrieval_hit_rate`
- `mean_token_f1`
- `judge_accuracy`
- `mean_judge_score`
- `ragas` (có thể là skipped/error nếu không bật `RUN_RAGAS`)

### Quality/freshness signals phải lưu

- Row count.
- `paper_id` missing/duplicate.
- Title missing.
- Summary missing hoặc quá ngắn.
- Duplicate rows.
- `age_days` hợp lệ.
- `latest_published`, `oldest_published`, `stale_rows`, `total_rows`, `is_fresh`.

### Artifact checklist

Baseline:

- `data/raw/crossref_response.json`
- `data/raw/crossref_records.json`
- `data/clean/papers_clean.csv` và `.json`
- `data/embeddings/papers_embeddings.json`
- `data/eval/test_set.json`
- `data/results/baseline_metrics.json`
- `data/results/baseline_answers.json`
- quality/freshness files trong `data/quality/`
- `data/reports/phase1_report.md`

Corrupted/repaired:

- corrupted/repaired clean CSV/JSON và embedding manifests riêng.
- `data/results/corruption_log.json`
- `data/results/corrupted_metrics.json`, `corrupted_answers.json`
- `data/results/repaired_metrics.json`, `repaired_answers.json`
- quality/freshness artifacts riêng theo trạng thái.
- `data/reports/corruption_report.md`

### Luận điểm báo cáo cần chứng minh bằng artifact

1. Một corruption được log làm thay đổi quality/freshness signal và đồng thời làm thay đổi retrieval/answer metric, nếu số liệu thực tế cho thấy điều đó.
2. Repair được chạy lại từ raw/source đáng tin cậy, sau đó quality/freshness và metric được đo lại trên cùng test set.
3. Nếu metric không thay đổi hoặc không hồi phục, report phải ghi đúng kết quả thay vì suy diễn recovery.

## Handoff cần nhận trước CP1/CP2

- Vai trò 2: raw schema và một raw snapshot truy vết được.
- Vai trò 3: cleaned DataFrame theo contract, gồm `paper_id`, `text_for_embedding`, `age_days` và metadata index cần thiết.
- Vai trò 4: baseline index/manifest và kết quả smoke test với record thật.
- Vai trò 1: orchestration gọi đúng paths trong `Settings`, không refresh source/test set ngoài ý muốn.
