-- Star schema CSAT (L8) - SQLite
-- Grain: một dòng fact_survey = một phiếu bảo hành đã đóng (DA_DONG)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_date (
    date_key    INTEGER PRIMARY KEY,           -- YYYYMMDD
    full_date   DATE        NOT NULL,
    month       SMALLINT    NOT NULL CHECK (month BETWEEN 1 AND 12),
    quarter     SMALLINT    NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year        SMALLINT    NOT NULL,
    year_month  VARCHAR(7)  NOT NULL           -- YYYY-MM
);

CREATE TABLE IF NOT EXISTS dim_center (
    center_key   INTEGER PRIMARY KEY,
    center_id    INTEGER      NOT NULL UNIQUE, -- 1-6
    center_name  VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_technician (
    technician_key  INTEGER PRIMARY KEY,
    technician_id   INTEGER NOT NULL UNIQUE,   -- 1-38
    center_id       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_survey (
    ticket_id            BIGINT   PRIMARY KEY,
    closed_date_key      INTEGER  NOT NULL REFERENCES dim_date(date_key),
    responded_date_key   INTEGER  NULL     REFERENCES dim_date(date_key),
    center_key           INTEGER  NOT NULL REFERENCES dim_center(center_key),
    technician_key       INTEGER  NOT NULL REFERENCES dim_technician(technician_key),
    has_response         BOOLEAN  NOT NULL CHECK (has_response IN (0, 1)),
    score                SMALLINT NULL CHECK (score BETWEEN 1 AND 5),
    is_satisfied         BOOLEAN  NULL CHECK (is_satisfied IN (0, 1)),
    response_delay_days  SMALLINT NULL CHECK (response_delay_days >= 0),
    comment              TEXT     NULL CHECK (comment IS NULL OR length(comment) <= 500),
    -- Phiếu chưa phản hồi thì các cột phản hồi phải rỗng; có phản hồi thì phải có điểm
    CHECK (
        (has_response = 0 AND score IS NULL AND responded_date_key IS NULL)
        OR (has_response = 1 AND score IS NOT NULL AND responded_date_key IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_fact_center_closed ON fact_survey(center_key, closed_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_technician    ON fact_survey(technician_key, closed_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_score         ON fact_survey(score);
