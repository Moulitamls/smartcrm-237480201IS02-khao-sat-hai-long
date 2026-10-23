"""Xuất 2 biểu đồ ra docs/ làm minh chứng: python -m scripts.export_charts"""
import sqlite3
import matplotlib
matplotlib.use("Agg")
import yaml
from src.dashboard import queries as q
from src.dashboard.charts import chart_trend, chart_technician

cfg = yaml.safe_load(open("config/config.yaml", encoding="utf-8"))
R, conn = cfg["rules"], sqlite3.connect(cfg["paths"]["db"])
f, stamp, src = q.Filters(), q.data_timestamp(conn), cfg["dashboard"]["source_note"]
ov = q.overall(conn, f, R["csat_min_score"])
chart_trend(q.q3_trend(conn, f, R["csat_min_score"]), ov["csat_rate"], src, stamp).savefig("docs/chart1_csat_trend.png", dpi=130)
chart_technician(q.q2_technician(conn, f, R["csat_min_score"], R["small_sample_threshold"]), ov["avg_score"], src, stamp)\
    .savefig("docs/chart2_technician.png", dpi=130)
print("Đã ghi docs/chart1_csat_trend.png và docs/chart2_technician.png")
