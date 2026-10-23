import pandas as pd
from tests.conftest import T, S, run_pipeline
from src.dashboard import queries as q


def test_csat_va_ty_le_phan_hoi_tinh_dung(cfg, tmp_path):               # luồng đúng
    tk = [T(f"T{i}") for i in range(1, 5)]
    sv = [S("r1", "T1", "5"), S("r2", "T2", "4"), S("r3", "T3", "2")]    # T4 chưa phản hồi
    _, c = run_pipeline(cfg, tmp_path, tk, sv)
    ov = q.overall(c, q.Filters())
    assert round(ov["avg_score"], 2) == 3.67 and round(ov["csat_rate"], 2) == 0.67 and ov["response_rate"] == 0.75


def test_ky_khong_co_phan_hoi_khong_hien_0_diem_va_bo_loc_rong(cfg, tmp_path):   # dữ liệu sai / rỗng
    _, c = run_pipeline(cfg, tmp_path, [T("T1"), T("T2")], [])           # có phiếu đóng nhưng chưa ai phản hồi
    ov = q.overall(c, q.Filters())
    assert ov["n_closed"] == 2 and pd.isna(ov["avg_score"]) and ov["response_rate"] == 0
    assert q.fmt_avg(ov["avg_score"]) == "Chưa có dữ liệu" and q.fmt_pct(ov["csat_rate"]) == "Chưa có dữ liệu"
    assert q.q3_trend(c, q.Filters(date_from="2030-01-01")).empty        # bộ lọc không khớp → rỗng


def test_bien_mau_nho_9_phan_hoi_co_co_10_thi_khong(cfg, tmp_path):     # biên
    tk = [T(f"A{i}", tech="1") for i in range(9)] + [T(f"B{i}", tech="2") for i in range(10)]
    sv = [S(f"ra{i}", f"A{i}") for i in range(9)] + [S(f"rb{i}", f"B{i}") for i in range(10)]
    _, c = run_pipeline(cfg, tmp_path, tk, sv)
    df = q.q2_technician(c, q.Filters(), small_sample=10).set_index("technician_name")
    assert bool(df.loc["Kỹ thuật viên 1", "small_sample"]) is True
    assert bool(df.loc["Kỹ thuật viên 2", "small_sample"]) is False


def test_phan_hoi_diem_thap_kem_nhan_xet(cfg, tmp_path):
    sv = [S("r1", "T1", "2", "Sửa lâu quá"), S("r2", "T2", "3")]
    _, c = run_pipeline(cfg, tmp_path, [T("T1"), T("T2")], sv)
    low = q.q4_low_scores(c, q.Filters())
    assert low["ticket_id"].tolist() == ["T1"] and low["comment"].iloc[0] == "Sửa lâu quá"
