# Báo cáo Checkpoint 5 — Corruption có kiểm soát & đo impact

**Thành viên thực hiện:** Vũ Nguyễn Quốc Đạt (Role 1)
**Dự án:** Day 10 — Data Pipeline & Data Observability Lab

---

## 1. Triển khai (Mục tiêu CP5)

Đã hoàn thiện hai file starter còn `TODO(student)`/`NotImplementedError`:

- **`src/ingestion/corruption.py`** — `corrupt_clean_dataframe()`: áp dụng đúng 6 loại lỗi dữ liệu có chủ đích, mỗi loại tác động lên một tập record riêng biệt (không chồng lấn), có log đầy đủ:
  1. `dropped_latest_record` — xóa các record được publish gần nhất (mô phỏng mất dữ liệu mới).
  2. `blank_summary` — làm rỗng summary.
  3. `noisy_summary` — chèn text nhiễu vào summary.
  4. `truncated_title` — cắt ngắn title còn 40 ký tự.
  5. `stale_published_date` — đẩy ngày publish về quá khứ xa (2000-01-01), `age_days=9999`.
  6. `duplicate_row` — nhân bản nguyên vẹn một số record (phá vỡ tính unique của `paper_id`).
- **`src/pipelines/corruption_flow.py`** — điều phối đủ luồng: đọc baseline → corrupt → lưu artifact riêng → build index `papers-corrupted` → evaluate trên test set khóa cứng → quality/freshness → **repair bằng cách clean lại từ raw source** (không sửa tay dữ liệu corrupted) → build index `papers-repaired` → evaluate → quality/freshness → sinh comparison report.
- **`src/observability/reporting.py`** — sửa `generate_corruption_report()` để dùng **số liệu baseline quality/freshness thật** (trước đây hard-code "All Passed"/"Fresh" — lỗi đã phát hiện và sửa ở CP3 audit) và thêm bảng tóm tắt corruption log vào report.
- **`src/core/config.py`** — bổ sung `corrupted_freshness_report` và `repaired_freshness_report` vào `Paths` để freshness report của 3 trạng thái không ghi đè lẫn nhau (baseline vốn đã có path riêng, corrupted/repaired thiếu path riêng nên đã bổ sung theo đúng pattern có sẵn của `corrupted_metrics`/`repaired_metrics`).

Chạy bằng: `python script/run_corruption_flow.py` (venv Python 3.11, sau khi `script/run_phase1.py` đã tạo baseline).

---

## 2. Kết quả chạy end-to-end (thật, đọc trực tiếp từ artifact)

### 2.1 Corruption log (`data/results/corruption_log.json`)

| Loại lỗi | Số record |
| --- | :---: |
| `dropped_latest_record` | 4 |
| `blank_summary` | 4 |
| `noisy_summary` | 4 |
| `truncated_title` | 4 |
| `stale_published_date` | 4 |
| `duplicate_row` | 4 |

Baseline 24 dòng → sau corrupt vẫn 24 dòng (4 dòng bị xóa nhưng 4 dòng bị nhân bản, tổng số dòng trùng ngẫu nhiên — buộc các bước kiểm tra sau phải phát hiện lỗi qua data quality chứ không chỉ nhìn row count).

### 2.2 So sánh metric (từ `data/reports/corruption_report.md`, sinh tự động)

