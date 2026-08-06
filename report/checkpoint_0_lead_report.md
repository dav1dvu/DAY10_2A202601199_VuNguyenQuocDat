# Báo cáo Checkpoint 0 — Vai trò 1 (Lead / Pipeline Integrator)
**Thành viên thực hiện:** Vũ Nguyễn Quốc Đạt (Role 1)
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Chốt phân công vai trò, nhánh Git, và Artifact bàn giao
Để đảm bảo tính nhất quán và độc lập khi làm việc song song, nhóm 5 người thống nhất phân công vai trò, quy ước đặt tên nhánh Git và các artifact bàn giao như sau:

### Phân công chi tiết & Đường dẫn file

| Thành viên | Vai trò | Nhánh Git | File source phụ trách | Artifact bàn giao chính (Đường dẫn tương đối) |
| :--- | :--- | :--- | :--- | :--- |
| **Đạt** | **Role 1: Lead / Pipeline Integrator** | `feature/dat-lead-pipeline` | `src/core/config.py`<br>`src/core/utils.py`<br>`src/pipelines/phase1.py`<br>`src/pipelines/corruption_flow.py` | - `script/run_phase1.py`<br>- `script/run_corruption_flow.py` |
| **Biên** | **Role 2: Ingestion Owner** | `feature/bien-ingest` | `src/ingestion/crossref.py` | - `data/raw/crossref_response.json`<br>- `data/raw/crossref_records.json` |
| **Quỳnh** | **Role 3: Cleaning & Corruption Owner** | `feature/quynh-clean-corruption` | `src/ingestion/cleaning.py`<br>`src/ingestion/corruption.py` | - `data/clean/papers_clean.csv`<br>- `data/clean/papers_clean.json`<br>- `data/clean/papers_clean_corrupted.csv`<br>- `data/clean/papers_clean_repaired.csv`<br>- `data/results/corruption_log.json` |
| **Lan** | **Role 4: RAG & Agent Owner** | `feature/lan-rag-agent` | `src/retrieval/index.py`<br>`src/retrieval/embeddings.py`<br>`src/retrieval/agent.py`<br>`src/retrieval/qa.py`<br>`src/retrieval/llm.py` | - `data/chroma/`<br>- `data/embeddings/papers_embeddings.json`<br>- `data/embeddings/papers_embeddings_corrupted.json`<br>- `data/embeddings/papers_embeddings_repaired.json` |
| **Nam** | **Role 5: Evaluation & Observability** | `feature/nam-eval-observe` | `src/evaluation/testset.py`<br>`src/observability/quality.py`<br>`src/observability/reporting.py` | - `data/eval/test_set.json`<br>- `data/results/*_metrics.json`<br>- `data/results/*_answers.json`<br>- `data/quality/`<br>- `data/reports/phase1_report.md`<br>- `data/reports/corruption_report.md` |

### Tiêu chí hoàn thành (Definition of Done - DoD) cho các Checkpoint
- **Code:** Code chạy không có lỗi biên dịch/runtime, tuân thủ cấu trúc của starter code và không thay đổi chữ ký hàm có sẵn trong core.
- **Không lộ Secret:** Tuyệt đối không commit file `.env` hoặc API keys lên repository.
- **Artifact:** Mọi artifact được sinh ra đúng định dạng (JSON/CSV/MD) và lưu trữ chính xác tại thư mục cấu hình trong `src/core/config.py`.
- **Nhất quan:** Bộ dữ liệu đánh giá (Test Set) được tạo một lần ở baseline và giữ nguyên khi so sánh baseline, corrupted và repaired.

---

## 2. Kiểm tra Môi trường & Cấu hình cục bộ

Dưới sự điều phối của Lead (Đạt), hệ thống môi trường và cấu hình cục bộ đã được kiểm tra và ghi nhận kết quả:

1. **Phiên bản Python:** 
   - Kiểm tra thành công: `Python 3.12.10` (Nằm trong khoảng yêu cầu `3.11` – `3.13`).
