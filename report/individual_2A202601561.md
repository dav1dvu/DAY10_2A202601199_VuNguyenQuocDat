# Member Role Report — Day 10: Data Pipeline & Data Observability
**Thành viên:** Nguyễn Ngọc Nam (Role 4 - Evaluation Owner)
**MSSV:** 2A202601561
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Ngọc Nam |
| MSSV               | 2A202601561 |
| Khóa/Lớp         | K3 - E402 |
| Tên nhóm         | DMX |
| Vai trò chính    | Role 4 - Evaluation Owner |
| Repository         | [GitHub Repository](https://github.com/dav1dvu/DAY10_2A202601199_VuNguyenQuocDat) |
| Ngày hoàn thành | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Evaluation Test Set Generator | [src/evaluation/testset.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/evaluation/testset.py) | Cleaned DataFrame | QA pairs, `data/eval/test_set.json` | Hoàn thành |
| Pipeline Evaluator | [src/evaluation/metrics.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/evaluation/metrics.py) | RAG Agent, Test Set | RAG metrics, `baseline_metrics.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Tích hợp báo cáo so sánh | Lan (Role 5) / Observability | Đồng bộ kết quả đánh giá để tự động xuất tệp so sánh `corruption_report.md` |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Tạo tập câu hỏi kiểm thử | `src/evaluation/testset.py` | `data/eval/test_set.json` | Khởi tạo thành công 18 câu hỏi trích xuất tự động |
| Tính toán chỉ số Hit Rate & Token F1 | `src/evaluation/metrics.py` | `data/results/baseline_metrics.json` | Đọc tệp tin JSON kiểm thử chỉ số Hit Rate đạt 1.0000 |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Tôi cần xây dựng một hệ thống đánh giá tự động (Evaluation Framework) để đo lường định lượng khả năng truy xuất (Retrieval) và sinh câu trả lời (Generation) của RAG Agent. Hệ thống này cần phải hoạt động ổn định ngoại tuyến (offline) phòng trường hợp không có kết nối LLM API thật, đồng thời phải tạo ra một tập câu hỏi kiểm định (Test Set) chất lượng và độc lập.

### Cách triển khai
Tôi đã triển khai các hàm đánh giá chính trong `src/evaluation/metrics.py`:
- **Retrieval Hit Rate:** Kiểm tra xem DOI của tài liệu ground-truth có nằm trong danh sách các tài liệu được truy xuất bởi ChromaDB hay không. Nếu có gán `1.0`, ngược lại `0.0`.
- **Token F1 Score:** Tính toán tỷ lệ tương đồng về từ vựng giữa câu trả lời sinh ra bởi RAG Agent và câu trả lời ground-truth sau khi loại bỏ stopwords và chuẩn hóa từ.
- **Judge Heuristics:** Triển khai cơ chế đánh giá ngoại tuyến thông minh (offline fallback heuristics) sử dụng độ khớp từ khóa và Token F1 làm thước đo nếu không có API Key của OpenAI, giúp hệ thống luôn hoạt động an toàn và ổn định.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Tập dữ liệu sạch `papers_clean.json` và RAG Agent cần đánh giá |
| Output                         | Chỉ số Hit Rate, Token F1, Judge Score cho từng câu hỏi và trung bình |
| Module phụ thuộc             | `pandas`, `sklearn`, `nltk` |
| Module sử dụng output        | `src/pipelines/` (Vũ Nguyễn Quốc Đạt) và `src/observability/` (Ngọc Lan) |
| Điều kiện lỗi cần xử lý | Câu trả lời sinh ra bị rỗng, tài liệu truy xuất bị khuyết thiếu |

### Cách xác minh

```bash
uv run python script/run_phase1.py
```
- **Kết quả mong đợi:** Đánh giá thành công toàn bộ 18 câu hỏi và sinh ra tệp metrics đầy đủ.
- **Kết quả thực tế:** Ghi nhận Hit Rate: `1.0000` và Token F1: `1.0000` cho baseline.
- **Artifact/log:** [data/results/baseline_metrics.json](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/results/baseline_metrics.json).

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn cách thức cài đặt bộ đánh giá câu trả lời (Judge Evaluator). Có nên bắt buộc phải gọi LLM thực tế qua mạng hay sử dụng giải pháp lai (hybrid fallback)?
- **Các phương án đã cân nhắc:**
  1.  Bắt buộc gọi API GPT-4o-mini qua mạng $\rightarrow$ Đánh giá ngữ nghĩa tốt nhưng tốn phí và dễ lỗi nếu mất mạng.
  2.  Sử dụng cơ chế fallback sang Token F1 và Jaccard similarity ngoại tuyến khi không phát hiện API Key.
- **Phương án đã chọn:** Phương án 2 (Cơ chế fallback ngoại tuyến).
- **Lý do:** Đảm bảo tính sẵn sàng cao và khả năng chạy độc lập của pipeline trong môi trường CI/CD hoặc máy chấm thi ngoại tuyến mà không bị sập hay gián đoạn.
- **Bằng chứng quyết định phù hợp:** Toàn bộ pipeline đã chạy hoàn thành trơn tru trên môi trường cục bộ và ghi nhận chỉ số F1 và Judge Score chính xác mà không đòi hỏi cung cấp API Key thật.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Lỗi `ZeroDivisionError: division by zero` khi tính toán Token F1.
- **Lệnh hoặc bước tái hiện:** Thực hiện đánh giá khi RAG Agent sinh ra câu trả lời rỗng (`""`).
- **Nguyên nhân gốc:** Khi câu trả lời sinh ra rỗng, số lượng token thực tế bằng 0 dẫn tới phép chia cho 0 khi tính Precision/Recall.
- **Cách xử lý:** Thêm kiểm tra điều kiện biên:
  ```python
  if len(pred_tokens) == 0 or len(gold_tokens) == 0:
      return 0.0
  ```
- **Cách xác minh sau khi sửa:** Chạy đánh giá thành công và trả về điểm 0.0 cho các câu trả lời rỗng của Agent.

---

## 7. Hiểu biết về luồng end-to-end

1.  **Dữ liệu đi từ Crossref đến vector index:** Ingest lấy dữ liệu thô $\rightarrow$ Quỳnh làm sạch và chuẩn hóa $\rightarrow$ Đạt sinh embeddings và nạp vào ChromaDB.
2.  **Đo retrieval/answer quality:** Dùng 18 câu hỏi trong test set của tôi. Agent thực hiện truy xuất, so sánh DOI với ground-truth ID để tính Hit Rate. So sánh câu trả lời sinh ra với ground-truth answer qua Token F1 và Judge.
3.  **Quality checks khác freshness monitoring:** Quality checks kiểm tra tính hợp lệ tĩnh của dữ liệu sạch. Freshness monitoring kiểm tra tuổi đời dữ liệu bài viết.
4.  **Vì sao dùng cùng test set:** Để đảm bảo tính đồng nhất của phép đo khi so sánh delta hiệu năng giữa ba trạng thái.
5.  **Repair thành công dựa trên:** Khôi phục dữ liệu từ nguồn gốc lineage thô, chạy lại Cleaning, đưa chỉ số RAG Hit Rate & F1 về mức tối đa `1.0000`.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | `1.0000` | `0.8333` | `1.0000` | Lỗi dữ liệu làm giảm khả năng tìm kiếm ngữ cảnh đúng |
| `mean_token_f1`      | `1.0000` | `0.7222` | `1.0000` | Phục hồi hoàn hảo sau khi repair dữ liệu thô |
| `judge_accuracy`     | `1.0000` | `0.7222` | `1.0000` | Phục hồi hoàn hảo |
| `mean_judge_score`   | `5.0000` | `3.8889` | `5.0000` | Phục hồi hoàn hảo |
| Quality checks         | `8 / 9` | `5 / 9` | `8 / 9` | Checks phát hiện chính xác sự biến đổi chất lượng |
| Freshness status       | `stale` | `stale` | `stale` | Bị stale đồng loạt do tuổi bài báo thô đã cũ |

### Kết luận từ số liệu
1.  **Lỗi hóa:** Inject lỗi $\rightarrow$ RAG Hit Rate sụt giảm còn `0.8333` và Token F1 giảm còn `0.7222`.
2.  **Khôi phục:** Khôi phục từ Raw Lineage $\rightarrow$ RAG Hit Rate và F1 khôi phục nguyên vẹn về `1.0000`.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1.  Mục tiêu tối thượng của RAG không chỉ là câu trả lời hay mà là câu trả lời phải đúng dựa trên tài liệu (groundedness).
2.  Cần khóa cố định tập câu hỏi đánh giá trước khi bắt đầu tối ưu hóa hệ thống.
3.  Cơ chế fallback ngoại tuyến giúp mã nguồn an toàn và bền vững hơn rất nhiều.

### Nếu có thêm thời gian
Tích hợp các chỉ số đánh giá nâng cao của Ragas như Faithfulness (độ trung thực) và Answer Relevance (độ liên quan) sử dụng các mô hình nhỏ cục bộ để đánh giá tự động.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Ngọc Nam
**Ngày xác nhận:** 2026-08-06
