# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Vũ Nguyễn Quốc Đạt         |
| MSSV               | 2A202601199                |
| Khóa/Lớp         | [Khóa/Lớp]                 |
| Tên nhóm         | Nhóm 5 người               |
| Vai trò chính    | Role 1 - Lead / Pipeline Integrator |
| Repository         | [Đường dẫn repository] |
| Ngày hoàn thành | 2026-08-06                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Settings & Config | `src/core/config.py`<br>`src/core/utils.py` | Environment variables, `.env` file | `Settings` object, path configuration | Hoàn thành phần thiết lập ban đầu (CP0) |
| Orchestration & Pipeline | `src/pipelines/phase1.py`<br>`src/pipelines/corruption_flow.py` | Cleaned data, metrics, evaluation output | E2E baseline & corruption pipelines (`script/run_phase1.py`, `script/run_corruption_flow.py`) | Sẽ hoàn thiện ở các checkpoint tiếp theo |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Hỗ trợ thiết lập môi trường | Biên (Role 2), Quỳnh (Role 3), Lan (Role 4), Nam (Role 5) | Đồng bộ môi trường Python 3.12, cài dependencies và khởi tạo file cấu hình `.env` cục bộ. |

## 3. Kết quả theo vai trò

| Giai đoạn | Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| :--- | :--- | :--- | :--- | :--- |
| **CP0** | Chốt sơ đồ luồng dữ liệu & phân công vai trò | [checkpoint_0_lead_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/report/checkpoint_0_lead_report.md) | Bản thiết kế chi tiết luồng bàn giao dữ liệu | Đã nộp báo cáo CP0 |
| **CP0** | Đồng bộ môi trường và khởi tạo file `.env` | `.env` | File `.env` chứa API keys và config | Đã chạy thành công lệnh kiểm tra import gói `src` |
| **CP2** | Kiểm tra chốt clean schema contract | `src/ingestion/cleaning.py` | Schema dữ liệu sạch thống nhất cho RAG | Xác minh qua DataFrame load từ `papers_clean.json` |
| **CP2** | Xác minh ChromaDB collections tách biệt | `src/retrieval/index.py` | Tách riêng 3 collection: `papers-baseline`, `papers-corrupted`, `papers-repaired` | Chạy smoke test, ghi nhận embedding manifest thành công |
| **CP2** | Ghi nhận blocker và chạy smoke test | `data/eval/test_set.json`<br>`data/embeddings/papers_embeddings.json` | Khởi tạo thành công bộ câu hỏi (18 câu) và vector index | Chạy smoke test RAG Agent (search & lookup) thành công |
| **CP3** | Triển khai baseline pipeline end-to-end | `src/pipelines/phase1.py` | Điều phối toàn bộ dữ liệu thô $\rightarrow$ sạch $\rightarrow$ index $\rightarrow$ đánh giá $\rightarrow$ báo cáo | Chạy `uv run python script/run_phase1.py` thành công |
| **CP3** | Cài đặt module xuất báo cáo Markdown | `src/observability/reporting.py` | Hàm tự động xuất báo cáo Phase 1 & báo cáo so sánh | Sinh thành công báo cáo [phase1_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/reports/phase1_report.md) |
| **CP4** | Nghỉ giải lao & chốt kế hoạch giả lập lỗi | [checkpoint_4_break_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/report/checkpoint_4_break_report.md) | Bản kế hoạch chi tiết kịch bản dữ liệu lỗi cho 5 vai trò | Đã nộp báo cáo giải lao CP4 |

## 4. Giải thích phần kỹ thuật đã thực hiện (Checkpoint 2 & 3 & 4)

### Vấn đề cần giải quyết
1.  **Thiết lập pipeline tự động (CP3):** Điều phối toàn bộ vòng đời dữ liệu của Baseline pha 1, bao gồm việc đọc/tải dữ liệu thô từ API Crossref, chạy Cleaning để loại bỏ HTML/JATS, xây dựng chỉ mục vector ChromaDB, sinh test set đánh giá, đo đạc hiệu năng RAG, chạy data quality checks & freshness, và cuối cùng xuất báo cáo Markdown.
2.  **Module báo cáo tự động (CP3):** Lập trình các hàm xuất dữ liệu chất lượng, độ tươi mới và hiệu năng RAG thành báo cáo trực quan cho các checkpoint sau.
3.  **Kế hoạch Corruption (CP4):** Thống nhất kịch bản làm lỗi dữ liệu (droppping records, blanking text, staling timestamps, etc.) để chuẩn bị chạy tích hợp trong CP5.

### Cách triển khai & Triển khai baseline (Phase 1)
Tôi đã viết code triển khai cho `src/pipelines/phase1.py` thực hiện:
- Kiểm tra cache hoặc gọi API Crossref để tải và phân tích 24 records thô.
- Áp dụng `build_clean_dataframe` thu được 24 bản ghi sạch, lưu trữ tại `data/clean/papers_clean.json` và `papers_clean.csv`.
- Xây dựng chỉ mục vector `papers-baseline` qua `LocalEmbeddingIndex.build`.
- Chạy đánh giá bằng `evaluate_pipeline` trên bộ câu hỏi 18 câu từ `data/eval/test_set.json`.
- Đo đạc observability bằng `run_data_quality_checks` và `build_freshness_report`.
- Gọi `generate_phase1_report` để xuất kết quả hoàn chỉnh ra file Markdown.

### Kết quả chạy thử nghiệm & Baseline Metrics
Khi chạy lệnh tích hợp đầu tiên `uv run python script/run_phase1.py`, toàn bộ luồng đã chạy thành công và ghi nhận các số liệu ấn tượng:
*   **Retrieval Hit Rate:** `1.0000` (Truy xuất trúng 100% tài liệu đúng).
*   **Mean Token F1 Score:** `0.9840` (Độ khớp câu trả lời cực kỳ cao).
*   **Data Quality Checks Passed:** `9 / 9` kiểm tra chất lượng đạt (Không trùng lặp, không rỗng).
*   **Freshness Status:** `fresh` (Dữ liệu bài viết cập nhật dưới ngưỡng 180 ngày).

---
*LƯU Ý: CÁC PHẦN TỪ MỤC 5 ĐẾN 9 DƯỚI ĐÂY SẼ ĐƯỢC HOÀN THIỆN DẦN KHI TIẾN HÀNH THỰC HIỆN CÁC BƯỚC TIẾP THEO CỦA DỰ ÁN.*

