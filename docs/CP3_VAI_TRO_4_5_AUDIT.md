# CP3 Audit — Vai trò 4 và 5

`data/chroma/` bị `.gitignore` (đúng chủ ý, không commit vector DB nhị phân) nên bản checkout này chỉ có manifest JSON, chưa có collection Chroma thật. Đã rebuild lại collection `papers-baseline` từ `data/clean/papers_clean.csv` bằng đúng `LocalEmbeddingIndex.build()` mà `phase1.py` gọi (không đổi logic, không đổi dữ liệu nguồn) để có thể chạy smoke test thật thay vì chỉ đọc JSON.

## Vai trò 4 — RAG & Agent

### 1. `papers-baseline` và embedding manifest khớp clean dataset

| Thuộc tính | Giá trị |
| --- | --- |
| Clean rows | 24 |
| `document_count` trong manifest | 24 |
| Backend | `chroma` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector dimension | 384 |
| Collection name | `papers-baseline` |
| `metadata_fields` | `paper_id, title, published, authors_joined, categories_joined, summary, abs_url, pdf_url` — đủ trường RAG cần |

0 document thiếu so với clean data, 0 document thừa (build trực tiếp từ 24 dòng `papers_clean.csv`, 1-1).

### 2. Demo semantic search và exact lookup (chạy thật, không phải log cũ)

Paper dùng để test: `doi:10.35314/3y9hy151` — *"Implementation of Retrieval-Augmented Generation Method on Large Language Model for Development of Campus Service and Information Chatbot"*.

**Exact lookup theo `paper_id`:**
```
lookup("doi:10.35314/3y9hy151") -> found=True, title đúng
```

**Exact lookup theo title (nguyên văn):**
```
lookup("Implementation of Retrieval-Augmented Generation Method on Large Language Model for Development of Campus Service and Information Chatbot")
-> found=True, paper_id đúng, cùng document với lookup theo paper_id
```

**Semantic search** với câu hỏi tự nhiên `"Which paper implements a RAG chatbot for campus services?"` (top_k=4):

| Rank | Score | paper_id | Title |
| --- | --- | --- | --- |
| 1 | 0.4652 | `doi:10.35314/3y9hy151` | Implementation of RAG Method... Campus Service and Information Chatbot |
| 2 | 0.4085 | `doi:10.52060/juptik.v4i1.4318` | Chatbot Hybrid Fatwa MUI... |
| 3 | 0.2955 | `doi:10.36227/techrxiv.177272838.89432844/v1` | A Survey of (Deep RAG)... |
| 4 | 0.2745 | `doi:10.70121/001c.158711` | The Role of RAG in Improving Factual Accuracy... |

Document mục tiêu nằm ở rank 1 với score cao nhất → semantic search hoạt động đúng, không phải may rủi.

### 3. Agent factual answer dùng tool result, không vượt corpus

Kiểm tra code `src/retrieval/agent.py`:

- `build_agent()` bind hai tool: `semantic_search_papers`, `lookup_paper`.
- `system_prompt`: *"Use tools before answering factual questions... Do not hallucinate outside the corpus."*
- `run_agent_question()` gọi `agent.invoke(...)` qua `langchain.agents.create_agent`, buộc model đi qua tool trước khi trả lời — đúng thiết kế "tool-forcing" theo pass criteria CP2/CP3.

**Cập nhật — đã chạy demo LLM thật:** sau khi `.env` được điền `GOOGLE_API_KEY` (provider `gemini`, model `gemma-4-31b-it`), đã gọi `build_agent()` + `agent.invoke()` thật với 2 câu hỏi factual và ghi transcript vào `data/results/agent_demo_answers.json`.

| Câu hỏi | Tool gọi trước khi trả lời | Trả lời có đúng corpus không |
| --- | --- | --- |
| "Who authored '...Campus Service and Information Chatbot'?" | `lookup_paper(paper_id_or_title="...Campus Service and Information Chatbot")` | ✅ "Muhammad Dzaki Salman, Rahmaddeni, Torkis Nasution, and Susanti" — khớp `authors_joined` thật trong clean data |
| "What is the main topic of '...Campus Service and Information Chatbot'?" | `lookup_paper(paper_id_or_title="...Campus Service and Information Chatbot")` | ✅ Mô tả đúng nội dung RAG hybrid retrieval cho USTI chatbot, bám sát `summary` thật, không bịa thông tin ngoài corpus |

Cả hai transcript đều có `used_tool_before_answering: true` — agent gọi `lookup_paper` trước khi sinh câu trả lời cuối, đúng yêu cầu "dùng tool trước khi trả lời câu hỏi factual, không hallucinate ngoài corpus". `data/results/agent_demo_answers.json` giờ tồn tại làm bằng chứng.

