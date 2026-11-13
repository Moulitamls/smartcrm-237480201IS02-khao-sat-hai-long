# Data Dictionary — Smart CRM CSAT warehouse (flow L8, track DA)

Database: SQLite `csat.db` (local run: `data/csat.db`; Docker: `/var/lib/csat/csat.db` in volume `csatdata`). DDL: `src/star_schema.sql`.
Generated from the real database with `PRAGMA table_info` on pipeline run of 2026-11-11 (6,350 fact rows); every column of every table below is documented (checked by script).

**Fields per column (6):** Column · Type · Key / Null · Description · Data classification · Security handling.
**Classification:** *Internal* = business metric or technical value; *Personal-linked (indirect)* = pseudonymous ID that could be linked to a person only through other systems; *Free text* = may contain personal data typed by people; *Technical/audit* = pipeline bookkeeping.

## fact_survey

Grain: one row per closed ticket. Loaded by upsert on `ticket_id`.

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `ticket_id` | TEXT | PK, NOT NULL | Business key of the closed warranty ticket (grain: one row per closed ticket). | Personal-linked (indirect) | Pseudonymous ID, no name or phone. Not exposed outside the dashboard table. |
| `response_id` | TEXT | NULL | ID of the accepted survey response for this ticket; NULL if the customer did not respond. | Personal-linked (indirect) | Pseudonymous ID. Joined to stg_survey_response only for the low-score table. |
| `closed_date_key` | INTEGER | FK dim_date, NOT NULL | Date the ticket was closed, as yyyymmdd; FK to dim_date.date_key. | Internal | None needed. |
| `responded_date_key` | INTEGER | FK dim_date, NULL | Date of the response as yyyymmdd; FK to dim_date.date_key; NULL if no response. | Internal | None needed. |
| `center_key` | INTEGER | FK dim_center, NOT NULL | FK to dim_center.center_key; -1 when the ticket has no centre. | Internal | None needed. |
| `technician_key` | INTEGER | FK dim_technician, NOT NULL | FK to dim_technician.technician_key; -1 when the ticket has no technician. | Internal | Technician is shown as a placeholder name only (see dim_technician). |
| `has_response` | INTEGER | NOT NULL | 1 if the ticket has an accepted response, otherwise 0. Used for response rate. | Internal | None needed. |
| `score` | INTEGER | NULL | Satisfaction score 1-5 (CHECK constraint); NULL if no response. | Internal | Validated by rule score_ngoai_1_5 before load. |
| `is_satisfied` | INTEGER | NULL | 1 if score >= csat_min_score (4), 0 otherwise; NULL if no response. Used for CSAT rate. | Internal | None needed. |
| `response_delay_days` | INTEGER | NULL | Whole days between closing date and response date; NULL if no response. | Internal | None needed. |
| `comment_length` | INTEGER | NULL | Number of characters of the comment; the comment text itself is NOT stored in the fact (TD-14). | Internal | Text kept out of the fact on purpose to limit personal data in the reporting table. |
| `hours_to_respond` | REAL | NULL | Hours between closed_at and responded_at, floored at 0; NULL if no response. | Internal | None needed. |
| `loaded_at` | TEXT | NOT NULL | Timestamp of the last upsert of this row (yyyy-mm-dd hh:mm:ss). | Technical/audit | None needed. |

## dim_date

One row per calendar day between the first and last date found in the data (738 rows).

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `date_key` | INTEGER | PK, NOT NULL | Surrogate key, yyyymmdd as integer. | Internal | None needed. |
| `full_date` | TEXT | NOT NULL | Calendar date, yyyy-mm-dd. | Internal | None needed. |
| `year` | INTEGER | NOT NULL | Calendar year. | Internal | None needed. |
| `quarter` | INTEGER | NOT NULL | Quarter of the year, 1-4. | Internal | None needed. |
| `month` | INTEGER | NOT NULL | Month number, 1-12. | Internal | None needed. |
| `day` | INTEGER | NOT NULL | Day of month, 1-31. | Internal | None needed. |
| `year_month` | TEXT | NOT NULL | Month label yyyy-mm; used to group the monthly CSAT trend. | Internal | None needed. |

