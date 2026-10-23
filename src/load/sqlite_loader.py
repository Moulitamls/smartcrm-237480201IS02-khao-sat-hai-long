"""Nạp staging, dimension (theo khoá nghiệp vụ), fact (theo lô ngày). Chạy lại không nhân đôi dòng."""
import sqlite3
from datetime import datetime
import pandas as pd

UNKNOWN_KEY = -1


def connect(db_path, schema_path):
    conn = sqlite3.connect(db_path)
    with open(schema_path, encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn


def _py(v):
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return None
    if hasattr(v, "item"):
        return v.item()
    return v


def load_staging(conn, tickets_df, survey_df):
    """Staging là vùng đáp: xoá và nạp lại toàn bộ mỗi lần chạy (không tích luỹ)."""
    t = tickets_df.copy()
    for c in ("created_at", "closed_at"):
        if c in t.columns:
            t[c] = t[c].dt.strftime("%Y-%m-%d %H:%M:%S")
    t = t.drop(columns=[c for c in t.columns if c.endswith("_invalid")])
    s = survey_df.copy()
    s["responded_at"] = s["responded_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    s["score"] = s["score_int"].astype(object).where(s["score_int"].notna(), None)
    s = s[["response_id", "ticket_id", "score", "comment", "responded_at"]]
    t.to_sql("stg_ticket", conn, if_exists="replace", index=False)
    s.to_sql("stg_survey_response", conn, if_exists="replace", index=False)


def load_dim_date(conn, dates):
    dates = pd.Series(dates).dropna()
    if dates.empty:
        return 0
    rng = pd.date_range(dates.min().normalize(), dates.max().normalize(), freq="D")
    rows = [(int(d.strftime("%Y%m%d")), d.strftime("%Y-%m-%d"), d.year, (d.month - 1) // 3 + 1,
             d.month, d.day, d.strftime("%Y-%m")) for d in rng]
    conn.executemany("INSERT OR IGNORE INTO dim_date VALUES (?,?,?,?,?,?,?)", rows)
    conn.commit()
    return len(rows)


def load_dim_business_key(conn, table, id_col, name_col, ids, label):
    """Dimension nạp theo khoá nghiệp vụ + dòng 'Không xác định' (key = -1)."""
    conn.execute(f"INSERT OR IGNORE INTO {table} ({table.replace('dim_', '')}_key, {id_col}, {name_col}) "
                 f"VALUES ({UNKNOWN_KEY}, 'UNKNOWN', 'Không xác định')")
    rows = [(str(i), f"{label} {i}") for i in sorted(set(pd.Series(ids).dropna()), key=str)]
    conn.executemany(f"INSERT OR IGNORE INTO {table} ({id_col}, {name_col}) VALUES (?,?)", rows)
    conn.commit()


_UPSERT = """
INSERT INTO fact_survey (ticket_id, response_id, closed_date_key, responded_date_key, center_key,
  technician_key, has_response, score, is_satisfied, response_delay_days, comment_length, hours_to_respond, loaded_at)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
ON CONFLICT(ticket_id) DO UPDATE SET
  response_id=excluded.response_id, closed_date_key=excluded.closed_date_key,
  responded_date_key=excluded.responded_date_key, center_key=excluded.center_key,
  technician_key=excluded.technician_key, has_response=excluded.has_response,
  score=excluded.score, is_satisfied=excluded.is_satisfied,
  response_delay_days=excluded.response_delay_days, comment_length=excluded.comment_length,
  hours_to_respond=excluded.hours_to_respond, loaded_at=excluded.loaded_at
"""


def load_fact_by_day(conn, closed_tickets, survey_ok, csat_min=4):
    """Nạp fact theo lô ngày đóng phiếu; mỗi lô một transaction. Trả về danh sách (ngày, số dòng)."""
    m = closed_tickets.merge(
        survey_ok[["ticket_id", "response_id", "score_int", "comment", "responded_at"]],
        on="ticket_id", how="left")
    centers = dict(conn.execute("SELECT center_id, center_key FROM dim_center"))
    techs = dict(conn.execute("SELECT technician_id, technician_key FROM dim_technician"))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m["closed_day"] = m["closed_at"].dt.normalize()
    batches = []
    for day, g in m.groupby("closed_day"):
        rows = []
        for r in g.itertuples(index=False):
            has = pd.notna(r.response_id)
            resp_key = int(r.responded_at.strftime("%Y%m%d")) if has and pd.notna(r.responded_at) else None
            hours = max(0.0, (r.responded_at - r.closed_at).total_seconds() / 3600) if has and pd.notna(r.responded_at) else None
            rows.append((
                r.ticket_id, _py(r.response_id) if has else None,
                int(day.strftime("%Y%m%d")), resp_key,
                centers.get(str(r.center_id), UNKNOWN_KEY) if pd.notna(r.center_id) else UNKNOWN_KEY,
                techs.get(str(r.technician_id), UNKNOWN_KEY) if pd.notna(r.technician_id) else UNKNOWN_KEY,
                1 if has else 0, int(r.score_int) if has else None,
                (1 if r.score_int >= csat_min else 0) if has else None,
                (r.responded_at.normalize() - r.closed_at.normalize()).days if has and pd.notna(r.responded_at) else None,
                len(r.comment) if has and pd.notna(r.comment) else None, hours, now))
        with conn:
            conn.executemany(_UPSERT, rows)
        batches.append((day.strftime("%Y-%m-%d"), len(rows)))
    return batches


def save_rejects(conn, rejects):
    with conn:
        conn.execute("DELETE FROM reject_rows")
        rejects.to_sql("reject_rows", conn, if_exists="append", index=False)


def count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

