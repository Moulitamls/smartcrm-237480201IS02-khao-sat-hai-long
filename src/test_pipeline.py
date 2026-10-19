import sqlite3
from pathlib import Path

from src.pipeline import load_config, run

TICKETS = """ticket_id,center_id,technician_id,status,closed_at
1,1,1,DA_DONG,2026-09-01 09:00:00
2,1,2,DA_DONG,02/09/2026 10:00
3,2,3,DA_DONG,2026-09-03
4,2,3,DANG_XU_LY,
5,1,1,DA_DONG,ngay-hong
"""
RESPONSES = """response_id,ticket_id,score,comment,responded_at
1,1,5,Tốt,2026-09-03 08:00:00
2,2,2,Sửa lâu,05/09/2026 12:00
3,4,4,,2026-09-06
"""


def test_pipeline_chay_mot_lenh(tmp_path):
    (tmp_path / "t.csv").write_text(TICKETS, encoding="utf-8")
    (tmp_path / "s.csv").write_text(RESPONSES, encoding="utf-8")
    cfg = load_config("config/config.yaml")
    cfg["paths"].update(
        tickets_csv=str(tmp_path / "t.csv"),
        survey_csv=str(tmp_path / "s.csv"),
        database=str(tmp_path / "csat.db"),
        report_dir=str(tmp_path / "reports"),
        ddl=str(Path("db/star_schema.sql")),
    )
    stats = run(cfg, echo=lambda *_: None)

    conn = sqlite3.connect(tmp_path / "csat.db")
    # 3 phiếu đóng hợp lệ (1, 2, 3); phiếu 5 có ngày hỏng nên bị loại
    assert conn.execute("select count(*) from fact_survey").fetchone()[0] == 3
    assert conn.execute("select count(*) from fact_survey where has_response=1").fetchone()[0] == 2
    assert conn.execute("select score, is_satisfied from fact_survey where ticket_id=2").fetchone() == (2, 0)
    assert conn.execute("select response_delay_days from fact_survey where ticket_id=1").fetchone()[0] == 2
    reasons = {r[0] for r in conn.execute("select reason from reject_rows")}
    assert reasons == {"ngay_dong_khong_doc_duoc", "phieu_chua_da_dong"}
    assert abs(stats["response_rate"] - 2 / 3 * 100) < 1e-6
    assert list((tmp_path / "reports").glob("chat-luong-*.md"))

    # chạy lại lần hai vẫn cho cùng kết quả (idempotent)
    run(cfg, echo=lambda *_: None)
    assert conn.execute("select count(*) from fact_survey").fetchone()[0] == 3
    conn.close()