## dim_center

Loaded by business key. 7 rows = 6 centres + the 'Unknown' row (key -1).

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `center_key` | INTEGER | PK, NOT NULL | Surrogate key. -1 is the row 'Không xác định' (unknown) used for missing centres. | Internal | None needed. |
| `center_id` | TEXT | UNIQUE, NOT NULL | Business key from tickets_history.csv (values 1-6) or 'UNKNOWN' for key -1. UNIQUE. | Internal | None needed. |
| `center_name` | TEXT | NOT NULL | Display name; a placeholder ('Trung tâm N') because no centre master file exists yet. | Internal | None needed. |

## dim_technician

Loaded by business key. 39 rows = 38 technicians + the 'Unknown' row (key -1).

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `technician_key` | INTEGER | PK, NOT NULL | Surrogate key. -1 is the row 'Không xác định' used for missing technicians. | Internal | None needed. |
| `technician_id` | TEXT | UNIQUE, NOT NULL | Business key from tickets_history.csv (38 distinct values) or 'UNKNOWN'. UNIQUE. | Personal-linked (indirect) | Pseudonymous ID. |
| `technician_name` | TEXT | NOT NULL | Display name; a placeholder ('Kỹ thuật viên N'), not a real person's name. | Personal-linked (indirect) | Pseudonymised by design: no real names are loaded. |

## reject_rows

Rows rejected by the quality rules. Emptied and rewritten on every run. 0 rows on the real data; 30 on the demo data.

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `source_table` | TEXT | NULL | Staging table the rejected row came from (stg_ticket or stg_survey_response). | Technical/audit | None needed. |
| `record_key` | TEXT | NULL | ticket_id or response_id of the rejected row; 'dong_<n>' when the key itself is empty. | Personal-linked (indirect) | Keys only, never the row content. |
| `reason` | TEXT | NULL | Machine-readable rejection reason (one reason per row, first violated rule wins). | Technical/audit | None needed. |
| `detail` | TEXT | NULL | Short human-readable explanation of the rule that was violated. | Technical/audit | Generic text only; contains no row values. |

## etl_run

One row per pipeline run (audit trail).

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `run_id` | INTEGER | PK, NOT NULL | Auto-increment ID of the pipeline run. | Technical/audit | None needed. |
| `started_at` | TEXT | NULL | Run start time. | Technical/audit | None needed. |
| `finished_at` | TEXT | NULL | Run end time; shown on the dashboard as 'data updated at'. | Technical/audit | None needed. |
| `n_stg_ticket` | INTEGER | NULL | Rows in stg_ticket for this run. | Technical/audit | None needed. |
| `n_stg_survey` | INTEGER | NULL | Rows in stg_survey_response for this run. | Technical/audit | None needed. |
| `n_fact` | INTEGER | NULL | Rows in fact_survey after the run. | Technical/audit | None needed. |
| `n_rejects` | INTEGER | NULL | Rows written to reject_rows in this run (tickets + responses). | Technical/audit | None needed. |

## stg_survey_response

Staging copy of survey_responses.csv after normalisation. Dropped and recreated on every run.

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `response_id` | TEXT | NULL | Response ID from the source CSV. | Personal-linked (indirect) | Pseudonymous ID. |
| `ticket_id` | TEXT | NULL | Ticket the response belongs to. | Personal-linked (indirect) | Pseudonymous ID. |
| `score` | INTEGER | NULL | Score coerced to integer; NULL if not a whole number. | Internal | Validated before load into the fact. |
| `comment` | TEXT | NULL | Free-text comment from the customer, up to 500 chars accepted. | Free text (may contain personal data) | Checked: 0 of 1,884 comments contain a phone number or e-mail (regex check). Shown only in the low-score table; never written to logs. |
| `responded_at` | TEXT | NULL | Response time normalised to yyyy-mm-dd hh:mm:ss. | Internal | None needed. |

