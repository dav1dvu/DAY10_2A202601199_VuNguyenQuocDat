# Member Role Report — Day 10: Data Pipeline & Data Observability
**Thành viên:** Trần Thị Ngọc Lan (Role 5 - Observability Owner)
**MSSV:** 2A202601199_L
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Trần Thị Ngọc Lan |
| MSSV               | 2A202601199_L |
| Khóa/Lớp         | Lớp AI Thực Chiến - Advanced Agentic Coding |
| Tên nhóm         | Vũ Nguyễn Quốc Đạt Group |
| Vai trò chính    | Role 5 - Observability Owner |
| Repository         | [GitHub Repository](https://github.com/dav1dvu/DAY10_2A202601199_VuNguyenQuocDat) |
| Ngày hoàn thành | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Quality & Freshness Checker | [src/observability/quality.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/observability/quality.py) | Cleaned DataFrame, Settings | `baseline-quality.json`, `freshness_report.json` | Hoàn thành |
| Auto Reporting Engine | [src/observability/reporting.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/observability/reporting.py) | Quality JSON, Metrics JSON | `phase1_report.md`, `corruption_report.md` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Sửa lỗi kiểu dữ liệu Pandas | Quỳnh (Role 3) / Cleaning | Quỳnh bóc tách tác giả thành dạng chuỗi giúp tôi kiểm tra trùng lặp trên dataframe không bị crash |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Cài đặt 9 chiều kiểm thử chất lượng | `src/observability/quality.py` | `data/quality/baseline-quality.json` | Đọc tệp tin JSON kiểm thử chất lượng baseline |
| Sinh tự động báo cáo so sánh Pha 2 | `src/observability/reporting.py` | `data/reports/corruption_report.md` | Mở tệp tin kiểm tra bảng so sánh 3 pha |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Tôi cần xây dựng một "Observability Engine" để giám sát chất lượng dữ liệu chảy qua pipeline thời gian thực. Hệ thống này cần phát hiện sớm các vấn đề về chất lượng (dòng trùng lặp, thiếu trường bắt buộc, dữ liệu quá ngắn) và độ tươi mới (freshness) để cảnh báo trước khi dữ liệu đi vào cơ sở dữ liệu vector của Lan, tránh làm hỏng ứng dụng RAG.

### Cách triển khai
Tôi đã viết code kiểm thử trong `src/observability/quality.py`:
- Định nghĩa 9 bài kiểm thử chất lượng dữ liệu bao gồm: trùng lặp DOI (`duplicate_paper_ids`), rỗng DOI (`blank_paper_ids`), rỗng tiêu đề (`blank_titles`), tóm tắt quá ngắn dưới 20 ký tự (`short_summaries`), rỗng chuỗi embedding (`blank_embedding_texts`), trùng lặp dòng (`duplicate_rows`), tuổi bài viết âm (`invalid_age_days`), và tuổi bài viết quá 180 ngày (`stale_rows`).
- Triển khai hàm `build_freshness_report` để tính toán trạng thái "fresh" hoặc "stale" của bộ dữ liệu dựa trên bài viết mới nhất.
Trong `src/observability/reporting.py`, tôi lập trình các hàm sinh văn bản Markdown để tự động xuất ra báo cáo Phase 1 và báo cáo so sánh 3 trạng thái.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | DataFrame sạch từ Quỳnh và bộ Metrics từ Nam |
| Output                         | Báo cáo chất lượng dữ liệu JSON và báo cáo so sánh Markdown |
| Module phụ thuộc             | `pandas`, `pathlib`, `json` |
| Module sử dụng output        | Pipeline Integrator (Đạt) và Giáo viên chấm bài |
| Điều kiện lỗi cần xử lý | Cột dữ liệu chứa list làm crash hàm kiểm tra trùng lặp của Pandas |

### Cách xác minh

```bash
uv run python script/run_corruption_flow.py
```
- **Kết quả mong đợi:** Xuất ra báo cáo so sánh `corruption_report.md` ghi nhận sự sụt giảm chất lượng ở pha lỗi và khôi phục ở pha repair.
- **Kết quả thực tế:** Báo cáo ghi nhận quality checks sụt giảm từ `8 / 9` về `5 / 9` và hồi phục thành công về `8 / 9`.
- **Artifact/log:** [data/reports/corruption_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/reports/corruption_report.md).

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp xử lý lỗi trùng lặp dòng `duplicate_rows` trong dữ liệu. Nên kiểm thử trên toàn bộ các cột của DataFrame hay loại trừ một số trường?
- **Các phương án đã cân nhắc:**
  1.  Kiểm thử trùng lặp dòng trên toàn bộ các cột của DataFrame `df.duplicated()`.
  2.  Loại trừ các cột có kiểu dữ liệu dạng list (`authors`, `categories`) trước khi kiểm tra trùng lặp.
- **Phương án đã chọn:** Phương án 2 (Loại trừ cột dạng list).
- **Lý do:** Tránh lỗi crash `TypeError: unhashable type: 'list'` của thư viện Pandas, vì Pandas không thể băm các cột chứa list để so sánh trùng lặp. Điều này giúp kiểm thử chất lượng chạy an toàn trên mọi phiên bản Pandas.
- **Bằng chứng quyết định phù hợp:** Pipeline chạy tích hợp hoàn thành trơn tru không phát sinh lỗi crash kiểu dữ liệu.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Lỗi `TypeError: generate_corruption_report() missing 2 required positional arguments: 'corrupted_freshness' and 'repaired_freshness'` trong pipeline.
- **Lệnh hoặc bước tái hiện:** Chạy `uv run python script/run_corruption_flow.py` tích hợp Pha 2.
- **Nguyên nhân gốc:** Hàm `generate_corruption_report` do tôi thiết kế yêu cầu 10 đối số vị trí (bao gồm cả freshness thô và baseline) nhưng pipeline của Đạt chỉ truyền vào 8 đối số.
- **Cách xử lý:** Thống nhất với Đạt bổ sung đầy đủ tham số đầu vào trong `corruption_flow.py`: truyền thêm `baseline_quality`, `baseline_freshness`, và `corruption_log`.
- **Cách xác minh sau khi sửa:** Chạy pipeline tích hợp và xuất báo cáo so sánh thành công 100%.

---

## 7. Hiểu biết về luồng end-to-end

1.  **Dữ liệu đi từ Crossref đến vector index:** Ingest lấy dữ liệu thô $\rightarrow$ Quỳnh làm sạch và chuẩn hóa DataFrame $\rightarrow$ Đạt nhúng vector và nạp vào ChromaDB.
2.  **Đo RAG quality:** Nam dùng 18 câu hỏi trong test set để đánh giá Hit Rate và Token F1 trên Agent.
3.  **Quality checks khác freshness monitoring:** Quality checks là kiểm tra cấu trúc hợp lệ tĩnh của dữ liệu sạch. Freshness monitoring là kiểm tra độ cũ động của dữ liệu bài viết so với thời điểm chạy thực tế.
4.  **Vì sao dùng cùng test set:** Để đảm bảo tính đồng nhất của phép đo khi so sánh delta hiệu năng giữa ba trạng thái.
5.  **Repair thành công dựa trên:** Khôi phục dữ liệu từ raw records thô gốc, làm sạch lại, build lại index và đạt RAG Hit Rate & F1 về `1.0000`.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | `1.0000` | `0.8333` | `1.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| `mean_token_f1`      | `1.0000` | `0.7222` | `1.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| `judge_accuracy`     | `1.0000` | `0.7222` | `1.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| `mean_judge_score`   | `5.0000` | `3.8889` | `5.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| Quality checks         | `8 / 9` | `5 / 9` | `8 / 9` | Quality checks sụt giảm do xuất hiện trùng lặp và trống tóm tắt |
| Freshness status       | `stale` | `stale` | `stale` | Đều stale do dữ liệu Crossref gốc đã cũ |

### Kết luận từ số liệu
1.  **Lỗi hóa:** Inject lỗi dữ liệu $\rightarrow$ Quality checks sụt giảm từ `8/9` xuống `5/9` $\rightarrow$ RAG Hit Rate sụt giảm còn `0.8333`.
2.  **Khôi phục:** Khôi phục từ Raw Lineage $\rightarrow$ Quality checks khôi phục về `8/9` $\rightarrow$ RAG Hit Rate quay lại `1.0000`.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1.  Observability là tầng phòng vệ thiết yếu đối với mọi data pipeline chạy thực tế để sớm phát hiện lỗi.
2.  Cần viết log và xuất báo cáo so sánh chi tiết dạng Markdown để dễ dàng debug và báo cáo kết quả.
3.  Phân biệt rõ ràng giữa kiểm tra chất lượng cấu trúc tĩnh và giám sát độ tươi động của dữ liệu.

### Nếu có thêm thời gian
Tích hợp gửi cảnh báo tự động qua Discord/Slack khi phát hiện quality checks bị thất bại ở các bước chạy hàng ngày.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Trần Thị Ngọc Lan
**Ngày xác nhận:** 2026-08-06
