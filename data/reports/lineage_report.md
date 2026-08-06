# Data Lineage Report: Crossref Raw to Clean

## 1. Quy tắc tạo `paper_id`
`paper_id` được sinh ra tự động trong module `src/ingestion/crossref.py` (hàm `generate_stable_id`) theo độ ưu tiên sau:
1. **DOI**: Lấy từ trường `DOI` trong response của Crossref, xóa khoảng trắng và chuyển thành chữ thường, thêm tiền tố `doi:`.
2. **URL**: Nếu không có DOI, lấy trường `URL`, xóa khoảng trắng và chuyển thành chữ thường, thêm tiền tố `url:`.
3. **Hash Fallback**: Nếu thiếu cả DOI và URL, sử dụng hàm băm SHA-256 của chuỗi Tiêu đề (Title), lấy 12 ký tự đầu tiên, thêm tiền tố `hash:`.

## 2. Số lượng Records
- **Raw Records**: 24
- **Clean Records**: 24

## 3. Bảng Mapping Mẫu
| paper_id | raw DOI | raw URL | clean record | trạng thái |
| -------- | ------- | ------- | ------------ | ---------- |
| doi:10.47576/2949-1894.2026.7.7.023 | 10.47576/2949-1894.2026.7.7.023 | https://doi.org/10.47576/2949-1894.2026.7.7.023 | Yes | mapped |
| doi:10.36227/techrxiv.177272838.89432844/v1 | 10.36227/techrxiv.177272838.89432844/v1 | https://doi.org/10.36227/techrxiv.177272838.89432844/v1 | Yes | mapped |
| doi:10.63646/kpqm1958 | 10.63646/kpqm1958 | https://doi.org/10.63646/kpqm1958 | Yes | mapped |
| doi:10.20944/preprints202604.0339.v1 | 10.20944/preprints202604.0339.v1 | https://doi.org/10.20944/preprints202604.0339.v1 | Yes | mapped |
| doi:10.3390/app16052244 | 10.3390/app16052244 | https://doi.org/10.3390/app16052244 | Yes | mapped |

## 4. Thống kê
- **Mapped (Truy ngược thành công)**: 24
- **Missing DOI**: 0
- **Missing URL**: 0
- **Hash Fallback**: 0
- **Duplicate (Trùng lặp trong Clean)**: 0
- **Unmapped (Bị loại bỏ trong Clean)**: 0

## 5. Danh sách lỗi hoặc bất thường
- Không phát hiện lỗi bất thường. Mọi clean record đều có duy nhất 1 nguồn gốc hợp lệ.

## 6. Kết luận
- Pipeline tuân thủ chặt chẽ nguyên tắc **Data Lineage**.
- Toàn bộ dữ liệu tại `papers_clean.json` (100%) có thể được ánh xạ ngược (traced back) thành công về `crossref_records.json` thông qua khóa chính `paper_id`.
- Tiêu chí đánh giá lineage: **ĐẠT (PASS)**.
