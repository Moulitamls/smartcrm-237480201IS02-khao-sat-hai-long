"""Tầng load: nạp staging, dựng kho dữ liệu (star schema) và ghi bảng reject vào SQLite."""
import sqlite3
from pathlib import Path

import pandas as pd

WAREHOUSE_TABLES = ["fact_survey", "dim_technician", "dim_center", "dim_date"]


def connect(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def load_staging(conn, raw_tickets, raw_responses):
    """Nạp nguyên văn dữ liệu nguồn vào staging (chưa làm sạch)."""
    raw_tickets.to_sql("stg_ticket", conn, if_exists="replace", index=False)
    raw_responses.to_sql("stg_survey_response", conn, if_exists="replace", index=False)


def load_rejects(conn, rejects):
    rejects.to_sql("reject_rows", conn, if_exists="replace", index=False)


def _date_key(ts):
    return ts.dt.strftime("%Y%m%d").astype("Int64")


def build_dimensions(closed, responses):
    """Dựng 3 bảng chiều từ dữ liệu đã làm sạch."""
    day_values = pd.concat([closed["closed_at"], responses["responded_at"]]).dropna().dt.normalize()
    days = pd.date_range(day_values.min(), day_values.max(), freq="D")
    dim_date = pd.DataFrame({"full_date": days})
    dim_date["date_key"] = _date_key(dim_date["full_date"])
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["year_month"] = dim_date["full_date"].dt.strftime("%Y-%m")
    dim_date["full_date"] = dim_date["full_date"].dt.strftime("%Y-%m-%d")

    centers = sorted(closed["center_id"].dropna().unique())
    dim_center = pd.DataFrame(
        {
            "center_key": range(1, len(centers) + 1),
            "center_id": centers,
            # Dữ liệu nguồn chưa có tên trung tâm: dùng tên tạm, thay khi có file danh mục.
            "center_name": [f"Trung tâm {c}" for c in centers],
        }
    )

    # Mỗi kỹ thuật viên gắn với trung tâm xuất hiện nhiều nhất trong các phiếu của họ.
    tech_center = (
        closed.groupby("technician_id")["center_id"].agg(lambda s: s.mode().iloc[0]).reset_index()
    )
    dim_technician = pd.DataFrame(
        {
            "technician_key": range(1, len(tech_center) + 1),
            "technician_id": tech_center["technician_id"].values,
            "center_id": tech_center["center_id"].values,
        }
    )
    return dim_date, dim_center, dim_technician


def build_fact(closed, responses, dim_center, dim_technician, closed_date_only=True):
    """Mỗi phiếu đã đóng một dòng; LEFT JOIN với phản hồi (grain: một phiếu đã đóng)."""
    merged = closed.merge(
        responses[["ticket_id", "score", "comment", "responded_at"]], on="ticket_id", how="left"
    )
    center_key = dict(zip(dim_center["center_id"], dim_center["center_key"]))
    tech_key = dict(zip(dim_technician["technician_id"], dim_technician["technician_key"]))
    has_response = merged["score"].notna()
    closed_day = merged["closed_at"].dt.normalize()
    responded_day = merged["responded_at"].dt.normalize()
    fact = pd.DataFrame(
        {
            "ticket_id": merged["ticket_id"],
            "closed_date_key": _date_key(closed_day),
            "responded_date_key": _date_key(responded_day),
            "center_key": merged["center_id"].map(center_key),
            "technician_key": merged["technician_id"].map(tech_key),
            "has_response": has_response.astype(int),
            "score": merged["score"],
            "is_satisfied": pd.Series(pd.NA, index=merged.index, dtype="Int64"),
            "response_delay_days": (responded_day - closed_day).dt.days.astype("Int64"),
            "comment": merged["comment"],
        }
    )
    return fact, merged


def load_warehouse(conn, ddl_path, dims, fact, satisfied_min_score):
    """Tạo lại các bảng kho theo DDL rồi nạp dữ liệu (chạy lại nhiều lần vẫn cho kết quả giống nhau)."""
    for table in WAREHOUSE_TABLES:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.executescript(Path(ddl_path).read_text(encoding="utf-8"))
    fact = fact.copy()
    scored = fact["score"].notna()
    fact.loc[scored, "is_satisfied"] = (fact.loc[scored, "score"] >= satisfied_min_score).astype(int)
    dim_date, dim_center, dim_technician = dims
    dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
    dim_center.to_sql("dim_center", conn, if_exists="append", index=False)
    dim_technician.to_sql("dim_technician", conn, if_exists="append", index=False)
    fact.to_sql("fact_survey", conn, if_exists="append", index=False)
    conn.commit()
    return len(fact)
