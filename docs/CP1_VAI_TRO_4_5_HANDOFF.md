# CP1 Handoff — Vai trò 4 và 5

## Vai trò 4 — RAG & Agent: audit trước index

Đã kiểm tra `data/clean/papers_clean.csv`:

| Điều kiện index | Kết quả |
| --- | --- |
| Số clean rows | 24 |
| `paper_id` unique | Có |
| Title rỗng | 0 |
| Summary rỗng | 0 |
| `text_for_embedding` rỗng | 0 |
| JATS/HTML trong summary hoặc embedding text | 0 |
| Authors có dữ liệu | 24/24 |
| Categories có dữ liệu | 0/24 |

Clean dataframe có đủ trường `LocalEmbeddingIndex._build_documents()` yêu cầu: `paper_id`, `title`, `text_for_embedding`, `published`, `authors_joined`, `categories_joined`, `summary`, `abs_url`, `pdf_url`.

### Cấu hình baseline đã chuẩn bị

- Input: `data/clean/papers_clean.csv`
- Collection: `papers-baseline`
- Persist path: `data/chroma/`
- Manifest: `data/embeddings/papers_embeddings.json`
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- `top_k`: 4

Chưa build final collection ở CP1. Việc đó thuộc CP2 sau khi môi trường chạy được và test set đã khóa.

## Vai trò 5 — Evaluation & Observability

### Evaluation set đã chốt

`src/evaluation/testset.py` chọn 6 paper phân bố đều trong clean dataset và tạo câu hỏi từ dữ liệu đã clean. Với snapshot hiện tại sẽ tạo 18 sample: 6 `summary`, 6 `authors`, 6 `date`.

Không có sample `categories`: `categories_joined` rỗng ở toàn bộ 24 records; builder xử lý `NaN` là rỗng và không sinh ground truth giả.

Các `paper_id` đại diện đã kiểm tra:

- `doi:10.35314/3y9hy151`
- `doi:10.20944/preprints202604.0339.v1`
- `doi:10.22214/ijraset.2026.82233`
- `doi:10.47576/2949-1894.2026.7.7.023`
- `doi:10.2196/preprints.106157`
- `doi:10.2118/234689-pa`

### Quality/freshness baseline dự kiến

`src/observability/quality.py` đã triển khai các checks row count, `paper_id` present/unique, title, summary length, embedding text, duplicate row, `age_days` validity và freshness threshold.

Kiểm tra trực tiếp từ clean CSV:

- `age_days` min/max: 0 / 192.
- 1/24 rows cũ hơn ngưỡng 180 ngày.
- Vì vậy quality check `freshness_threshold` phải **fail**, freshness status là **stale**. Đây là evidence trung thực, không phải lỗi làm report thất bại.

## Blocker để tạo artifact CP1

Môi trường hiện tại vẫn là Python 3.10.11, thiếu `pandas`; project yêu cầu Python 3.11–3.13. Sau khi Vai trò 1 sửa môi trường, chạy builder để tạo `data/eval/test_set.json` và chạy quality/freshness functions để ghi JSON thật vào `data/quality/`.
