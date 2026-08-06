# Member Role Report — Day 10: Data Pipeline & Data Observability
**Thành viên:** Vũ Nguyễn Quốc Đạt (Role 1 - Lead / Pipeline Integrator)
**MSSV:** 2A202601199
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Vũ Nguyễn Quốc Đạt |
| MSSV               | 2A202601199 |
| Khóa/Lớp         | K3 - E402 |
| Tên nhóm         | DMX |
| Vai trò chính    | Role 1 - Lead / Pipeline Integrator |
| Repository         | [GitHub Repository](https://github.com/dav1dvu/DAY10_2A202601199_VuNguyenQuocDat) |
| Ngày hoàn thành | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Baseline Orchestration | [src/pipelines/phase1.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/pipelines/phase1.py) | Settings, Raw crossref cache | `papers_clean.json`, `baseline_metrics.json`, `phase1_report.md` | Hoàn thành |
| Corruption & Repair Integration | [src/pipelines/corruption_flow.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/pipelines/corruption_flow.py) | Baseline metrics, Raw cache | `papers_clean_corrupted.json`, `papers_clean_repaired.json`, `corruption_report.md` | Hoàn thành |
| Design & Setup | `report/checkpoint_*` | Starter code, Sơ đồ luồng | Báo cáo mốc thiết kế CP0-CP6, sơ đồ Mermaid | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Hỗ trợ sửa lỗi unhashable list | Quỳnh (Role 3) & Nam (Role 5) / Observability | Sửa thành công lỗi crash pandas `df.duplicated()` |
| Hỗ trợ cấu hình ChromaDB dynamic collections | Lan (Role 4) / RAG & Agent | Lan thiết lập thành công 3 collections độc lập trong ChromaDB |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **CP0** - Chốt sơ đồ luồng dữ liệu & phân công vai trò | [checkpoint_0_lead_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/report/checkpoint_0_lead_report.md) | Bản thiết kế chi tiết luồng bàn giao dữ liệu | Đã nộp báo cáo CP0 |
| **CP2** - Chốt clean schema contract & smoke test | `data/eval/test_set.json`<br>`data/embeddings/papers_embeddings.json` | Khởi tạo thành công bộ câu hỏi (18 câu) và vector index | Chạy smoke test RAG Agent thành công |
| **CP3** - Triển khai baseline pipeline end-to-end | [src/pipelines/phase1.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/pipelines/phase1.py) | Điều phối toàn bộ dữ liệu thô $\rightarrow$ sạch $\rightarrow$ index $\rightarrow$ đánh giá $\rightarrow$ báo cáo | Chạy `uv run python script/run_phase1.py` thành công |
| **CP4** - Thiết kế kịch bản dữ liệu lỗi | [checkpoint_4_break_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/report/checkpoint_4_break_report.md) | Bản kế hoạch chi tiết kịch bản dữ liệu lỗi cho 5 vai trò | Đã nộp báo cáo giải lao CP4 |
| **CP5** - Giả lập lỗi & đo lường độ suy giảm hiệu năng | [src/pipelines/corruption_flow.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/pipelines/corruption_flow.py) | `papers_clean_corrupted.json`<br>`corrupted_metrics.json` | Chạy pipeline ghi nhận sụt giảm Hit Rate về `0.8333` |
| **CP6** - Phục hồi dữ liệu từ lineage & báo cáo so sánh | [src/pipelines/corruption_flow.py](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/src/pipelines/corruption_flow.py) | `papers_clean_repaired.json`<br>`repaired_metrics.json`<br>`corruption_report.md` | Phục hồi RAG Hit Rate & F1 về `1.0000` |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Là Lead / Pipeline Integrator, nhiệm vụ của tôi là thiết lập luồng dữ liệu tự động cho cả Pha 1 và Pha 2, liên kết các module do Biên (Ingestion), Quỳnh (Cleaning/Corruption), Lan (RAG), và Nam (Evaluation/Observability) phát triển thành một hệ thống liền mạch, đồng thời đảm bảo cơ chế tự động ghi nhận và xuất báo cáo so sánh.

### Cách triển khai
Tôi đã viết code triển khai cho `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py`:
- Sử dụng cấu trúc lập trình hướng modul, gọi tuần tự các hàm xử lý từ các package con.
- Sử dụng file cấu hình `settings` làm cầu nối định cấu hình đường dẫn cho các tệp trung gian, đảm bảo tính động và linh hoạt.
- Tự động hóa việc ghi nhận kết quả đánh giá (metrics, answers) và báo cáo chất lượng dữ liệu (quality, freshness) thành báo cáo Markdown thông qua hàm `generate_corruption_report` của Nam.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Dữ liệu cấu hình `Settings` từ `src/core/config.py` và cache dữ liệu thô `crossref_records.json` |
| Output                         | Các tệp CSV/JSON sạch, embeddings, bộ metrics đánh giá, và báo cáo comparison report Markdown |
| Module phụ thuộc             | `ingestion`, `retrieval`, `evaluation`, `observability` |
| Module sử dụng output        | RAG Agent QA và Báo cáo tổng thể cho Nhóm/Giáo viên |
| Điều kiện lỗi cần xử lý | Lỗi thiếu tệp tin baseline khi bắt đầu chạy Pha 2, lỗi database bị khóa do đa luồng |

### Cách xác minh

```bash
uv run python script/run_corruption_flow.py
```
- **Kết quả mong đợi:** Toàn bộ quy trình lỗi hóa, đánh giá, khôi phục, và sinh so sánh diễn ra tự động 100% không phát sinh lỗi. Báo cáo `corruption_report.md` được sinh ra với đầy đủ số liệu 3 cột.
- **Kết quả thực tế:** Toàn bộ pipeline chạy hoàn thành thành công trong 10 giây.
- **Artifact/log:** [data/reports/corruption_report.md](file:///c:/CODE/AITHUCCHIEN/LABS/DAY10_2A202601199_VuNguyenQuocDat/data/reports/corruption_report.md).

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp đặt tên collection cho ChromaDB. Nếu sử dụng một collection cố định cho cả ba pha (Baseline, Corrupted, Repaired), dữ liệu sẽ bị ghi đè chéo, dẫn đến sai lệch kết quả đo.
- **Các phương án đã cân nhắc:**
  1.  Sử dụng một cơ sở dữ liệu ChromaDB duy nhất và xóa/recreate collection liên tục.
  2.  Đặt tên collection động dựa trên đường dẫn tệp embeddings manifest đầu ra (`embeddings_output_path`).
- **Phương án đã chọn:** Phương án 2 (Đặt tên collection động).
- **Lý do:** Giúp duy trì đồng thời cả ba collections (`papers-baseline`, `papers-corrupted`, `papers-repaired`) trong cơ sở dữ liệu SQLite của ChromaDB, cho phép RAG Agent có thể truy xuất và so sánh kết quả độc lập bất cứ lúc nào mà không cần build lại chỉ mục từ đầu.
- **Bằng chứng quyết định phù hợp:** Kết quả của smoke test và test set đánh giá ở CP5/CP6 chạy độc lập và ghi nhận metrics hoàn chỉnh cho cả 3 trạng thái.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Lỗi `chromadb.errors.InternalError: Collection [papers-baseline] already exists` khi chạy lại pipeline.
- **Lệnh hoặc bước tái hiện:** Chạy lại `uv run python script/run_phase1.py` khi collection đã tồn tại trong cơ sở dữ liệu SQLite của ChromaDB.
- **Nguyên nhân gốc:** Khi sử dụng SQLite persistent backend của ChromaDB phiên bản mới, hàm `delete_collection` đôi khi bị trễ hoặc bị khóa do tiến trình trước đó chưa được ngắt hẳn, dẫn tới việc gọi `create_collection` ngay sau đó bị lỗi trùng lặp collection.
- **Cách xử lý:** Bổ sung cơ chế fallback trong `src/retrieval/index.py`:
  ```python
  try:
      collection = client.create_collection(name=collection_name, configuration={"hnsw": {"space": "cosine"}})
  except Exception:
      collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
      existing = collection.get()
      if existing and existing.get("ids"):
          collection.delete(ids=existing["ids"])
  ```
- **Cách xác minh sau khi sửa:** Chạy lại script nhiều lần liên tiếp không còn phát sinh lỗi trùng lặp collection.

---

## 7. Hiểu biết về luồng end-to-end

1.  **Dữ liệu đi từ Crossref đến vector index:** Ingest lấy dữ liệu thô (JSON) $\rightarrow$ Cleaning loại bỏ thẻ JATS/HTML, chuẩn hóa schema sang Pandas DataFrame $\rightarrow$ Sinh embeddings thông qua mô hình MiniLM $\rightarrow$ Nạp embeddings, metadata và ID vào collection của ChromaDB.
2.  **Đo retrieval/answer quality:** Dùng 18 câu hỏi trong test set. Với mỗi câu hỏi, RAG Agent tìm top_k tài liệu tương đồng nhất. Đánh giá tính chính xác của retrieval bằng cách so sánh DOI tài liệu trích xuất được với ground-truth ID. So sánh câu trả lời của LLM với ground-truth answer thông qua Token F1 và Judge evaluator để tính điểm chính xác.
3.  **Quality checks khác freshness monitoring:** Quality checks là kiểm tra tính toàn vẹn tĩnh của dữ liệu (trùng lặp, rỗng, độ dài tối thiểu). Freshness monitoring là kiểm tra động theo thời gian thực (tuổi của dữ liệu có vượt quá ngưỡng 180 ngày so với thời điểm chạy hay không).
4.  **Vì sao dùng cùng test set:** Để đảm bảo tính đồng nhất của phép đo. Bất kỳ sự thay đổi nào của test set sẽ làm nhiễu kết quả đánh giá, khiến ta không thể đo lường chính xác tác động thực tế của lỗi dữ liệu và hiệu quả của cơ chế phục hồi.
5.  **Repair thành công dựa trên:** RAG Hit Rate & Token F1 khôi phục về mức baseline (`1.0000`), chất lượng dữ liệu sạch đạt `8 / 9` checks thành công, và tệp so sánh `corruption_report.md` được cập nhật đầy đủ số liệu phục hồi.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | `1.0000` | `0.8333` | `1.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| `mean_token_f1`      | `1.0000` | `0.7222` | `1.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| `judge_accuracy`     | `1.0000` | `0.7222` | `1.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| `mean_judge_score`   | `5.0000` | `3.8889` | `5.0000` | Sụt giảm mạnh ở pha lỗi và hồi phục 100% |
| Quality checks         | `8 / 9` | `5 / 9` | `8 / 9` | Rơi rớt 3 checks ở pha lỗi và hồi phục hoàn toàn |
| Freshness status       | `stale` | `stale` | `stale` | Bị stale từ baseline do dữ liệu thử nghiệm cũ |

### Kết luận từ số liệu
1.  **Lỗi hóa:** Dữ liệu bị làm lỗi (`missing summary`, `noisy text`) $\rightarrow$ Kiểm định chất lượng giảm từ `8/9` xuống `5/9` $\rightarrow$ RAG Hit Rate giảm từ `1.0000` xuống `0.8333`.
2.  **Khôi phục:** Khôi phục từ Raw Lineage $\rightarrow$ Chất lượng dữ liệu phục hồi về `8/9` $\rightarrow$ RAG Hit Rate quay lại `1.0000`.

Lỗi `blank_summary` và `noisy_summary` ảnh hưởng rõ nhất vì tóm tắt là trường dữ liệu chứa nhiều ngữ nghĩa quan trọng nhất để sinh embedding vector. Khi tóm tắt bị mất hoặc bị nhiễu, khoảng cách cosine giữa câu hỏi và tài liệu bị lệch hướng nghiêm trọng.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1.  Hiểu rõ cơ chế xây dựng một data pipeline tự động end-to-end từ thu thập đến ứng dụng RAG.
2.  Nhận thức được tầm quan trọng của Data Observability: dữ liệu thầm lặng bị lỗi sẽ phá hỏng ứng dụng AI phía sau mà không hề báo trước nếu không có quality/freshness checks.
3.  Phương pháp khôi phục dữ liệu chuẩn mực nhất là sửa lỗi từ gốc (Raw Lineage) và chạy lại pipeline thay vì sửa đổi thủ công trên tầng sạch.

### Nếu có thêm thời gian
Tích hợp kiểm tra chất lượng dữ liệu tự động (Great Expectations) trực tiếp vào luồng CI/CD, ngăn chặn việc cập nhật cơ sở dữ liệu vector nếu kiểm thử chất lượng bị thất bại.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Vũ Nguyễn Quốc Đạt
**Ngày xác nhận:** 2026-08-06