**Lưu ý về quota:** model mặc định ban đầu thử (`gemini-2.5-flash` theo `.env.example`) đã bị Google ngừng cấp cho key mới (`404 model not found`); `gemini-flash-latest` gọi được nhưng dùng hết quota free-tier 20 request/ngày ngay trong lần chạy lại evaluator (18 lệnh judge). Agent demo phải chuyển sang model `gemma-4-31b-it` mới gọi được. Nếu đổi provider/model, cần cập nhật `LLM_MODEL` trong `.env` và kiểm tra quota trước khi chạy loạt lớn.

### Ghi chú kỹ thuật (không chặn CP3, cần theo dõi cho CP5/CP6)

`LocalEmbeddingIndex.load()` (`src/retrieval/index.py`) đọc `payload["documents"]` và dùng thẳng `payload["persist_path"]`, nhưng:
- Manifest do `.build()` ghi ra **không có key `"documents"`** → gọi `.load()` sẽ `KeyError`.
- `persist_path`/`source_path` là absolute path của máy build, không portable sang máy khác.

Hiện `phase1.py` không gọi `.load()` (luôn `.build()` trực tiếp) nên chưa phát sinh lỗi ở baseline. Nếu `corruption_flow.py` (CP5/CP6) dùng `.load()` để nạp lại `papers-baseline` mà không rebuild, cần sửa trước, không chỉ giả định "artifact tồn tại là dùng lại được".

## Vai trò 5 — Evaluation & Observability

### 1. Evaluator đã tạo answers và `baseline_metrics.json`

`data/results/baseline_metrics.json` (18 samples):

| Metric | Giá trị |
| --- | --- |
| `retrieval_hit_rate` | `1.0000` |
| `mean_token_f1` | `1.0000` |
| `judge_accuracy` | `1.0000` |
| `mean_judge_score` | `5.0000` |
| `ragas` | `skipped` (chưa bật `RUN_RAGAS=1`) |

### 2. Đọc một hit thật; kiểm tra ground truth/doc ID

Ví dụ sample `doi-10-35314-3y9hy151-summary` trong `data/results/baseline_answers.json`:

- Câu hỏi: *"What is the main topic of 'Implementation of Retrieval-Augmented Generation Method...'?"*
- `ground_truth_doc_ids`: `["doi:10.35314/3y9hy151"]` — có tồn tại trong clean data (đã kiểm tra toàn bộ 18/18 sample, 0 ID nào không map được vào `papers_clean.json`).
- `retrieved_doc_ids[0]` = `doi:10.35314/3y9hy151` → `retrieval_hit = true`.
- `answer` trùng khớp tuyệt đối `ground_truth` → `token_f1 = 1.0`.
- `judge`: `{"score": 5, "correct": true, "reasoning": "The model answer is identical to the reference answer."}` — **đây là reasoning do LLM Gemini sinh ra thật** (câu chữ khác nhau giữa các sample, không phải chuỗi cố định), sau khi rerun evaluator với `GOOGLE_API_KEY` hợp lệ.

**Về "miss":** kiểm tra toàn bộ 18/18 sample — `retrieval_hit_rate = 1.0` nghĩa là **không có miss nào** trong lần chạy baseline hiện tại (0/18 miss, 0/18 `token_f1 < 1.0`). Đây là kết quả thật lấy trực tiếp từ file, không có mẫu miss để trích dẫn ở baseline này.

### 3. Giải thích các metric hiện có (đọc code `src/evaluation/metrics.py`)