## stg_ticket

Staging copy of tickets_history.csv (all 15 source columns, 7,800 rows). Dropped and recreated on every run. Only 5 columns are used downstream.

| Column | Type | Key / Null | Description | Data classification | Security handling |
|---|---|---|---|---|---|
| `ticket_id` | TEXT | NULL | Ticket ID from the source CSV (business key). | Personal-linked (indirect) | Pseudonymous ID. |
| `ticket_code` | TEXT | NULL | Human-readable ticket code (BH-000001/2025). Not used by the pipeline. | Personal-linked (indirect) | Pseudonymous code. |
| `customer_id` | TEXT | NULL | Customer identifier (6,443 distinct values). Not used by the pipeline. | Personal-linked (indirect) | Numeric pseudonym, no name or phone in the dataset (TD-05). Kept only in staging, never in the fact. |
| `serial_no` | TEXT | NULL | Device serial number. Not used by the pipeline. | Personal-linked (indirect) | Staging only; not loaded to the fact. |
| `product_id` | TEXT | NULL | Product ID. Not used by the pipeline. | Internal | None needed. |
| `center_id` | TEXT | NULL | Service centre ID (1-6); empty -> mapped to key -1 in the fact. | Internal | None needed. |
| `issue_desc` | TEXT | NULL | Free-text description of the fault written at intake. Not used by the pipeline. | Free text (may contain personal data) | Checked: 0 of 7,800 values contain a phone number or e-mail. Staging only. |
| `category_id` | TEXT | NULL | Fault category ID. Not used by the pipeline. | Internal | None needed. |
| `priority` | TEXT | NULL | Priority label (e.g. TRUNG_BINH, CAO). Not used by the pipeline. | Internal | None needed. |
| `status` | TEXT | NULL | Ticket status; only DA_DONG (closed) tickets enter the fact. | Internal | None needed. |
| `technician_id` | TEXT | NULL | Technician ID (38 distinct values); empty -> key -1. | Personal-linked (indirect) | Pseudonymous ID. |
| `received_at` | TEXT | NULL | Intake time (text, source format). Not used by the pipeline. | Internal | None needed. |
| `due_date` | TEXT | NULL | Committed due date (text, source format). Not used by the pipeline. | Internal | None needed. |
| `closed_at` | TEXT | NULL | Closing time normalised to yyyy-mm-dd hh:mm:ss; empty for open tickets (1,450 rows). | Internal | None needed. |
| `is_warranty` | TEXT | NULL | 'true'/'false' flag as text. Not used by the pipeline. | Internal | None needed. |

## Rejection reasons (values of `reject_rows.reason`)

| Reason | Table | Rule |
|---|---|---|
| `ticket_id_trong` | stg_ticket | ticket_id is empty |
| `ticket_id_trung` | stg_ticket | ticket_id repeated (first row kept) |
| `ngay_dong_khong_doc_duoc` | stg_ticket | closed_at present but not a valid date |
| `da_dong_thieu_closed_at` | stg_ticket | status is closed but closed_at is empty |
| `score_ngoai_1_5` | stg_survey_response | score is not a whole number between 1 and 5 |
| `nhan_xet_qua_dai` | stg_survey_response | comment longer than 500 characters |
| `ngay_tra_loi_khong_doc_duoc` | stg_survey_response | responded_at present but not a valid date |
| `phieu_chua_dong` | stg_survey_response | ticket does not exist or is not closed |
| `tra_loi_truoc_ngay_dong` | stg_survey_response | response date earlier than the closing date (compared by day) |
| `trung_phan_hoi` | stg_survey_response | ticket already has an accepted response (QT-10) |
