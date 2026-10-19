"""Chạy toàn bộ pipeline bằng MỘT lệnh:
    python -m src.pipeline --config config/config.yaml
Luồng: extract -> transform -> quality -> load (staging, kho dữ liệu, reject_rows) -> báo cáo.
"""
import argparse
from pathlib import Path

import pandas as pd
import yaml

from src.extract.reader import describe, read_csv
from src.load import sqlite_loader as loader
from src.quality.rejects import REJECT_COLUMNS
from src.quality.rules import check_responses, check_tickets
from src.report import write_report
from src.transform.normalize import normalize_responses, normalize_tickets


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(cfg, echo=print):
    paths = cfg["paths"]

    # 1. extract
    raw_tickets = read_csv(paths["tickets_csv"], cfg["columns"]["tickets"], "tickets_history")
    raw_resp = read_csv(paths["survey_csv"], cfg["columns"]["survey"], "survey_responses")
    profiles = [describe(raw_tickets, "tickets_history"), describe(raw_resp, "survey_responses")]
    echo("extract")
    for p in profiles:
        echo(f"  {p['name']:<18}{p['rows']:>7} dòng, {p['cols']} cột")
        for _, r in p["profile"].iterrows():
            echo(f"      {r['cot']:<16} trống {int(r['so_o_trong']):>6}  ({r['ti_le_trong_pct']:.2f}%)")

    # 2. transform
    tickets, rej_t1 = normalize_tickets(raw_tickets, cfg)
    resp, rej_r1 = normalize_responses(raw_resp, cfg)
    echo("transform")
    echo(f"  phiếu: ngày đọc được {len(tickets)}/{len(raw_tickets)}; "
         f"phản hồi: ngày đọc được {len(resp)}/{len(raw_resp)}")

    # 3. quality
    tickets, rej_t2 = check_tickets(tickets, cfg)
    resp, rej_r2 = check_responses(resp, tickets, cfg)
    rejects = pd.concat([rej_t1, rej_t2, rej_r1, rej_r2], ignore_index=True)[REJECT_COLUMNS]
    echo("quality")
    echo(f"  reject {len(rejects)} dòng -> bảng reject_rows (kèm lý do)")

    # 4. load
    closed = tickets[tickets["status"] == cfg["rules"]["closed_status"]]
    dims = loader.build_dimensions(closed, resp)
    fact, _ = loader.build_fact(closed, resp, dims[1], dims[2])
    conn = loader.connect(paths["database"])
    try:
        loader.load_staging(conn, raw_tickets, raw_resp)
        loader.load_rejects(conn, rejects)
        fact_rows = loader.load_warehouse(conn, paths["ddl"], dims, fact, cfg["rules"]["satisfied_min_score"])
    finally:
        conn.close()
    echo("load")
    echo(f"  stg_ticket {len(raw_tickets)}, stg_survey_response {len(raw_resp)}")
    echo(f"  dim_date {len(dims[0])}, dim_center {len(dims[1])}, dim_technician {len(dims[2])}, "
         f"fact_survey {fact_rows}")

    # 5. báo cáo
    by_reason = rejects.groupby(["source_table", "reason"]).size().to_dict()
    stats = {
        "tables": [
            {"name": "ticket", "read": len(raw_tickets),
             "rejected": int((rejects.source_table == "ticket").sum()), "valid": len(tickets)},
            {"name": "survey_response", "read": len(raw_resp),
             "rejected": int((rejects.source_table == "survey_response").sum()), "valid": len(resp)},
        ],
        "closed_tickets": len(closed),
        "responses_valid": len(resp),
        "response_rate": (len(resp) / len(closed) * 100) if len(closed) else 0.0,
        "fact_rows": fact_rows,
        "reject_by_reason": by_reason,
        "profiles": profiles,
    }
    report = write_report(paths["report_dir"], stats)
    echo(f"Báo cáo: {report}")
    return stats


def main():
    parser = argparse.ArgumentParser(description="Pipeline ETL cho báo cáo CSAT (L8)")
    parser.add_argument("--config", default="config/config.yaml")
    args = parser.parse_args()
    run(load_config(args.config))


if __name__ == "__main__":
    main()