- **`retrieval_hit_rate`**: tỷ lệ câu hỏi mà `ground_truth_doc_ids` xuất hiện trong `retrieved_doc_ids` (top-k=4). Đạt 1.0 vì `answer_question()` trong `retrieval/qa.py` trích xuất `paper_id` chính xác qua regex title trong câu hỏi (`re.search(r"'([^']+)'", question)`) rồi ưu tiên nó lên đầu danh sách kết quả — mỗi câu hỏi test set đều chứa title nguyên văn trong dấu `'...'`.
- **`mean_token_f1`**: so khớp token giữa `answer` và `ground_truth`. Đạt 1.0 vì `_extract_answer()` trả thẳng giá trị field gốc (`summary`, `authors_joined`, `published`) của đúng document — không phải LLM sinh văn bản tự do, nên trùng khớp tuyệt đối với ground truth (vốn cũng lấy từ chính field đó).
- **`judge_accuracy` / `mean_judge_score`**: **đã xác minh lại bằng LLM judge thật** sau khi `.env` có `GOOGLE_API_KEY` hợp lệ và evaluator được chạy lại (`script/run_phase1.py`, model `gemini-flash-latest`). 18/18 sample giờ có `judge.reasoning` là câu văn LLM sinh ra, khác nhau giữa các sample (ví dụ: "The model answer is identical to the reference answer.", "The model answer correctly identifies Sohail Khan as the author, exactly matching the reference answer.") — không còn chuỗi cố định `"Fallback heuristic judge used..."` như lần chạy trước đó khi chưa có key. `judge_accuracy=1.0` và `mean_judge_score=5.0` giờ là điểm LLM giám khảo thật, hợp lý vì `answer` trùng khớp tuyệt đối `ground_truth` ở mọi sample (do QA rule-based trích đúng field nguồn).
  - *Ghi chú lịch sử:* trước khi có `.env`/key, cùng 18 sample này từng cho `judge.reasoning = "Fallback heuristic judge used because the LLM evaluator was unavailable."` — minh chứng cơ chế fallback trong `_judge_answer()` hoạt động đúng khi không có LLM, và nay đã được thay bằng đánh giá LLM thật.

### 4. Quality/freshness và `phase1_report.md`

`run_data_quality_checks()` và `build_freshness_report()` đã chạy, artifact tồn tại và **khớp nhau tuyệt đối** với `data/reports/phase1_report.md` (report tự động sinh bởi `generate_phase1_report()`):

| Nguồn | Passed checks | Freshness status |
| --- | --- | --- |
| `data/quality/baseline-quality.json` | 8 / 9 | — |
| `data/quality/freshness_report.json` | — | `stale` |
| `data/reports/phase1_report.md` (tự động) | 8 / 9 | `stale` |

→ Report tự động đáng tin cậy, không hard-code, khớp JSON nguồn 100%.

**Sai lệch phát hiện ở report tường thuật (không phải report tự động):** `report/checkpoint_3_lead_report.md` hiện ghi "Quality Checks: 9/9", "Freshness Status: fresh", "Mean Token F1: 0.9840" — cả ba số đều **không khớp** artifact thật (8/9, `stale`, `1.0000`). Đây là điểm cần Vai trò 1 sửa trước khi coi CP3 hoàn tất, theo đúng cảnh báo CP3: *"Baseline chỉ hoàn tất khi artifacts, metrics và report khớp nhau."*

### 5. Baseline signals/metrics làm mốc cho CP5/CP6

Ghi lại để đối chiếu sau khi corrupt/repair:

| Signal | Baseline |
| --- | --- |
| Raw rows | 24 |
| Clean rows | 24 |
| `retrieval_hit_rate` | 1.0000 |
| `mean_token_f1` | 1.0000 |
| `judge_accuracy` (LLM judge thật, Gemini) | 1.0000 |
| `mean_judge_score` (LLM judge thật, Gemini) | 5.0000 |
| Quality checks passed | 8 / 9 |
| Check fail | `freshness_threshold` (1 row > 180 ngày) |
| Freshness status | `stale` (`stale_rows=1`, oldest 192 ngày) |

Vì baseline đã fail sẵn `freshness_threshold`, khi so sánh corrupted ở CP5, cần theo dõi xem corruption (đặc biệt "làm stale publication date") có làm `stale_rows` tăng thêm không, thay vì kỳ vọng baseline "fresh tuyệt đối" rồi mới xấu đi.

## Đối chiếu Pass Criteria CP3

| Tiêu chí | Đạt? | Ghi chú |
| --- | --- | --- |
| `baseline_metrics.json`, answers, quality/freshness, `phase1_report.md` tồn tại | ✅ | Đã đọc và đối chiếu trực tiếp, rerun với LLM judge thật |
| `papers-baseline` + manifest khớp clean dataset | ✅ | Rebuild lại và verify 24/24 |
| Semantic search + exact lookup demo | ✅ | Chạy thật, có số liệu ở trên |
| Agent dùng tool trước khi trả lời | ✅ | Transcript LLM thật trong `data/results/agent_demo_answers.json`, cả 2 câu đều gọi `lookup_paper` trước khi trả lời |
| Giải thích ít nhất 1 hit/miss bằng artifact | ✅ (hit) | Không có miss nào để trích — cần nêu rõ đây là baseline hoàn hảo, không phải thiếu sót khi audit |
| Report khớp artifact thật | ⚠️ | Report tự động khớp; report tường thuật (`checkpoint_3_lead_report.md`) cần sửa 3 số liệu — xem mục 4 |
