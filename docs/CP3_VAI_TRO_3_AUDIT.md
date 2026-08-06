# CP3 Audit — Vai trò 3: Cleaning & Corruption Owner

## 1. Clean schema, `age_days` và `text_for_embedding` trong artifact đã ghi

Kiểm tra trực tiếp `data/clean/papers_clean.json` (24 dòng):

| Trường | Kiểm tra | Kết quả |
| --- | --- | --- |
| Schema | Đủ 16 cột theo `build_clean_dataframe()` | ✅ `paper_id, title, summary, authors, categories, primary_category, published, updated, abs_url, pdf_url, comment, authors_joined, categories_joined, summary_chars, age_days, text_for_embedding` |
| `paper_id` | Unique, không rỗng | ✅ 24/24, 0 duplicate |
| `text_for_embedding` | Không rỗng | ✅ 0/24 rỗng |
| `text_for_embedding` + `summary` | Không còn JATS/HTML (`<jats:...>`, `<tag>`) | ✅ 0/24 record còn tag markup — regex quét toàn bộ 24 dòng không phát hiện `<[a-zA-Z/][^>]*>` |
| `age_days` | Số nguyên không âm | ✅ min=0, max=192 |
| Format `published` | ISO 8601 UTC | ✅ (ví dụ `2026-01-25T14:31:54+00:00`) |

`_clean_source_text()` trong `src/ingestion/cleaning.py` unescape HTML entity rồi strip tag bằng regex trước khi ghép vào `text_for_embedding` — khớp với việc 0 record còn markup trong artifact thật.

## 2. Quality check phản ánh dữ liệu thật, không hard-code pass

Đọc `src/observability/quality.py`: mọi số trong từng check (`blank_paper_ids`, `duplicate_paper_ids`, `short_summaries`, `stale_rows`, ...) được tính trực tiếp từ `DataFrame` bằng pandas, không có giá trị gán cứng.

Bằng chứng artifact thật (`data/quality/baseline-quality.json`):

| Check | Giá trị | Trạng thái |
| --- | --- | --- |
| row_count | 24 | ✅ pass |
| paper_id_present | 0 blank | ✅ pass |
| paper_id_unique | 0 duplicate | ✅ pass |
| title_present | 0 blank | ✅ pass |
| summary_min_length | 0 vi phạm | ✅ pass |
| embedding_text_present | 0 blank | ✅ pass |
| duplicate_rows | 0 | ✅ pass |
| age_days_valid | 0 invalid | ✅ pass |
| **freshness_threshold** | **1 row > 180 ngày** | ❌ **fail** |

**Tổng: 8/9 pass, 1/9 fail.** Check `freshness_threshold` fail thật (record cũ nhất có `age_days = 192`, vượt ngưỡng 180 ngày) — đây là bằng chứng check không bị hard-code thành pass, vì nếu hard-code thì tất cả phải pass. `freshness_report.json` đồng nhất: `"is_fresh": false, "status": "stale", "stale_rows": 1`.

## 3. Phát hiện: contract issue nằm ở report tường thuật, không nằm ở pipeline

Baseline artifact (`data/quality/baseline-quality.json`, `data/quality/freshness_report.json`) và report tự động (`data/reports/phase1_report.md`, do `generate_phase1_report()` sinh ra) **khớp nhau tuyệt đối**: cả hai đều ghi 8/9 pass, freshness `stale`.

Tuy nhiên `report/checkpoint_3_lead_report.md` (báo cáo tường thuật của Vai trò 1 nộp cho CP3) đang ghi sai:

| Nội dung trong `checkpoint_3_lead_report.md` | Artifact thật |
| --- | --- |
| "Quality Checks: `9 / 9` kiểm tra thành công" | `baseline-quality.json`: **8 / 9** |
| "Freshness Status: `fresh`" | `freshness_report.json`: **`stale`** |
| "Mean Token F1 Score: `0.9840`" | `baseline_metrics.json` hiện tại: **`1.0000`** |

Đây chính là loại lỗi mà cảnh báo CP3 nhắc tới: *"Baseline chỉ hoàn tất khi artifacts, metrics và report khớp nhau — không phải chỉ khi script exit code 0."* Pipeline và data quality logic **không có lỗi** — không cần sửa code hay chạy lại baseline. Việc cần làm là sửa lại nội dung tường thuật trong `checkpoint_3_lead_report.md` cho khớp với `phase1_report.md`/JSON thật trước khi coi CP3 là hoàn tất (xem đề xuất chi tiết trong `docs/CP3_VAI_TRO_4_5_AUDIT.md` mục 5).

## 4. Đối chiếu Pass Criteria CP3 (phần Vai trò 3)

| Tiêu chí | Đạt? |
| --- | --- |
| Clean schema, `age_days`, `text_for_embedding` đúng trong artifact | ✅ |
| Quality check phản ánh dữ liệu thật (có fail thật, không hard-code) | ✅ |
| Contract issue có evidence được nêu rõ | ✅ (sai lệch nằm ở report tường thuật, đã chỉ ra cụ thể ở mục 3) |
| Baseline cần chạy lại? | ❌ Không cần — artifact và report tự động đã đúng |
