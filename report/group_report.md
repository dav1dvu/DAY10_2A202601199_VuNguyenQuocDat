# Group Report — Day 10: Data Pipeline & Data Observability
**Nhóm thực hiện:** Nhóm 5 người (Đạt, Biên, Quỳnh, Nam, Lan)
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | K3 - E402 |
| Tên nhóm         | DMX |
| Repository         | [GitHub Repository](https://github.com/dav1dvu/DAY10_2A202601199_VuNguyenQuocDat) |
| Ngày hoàn thành | 2026-08-06 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Vũ Nguyễn Quốc Đạt | 2A202601199 | Role 1 - Lead / Pipeline Integrator | Cấu hình, điều phối E2E pipeline, báo cáo CP [src/pipelines/](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/pipelines/) |
| 2 | Nguyễn Hoàng Biên | 2A202601233 | Role 2 - Ingestion Owner | Gọi API Crossref, lấy raw data [src/ingestion/crossref.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/crossref.py) |
| 3 | Vũ Tú Quỳnh | 2A202601239 | Role 3 - Cleaning & Corruption | Tiền xử lý, giả lập lỗi dữ liệu [src/ingestion/cleaning.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/cleaning.py), [src/ingestion/corruption.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/corruption.py) |
| 4 | Nguyễn Ngọc Nam | 2A202601561 | Role 4 - Evaluation Owner | Lập test set câu hỏi, đo đạc chỉ số RAG Agent [src/evaluation/](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/evaluation/) |
| 5 | Trần Thị Ngọc Lan | 2A202601385 | Role 5 - Observability Owner | Kiểm định chất lượng dữ liệu, freshness, so sánh [src/observability/](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/observability/) |

---

## 2. Tóm tắt kết quả

Nhóm đã xây dựng hoàn chỉnh hệ thống **Data Pipeline và Data Observability** cho ứng dụng RAG Agent.
- **Baseline pipeline** đã chạy thành công, xử lý và chuẩn hóa 24 bài báo thô từ Crossref API thành định dạng sạch và sinh ra các chỉ mục vector ChromaDB. Toàn bộ 18 câu hỏi đánh giá của Agent đạt chỉ số chính xác **100%** (Hit Rate: `1.0000`, Token F1: `1.0000`).
- **Giả lập dữ liệu lỗi (Data Corruption):** Quỳnh áp dụng 6 kiểu lỗi khác nhau làm suy giảm hiệu năng hệ thống. Khi bị làm lỗi, điểm **Hit Rate** của Agent giảm mạnh về **`0.8333`** và **Token F1** giảm về **`0.7222`**. Số lượng bài kiểm tra chất lượng dữ liệu thành công bị tụt từ `8 / 9` xuống còn `5 / 9`.
- **Khôi phục dữ liệu (Data Repair):** Hệ thống tiến hành nạp lại dữ liệu thô gốc từ raw JSON và chạy lại quy trình chuẩn hóa từ đầu thay vì sửa lỗi thủ công. Kết quả, các chỉ số chất lượng được khôi phục nguyên vẹn `8 / 9` và hiệu năng Agent quay lại trạng thái hoàn hảo `1.0000` (100%).
- **Blocker lớn nhất đã xử lý:** Lỗi unhashable lists (`TypeError: unhashable type: 'list'`) khi kiểm tra trùng lặp trên các cột danh sách (`authors` và `categories`) và lỗi ghi trùng lặp collection trên Rust ChromaDB engine đã được xử lý triệt để.

---

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API
    -> raw response/raw records (data/raw/)
    -> cleaning và data modeling (src/ingestion/cleaning.py)
    -> embedding + ChromaDB index (src/retrieval/index.py)
    -> evaluation baseline (src/evaluation/metrics.py)
    -> quality/freshness reports (src/observability/quality.py)
    -> corruption (src/ingestion/corruption.py)
    -> re-index và re-evaluate
    -> repair từ dữ liệu nguồn (cached raw records)
    -> comparison report (data/reports/corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | API Crossref / Cache | Tải dữ liệu, parse thông tin bài báo | `data/raw/crossref_records.json` | Nguyễn Hoàng Biên |
| Cleaning          | Raw Records | Chuẩn hóa schema, loại bỏ thẻ JATS/HTML | `data/clean/papers_clean.json` | Vũ Tú Quỳnh |
| Embedding/index   | Cleaned Data | Sinh embeddings (MiniLM), lưu vào ChromaDB | `data/embeddings/papers_embeddings.json` | Vũ Nguyễn Quốc Đạt |
| Evaluation        | Test Set, Agent | Đánh giá Hit Rate, Token F1, Judge Score | `data/results/baseline_metrics.json` | Nguyễn Ngọc Nam |
| Observability     | Cleaned Data | Đánh giá 9 chiều chất lượng & freshness | `data/quality/baseline-quality.json` | Trần Thị Ngọc Lan |
| Corruption/repair | Cleaned Data / Raw | Giả lập 6 kiểu lỗi dữ liệu & nạp lại raw | `data/clean/papers_clean_corrupted.json` | Vũ Tú Quỳnh & Nguyễn Hoàng Biên |
| Orchestration     | Toàn bộ Pipeline | Lập kịch bản điều phối và xuất so sánh | `data/reports/corruption_report.md` | Vũ Nguyễn Quốc Đạt |

---

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | `openai` (Chế độ offline tự động fallback khi không có API Key) |
| `LLM_MODEL`                | `gpt-4o-mini` |
| Embedding model              | `all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24 |
| Retrieval `top_k`           | 3 |
| Freshness threshold          | 180 ngày |

### Lệnh cài đặt

```bash
uv sync
```

### Lệnh chạy

**Chạy Phase 1 Baseline:**
```bash
uv run python script/run_phase1.py
```

**Chạy Phase 2 Corruption & Repair:**
```bash
uv run python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | 2026-08-06 | `data/reports/phase1_report.md` |
| Corruption flow   | Thành công | 2026-08-06 | `data/reports/corruption_report.md` |

---

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref API |
| Query/filter                | `"Retrieval-Augmented Generation"` |
| Thời điểm lấy dữ liệu | 2026-08-06 12:00:00 (cached local) |
| Số record nhận được    | 24 |
| Cơ chế retry/backoff      | 3 lần thử lại với khoảng chờ nhân đôi (exponential backoff) |

### Raw và clean schema

| Trường        | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa   | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| `paper_id` | `str` | Có | Khóa chính (DOI chuẩn hóa chữ thường) | Bỏ qua record |
| `title` | `str` | Có | Tiêu đề bài báo sạch | Làm sạch hoặc gán trống |
| `summary` | `str` | Có | Tóm tắt bài báo sạch | Loại bỏ HTML/JATS, gán trống |
| `published` | `str` | Có | Ngày xuất bản định dạng ISO | Chuẩn hóa, gán NaT |
| `age_days` | `int` | Có | Số ngày tuổi kể từ khi xuất bản | Tính tự động từ ngày hiện tại |
| `text_for_embedding` | `str` | Có | Nội dung tổng hợp dùng để nhúng | Khởi tạo lại bằng định dạng chuẩn |

### Quy tắc cleaning

*   **Quy tắc 1:** Làm sạch JATS/HTML trong Title và Summary (Quality Dimension: `Validity`). Tác động 24 records.
*   **Quy tắc 2:** Chuẩn hóa định dạng tác giả thành chuỗi phân tách bằng dấu phẩy `authors_joined` (Quality Dimension: `Validity`). Tác động 24 records.
*   **Quy tắc 3:** Tính toán tự động số ngày tuổi `age_days` so với ngày chạy hiện tại (Quality Dimension: `Accuracy`). Tác động 24 records.

#### Giải thích các trường đặc biệt:
1.  `text_for_embedding`: Được ghép theo cấu trúc:
    ```text
    Title: <title>
    Authors: <authors_joined>
    Categories: <categories_joined>
    Summary: <summary>
    ```
2.  `paper_id`: Lấy DOI của bài báo thô và chuyển thành chữ thường để làm mã định danh duy nhất.
3.  `age_days`: Tính toán số ngày chênh lệch giữa ngày chạy hiện tại và ngày xuất bản (`published`) bằng thư viện Pandas datetime.

---

## 6. Evaluation setup

*   **Số câu hỏi:** 18 câu hỏi trích xuất từ 24 bài báo.
*   **Các question_type:** `summary`, `date`, `authors`, `categories`.
*   **Ground-truth document ID:** DOI của bài báo chứa ngữ cảnh gốc.
*   **Embedding model:** `all-MiniLM-L6-v2`.
*   **Vector store/collection:** ChromaDB Collection `papers-baseline`, `papers-corrupted`, và `papers-repaired`.
*   **Retrieval top_k:** 3.
*   **LLM provider/model:** `gpt-4o-mini` (hoặc fallback ngoại tuyến).
*   **Test set dùng chung:** [data/eval/test_set.json](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/eval/test_set.json).

**Lý do giữ nguyên test set:** Để đảm bảo tính khách quan của phép đo. Bất kỳ sự thay đổi nào của test set sẽ làm mất đi khả năng so sánh delta của metrics hiệu năng RAG giữa ba pha Baseline, Corrupted và Repaired.

---

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/`                          | Có | Chứa response gốc từ API |
| Cleaned dataset          | `data/clean/`                        | Có | Chứa csv và json sạch |
| Embedding manifest/index | `data/embeddings/`                   | Có | Chỉ mục vector ChromaDB |
| Evaluation set           | `data/eval/`                         | Có | Chứa test_set.json |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có | Hit Rate: 1.0000 |
| Quality/freshness        | `data/quality/`                      | Có | Passed 8 / 9 checks |
| Baseline report          | `data/reports/phase1_report.md`      | Có | Tự động sinh báo cáo |

### Baseline metrics

*   **Retrieval Hit Rate:** `1.0000` (Truy xuất trúng ngữ cảnh đúng 100%).
*   **Mean Token F1:** `1.0000` (Độ tương tự câu trả lời tối đa).
*   **Judge Accuracy:** `1.0000` (Mô hình ngoại tuyến hoặc judge đánh giá đúng 100%).
*   **Mean Judge Score:** `5.0000` (Điểm tối đa).

---

## 8. Data quality và freshness

### Quality checks

Tập kiểm định chất lượng gồm 9 checks. Dưới đây là kết quả baseline:
-   `duplicate_paper_ids`: Đạt (Không có DOI trùng lặp).
-   `blank_paper_ids`: Đạt (Tất cả bài viết đều có DOI).
-   `blank_titles`: Đạt (Tất cả bài viết đều có tiêu đề).
-   `short_summaries`: Đạt (Tất cả tóm tắt bài viết đều dài trên 20 ký tự).
-   `blank_embedding_texts`: Đạt (Mã nhúng không bị rỗng).
-   `duplicate_rows`: Đạt (Không có dòng trùng lặp hoàn toàn).
-   `invalid_age_days`: Đạt (Không có tuổi âm hoặc rỗng).
-   `stale_rows`: **Thất bại** (Do các bài báo thử nghiệm xuất bản trước tháng 8/2026 hơn 180 ngày).

### Freshness

*   **Đo tại:** `papers_clean.json`
*   **Timestamp mới nhất:** `2026-02-14`
*   **Ngưỡng freshness:** 180 ngày
*   **Trạng thái baseline:** `stale`
*   **Lý do:** Thời gian hiện tại là tháng 8/2026, các bài báo đều có tuổi đời trên 180 ngày.

---

## 9. Corruption scenarios và repair

| Corruption | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `dropped_latest_record` | Xóa các bài viết mới xuất bản | 4 | Tổng số dòng giảm | Mất dữ liệu mới nhất | Nạp lại raw records gốc |
| `blank_summary` | Làm rỗng summary | 4 | Kiểm định `short_summaries` thất bại | Hit Rate RAG sụt giảm | Chạy lại quy trình Cleaning tự động |
| `noisy_summary` | Chèn chuỗi gây nhiễu | 4 | Text length tăng bất thường | Token F1 RAG sụt giảm | Chạy lại quy trình Cleaning tự động |
| `truncated_title` | Cắt ngắn title về 40 ký tự | 4 | Title length giảm | Khả năng truy xuất giảm | Chạy lại quy trình Cleaning tự động |
| `stale_published_date` | Đổi ngày xuất bản về năm 2000 | 4 | Freshness check thất bại | Freshness = `stale` | Chạy lại quy trình Cleaning tự động |
| `duplicate_row` | Nhân bản các dòng | 4 | Kiểm định `duplicate_rows` thất bại | Quality checks sụt giảm | Chạy lại quy trình Cleaning tự động |

*   **Corruption log path:** `data/results/corruption_log.json` (Trạng thái: Có).
*   **Cơ chế repair:** Nạp lại dữ liệu thô gốc từ raw JSON lineage source, tiến hành làm sạch và chuẩn hóa lại từ đầu thay vì tìm cách sửa đổi thủ công trên tệp tin bị lỗi. Điều này đảm bảo tính nhất quán (Reproducibility) và độ tin cậy tuyệt đối của dữ liệu.

---

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | :--- |
| `retrieval_hit_rate`   | `1.0000` | `0.8333` | `1.0000` | `-0.1667` | `+0.1667` | Phục hồi hoàn toàn |
| `mean_token_f1`        | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` | Phục hồi hoàn toàn |
| `judge_accuracy`       | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` | Phục hồi hoàn toàn |
| `mean_judge_score`     | `5.0000` | `3.8889` | `5.0000` | `-1.1111` | `+1.1111` | Phục hồi hoàn toàn |
| Quality checks pass/fail | `8 / 9` | `5 / 9` | `8 / 9` | `-3 checks` | `+3 checks` | Phục hồi hoàn toàn |
| Freshness status         | `stale` | `stale` | `stale` | Không thay đổi | Phục hồi hoàn toàn | Baseline đã stale |

### Kết luận nhân quả:
1.  **Corruption Impact:** Khi chèn lỗi làm rỗng tóm tắt (`blank_summary`) và chèn nhiễu (`noisy_summary`), chỉ số chất lượng dữ liệu sụt giảm nghiêm trọng làm khả năng truy xuất đúng của ChromaDB bị suy giảm, kéo Hit Rate RAG từ `1.0000` xuống `0.8333`.
2.  **Repair Recovery:** Bằng cách khôi phục lại dữ liệu thô từ raw lineage source và chạy làm sạch tự động, tất cả các trường dữ liệu bị làm lỗi được hoàn trả về định dạng chuẩn, giúp khôi phục các chỉ số chất lượng và hiệu năng RAG về mức tối đa `1.0000`.

---

## 11. Vấn đề tích hợp quan trọng

*   **Triệu chứng:** Chạy kiểm định chất lượng dữ liệu bị crash với lỗi `TypeError: unhashable type: 'list'` khi gọi hàm `df.duplicated()`.
*   **Nguyên nhân:** Cột `authors` và `categories` trong DataFrame chứa các kiểu dữ liệu dạng danh sách (`list`), đây là kiểu dữ liệu không băm được (unhashable) trong Python. Hàm `df.duplicated()` của Pandas cố gắng băm tất cả các cột để kiểm tra trùng lặp dẫn tới lỗi crash.
*   **Cách xử lý:** Cập nhật hàm kiểm tra trùng lặp trong [src/observability/quality.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/observability/quality.py) bằng cách bỏ qua các cột list:
    ```python
    duplicate_rows = int(df.drop(columns=["authors", "categories"], errors="ignore").duplicated().sum())
    ```
*   **Cách xác minh:** Chạy pipeline `uv run python script/run_phase1.py` hoàn thành thành công mà không phát sinh lỗi crash.

---

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Đo đạc ngoại tuyến tự động | Giới hạn khả năng đánh giá bằng LLM thật khi không có internet/key | Tích hợp thư viện mô hình nhúng cục bộ và kiểm định thông qua Ollama/vLLM |
| Độ trễ khi nhúng vector | Xây dựng chỉ mục ChromaDB tuần tự có thể bị chậm khi dữ liệu lớn | Chuyển sang xử lý batch embeddings song song sử dụng đa luồng (multi-threading) |

---

## 13. Cam kết nhóm

Cả nhóm cam kết báo cáo phản ánh đúng kết quả chạy thực tế, không chứa thông tin nhạy cảm (API Keys, Secrets) và các artifacts có thể tái hiện chính xác.

**Đại diện nhóm ký tên:** Vũ Nguyễn Quốc Đạt
**Ngày nộp báo cáo:** 2026-08-06
