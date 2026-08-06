# Báo cáo Checkpoint 3 — Vai trò 1 (Lead / Pipeline Integrator)
**Thành viên thực hiện:** Vũ Nguyễn Quốc Đạt (Role 1)
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Triển Khai baseline Pipeline (Mục 1 của CP3)
Đã hoàn thành cài đặt file điều phối baseline `src/pipelines/phase1.py` chạy tuần tự qua các bước:
1.  **Cấu hình:** Load settings cục bộ từ `.env` và `src/core/config.py`.
2.  **Ingestion:** Kiểm tra cache hoặc gọi API Crossref để tải và phân tích 24 records thô.
3.  **Cleaning:** Làm sạch dữ liệu thô, loại bỏ HTML/JATS, tính toán `age_days` và `text_for_embedding`.
4.  **Indexing:** Xây dựng ChromaDB index (`papers-baseline`) và lưu manifest.
5.  **Test Set:** Tạo lập hoặc đọc lại bộ câu hỏi đánh giá 18 câu từ dữ liệu sạch.
6.  **Evaluation:** Chạy đánh giá độ chính xác truy xuất ngữ cảnh và so khớp câu trả lời.
7.  **Observability:** Chạy kiểm định 9 luật data quality và tính toán freshness.
8.  **Reporting:** Tạo tự động báo cáo Phase 1 dạng Markdown.

---

## 2. Kết Quả Chạy End-to-End Baseline (Mục 2 của CP3)
Chạy thử nghiệm thành công bằng lệnh `uv run python script/run_phase1.py` với kết quả ghi nhận như sau:

- **Dữ liệu thô thu thập:** 24 records.
- **Dữ liệu sạch lưu trữ:** 24 papers sạch (lưu tại `data/clean/papers_clean.json` và `papers_clean.csv`).
- **Chất lượng RAG Agent:**
  - **Retrieval Hit Rate:** `1.0000` (Truy xuất trúng 100% ngữ cảnh đúng từ ground truth).
  - **Mean Token F1 Score:** `0.9840` (Điểm số so khớp token cực cao do cơ chế trích xuất dữ liệu xác thực).
- **Trạng thái Observability:**
  - **Quality Checks:** `9 / 9` kiểm tra thành công (Không có lỗi ID trống, trùng lặp, thiếu thông tin).
  - **Freshness Status:** `fresh` (Tuổi thọ trung bình của dữ liệu bài viết nằm trong ngưỡng freshness 180 ngày).

---

## 3. Xác Minh Artifacts & Paths (Mục 3 của CP3)
Mọi file kết quả đều đã được lưu trữ đúng quy hoạch thư mục trước khi bước vào pha tiếp theo:

| Artifact | Đường dẫn thực tế | Trạng thái | Kích thước |
| :--- | :--- | :---: | :--- |
| **Clean JSON** | `data/clean/papers_clean.json` | ✅ Tồn tại | ~112 KB |
| **Clean CSV** | `data/clean/papers_clean.csv` | ✅ Tồn tại | ~97 KB |
| **Chroma Database** | `data/chroma/chroma.sqlite3` | ✅ Tồn tại | ~960 KB |
| **Embedding Manifest** | `data/embeddings/papers_embeddings.json` | ✅ Tồn tại | ~114 KB |
| **Test Set JSON** | `data/eval/test_set.json` | ✅ Tồn tại | ~10 KB |
| **Evaluation Metrics** | `data/results/baseline_metrics.json` | ✅ Tồn tại | ~1 KB |
| **Evaluation Answers** | `data/results/baseline_answers.json` | ✅ Tồn tại | ~20 KB |
| **Quality Report** | `data/quality/baseline_quality.json` | ✅ Tồn tại | ~2 KB |
| **Freshness Report** | `data/quality/freshness_report.json` | ✅ Tồn tại | ~1 KB |
| **Baseline Report MD** | `data/reports/phase1_report.md` | ✅ Tồn tại | ~2 KB |

---
**Xác nhận mốc CP3:** Đạt (Role 1) xác nhận đã hoàn thành chạy baseline pipeline, toàn bộ artifacts đã được kiểm định đầy đủ và không phát sinh lỗi/blocker. Sẵn sàng sang Checkpoint 4 (nghỉ) và Checkpoint 5 (Corrupt dữ liệu).
