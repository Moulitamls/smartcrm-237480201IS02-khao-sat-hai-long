"""Dashboard Streamlit: streamlit run src/dashboard/app.py
Ba trạng thái: đang tải (spinner) · rỗng (giải thích) · lỗi (thông báo + nút Thử lại)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import sqlite3
import pandas as pd
import streamlit as st
import yaml

from src.dashboard import queries as q
from src.dashboard.charts import chart_trend, chart_technician, EMPTY_MESSAGE

CFG = yaml.safe_load(open(Path(__file__).resolve().parents[2] / "config" / "config.yaml", encoding="utf-8"))
DB = str(Path(__file__).resolve().parents[2] / CFG["paths"]["db"])
R = CFG["rules"]


@st.cache_data(ttl=CFG["dashboard"]["cache_ttl_seconds"])
def load_all(date_from, date_to, center_keys):
    conn = sqlite3.connect(DB)
    try:
        f = q.Filters(date_from, date_to, list(center_keys))
        return {
            "centers": pd.read_sql_query("SELECT center_key, center_name FROM dim_center WHERE center_key>0 ORDER BY center_name", conn),
            "range": conn.execute("SELECT MIN(full_date), MAX(full_date) FROM dim_date").fetchone(),
            "trend": q.q3_trend(conn, f, R["csat_min_score"]),
            "tech": q.q2_technician(conn, f, R["csat_min_score"], R["small_sample_threshold"]),
            "overall": q.overall(conn, f, R["csat_min_score"]),
            "low": q.q4_low_scores(conn, q.Filters(date_from, date_to, list(center_keys)), R["low_score_max"]),
            "stamp": q.data_timestamp(conn),
        }
    finally:
        conn.close()


st.set_page_config(page_title="CSAT — Mekong Mobile", layout="wide")
st.title("CSAT sau bảo hành — Mekong Mobile")

try:
    with st.spinner("Đang tải dữ liệu..."):
        base = load_all(None, None, ())
        lo, hi = base["range"]
        st.sidebar.header("Bộ lọc")
        d1 = st.sidebar.date_input("Từ ngày (ngày đóng phiếu)", pd.to_datetime(lo))
        d2 = st.sidebar.date_input("Đến ngày", pd.to_datetime(hi))
        names = st.sidebar.multiselect("Trung tâm", base["centers"]["center_name"].tolist())
        keys = tuple(base["centers"].loc[base["centers"]["center_name"].isin(names), "center_key"])
        data = load_all(str(d1), str(d2), keys)
except Exception as e:                       # trạng thái LỖI
    st.error(f"Không tải được dữ liệu: {e}")
    if st.button("Thử lại"):
        st.cache_data.clear(); st.rerun()
    st.stop()

src, stamp, ov = CFG["dashboard"]["source_note"], data["stamp"], data["overall"]
c1, c2, c3 = st.columns(3)
c1.metric("Điểm hài lòng TB", q.fmt_avg(ov["avg_score"]))
c2.metric("Tỉ lệ CSAT", q.fmt_pct(ov["csat_rate"]))
c3.metric("Tỉ lệ phản hồi", q.fmt_pct(ov["response_rate"]))

if data["trend"].empty:                      # trạng thái RỖNG
    st.info(EMPTY_MESSAGE)
else:
    f1 = chart_trend(data["trend"], ov["csat_rate"], src, stamp)
    f2 = chart_technician(data["tech"], ov["avg_score"], src, stamp)
    (st.pyplot(f1) if f1 else st.info(EMPTY_MESSAGE))
    (st.pyplot(f2) if f2 else st.info(EMPTY_MESSAGE))
    st.subheader("Phản hồi điểm thấp (≤ 2)")
    st.dataframe(data["low"]) if len(data["low"]) else st.info("Không có phản hồi điểm thấp trong bộ lọc này.")
st.caption(f"{src} · Dữ liệu cập nhật lúc {stamp}")
