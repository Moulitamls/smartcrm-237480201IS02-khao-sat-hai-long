-- Star schema cho luồng L8 (CSAT). Grain của fact_survey: 1 dòng cho mỗi phiếu đã đóng.

CREATE TABLE IF NOT EXISTS dim_date (
    date_key   INTEGER PRIMARY KEY,
    full_date  TEXT NOT NULL,
    year       INTEGER NOT NULL,
    quarter    INTEGER NOT NULL,
    month      INTEGER NOT NULL,
    day        INTEGER NOT NULL,
    year_month TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_center (
    center_key  INTEGER PRIMARY KEY AUTOINCREMENT,
    center_id   TEXT NOT NULL UNIQUE,
    center_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_technician (
    technician_key  INTEGER PRIMARY KEY AUTOINCREMENT,
    technician_id   TEXT NOT NULL UNIQUE,
    technician_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_survey (
    ticket_id           TEXT PRIMARY KEY,
    response_id         TEXT,
    closed_date_key     INTEGER NOT NULL REFERENCES dim_date(date_key),
    responded_date_key  INTEGER REFERENCES dim_date(date_key),
    center_key          INTEGER NOT NULL REFERENCES dim_center(center_key),
    technician_key      INTEGER NOT NULL REFERENCES dim_technician(technician_key),
    has_response        INTEGER NOT NULL CHECK (has_response IN (0,1)),
    score               INTEGER CHECK (score BETWEEN 1 AND 5),
    is_satisfied        INTEGER,
    response_delay_days INTEGER,
    comment_length      INTEGER,
    hours_to_respond    REAL,
    loaded_at           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reject_rows (
    source_table TEXT,
    record_key   TEXT,
    reason       TEXT,
    detail       TEXT
);

CREATE TABLE IF NOT EXISTS etl_run (
    run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at      TEXT,
    finished_at     TEXT,
    n_stg_ticket    INTEGER,
    n_stg_survey    INTEGER,
    n_fact          INTEGER,
    n_rejects       INTEGER
);

CREATE INDEX IF NOT EXISTS ix_fact_center ON fact_survey(center_key);
CREATE INDEX IF NOT EXISTS ix_fact_tech   ON fact_survey(technician_key);
CREATE INDEX IF NOT EXISTS ix_fact_closed ON fact_survey(closed_date_key);
