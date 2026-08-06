# CP3 Audit — Vai trò 2: Ingestion Owner

Kiểm tra sau khi baseline `uv run python script/run_phase1.py` đã chạy xong, đối chiếu trực tiếp với artifact thật trong `data/` (không suy diễn từ log terminal).

## 1. Raw response, raw records và lineage sample vẫn đọc được

| Artifact | Đường dẫn | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| Raw API response | `data/raw/crossref_response.json` | ✅ Đọc được | 238 KB, payload Crossref gốc |
| Raw parsed records | `data/raw/crossref_records.json` | ✅ Đọc được | 24 `PaperRecord`, `paper_id` unique |
| Lineage report | `data/reports/lineage_report.md` | ✅ Đọc được | Bảng mapping raw → clean |
| Lineage map | `data/results/lineage_map.json` | ✅ Tồn tại | Dùng cho audit truy vết |

`generate_stable_id()` (`src/ingestion/crossref.py`) ưu tiên DOI → URL → hash title. Theo `lineage_report.md`: 24/24 record dùng DOI (0 hash fallback), nên `paper_id` truy vết trực tiếp về DOI gốc.

## 2. So sánh raw/clean count

| Giai đoạn | Số record |
| --- | --- |
| Raw (`crossref_records.json`) | 24 |
| Clean (`papers_clean.json`) | 24 |
| Chênh lệch | 0 |

Đối chiếu `paper_id`: 0 raw `paper_id` bị thiếu trong clean, 0 `paper_id` clean không có trong raw (kiểm tra bằng set-diff hai chiều). `lineage_report.md` xác nhận cùng số liệu: Mapped 24, Unmapped 0, Duplicate 0, Missing DOI/URL 0.

**Kết luận:** không có record nào bị rớt ở bước cleaning trong lần chạy này — không cần giải thích chênh lệch vì chênh lệch bằng 0.

## 3. `phase1.py` không fetch lại source ngoài ý muốn

Trong `src/pipelines/phase1.py`:

```python
if settings.refresh_source or not settings.paths.raw_records_json.exists():
    records = fetch_source_records(settings)
else:
    records = load_raw_records(settings.paths.raw_records_json)
```

- `settings.refresh_source` đọc từ biến môi trường `REFRESH_SOURCE`, mặc định rỗng → `False`.
- `data/raw/crossref_records.json` đã tồn tại.

→ Điều kiện fetch lại **không** kích hoạt trong lần chạy baseline vừa rồi; pipeline dùng đúng snapshot raw đã lưu, không gọi lại Crossref API ngoài ý muốn (đúng shared rule "giữ nguyên test set/artifact khi so sánh baseline").

## 4. Đối chiếu Pass Criteria CP3 (phần Vai trò 2)

| Tiêu chí | Đạt? |
| --- | --- |
| Raw response và raw records đọc được | ✅ |
| Lineage sample đọc được | ✅ |
| Raw/clean count khớp, chênh lệch có lý do | ✅ (chênh lệch = 0) |
| Phase1 không refetch ngoài ý muốn | ✅ (xác minh bằng code, không chỉ bằng log) |

## 5. Handoff cho CP5 (corruption)

- Raw snapshot (`data/raw/crossref_records.json`, `crossref_response.json`) phải giữ nguyên, dùng làm điểm khôi phục (repair) — không sửa tay hay ghi đè trước khi corruption flow bắt đầu.
- `lineage_report.md`/`lineage_map.json` là bằng chứng dùng để chứng minh repair phục hồi đúng record khi so sánh baseline–corrupted–repaired ở CP6.
