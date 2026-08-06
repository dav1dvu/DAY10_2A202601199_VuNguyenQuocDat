# Member Role Report — Day 10: Data Pipeline & Data Observability
**Thành viên:** Nguyễn Hoàng Biên (Role 2 - Ingestion Owner)
**MSSV:** 2A202601233
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Hoàng Biên |
| MSSV               | 2A202601233 |
| Khóa/Lớp         | K3 - E402 |
| Tên nhóm         | DMX |
| Vai trò chính    | Role 2 - Ingestion Owner |
| Repository         | [GitHub Repository](https://github.com/dav1dvu/DAY10_2A202601199_VuNguyenQuocDat) |
| Ngày hoàn thành | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Crossref Ingestion | [src/ingestion/crossref.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/crossref.py) | Query filter, settings | `crossref_response.json`, `crossref_records.json` | Hoàn thành |
| Data Lineage Recovery | [src/ingestion/crossref.py:load_raw_records](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/crossref.py#L93) | Path to raw JSON cache | Loaded raw records array (used in Repair phase) | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Kiểm thử phục hồi | Đạt (Role 1) / Pipeline | Đóng góp hàm nạp cache thô cho luồng Repair của pipeline chính |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Thu thập và ghi nhận raw data | [src/ingestion/crossref.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/ingestion/crossref.py) | `data/raw/crossref_records.json` | Kiểm tra kích thước và định dạng JSON |
| Triển khai cơ chế retry & backoff | `src/ingestion/crossref.py` | Lập trình hàm `fetch_crossref_papers` có retry | Kiểm tra code và log chạy |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Việc gọi API công cộng của Crossref có thể gặp lỗi mạng, giới hạn tần suất gọi (rate limits) hoặc lỗi dịch vụ tạm thời. Tôi cần xây dựng một module thu thập dữ liệu thô có cơ chế tự động thử lại (retry backoff), lưu trữ cache cục bộ để đảm bảo pipeline chạy tái hiện được (reproducible) và làm điểm khôi phục gốc (Lineage Source) cho pha Repair.

### Cách triển khai
Tôi đã triển khai hàm `fetch_crossref_papers` trong `src/ingestion/crossref.py`:
- Sử dụng cấu trúc thử lại với số lần tối đa là 3. Khoảng thời gian chờ tăng theo hàm số mũ (Exponential Backoff): lần 1 chờ 1s, lần 2 chờ 2s, lần 3 chờ 4s để giảm tải cho API server.
- Sử dụng header `User-Agent` chứa thông tin lịch sự (mailto) theo khuyến cáo của Crossref để tránh bị đưa vào hàng chờ giới hạn tốc độ.
- Triển khai hàm `load_raw_records` đọc nhanh từ tệp tin JSON thô được cache cục bộ, giúp chạy thử nghiệm offline độc độc lập 100%.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Từ khóa tìm kiếm (query) và tham số số lượng tối đa (`max_results`) |
| Output                         | Danh sách các dict chứa cấu trúc bài báo thô từ API Crossref |
| Module phụ thuộc             | `requests`, `urllib` |
| Module sử dụng output        | `src/ingestion/cleaning.py` (Vũ Tú Quỳnh) |
| Điều kiện lỗi cần xử lý | Lỗi mất kết nối mạng, lỗi parse JSON khi API trả về lỗi 502/503 |

### Cách xác minh

```bash
uv run python script/run_phase1.py
```
- **Kết quả mong đợi:** Lấy được đầy đủ 24 bản ghi thô từ Crossref hoặc cache và ghi ra tệp tin JSON thô thành công.
- **Kết quả thực tế:** 24 bản ghi thô được nạp từ cache cục bộ thành công trong 0.5s.
- **Artifact/log:** [data/raw/crossref_records.json](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/raw/crossref_records.json).

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn giữa việc luôn tải mới dữ liệu từ API Crossref trực tiếp hay sử dụng tệp tin cache thô cục bộ trong quá trình chạy thử nghiệm.
- **Các phương án đã cân nhắc:**
  1.  Gọi API trực tiếp mỗi lần chạy pipeline $\rightarrow$ Luôn có dữ liệu mới.
  2.  Lưu cache cục bộ `crossref_records.json` $\rightarrow$ Tái hiện 100% dữ liệu gốc trong mọi pha.
- **Phương án đã chọn:** Phương án 2 (Sử dụng cache cục bộ).
- **Lý do:** Đảm bảo tính nhất quán của dữ liệu (Data Reproducibility). Nếu API thay đổi danh sách trả về, tập test set sẽ bị lệch và không thể đo đạc so sánh chính xác sự khác biệt giữa baseline, corrupted và repaired.
- **Bằng chứng quyết định phù hợp:** Chạy pipeline liên tục trong Pha 2 giữ nguyên tập dữ liệu 24 bài báo và đo lường delta của RAG Agent chính xác.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Lỗi API trả về rỗng hoặc HTTP 400 Bad Request khi sử dụng query chứa ký tự đặc biệt.
- **Lệnh hoặc bước tái hiện:** Fetch dữ liệu với query chứa dấu cách không được mã hóa.
- **Nguyên nhân gốc:** Chưa url-encode các tham số query khi ghép vào URL API.
- **Cách xử lý:** Sử dụng `urllib.parse.urlencode` để chuẩn hóa các tham số trước khi truyền vào phương thức HTTP request.
- **Cách xác minh sau khi sửa:** Gọi API thành công và nhận đủ dữ liệu JSON.

---

## 7. Hiểu biết về luồng end-to-end

1.  **Dữ liệu đi từ Crossref đến vector index:** Ingest lấy dữ liệu thô (JSON) $\rightarrow$ Cleaning loại bỏ HTML/JATS, chuẩn hóa schema DataFrame $\rightarrow$ Sinh embeddings thông qua mô hình MiniLM $\rightarrow$ Nạp embeddings vào collection của ChromaDB.
2.  **Đo retrieval/answer quality:** Dùng 18 câu hỏi trong test set. Agent truy xuất top_k tài liệu, so sánh DOI với ground-truth ID để tính Hit Rate. So sánh câu trả lời với ground-truth answer thông qua Token F1.
3.  **Quality checks khác freshness monitoring:** Quality checks kiểm tra cấu trúc và tính hợp lệ tĩnh (trùng lặp, rỗng). Freshness monitoring kiểm tra độ cũ của dữ liệu so với ngày chạy hiện tại.
4.  **Vì sao dùng cùng test set:** Để đảm bảo tính đồng nhất của phép đo khi so sánh delta hiệu năng giữa ba trạng thái.
5.  **Repair thành công dựa trên:** Khôi phục dữ liệu từ raw records thô gốc, làm sạch lại, build lại index và đạt RAG Hit Rate & F1 về `1.0000`.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | `1.0000` | `0.8333` | `1.0000` | Ingestion cung cấp gốc dữ liệu sạch giúp hồi phục hoàn toàn |
| `mean_token_f1`      | `1.0000` | `0.7222` | `1.0000` | Khôi phục 100% sau khi repair từ raw cache |
| `judge_accuracy`     | `1.0000` | `0.7222` | `1.0000` | Khôi phục 100% |
| `mean_judge_score`   | `5.0000` | `3.8889` | `5.0000` | Khôi phục 100% |
| Quality checks         | `8 / 9` | `5 / 9` | `8 / 9` | Vượt qua đầy đủ các checks sau khi repair |
| Freshness status       | `stale` | `stale` | `stale` | Bị stale do ngày xuất bản của tập dữ liệu cũ |

### Kết luận từ số liệu
1.  **Lỗi hóa:** Dữ liệu bị Quỳnh làm lỗi $\rightarrow$ RAG Hit Rate sụt giảm còn `0.8333`.
2.  **Khôi phục:** Phục hồi từ raw records thô gốc do tôi cung cấp $\rightarrow$ RAG Hit Rate quay lại `1.0000`.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1.  API công cộng cần có cơ chế exponential backoff và User-Agent lịch sự để vận hành bền vững.
2.  Cache thô là chìa khóa để xây dựng các kịch bản kiểm thử dữ liệu nhất quán.
3.  Không bao giờ sửa lỗi trên dữ liệu sạch; khôi phục từ nguồn lineage thô luôn là giải pháp an toàn nhất.

### Nếu có thêm thời gian
Xây dựng cơ chế tự động phát hiện thay đổi schema (Schema Drift) từ API Crossref để cảnh báo trước khi dữ liệu được nạp vào pipeline.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Hoàng Biên
**Ngày xác nhận:** 2026-08-06
