# Member Role Report — Day 10: Data Pipeline & Data Observability
**Thành viên:** Vũ Tú Quỳnh (Role 3 - Cleaning & Corruption Owner)
**MSSV:** 2A202601239
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Vũ Tú Quỳnh |
| MSSV               | 2A202601239 |
| Khóa/Lớp         | K3 - E402 |
| Tên nhóm         | DMX |
| Vai trò chính    | Role 3 - Cleaning & Corruption Owner |
| Repository         | [GitHub Repository](https://github.com/dav1dvu/DAY10_2A202601199_VuNguyenQuocDat) |
| Ngày hoàn thành | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Data Cleaning & Parser | [src/ingestion/cleaning.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/cleaning.py) | Raw records array | Cleaned DataFrame, `papers_clean.json`/`csv` | Hoàn thành |
| Data Corruption Simulator | [src/ingestion/corruption.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/corruption.py) | Cleaned DataFrame | Corrupted DataFrame, `papers_clean_corrupted.json`/`csv`, `corruption_log.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Tích hợp luồng khôi phục | Biên (Role 2) / Ingestion | Tích hợp thành công hàm `build_clean_dataframe` để làm sạch lại dữ liệu thô gốc trong pha Repair |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Làm sạch và định dạng schema | `src/ingestion/cleaning.py` | `data/clean/papers_clean.json` | Khởi tạo thành công dataframe sạch 24 dòng |
| Giả lập 6 lỗi dữ liệu song song | `src/ingestion/corruption.py` | `data/results/corruption_log.json` | Đọc tệp tin JSON kiểm tra các sự kiện lỗi |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Dữ liệu thô từ API Crossref thường chứa các thẻ HTML/XML định dạng (JATS XML tags) trong phần tiêu đề và tóm tắt, gây nhiễu cho mô hình nhúng (Embeddings). Đồng thời, định dạng tác giả và danh mục bài báo thô rất phức tạp. Tôi cần viết bộ làm sạch và bóc tách dữ liệu chuẩn xác, cũng như viết module giả lập 6 kiểu lỗi dữ liệu có chủ đích phục vụ đo đạc observability.

### Cách triển khai
Tôi đã triển khai hàm `clean_text` và `build_clean_dataframe` trong `cleaning.py`:
- Sử dụng biểu thức chính quy (Regex) `re.sub(r"<[^>]+>", "", text)` để loại bỏ hoàn toàn các thẻ JATS/HTML XML.
- Bóc tách danh sách tác giả `authors` và chuẩn hóa thành chuỗi `authors_joined` cách nhau bằng dấu phẩy.
- Tính toán tuổi bài báo `age_days` bằng cách so sánh ngày hiện tại (`run_date`) với ngày xuất bản (`published`).
Đối với giả lập lỗi dữ liệu trong `corruption.py`:
- Chia DataFrame sạch thành các lát cắt không chồng chéo (disjoint slices) và áp dụng lỗi: `missing_summary`, `truncated_title`, `stale_published_date`, `noisy_summary`, `duplicate_row`, và `dropped_latest_record`.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Danh sách dict dữ liệu thô từ API Crossref |
| Output                         | DataFrame chứa schema sạch chuẩn contract RAG |
| Module phụ thuộc             | `pandas`, `re`, `json` |
| Module sử dụng output        | `src/retrieval/index.py` (Vũ Nguyễn Quốc Đạt) |
| Điều kiện lỗi cần xử lý | Trường `published` bị thiếu thông tin ngày, tác giả bị rỗng |

### Cách xác minh

```bash
uv run python script/run_corruption_flow.py
```
- **Kết quả mong đợi:** Tệp `papers_clean_corrupted.json` được tạo ra chứa các lỗi dữ liệu rõ ràng và ghi đầy đủ log.
- **Kết quả thực tế:** Tạo thành công tệp corrupted và ghi 24 dòng log.
- **Artifact/log:** [data/results/corruption_log.json](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/results/corruption_log.json).

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn cách áp dụng lỗi dữ liệu (Data Corruption) lên DataFrame. Nên áp dụng dồn dập các lỗi trên cùng một bài viết hay áp dụng phân tách trên các dòng độc lập?
- **Các phương án đã cân nhắc:**
  1.  Áp dụng tất cả các kiểu lỗi lên toàn bộ DataFrame sạch cùng lúc.
  2.  Chia DataFrame thành các lát cắt độc lập (disjoint slices) và mỗi bài viết chỉ mang duy nhất một kiểu lỗi.
- **Phương án đã chọn:** Phương án 2 (Chia lát cắt độc lập).
- **Lý do:** Giúp chúng ta đo lường và cách ly được tác động độc lập của từng kiểu lỗi dữ liệu lên chất lượng observability và hiệu năng Agent RAG một cách định lượng (measurability), thay vì làm hỏng toàn bộ dữ liệu khiến không thể cô lập nguyên nhân.
- **Bằng chứng quyết định phù hợp:** Kết quả của `corruption_report.md` thể hiện rõ ràng số lượng bản ghi bị tác động cho từng loại lỗi là 4 dòng.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Lỗi `AttributeError: 'NoneType' object has no attribute 'get'` khi parse tác giả bài viết bị thiếu.
- **Lệnh hoặc bước tái hiện:** Thực hiện làm sạch một bài báo thô không có trường tác giả `author` trong JSON gốc.
- **Nguyên nhân gốc:** Trường `author` bị thiếu khiến `record.get("author")` trả về `None`, dẫn đến lỗi khi gọi vòng lặp bóc tách tên.
- **Cách xử lý:** Bổ sung kiểm tra mặc định:
  ```python
  authors_list = record.get("author") or []
  ```
- **Cách xác minh sau khi sửa:** Chạy làm sạch hoàn thành thành công và gán chuỗi tác giả rỗng cho bài báo bị khuyết thiếu.

---

## 7. Hiểu biết về luồng end-to-end

1.  **Dữ liệu đi từ Crossref đến vector index:** Ingest lấy dữ liệu thô $\rightarrow$ Tôi tiến hành làm sạch loại bỏ HTML/JATS và chuẩn hóa schema DataFrame $\rightarrow$ Đạt sinh embeddings và lưu vào collection ChromaDB.
2.  **Đo retrieval/answer quality:** Dùng 18 câu hỏi trong test set. RAG Agent tìm top_k tài liệu, so sánh DOI với ground-truth ID để tính Hit Rate. So sánh câu trả lời với ground-truth answer thông qua Token F1.
3.  **Quality checks khác freshness monitoring:** Quality checks là kiểm tra cấu trúc và tính hợp lệ tĩnh (trùng lặp, rỗng). Freshness monitoring là kiểm tra độ cũ của dữ liệu dựa trên ngày xuất bản.
4.  **Vì sao dùng cùng test set:** Để đảm bảo tính đồng nhất của phép đo khi so sánh delta hiệu năng giữa ba trạng thái Baseline, Corrupted và Repaired.
5.  **Repair thành công dựa trên:** Khôi phục dữ liệu từ raw records gốc, chạy lại Cleaning, chỉ số RAG Hit Rate & F1 khôi phục về mức tối đa `1.0000`.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | `1.0000` | `0.8333` | `1.0000` | Việc corrupt summary và title làm RAG giảm mạnh |
| `mean_token_f1`      | `1.0000` | `0.7222` | `1.0000` | Repair khôi phục hoàn hảo chất lượng text |
| `judge_accuracy`     | `1.0000` | `0.7222` | `1.0000` | Khôi phục 100% |
| `mean_judge_score`   | `5.0000` | `3.8889` | `5.0000` | Khôi phục 100% |
| Quality checks         | `8 / 9` | `5 / 9` | `8 / 9` | Quality checks phát hiện chính xác các lỗi tôi đã inject |
| Freshness status       | `stale` | `stale` | `stale` | Bị stale do dữ liệu thô vốn đã cũ |

### Kết luận từ số liệu
1.  **Lỗi hóa:** Inject lỗi dữ liệu (`blank summary`, `noisy text`, `duplicate`) $\rightarrow$ Quality checks phát hiện lỗi và sụt giảm chỉ số từ `8/9` xuống `5/9` $\rightarrow$ Hit Rate RAG sụt giảm còn `0.8333`.
2.  **Khôi phục:** Khôi phục dữ liệu từ Raw Lineage và làm sạch lại $\rightarrow$ Quality checks khôi phục về `8/9` $\rightarrow$ Hit Rate RAG khôi phục về `1.0000`.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1.  Biểu thức chính quy là công cụ mạnh mẽ nhưng cần viết cẩn thận để tránh làm mất mát thông tin hữu ích trong văn bản.
2.  Cách cô lập lỗi tốt nhất khi kiểm thử là sử dụng cơ chế chia lát cắt không chồng chéo (disjoint slices).
3.  Tính nhất quán của dữ liệu bắt buộc phải được bảo vệ từ tầng Ingest & Cleaning.

### Nếu có thêm thời gian
Xây dựng một giao diện trực quan cho phép người dùng cấu hình các tỷ lệ lỗi khác nhau trực tiếp trên giao diện để đo lường độ chịu lỗi của RAG Agent.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Vũ Tú Quỳnh
**Ngày xác nhận:** 2026-08-06
