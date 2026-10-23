from tests.conftest import T, S, run_pipeline
from src.pipeline import run_from_config


def test_nap_lan_hai_khong_nhan_doi_dong(cfg, tmp_path):                # luồng đúng
    tk = [T("T1"), T("T2", center="2", tech="2")]
    sv = [S("r1", "T1", "5")]
    _, c = run_pipeline(cfg, tmp_path, tk, sv)
    before = {t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("fact_survey", "dim_center", "dim_technician", "dim_date")}
    run_from_config(cfg)                                                 # nạp lần hai
    after = {t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in before}
    assert before == after and before["fact_survey"] == 2


def test_thieu_ky_thuat_vien_vao_dong_khong_xac_dinh(cfg, tmp_path):    # biên: không mất dòng fact
    tk = [T("T1", tech=""), T("T2", center="")]
    _, c = run_pipeline(cfg, tmp_path, tk, [])
    rows = c.execute("SELECT technician_key, center_key FROM fact_survey ORDER BY ticket_id").fetchall()
    assert rows == [(-1, 1), (1, -1)]


def test_doi_chieu_staging_bang_fact_cong_loai_cong_chua_dong(cfg, tmp_path):
    tk = [T("T1"), T("T1"), T("T2", status="DANG_XU_LY", closed=""), T("T3", closed="")]
    summary, _ = run_pipeline(cfg, tmp_path, tk, [S("r1", "T1"), S("r2", "TX")])
    rc = summary["reconcile"]
    assert (rc["stg_ticket"], rc["fact_rows"], rc["rejected_tickets"], rc["open_tickets"]) == (4, 1, 2, 1)
    assert rc["ticket_check"] and rc["survey_check"]
