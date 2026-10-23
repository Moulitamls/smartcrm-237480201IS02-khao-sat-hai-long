"""Điều phối: extract → transform → quality → load → report. Chạy bằng một lệnh:
   python -m src.pipeline --config config/config.yaml
"""
import argparse
from datetime import datetime
from pathlib import Path
import pandas as pd
import yaml

from src.extract.reader import read_csv, profile, print_profile
from src.transform.normalize import normalize_datetime_column, to_int_score_column
from src.quality.rules import check_tickets, check_surveys
from src.load import sqlite_loader as ld
from src.report import reconcile, write_quality_report


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_from_config(cfg):
    started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p, fmts, closed = cfg["paths"], cfg["date_formats"], cfg["closed_status"]
    Path(p["db"]).parent.mkdir(parents=True, exist_ok=True)

    # 1. Extract
    tickets = read_csv(p["tickets_csv"], cfg["columns"]["tickets"], "tickets_history")
    survey = read_csv(p["survey_csv"], cfg["columns"]["survey"], "survey_responses")
    profiles = [profile(tickets, "tickets_history"), profile(survey, "survey_responses")]
    for pr in profiles:
        print_profile(pr)

    # 2. Transform
    if "created_at" in tickets.columns:
        tickets["created_at"], tickets["created_at_invalid"] = normalize_datetime_column(tickets["created_at"], fmts)
    tickets["closed_at"], tickets["closed_at_invalid"] = normalize_datetime_column(tickets["closed_at"], fmts)
    survey["responded_at"], survey["responded_at_invalid"] = normalize_datetime_column(survey["responded_at"], fmts)
    survey["score_int"] = to_int_score_column(survey["score"])

    # 3. Quality
    tickets_ok, rej_t = check_tickets(tickets, closed)
    survey_ok, rej_s = check_surveys(survey, tickets_ok, closed, cfg["rules"])
    rejects = pd.concat([rej_t, rej_s], ignore_index=True)
    print(f"[quality] loại {len(rej_t)} dòng phiếu, {len(rej_s)} dòng phản hồi")

    # 4. Load
    conn = ld.connect(p["db"], p["schema"])
    ld.load_staging(conn, tickets, survey)
    closed_tickets = tickets_ok[tickets_ok["status"] == closed].copy()
    ld.load_dim_date(conn, pd.concat([closed_tickets["closed_at"], survey_ok["responded_at"]]))
    ld.load_dim_business_key(conn, "dim_center", "center_id", "center_name", closed_tickets["center_id"], "Trung tâm")
    ld.load_dim_business_key(conn, "dim_technician", "technician_id", "technician_name",
                             closed_tickets["technician_id"], "Kỹ thuật viên")
    batches = ld.load_fact_by_day(conn, closed_tickets, survey_ok, cfg["rules"]["csat_min_score"])
    ld.save_rejects(conn, rejects)

    n_fact = ld.count(conn, "fact_survey")
    in_fact = conn.execute("SELECT COALESCE(SUM(has_response),0) FROM fact_survey").fetchone()[0]
    rc = reconcile(len(tickets), n_fact, len(rej_t), int((tickets_ok["status"] != closed).sum()),
                   len(survey), int(in_fact), len(rej_s))
    finished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO etl_run (started_at, finished_at, n_stg_ticket, n_stg_survey, n_fact, n_rejects) "
                 "VALUES (?,?,?,?,?,?)", (started, finished, len(tickets), len(survey), n_fact, len(rejects)))
    conn.commit()
    conn.close()

    summary = {"started_at": started, "finished_at": finished, "profiles": profiles, "reconcile": rc,
               "reject_counts": rejects.groupby(["source_table", "reason"]).size().to_dict() if len(rejects) else {},
               "batches": batches}
    summary["report_path"] = write_quality_report(summary, p["reports_dir"])
    print(f"[load] {len(batches)} lô ngày; fact_survey = {n_fact} dòng; phản hồi trong fact = {in_fact}")
    print(f"[reconcile] stg_ticket {rc['stg_ticket']} = fact {n_fact} + loại {rc['rejected_tickets']} "
          f"+ chưa đóng {rc['open_tickets']}  -> {'ĐẠT' if rc['ticket_check'] else 'LỆCH'}")
    print(f"[report] {summary['report_path']}")
    return summary


def run(config_path):
    return run_from_config(load_config(config_path))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/config.yaml")
    run(ap.parse_args().config)

