"""Năm báo cáo Q1–Q5 trên kho dữ liệu. Tất cả trả DataFrame; kỳ không có phản hồi → avg_score/csat_rate là NaN
(giao diện hiển thị 'Chưa có dữ liệu', không hiển thị 0)."""
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd


@dataclass
class Filters:
    date_from: Optional[str] = None          # yyyy-mm-dd (theo ngày đóng phiếu)
    date_to: Optional[str] = None
    center_keys: list = field(default_factory=list)


def _where(f, date_col="dc.full_date"):
    clauses, params = [], []
    if f.date_from:
        clauses.append(f"{date_col} >= ?"); params.append(f.date_from)
    if f.date_to:
        clauses.append(f"{date_col} <= ?"); params.append(f.date_to)
    if f.center_keys:
        clauses.append(f"f.center_key IN ({','.join('?' * len(f.center_keys))})"); params += list(f.center_keys)
    return (" WHERE " + " AND ".join(clauses)) if clauses else "", params


def _metrics(csat_min):
    return (f"COUNT(*) AS n_closed, SUM(f.has_response) AS n_response, AVG(f.score) AS avg_score, "
            f"1.0*SUM(CASE WHEN f.score>={int(csat_min)} THEN 1 ELSE 0 END)/NULLIF(COUNT(f.score),0) AS csat_rate, "
            f"1.0*SUM(f.has_response)/COUNT(*) AS response_rate")


_JOINS = ("FROM fact_survey f JOIN dim_date dc ON dc.date_key=f.closed_date_key "
          "JOIN dim_center c ON c.center_key=f.center_key "
          "JOIN dim_technician t ON t.technician_key=f.technician_key")


def q1_center_month(conn, f, csat_min=4):
    w, p = _where(f)
    return pd.read_sql_query(f"SELECT dc.year_month, c.center_name, {_metrics(csat_min)} {_JOINS}{w} "
                             f"GROUP BY dc.year_month, c.center_name ORDER BY dc.year_month, c.center_name", conn, params=p)


def q2_technician(conn, f, csat_min=4, small_sample=10):
    w, p = _where(f)
    df = pd.read_sql_query(f"SELECT t.technician_name, {_metrics(csat_min)} {_JOINS}{w} "
                           f"GROUP BY t.technician_key ORDER BY avg_score", conn, params=p)
    df["small_sample"] = df["n_response"] < small_sample      # biên: 9 → mẫu nhỏ, 10 → không
    return df


def q3_trend(conn, f, csat_min=4):
    w, p = _where(f)
    return pd.read_sql_query(f"SELECT dc.year_month, {_metrics(csat_min)} {_JOINS}{w} "
                             f"GROUP BY dc.year_month ORDER BY dc.year_month", conn, params=p)


def q4_low_scores(conn, f, low_max=2):
    w, p = _where(f, "dr.full_date")
    cond = f"f.score <= {int(low_max)}"
    w = (w + " AND " if w else " WHERE ") + cond
    
    return pd.read_sql_query(
        """SELECT f.ticket_id, c.center_name, f.score, 
           COALESCE(s.comment, '(không có nhận xét)') AS comment, 
           dr.full_date AS responded_date 
           FROM fact_survey f 
           JOIN dim_center c ON c.center_key=f.center_key 
           JOIN dim_date dr ON dr.date_key=f.responded_date_key 
           LEFT JOIN stg_survey_response s ON s.response_id=f.response_id""" + w + 
        " ORDER BY dr.full_date DESC, f.ticket_id", conn, params=p)

def q5_response_rate_center(conn, f, csat_min=4):
    w, p = _where(f)
    return pd.read_sql_query(f"SELECT c.center_name, {_metrics(csat_min)} {_JOINS}{w} "
                             f"GROUP BY c.center_key ORDER BY c.center_name", conn, params=p)


def overall(conn, f, csat_min=4):
    w, p = _where(f)
    return pd.read_sql_query(f"SELECT {_metrics(csat_min)} {_JOINS}{w}", conn, params=p).iloc[0]


def data_timestamp(conn):
    row = conn.execute("SELECT finished_at FROM etl_run ORDER BY run_id DESC LIMIT 1").fetchone()
    return row[0] if row else "chưa có lần nạp nào"


def fmt_avg(v, digits=2):
    return "Chưa có dữ liệu" if v is None or pd.isna(v) else f"{v:.{digits}f}"


def fmt_pct(v):
    return "Chưa có dữ liệu" if v is None or pd.isna(v) else f"{v * 100:.1f}%"
