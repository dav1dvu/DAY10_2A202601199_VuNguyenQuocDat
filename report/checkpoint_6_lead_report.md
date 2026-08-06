# Báo cáo Checkpoint 6 — Lead / Pipeline Integrator (Đạt)
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab
**Nhóm thực hiện:** Nhóm 5 người (Đạt, Biên, Quỳnh, Lan, Nam)

---

## 1. Kết quả chạy tích hợp Pha 2 (Corruption & Repair Flow)
Quy trình tích hợp Pha 2 đã chạy thành công thông qua lệnh:
```bash
uv run python script/run_corruption_flow.py
```
Toàn bộ luồng dữ liệu tự động đã được thực thi đầy đủ 10s:
1.  **Baseline Loading:** Tải dữ liệu và độ đo baseline pha 1.
2.  **Intentional Corruption:** Giả lập lỗi trên tập dữ liệu sạch (24 dòng baseline $\rightarrow$ 24 dòng lỗi).
3.  **Corrupted Indexing & Evaluation:** Xây dựng collection `papers-corrupted` trên ChromaDB và chạy đánh giá trên 18 câu hỏi.
4.  **Corrupted Observability:** Đánh giá chất lượng dữ liệu và độ tươi mới trên dữ liệu lỗi.
5.  **Lineage Recovery & Repair:** Biên dịch lại từ tệp tin thô ban đầu `crossref_records.json` để tái tạo tập dữ liệu sạch hoàn chỉnh `papers_clean_repaired.json`.
6.  **Repaired Indexing & Evaluation:** Xây dựng collection `papers-repaired` trên ChromaDB và đánh giá lại.
7.  **Comparison Reporting:** Tự động sinh báo cáo so sánh tại [corruption_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/reports/corruption_report.md).

---

## 2. Báo cáo so sánh chi tiết hiệu năng và chất lượng (Comparison Report)

### 2.1. So sánh hiệu năng RAG Agent (Core Performance)
| Chỉ số (Metric) | Baseline | Corrupted (Lỗi) | Repaired (Phục hồi) | Delta (Corrupted - Baseline) | Recovery (Repaired - Corrupted) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Retrieval Hit Rate** | `1.0000` | `0.8333` | `1.0000` | `-0.1667` | `+0.1667` |
| **Mean Token F1** | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` |
| **Judge Accuracy** | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` |
| **Mean Judge Score** | `5.0000` | `3.8889` | `5.0000` | `-1.1111` | `+1.1111` |

### 2.2. Phân tích chi tiết giả lập lỗi (Corruption Log)
Tập dữ liệu thô gốc gồm 24 dòng được biến đổi ngẫu nhiên sang 6 kiểu lỗi song song, không chồng chéo trên từng dòng:
-   `blank_summary` (4 dòng): Làm trống phần tóm tắt.
-   `dropped_latest_record` (4 dòng): Xóa các bản ghi mới xuất bản $\rightarrow$ Mất dữ liệu.
-   `duplicate_row` (4 dòng): Nhân bản dòng $\rightarrow$ Lỗi Uniqueness.
-   `noisy_summary` (4 dòng): Chèn chuỗi gây nhiễu `##CORRUPTED-NOISE##`.
-   `stale_published_date` (4 dòng): Kéo lùi ngày về năm 2000 $\rightarrow$ Phá hỏng Freshness.
-   `truncated_title` (4 dòng): Cắt ngắn tiêu đề.

### 2.3. Chất lượng dữ liệu và độ tươi mới (Data Observability)
| Chỉ số | Baseline | Corrupted | Repaired |
| :--- | :--- | :--- | :--- |
| **Data Quality Checks Passed** | `8 / 9` | `5 / 9` | `8 / 9` |
| **Freshness Status** | `stale` | `stale` | `stale` |

> [!NOTE]
> Độ tươi mới (Freshness) được ghi nhận là `stale` ở cả 3 pha do các bản ghi Crossref thử nghiệm đều được xuất bản quá 180 ngày so với thời gian chạy hiện tại (Tháng 8/2026). Khi chạy giả lập lỗi, số bài kiểm tra chất lượng dữ liệu thành công giảm mạnh từ `8 / 9` xuống `5 / 9` (do vi phạm các kiểm tra trùng lặp và trống nội dung), và sau đó phục hồi hoàn hảo về `8 / 9` sau khi chạy quy trình Repair từ Raw lineage source.

---

## 3. Hoàn thiện đầu mục bàn giao cho 5 vai trò tại CP6
1.  **VAI TRÒ 1 (Lead - Đạt):** Orchestrate thành công toàn bộ luồng tích hợp, xác minh và lưu trữ delta hiệu năng RAG, đảm bảo không có API key hay thông tin nhạy cảm bị rò rỉ.
2.  **VAI TRÒ 2 (Ingestion - Biên):** Kiểm chứng tính đúng đắn của Lineage, khôi phục dữ liệu từ nguồn gốc `crossref_records.json` thay vì sửa tay.
3.  **VAI TRÒ 3 (Cleaning - Quỳnh):** Chạy lại quy trình Cleaning tự động trên dữ liệu thô để tạo tập dữ liệu Repaired sạch đạt chuẩn 100%.
4.  **VAI TRÒ 4 (RAG - Lan):** Nạp và khởi tạo bộ chỉ mục `papers-repaired` trên ChromaDB độc lập, xác minh RAG Agent truy xuất bình thường trở lại.
5.  **VAI TRÒ 5 (Eval & Obs - Nam):** Sử dụng tập test set khóa ở CP2 để đánh giá khách quan, đo lường các chỉ số delta và tự động xuất ra tệp báo cáo so sánh.

---
**Xác nhận bàn giao CP6:** Báo cáo so sánh hiệu năng, artifacts chất lượng dữ liệu lỗi và phục hồi đã được đẩy lên kho chứa Git an toàn. Cả 5 vai trò hoàn thành CP6 đúng hạn và đạt chuẩn chất lượng cao!
