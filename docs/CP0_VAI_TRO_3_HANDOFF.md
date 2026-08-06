# CP0 Handoff — Vai trò 3: Cleaning & Corruption

## Clean-data contract đã chốt

| Trường | Trạng thái | Rule |
| --- | --- | --- |
| `paper_id` | Bắt buộc | Normalize lowercase, không rỗng, dedupe giữ record đầu tiên. |
| `title` | Bắt buộc | Bỏ JATS/HTML, decode HTML entities, normalize whitespace. |
| `summary` | Bắt buộc | Bỏ JATS/HTML, decode HTML entities, normalize whitespace. |
| `published` | Bắt buộc | Parse UTC; loại record không parse được; tính `age_days` không âm. |
| `authors` | Tùy chọn | Clean từng phần tử, loại phần tử rỗng, dedupe giữ thứ tự. |
| `categories` | Tùy chọn | Giữ mảng rỗng khi nguồn không cấp dữ liệu; không tự gán category. |
| `text_for_embedding` | Bắt buộc | Ghép title, authors (nếu có), categories (nếu có), summary; không chứa JATS/HTML. |

## Kiểm tra raw snapshot

- Có 24 raw records trong `data/raw/crossref_records.json`.
- 24/24 records có `paper_id`, title, summary và published; `paper_id` unique.
- 0/24 records có categories. Đây là thiếu dữ liệu nguồn, không phải lỗi để sửa bằng cách bịa giá trị.
- Abstract của Crossref chứa JATS/HTML. `src/ingestion/cleaning.py` đã bổ sung bước bỏ markup trước khi tạo `summary` và `text_for_embedding`.

## Handoff và blocker

- Bàn giao cho Vai trò 4: clean schema ở trên; `paper_id` phải được giữ nguyên để index và retrieval dùng làm document identity.
- Bàn giao cho Vai trò 5: chỉ sinh question type `summary`, `authors`, `date` cho đến khi nhóm bổ sung được categories từ nguồn đáng tin cậy hoặc quyết định bỏ loại câu hỏi đó.
- Vai trò 1 cần chuẩn bị Python 3.11–3.13 và dependencies trước khi chạy validation thực tế. Môi trường hiện tại là Python 3.10.11, không cài `pandas`.

## Validation cần chạy ở CP1 khi môi trường sẵn sàng

- [ ] Build DataFrame từ `data/raw/crossref_records.json`.
- [ ] Ghi `data/clean/papers_clean.csv` và `data/clean/papers_clean.json`.
- [ ] Xác nhận `paper_id` unique, `summary`/`text_for_embedding` không rỗng.
- [ ] Xác nhận `summary` và `text_for_embedding` không chứa `<jats:` hoặc HTML tags.
- [ ] Xác nhận `age_days >= 0` và `published` parse được.
- [ ] Log raw count, clean count và số record bị loại/dedupe.