2. **Dependencies:**
   - Các gói thư viện cốt lõi đã được cài đặt đầy đủ: `pandas`, `chromadb`, `sentence-transformers`, `torch`, `great-expectations`, `ragas`, `python-dotenv`.
   - Gói cục bộ `src` đã được đăng ký thành công trong môi trường ảo (Editable mode). Import thành công: `import src; print('Import OK')`.
3. **Cấu hình cục bộ (.env):**
   - Đã khởi tạo file `.env` từ `.env.example` tại thư mục gốc của project.
   - *Lưu ý thành viên:* Mỗi thành viên cần tự điền API Key tương ứng với LLM Provider mà mình sử dụng (ví dụ: `GOOGLE_API_KEY` cho Gemini hoặc `OPENAI_API_KEY` cho OpenAI).

---

## 3. Sơ đồ luồng bàn giao dữ liệu (Handoff Flow)

Dưới đây là sơ đồ chi tiết biểu diễn quá trình chuyển giao dữ liệu giữa các vai trò trong nhóm từ lúc lấy dữ liệu từ API Crossref cho đến khi xuất báo cáo so sánh cuối cùng.

```mermaid
sequenceDiagram
    autonumber
    actor B as Biên (Ingestion)
    actor Q as Quỳnh (Clean & Corrupt)
    actor L as Lan (RAG & Agent)
    actor N as Nam (Eval & Obs)
    actor D as Đạt (Integrator)

    Note over B,D: PHA 1: THIẾT LẬP BASELINE DỮ LIỆU SẠCH
    B->>Q: Bàn giao raw response & raw records JSON<br>(data/raw/crossref_records.json)
    Note over Q: Thực hiện chuẩn hóa, deduplicate,<br/>tính age_days và text_for_embedding
    Q->>L: Bàn giao Cleaned CSV/JSON (data/clean/papers_clean.json)
    Q->>N: Bàn giao Cleaned CSV/JSON (data/clean/papers_clean.json)
    Note over L: Build embeddings & ChromaDB index (papers-baseline)
    L->>N: Bàn giao embeddings manifest JSON (papers_embeddings.json)
    Note over N: Tạo test_set.json cố định từ cleaned data.<br/>Chạy Evaluation và Data Quality/Freshness checks.
    N->>D: Bàn giao baseline_metrics.json, baseline_answers.json,<br/>và quality_report.json

    Note over B,D: PHA 2: GIẢ LẬP LỖI & PHỤC HỒI (REPAIR)
    Q->>L: Bàn giao dữ liệu giả lập lỗi (papers_clean_corrupted.json)
    Q->>N: Bàn giao corruption log (corruption_log.json)
    Note over L: Re-index trên collection "papers-corrupted"
    L->>N: Bàn giao corrupted embeddings manifest
    Note over N: Đánh giá chất lượng agent trên tập test_set.json cũ
    N->>D: Bàn giao corrupted_metrics.json & corrupted_answers.json

    B->>Q: Nạp lại raw records gốc (chứa lineage thông tin ban đầu)
    Note over Q: Tiến hành sửa lỗi (Repair) bằng cách ghi đè dữ liệu sạch từ raw
    Q->>L: Bàn giao dữ liệu đã phục hồi (papers_clean_repaired.json)
    Note over L: Re-index trên collection "papers-repaired"
    L->>N: Bàn giao repaired embeddings manifest
    Note over N: Đánh giá chất lượng agent lần cuối trên tập test_set.json cũ
    N->>D: Bàn giao repaired_metrics.json & repaired_answers.json

    Note over D: CHẠY ĐỒNG BỘ & HOÀN THÀNH BÁO CÁO
    D->>N: Điều phối hoàn thiện Phase 1 Report & Comparison Report
    N->>D: Trả về phase1_report.md & corruption_report.md hoàn thiện
    Note over D: Tái hiện end-to-end flow, kiểm chứng kết quả và đóng gói release
```

---
**Xác nhận mốc CP0:** Đạt (Role 1) đã hoàn thành việc thiết lập hạ tầng dự án, kiểm tra môi trường và thống nhất sơ đồ luồng dữ liệu cùng các thành viên. Sẵn sàng chuyển giao sang Checkpoint 1.
