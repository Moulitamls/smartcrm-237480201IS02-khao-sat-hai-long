from tests.conftest import T, S, run_pipeline


def reasons(conn):
    return dict(conn.execute("SELECT record_key, reason FROM reject_rows").fetchall())


def test_phieu_dong_thieu_closed_at_va_trung_ma(cfg, tmp_path):        # dữ liệu sai
    _, c = run_pipeline(cfg, tmp_path, [T("A"), T("A"), T("B", closed=""), T("C", closed="31/02/2026")], [])
    r = reasons(c)
    assert r == {"A": "ticket_id_trung", "B": "da_dong_thieu_closed_at", "C": "ngay_dong_khong_doc_duoc"}


def test_bien_diem_1_va_5_hop_le_0_va_6_bi_loai(cfg, tmp_path):        # biên
    tk = [T(f"T{i}") for i in range(4)]
    sv = [S("r0", "T0", "1"), S("r1", "T1", "5"), S("r2", "T2", "0"), S("r3", "T3", "6")]
    _, c = run_pipeline(cfg, tmp_path, tk, sv)
    assert reasons(c) == {"r2": "score_ngoai_1_5", "r3": "score_ngoai_1_5"}
    assert c.execute("SELECT COUNT(*) FROM fact_survey WHERE has_response=1").fetchone()[0] == 2


def test_bien_nhan_xet_500_hop_le_501_bi_loai(cfg, tmp_path):          # biên
    sv = [S("r1", "T1", comment="x" * 500), S("r2", "T2", comment="x" * 501)]
    _, c = run_pipeline(cfg, tmp_path, [T("T1"), T("T2")], sv)
    assert reasons(c) == {"r2": "nhan_xet_qua_dai"}


def test_phan_hoi_phieu_chua_dong_va_tra_loi_truoc_ngay_dong(cfg, tmp_path):   # ngoại lệ QT-10
    tk = [T("T1"), T("T2", status="DANG_XU_LY", closed=""), T("T3")]
    sv = [S("r1", "T2"), S("r2", "T3", at="2026-03-09"), S("r3", "T1", at="2026-03-10")]  # r3: cùng ngày đóng → hợp lệ
    _, c = run_pipeline(cfg, tmp_path, tk, sv)
    assert reasons(c) == {"r1": "phieu_chua_dong", "r2": "tra_loi_truoc_ngay_dong"}


def test_moi_phieu_mot_phan_hoi(cfg, tmp_path):                         # QT-10
    sv = [S("r1", "T1", "5"), S("r2", "T1", "1")]
    _, c = run_pipeline(cfg, tmp_path, [T("T1")], sv)
    assert reasons(c) == {"r2": "trung_phan_hoi"}
    assert c.execute("SELECT score FROM fact_survey").fetchone()[0] == 5

