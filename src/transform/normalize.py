"""Chuẩn hoá ngày (nhiều định dạng) và ép kiểu điểm số nguyên."""
from datetime import datetime
import pandas as pd


def parse_datetime(value, formats):
    """Trả về Timestamp, hoặc NaT nếu trống / không đọc được."""
    if value is None or pd.isna(value):
        return pd.NaT
    s = str(value).strip()
    if not s:
        return pd.NaT
    for fmt in formats:
        try:
            return pd.Timestamp(datetime.strptime(s, fmt))
        except ValueError:
            continue
    return pd.NaT


def normalize_datetime_column(series, formats):
    """Trả về (cột đã chuẩn hoá, mask ô CÓ giá trị nhưng không đọc được).
    Ô trống giữ nguyên NaT và KHÔNG bị đánh dấu lỗi."""
    blank = series.isna() | (series.astype(str).str.strip() == "")
    parsed = pd.to_datetime(series.map(lambda v: parse_datetime(v, formats)), errors="coerce")
    invalid = (~blank) & parsed.isna()
    return parsed, invalid


def parse_score(value):
    """'4' -> 4, '4.0' -> 4, '4.5' / 'abc' / trống -> None."""
    if value is None or pd.isna(value):
        return None
    try:
        f = float(str(value).strip().replace(",", "."))
    except ValueError:
        return None
    return int(f) if f.is_integer() else None


def to_int_score_column(series):
    return series.map(parse_score).astype("Int64")

