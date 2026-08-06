# Báo cáo Checkpoint 2 — Vai trò 1 (Lead / Pipeline Integrator)
**Thành viên thực hiện:** Vũ Nguyễn Quốc Đạt (Role 1)
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Kết Quả Kiểm Tra Clean Schema & Bàn Giao Handoff (Mục 1 của CP2)
Hệ thống Clean Schema đã được thống nhất giữa các vai trò (Ingestion -> Cleaning -> RAG -> Eval).

### Thống nhất Clean Schema:
- **`paper_id`**: Định dạng DOI chuẩn hóa chữ thường.
- **`title` & `summary`**: Đã loại bỏ hoàn toàn các thẻ HTML/JATS.
- **`authors_joined` & `categories_joined`**: Chuỗi chuẩn hóa phân tách bằng dấu phẩy.
- **`age_days`**: Được tính toán động từ ngày xuất bản (`published`) đến thời điểm chạy.
- **`text_for_embedding`**: Đã chuẩn hóa định dạng kết hợp đầy đủ:
  ```text
  Title: [title]
  Authors: [authors_joined]
  Categories: [categories_joined]
  Summary: [summary]
  ```

---

## 2. Xác Minh Tính Tách Biệt Collections & Paths (Mục 2 của CP2)
Mọi collection và đường dẫn lưu trữ embeddings manifest cho 3 trạng thái của dữ liệu đều được phân tách biệt lập:
1.  **Baseline Collection (`papers-baseline`)**:
    - Metadata lưu trữ tại: `data/embeddings/papers_embeddings.json`
2.  **Corrupted Collection (`papers-corrupted`)**:
    - Metadata lưu trữ tại: `data/embeddings/papers_embeddings_corrupted.json`
3.  **Repaired Collection (`papers-repaired`)**:
    - Metadata lưu trữ tại: `data/embeddings/papers_embeddings_repaired.json`
4.  **Chroma Database Client Path**:
    - Lưu trữ tập trung tại: `data/chroma/chroma.sqlite3`

Sự phân tách này đảm bảo trong quá trình so sánh baseline và corrupted, dữ liệu không bị ghi đè chéo, giúp kết quả đánh giá delta chính xác 100%.

---

## 3. Nhật Ký Kết Quả Smoke Test CP2
Đã chạy kịch bản thử nghiệm nhanh (`scratch/cp2_smoke_test.py`) và thu được các kết quả như sau:

- **Tổng số records sạch được nạp:** 24 papers.
- **Số câu hỏi trong Test Set (`data/eval/test_set.json`):** 18 câu hỏi trích xuất từ dữ liệu sạch (dạng: `summary`, `date`, `authors`, `categories`).
- **Semantic Search Test:** Tìm kiếm ngữ nghĩa với query `"agentic RAG pipeline data quality"` cho ra kết quả có độ tương đồng cao (Score cao nhất: `0.2673` đối với paper cùng chủ đề).
- **Exact Lookup Test:** Truy vấn DOI chính xác `"doi:10.35314/3y9hy151"` trả về thông tin bài báo tương ứng.
- **QA Generation Test:** Agent tạo câu trả lời thành công từ thông tin trích xuất ngữ cảnh.

---

## 4. Blockers Ghi Nhận Trước CP3
- **Blocker 1:** File điều phối baseline chạy end-to-end `src/pipelines/phase1.py` chưa được implement. Đạt (Lead) sẽ tiến hành cài đặt ở CP3.
- **Khuyến nghị LLM Key:** Đã kích hoạt cơ chế fallback tính toán token F1 tự động khi LLM key chưa được nạp. Tuy nhiên, khuyến nghị các thành viên điền API key vào `.env` trước CP3 để chạy đánh giá bằng LLM sinh.

**Xác nhận mốc CP2:** Đạt (Role 1) xác nhận đã hoàn thành kiểm tra smoke test, tạo bộ câu hỏi đánh giá và collection baseline. Sẵn sàng tích hợp baseline end-to-end tại CP3.
