# Pipeline Documentation — CSAT pipeline (flow L8, track DA)

Source of truth: the code in `src/`. Numbers below come from runs on 2026-11-11 (real data) and on the demo data (`src/config.demo.yaml`).

## 1. Phase diagram

```
tickets_history.csv ─┐
                     ├─► EXTRACT ─► TRANSFORM ─► QUALITY ─► LOAD ─────────────► REPORT ─► SERVE
survey_responses.csv ┘   read, check  dates (8      10 rules,   stg_* (replace)    reconcile   queries Q1–Q5
                         columns,     formats),     1 reason/   dim_* (insert-or-   + quality   + Streamlit
                         null stats   score → int   row →       ignore)             markdown    dashboard
                                                    reject_rows fact (upsert/day)   report
```

Code map: `src/extract/reader.py` → `src/transform/normalize.py` → `src/quality/rules.py` → `src/load/sqlite_loader.py` → `src/report.py`; orchestrated by `src/pipeline.py`, served by `src/queries.py` and `src/app.py`. Diagrams: `docs/DataFlow.drawio.png`, `docs/01_pipeline.png`.

## 2. Sources

| Source | Rows × columns | Columns used | Notes |
|---|---|---|---|
| `data/raw/tickets_history.csv` | 7,800 × 15 | `ticket_id`, `center_id`, `technician_id`, `status`, `closed_at` | 18.59% empty `closed_at` = 1,450 open tickets |
| `data/raw/survey_responses.csv` | 2,600 × 5 | all 5 | 27.54% empty `comment` |

Dates appear in 8 formats (e.g. `2025-05-22 21:30`, `dd/mm/yyyy`, `dd-mm-yyyy`); `dd/mm` is always day-first (`config.yaml`).

## 3. Target and grain

| Table | Grain | Load strategy | Rows (real data) |
|---|---|---|---|
| `fact_survey` | one row per **closed** ticket (with or without a response) | upsert on `ticket_id`, one transaction per closing day (734 batches) | 6,350 |
| `dim_center`, `dim_technician` | one row per business key (+ "Unknown", key −1) | insert-or-ignore | 7 and 39 |
| `dim_date` | one row per calendar day | insert-or-ignore | 738 |
| `stg_ticket`, `stg_survey_response` | raw copy after normalisation | dropped and recreated each run | 7,800 and 2,600 |
| `reject_rows`, `etl_run` | one row per rejected record / per run | rewritten / appended | 0 and 1 per run |

Reconciliation printed by every run: `stg_ticket = fact + rejected tickets + open tickets` (7,800 = 6,350 + 0 + 1,450 → ĐẠT) and `stg_survey = responses in fact + rejected responses` (2,600 = 2,600 + 0).

## 4. Cleaning rules and rows removed

Each row is rejected for the **first** rule it violates. "Demo" = `make_sample_data` file with deliberately wrong rows.

| # | Rule (reason code) | Real data | Demo data |
|---|---|---|---|
| 1 | Ticket ID not empty (`ticket_id_trong`) | 0 | 0 |
| 2 | Ticket ID unique, first row kept (`ticket_id_trung`) | 0 | 5 |
| 3 | `closed_at`, if present, is a valid date (`ngay_dong_khong_doc_duoc`) | 0 | 4 |
| 4 | Closed ticket has `closed_at` (`da_dong_thieu_closed_at`) | 0 | 3 |
| 5 | Score is an integer in 1–5 (`score_ngoai_1_5`) | 0 | 3 |
| 6 | Comment ≤ 500 characters (`nhan_xet_qua_dai`) | 0 | 3 |
| 7 | `responded_at`, if present, is a valid date (`ngay_tra_loi_khong_doc_duoc`) | 0 | 0 |
| 8 | Response belongs to an existing closed ticket (`phieu_chua_dong`) | 0 | 3 |
| 9 | Response date not earlier than closing date, compared by day (`tra_loi_truoc_ngay_dong`) | 0 | 4 |
| 10 | One response per ticket, first kept (`trung_phan_hoi`) | 0 | 5 |
| | **Total rejected** | **0** | **30** (12 tickets + 18 responses) |

Other transformations: empty strings become NULL; missing `center_id` / `technician_id` map to key −1 instead of dropping the ticket; only the comment *length* goes to the fact. The real files contain no invalid rows, which is why the demo data exists.

## 5. Schedule and backfill

- **Schedule:** none is configured; the pipeline runs on demand (`docker compose up -d --build` or `docker compose run --rm pipeline`). Duration on the real data: about 3 seconds. A daily run after the source CSVs are refreshed (cron or Windows Task Scheduler calling `docker compose run --rm pipeline`) is recommended but not implemented.
- **Re-run / backfill:** the pipeline is idempotent. Re-running on the same files leaves `fact_survey` at 6,350 rows (verified: two consecutive runs, and test `test_nap_lan_hai_khong_nhan_doi_dong`). To backfill history, replace the CSV files with a longer extract and re-run: dimensions only gain new keys and the fact rows are updated by `ticket_id`.
- **Failure:** each closing day is committed separately; after a crash, simply re-run — already loaded days are overwritten with identical values.

## 6. Known limitations (and business impact)

1. **Deletions are not propagated.** A ticket or response removed from the CSV stays in `fact_survey` (upsert only). Impact: CSAT may include a withdrawn response until the volume is recreated (`docker compose down -v`).
2. **First response wins.** A second response to the same ticket is rejected (QT-10). Impact: a customer who corrects their score is ignored.
3. **Comparison by day, not by time.** A response earlier in the same day than the closing time is accepted. Impact: `hours_to_respond` is floored at 0 for such rows.
4. **Placeholder names.** Centre and technician names are generated (`Trung tâm 5`, `Kỹ thuật viên 31`) because no master files exist. Impact: managers cannot see real names on the dashboard.
5. **Out of scope (TD-15):** customer table and phone numbers, survey invitations, Excel export, second reminder. Impact: Marketing cannot contact low-score customers from the dashboard.
6. **SQLite is single-writer.** Running two pipelines at once, or opening the DB in another tool, can raise `database is locked`.
7. **Two rules are untested.** `ticket_id_trong` and `ngay_tra_loi_khong_doc_duoc` are not exercised by any unit test or by the demo data (0 rows in both runs).
8. **No raw history.** Staging is recreated every run, so earlier raw loads cannot be inspected.
