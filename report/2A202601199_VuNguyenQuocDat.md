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

## 4. Giải thích phần kỹ thuật đã thực hiện (Checkpoint 2)

### Vấn đề cần giải quyết
Trước khi bắt đầu chạy pipeline end-to-end ở CP3, Lead cần đảm bảo:
1. Schema đầu ra của Cleaning khớp chính xác với yêu cầu của Indexer và Generator.
2. Các đường dẫn và collection của ChromaDB cho 3 pha (Baseline, Corrupt, Repair) được phân tách độc lập để tránh ghi đè dữ liệu chéo.
3. Chạy thử nghiệm thành công (Smoke Test) luồng: Cleaned Data → Test Set → Vector Index → Retrieval/Agent QA.

### Cách triển khai & Contract Schema sạch
Sau khi Quỳnh (Role 3) hoàn thành Cleaning và Nam (Role 5) hoàn thành TestSet ở CP1, tôi đã tiến hành khóa contract dữ liệu sạch gồm các trường:
*   `paper_id`: Khóa chính (DOI chuẩn hóa chữ thường).
*   `title`, `summary`: Tiêu đề và tóm tắt đã làm sạch thẻ JATS/HTML.
*   `authors_joined`, `categories_joined`: Chuỗi chuẩn hóa phân tách bằng dấu phẩy.
*   `age_days`: Tính tuổi bài báo từ `published` date đến ngày hiện tại.
*   `text_for_embedding`: Định dạng chuẩn hóa:
    ```text
    Title: <title>
    Authors: <authors_joined>
    Categories: <categories_joined>
    Summary: <summary>
    ```

### Kiểm tra tách biệt Collection và Manifest
Tôi đã xác minh cấu hình trong `src/core/config.py` và `src/retrieval/index.py` đảm bảo cơ chế đặt tên collection tự động dựa trên đường dẫn file manifest:
*   `papers_embeddings.json` $\rightarrow$ Collection: `papers-baseline`
*   `papers_embeddings_corrupted.json` $\rightarrow$ Collection: `papers-corrupted`
*   `papers_embeddings_repaired.json` $\rightarrow$ Collection: `papers-repaired`

### Kết quả chạy thử nghiệm (Smoke Test)
Tôi đã chạy script kiểm tra nhanh và ghi nhận kết quả:
*   **Test Set:** Tạo thành công 18 câu hỏi (các dạng: `summary`, `date`, `authors`, `categories`) lưu tại `data/eval/test_set.json`.
*   **Vector Index:** Khởi tạo thành công ChromaDB và nạp 24 papers sạch vào collection `papers-baseline`.
*   **Agent QA:** Chạy thử nghiệm câu hỏi tìm kiếm ngữ nghĩa và truy xuất chính xác bằng DOI:
    *   *Query:* `What is the main topic of 'Implementation of Retrieval-Augmented Generation Method...'?`
    *   *Result:* Trích xuất đúng câu trả lời thực tế từ nội dung bài báo.

### Blockers còn lại trước CP3
*   Orchestration pipeline `src/pipelines/phase1.py` chưa được implement (sẽ giải quyết trực tiếp tại CP3).

---
*LƯU Ý: CÁC PHẦN TỪ MỤC 5 ĐẾN 9 DƯỚI ĐÂY SẼ ĐƯỢC HOÀN THIỆN DẦN KHI TIẾN HÀNH THỰC HIỆN CÁC BƯỚC TIẾP THEO CỦA DỰ ÁN.*
