# Báo cáo Checkpoint 4 — Vai trò 1, 2, 3, 4, 5 (Nghỉ giải lao & Chuẩn bị Corruption)
**Nhóm thực hiện:** Nhóm 5 người (Đạt, Biên, Quỳnh, Lan, Nam)
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Nhật Ký Nghỉ Giải Lao (Mốc CP4)
Cả 5 thành viên đã hoàn thành Pha 1 (Baseline) xuất sắc và dành 15 phút nghỉ giải lao để nạp năng lượng, đồng thời thảo luận phương án triển khai dữ liệu lỗi (Data Corruption) và phục hồi (Data Repair) cho Pha 2.

---

## 2. Hoàn Thiện Các Đầu Mục Cho Từng Vai Trò tại CP4

### 2.1. VAI TRÒ 1: Lead / Pipeline Integrator (Đạt)
- **Baseline Checklist đã hoàn thành:**
  - [x] Raw Ingestion: `crossref_response.json` và `crossref_records.json` đã lưu đầy đủ.
  - [x] Data Cleaning: `papers_clean.csv` và `papers_clean.json` đạt chuẩn schema.
  - [x] ChromaDB Index: Collection `papers-baseline` được khởi tạo và nạp embeddings thành công.
  - [x] Test Set: Đã khóa tập câu hỏi 18 mẫu tại `test_set.json`.
  - [x] Evaluation: Đã chạy đánh giá và ghi nhận baseline metrics.
  - [x] Observability: Đã xuất báo cáo chất lượng và freshness của pha baseline.
  - [x] Reporting: Đã hoàn thiện báo cáo Phase 1.
- **Một Blocker còn lại:**
  - Chưa triển khai luồng tích hợp Pha 2 trong `src/pipelines/corruption_flow.py` và giả lập lỗi dữ liệu trong `src/ingestion/corruption.py` (Sẽ thực hiện tại CP5).

### 2.2. VAI TRÒ 2: Ingestion Owner (Biên)
- **Phương án khôi phục dữ liệu (Repair):**
  - Biên đã xác minh tệp tin dữ liệu thô gốc `data/raw/crossref_records.json` làm điểm khôi phục (Authoritative Lineage Source).
  - Khi luồng repair diễn ra ở CP6, Biên sẽ cung cấp bản sao dữ liệu gốc này cho Quỳnh để tiến hành chạy lại quy trình làm sạch từ đầu, đảm bảo không sửa tay (hard-code) dữ liệu lỗi.

### 2.3. VAI TRÒ 3: Cleaning & Corruption Owner (Quỳnh)
- **Lựa chọn kịch bản giả lập lỗi dữ liệu có chủ đích (CP5):**
  - Quỳnh đã phác thảo 5 kịch bản làm lỗi dữ liệu trên DataFrame sạch:
    1.  **Missing Summary:** Làm rỗng tóm tắt (`summary = ""`) ở một số dòng đầu tiên $\rightarrow$ Làm giảm chất lượng nội dung nhúng.
    2.  **Truncated Title:** Cắt ngắn tiêu đề $\rightarrow$ Gây mất mát thông tin nhận diện bài viết.
    3.  **Stale Published Date:** Chuyển ngày xuất bản về năm 2000 (`age_days = 9999`) $\rightarrow$ Phá hỏng chỉ số Freshness.
    4.  **Drop Latest Records (Sẽ bổ sung):** Bỏ bớt một số bản ghi mới nhất.
    5.  **Duplicate Rows (Sẽ bổ sung):** Nhân bản dữ liệu $\rightarrow$ Vi phạm luật kiểm tra tính duy nhất (Uniqueness).

### 2.4. VAI TRÒ 4: RAG & Agent Owner (Lan)
- **Mẫu Query so sánh đối chiếu:**
  - Lan đã lưu trữ các câu truy vấn mẫu và kết quả truy xuất baseline để so sánh chéo ở CP5:
    - *Query 1:* `"agentic RAG pipeline data quality"` (Baseline Score: `0.2673`).
    - *Query 2:* Trích xuất bài báo cụ thể bằng exact lookup DOI `"doi:10.35314/3y9hy151"`.
  - Mục tiêu: Đo đạc xem sau khi Quỳnh corrupt dữ liệu, điểm số tương đồng (Score) và nội dung câu trả lời của Agent bị suy giảm thế nào.

### 2.5. VAI TRÒ 5: Evaluation & Observability (Nam)
- **Tập đánh giá Test Set:**
  - Nam cam kết giữ nguyên 100% tập câu hỏi `data/eval/test_set.json` (18 câu) để đảm bảo tính công bằng khi đánh giá delta giữa ba trạng thái: Baseline - Corrupted - Repaired.
- **Dự báo thay đổi của tín hiệu chất lượng dữ liệu (Quality/Freshness Signals):**
  - *Dự báo Quality Checks:* Các kiểm tra về `duplicate_rows`, `title_present`, `summary_min_length` sẽ chuyển sang trạng thái **FAIL**.
  - *Dự báo Freshness:* Freshness status sẽ bị chuyển từ `fresh` sang **`stale`** do ngày xuất bản bị kéo lùi về quá khứ.
  - *Dự báo Agent Performance:* Chỉ số `retrieval_hit_rate` và `mean_token_f1` sẽ sụt giảm nghiêm trọng do dữ liệu nhúng bị mất mát và nhiễu thông tin.

---
**Xác nhận mốc CP4:** Cả nhóm 5 người đã hoàn thành thảo luận kế hoạch CP4 trong 15 phút giải lao. Toàn bộ các vai trò đã nắm rõ nhiệm vụ bàn giao cho CP5. Sẵn sàng bắt đầu Pha 2!
