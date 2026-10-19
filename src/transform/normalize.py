"""Tầng transform: chuẩn hóa kiểu dữ liệu. Dòng không quy đổi được đưa vào bảng reject."""
import pandas as pd

from src.quality.rejects import build_rejects


def parse_datetime(value, formats):
    """Quy đổi một giá trị ngày về Timestamp theo danh sách định dạng; không được thì trả NaT."""
    if pd.isna(value):
        return pd.NaT
    text = str(value).strip()
    for fmt in formats:
        try:
            return pd.to_datetime(text, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT


def normalize_datetime_column(series, formats):
    """Trả về (cột đã quy đổi, mặt nạ các dòng có giá trị nhưng không đọc được)."""
    parsed = pd.to_datetime(series.map(lambda v: parse_datetime(v, formats)))
    unparseable = series.notna() & parsed.isna()
    return parsed, unparseable


def _to_int(series):
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def normalize_tickets(df, cfg):
    """Chuẩn hóa bảng phiếu. Trả về (bảng sạch, bảng reject)."""
    out = df.copy()
    out["ticket_id"] = _to_int(out["ticket_id"])
    out["center_id"] = _to_int(out["center_id"])
    out["technician_id"] = _to_int(out["technician_id"])
    out["status"] = out["status"].str.upper()
    out["closed_at"], bad_date = normalize_datetime_column(out["closed_at"], cfg["date_formats"])

    bad_id = out[["ticket_id", "center_id", "technician_id"]].isna().any(axis=1)
    rejects = [
        build_rejects(df[bad_id], "ticket", "ticket_id", "id_khong_hop_le"),
        build_rejects(df[bad_date & ~bad_id], "ticket", "ticket_id", "ngay_dong_khong_doc_duoc", "closed_at"),
    ]
    keep = ~(bad_id | bad_date)
    return out[keep].reset_index(drop=True), pd.concat(rejects, ignore_index=True)


def normalize_responses(df, cfg):
    """Chuẩn hóa bảng phản hồi. Trả về (bảng sạch, bảng reject)."""
    out = df.copy()
    out["response_id"] = _to_int(out["response_id"])
    out["ticket_id"] = _to_int(out["ticket_id"])
    score = pd.to_numeric(out["score"], errors="coerce")
    score = score.where(score == score.round())  # điểm phải là số nguyên
    out["score"] = score.astype("Int64")
    out["responded_at"], bad_date = normalize_datetime_column(out["responded_at"], cfg["date_formats"])

    bad_id = out[["response_id", "ticket_id"]].isna().any(axis=1)
    bad_score = out["score"].isna() & ~bad_id
    rejects = [
        build_rejects(df[bad_id], "survey_response", "response_id", "id_khong_hop_le"),
        build_rejects(df[bad_score], "survey_response", "response_id", "score_khong_phai_so_nguyen", "score"),
        build_rejects(
            df[bad_date & ~bad_id & ~bad_score], "survey_response", "response_id",
            "ngay_tra_loi_khong_doc_duoc", "responded_at",
        ),
    ]
    keep = ~(bad_id | bad_score | bad_date)
    return out[keep].reset_index(drop=True), pd.concat(rejects, ignore_index=True)
