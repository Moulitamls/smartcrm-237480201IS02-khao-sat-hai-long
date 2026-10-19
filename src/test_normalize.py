import pandas as pd

from src.pipeline import load_config
from src.transform.normalize import normalize_datetime_column, normalize_responses, parse_datetime

CFG = load_config("config/config.yaml")
FORMATS = CFG["date_formats"]


def test_parse_ba_dinh_dang_ngay():
    expected = pd.Timestamp("2026-09-15 10:30:00")
    assert parse_datetime("2026-09-15 10:30:00", FORMATS) == expected
    assert parse_datetime("15/09/2026 10:30", FORMATS) == expected
    assert parse_datetime("2026-09-15T10:30:00", FORMATS) == expected


def test_parse_ngay_khong_doc_duoc_tra_nat():
    assert pd.isna(parse_datetime("khong-phai-ngay", FORMATS))
    assert pd.isna(parse_datetime("31/02/2026", FORMATS))  # ngày không tồn tại
    assert pd.isna(parse_datetime(pd.NA, FORMATS))


def test_cot_ngay_phan_biet_trong_va_loi():
    s = pd.Series(["2026-09-15", None, "abc"], dtype="string")
    parsed, bad = normalize_datetime_column(s, FORMATS)
    assert list(bad) == [False, False, True]  # ô trống hợp lệ, "abc" là lỗi
    assert parsed.isna().tolist() == [False, True, True]


def test_score_phai_la_so_nguyen():
    df = pd.DataFrame(
        {
            "response_id": ["1", "2", "3"],
            "ticket_id": ["10", "11", "12"],
            "score": ["4", "3.5", "x"],
            "comment": [None, None, None],
            "responded_at": ["2026-09-15"] * 3,
        }
    )
    clean, rejects = normalize_responses(df, CFG)
    assert clean["response_id"].tolist() == [1]
    assert set(rejects["reason"]) == {"score_khong_phai_so_nguyen"}
    assert len(rejects) == 2
