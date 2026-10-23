import pandas as pd
from src.transform.normalize import parse_datetime, normalize_datetime_column, parse_score

FMT = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]


def test_ba_dinh_dang_ngay_cho_cung_mot_ngay():                      # luồng đúng
    got = {parse_datetime(v, FMT).date().isoformat() for v in ["2026-03-05", "05/03/2026", "05-03-2026"]}
    assert got == {"2026-03-05"}


def test_ngay_khong_doc_duoc_tra_ve_NaT():                           # dữ liệu sai
    assert pd.isna(parse_datetime("31/02/2026", FMT)) and pd.isna(parse_datetime("không phải ngày", FMT))


def test_cot_ngay_phan_biet_o_trong_va_o_loi():                      # biên
    parsed, invalid = normalize_datetime_column(pd.Series(["2026-03-05", None, "", "abc"]), FMT)
    assert invalid.tolist() == [False, False, False, True]
    assert parsed.isna().tolist() == [False, True, True, True]


def test_diem_phai_la_so_nguyen():
    assert parse_score("4") == 4 and parse_score("4.0") == 4
    assert parse_score("4.5") is None and parse_score("abc") is None and parse_score(None) is None


