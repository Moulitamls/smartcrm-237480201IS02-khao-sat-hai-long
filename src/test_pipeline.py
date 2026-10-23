from src.conftest import T, S, run_pipeline

def test_pipeline_chay_tron_ven_bang_mot_lenh_tren_du_lieu_nho(cfg, tmp_path):
    tk = [T("T1"), T("T2", status="HOAN_TAT", closed=""), T("T3", closed="05/03/2026")]
    summary, c = run_pipeline(cfg, tmp_path, tk, [S("r1", "T1", "4"), S("r2", "T3", "5", at="06-03-2026")])
    assert c.execute("SELECT COUNT(*) FROM fact_survey").fetchone()[0] == 2
    assert c.execute("SELECT COUNT(*) FROM reject_rows").fetchone()[0] == 0
    assert (tmp_path / "rep").exists() and summary["report_path"].endswith(".md")

