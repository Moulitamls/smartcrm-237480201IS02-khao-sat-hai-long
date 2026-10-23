import sqlite3
import pandas as pd
import pytest
import yaml
from src.pipeline import run_from_config


@pytest.fixture
def cfg():
    return yaml.safe_load(open("src/config.yaml", encoding="utf-8"))


def write_csvs(tmp_path, tickets, survey):
    t, s = tmp_path / "t.csv", tmp_path / "s.csv"
    pd.DataFrame(tickets, columns=["ticket_id", "center_id", "technician_id", "status", "created_at", "closed_at"]).to_csv(t, index=False)
    pd.DataFrame(survey, columns=["response_id", "ticket_id", "score", "comment", "responded_at"]).to_csv(s, index=False)
    return t, s


def run_pipeline(cfg, tmp_path, tickets, survey):
    t, s = write_csvs(tmp_path, tickets, survey)
    cfg["paths"].update(tickets_csv=str(t), survey_csv=str(s), db=str(tmp_path / "x.db"),
                        reports_dir=str(tmp_path / "rep"))
    summary = run_from_config(cfg)
    return summary, sqlite3.connect(cfg["paths"]["db"])


def T(tid, status="DA_DONG", closed="2026-03-10 09:00:00", center="1", tech="1"):
    return {"ticket_id": tid, "center_id": center, "technician_id": tech, "status": status,
            "created_at": "2026-03-01 08:00:00", "closed_at": closed}


def S(rid, tid, score="4", comment="", at="2026-03-11 10:00:00"):
    return {"response_id": rid, "ticket_id": tid, "score": score, "comment": comment, "responded_at": at}