| Metric | Baseline | Corrupted | Repaired | Impact | Recovery |
| --- | :---: | :---: | :---: | :---: | :---: |
| Retrieval Hit Rate | `1.0000` | `0.8333` | `1.0000` | `-0.1667` | `+0.1667` |
| Mean Token F1 | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` |
| Judge Accuracy (LLM thật) | `1.0000` | `0.7222` | `1.0000` | `-0.2778` | `+0.2778` |
| Mean Judge Score (LLM thật) | `5.0000` | `3.8889` | `5.0000` | `-1.1111` | `+1.1111` |
| Quality Checks Passed | `8/9` | `5/9` | `8/9` | `-3` | `+3` |
| Freshness Status | `stale` | `stale` | `stale` | không đổi | không đổi |

**Bằng chứng judge_accuracy giảm là thật (không phải trùng hợp token_f1):** 3 sample bị retrieval miss, 5 sample có `token_f1 < 1.0`, và `judge.reasoning` do LLM Gemini sinh ra nêu đúng lý do, ví dụ sample `doi-10-35314-3y9hy151-summary` (bị `blank_summary` corrupt) trả về `answer=""`, judge chấm `score=1, correct=false, reasoning="The model answer is empty."`. Các reasoning khác ghi nhận "provides a completely different date/authors than the reference answer" — đúng với corruption `stale_published_date`/nhiễu dữ liệu đã áp dụng.

### 2.3 Data quality corrupted (`data/quality/corrupted-quality.json`) — 5/9 pass, 4 fail mới xuất hiện

| Check | Baseline | Corrupted | Nguyên nhân (theo corruption log) |
| --- | :---: | :---: | --- |
| `paper_id_unique` | pass | **fail** (4 duplicate) | `duplicate_row` |
| `summary_min_length` | pass | **fail** (4 < 20 ký tự) | `blank_summary` |
| `duplicate_rows` | pass | **fail** (4 duplicate) | `duplicate_row` |
| `freshness_threshold` | fail (1 stale) | **fail nặng hơn** (5 stale) | 1 stale gốc + 4 record bị `stale_published_date` |

→ Corruption log nối trực tiếp với quality signal thay đổi — đúng yêu cầu CP5 cho vai trò Observability.

### 2.4 Repair — phục hồi bằng re-clean từ raw, không sửa tay

`corruption_flow.py` gọi lại `load_raw_records()` + `build_clean_dataframe()` trên **raw source gốc** (`data/raw/crossref_records.json`, không refetch Crossref) để tạo `papers_clean_repaired.*` — không copy/sửa tay từ dữ liệu corrupted. Kết quả: quality quay lại `8/9` (khớp baseline tuyệt đối), toàn bộ metric RAG phục hồi `1.0000` — repair thành công và có thể tái lập.

**Freshness không được "sơn đẹp":** cả baseline lẫn repaired đều báo `stale` (không phải `fresh`) vì bản chất dữ liệu Crossref gốc đã có 1 record 192 ngày tuổi — repair đúng cách không thể và không nên "sửa" sự thật này, report ghi đúng thực tế thay vì tô hồng.

---

## 3. Xác minh Pass Criteria CP5

| Tiêu chí | Đạt? | Bằng chứng |
| --- | :---: | --- |
| Corruption log tồn tại | ✅ | `data/results/corruption_log.json` |
| Corrupted clean/index/answers/metrics/quality đủ | ✅ | `papers_clean_corrupted.*`, collection `papers-corrupted`, `corrupted_answers.json`, `corrupted_metrics.json`, `corrupted-quality.json`, `freshness_report_corrupted.json` |
| Report so sánh tồn tại | ✅ | `data/reports/corruption_report.md` |
| **Baseline không bị ghi đè** | ✅ | So checksum SHA-256 8 file baseline trước/sau khi chạy corruption flow — **giống hệt tuyệt đối** |
| `papers-baseline` collection không bị mutate | ✅ | `LocalEmbeddingIndex.build()` chỉ xóa/tạo lại collection theo đúng tên đang build (`papers-corrupted`/`papers-repaired`), không đụng `papers-baseline` |
| Path/collection riêng cho 3 trạng thái | ✅ | Baseline/`papers_clean_corrupted`/`papers_clean_repaired`, 3 collection Chroma riêng, 3 bộ metrics/answers/quality/freshness riêng |
| Test set giữ nguyên khi so sánh | ✅ | Cả corrupted và repaired evaluate trên cùng `data/eval/test_set.json` (18 câu, không tạo lại) |
| Evaluator không silently fallback thành success giả | ✅ | Judge dùng LLM Gemini thật (reasoning đa dạng theo từng case, không phải chuỗi fallback cố định); nếu fallback heuristic từng kích hoạt thì reasoning ghi rõ "Fallback heuristic judge used..." — không bị che giấu |
| Chứng minh corruption làm giảm chất lượng + repair phục hồi | ✅ | Xem bảng mục 2.2 — giảm rõ rệt rồi phục hồi hoàn toàn trên mọi metric RAG |

---

**Xác nhận mốc CP5:** Đạt. Corruption có chủ đích, có log chi tiết từng record/loại lỗi, đo được tác động thật lên cả data quality lẫn chất lượng agent (bằng LLM judge thật, không phải heuristic), và repair từ raw source phục hồi đầy đủ mà không sửa tay kết quả. Baseline được bảo toàn nguyên vẹn trong suốt flow. Sẵn sàng sang Checkpoint 6 (Repair review, comparison cuối, demo).
