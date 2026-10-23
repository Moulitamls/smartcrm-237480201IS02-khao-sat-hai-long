"""Quy tắc chất lượng. Mỗi dòng chỉ bị ghi MỘT lý do: lý do đầu tiên vi phạm theo thứ tự."""
import pandas as pd
from .rejects import build_rejects, empty_rejects


class _Reasons:
    def __init__(self, index):
        self.reason = pd.Series(pd.NA, index=index, dtype=object)
        self.detail = pd.Series(pd.NA, index=index, dtype=object)

    def mark(self, mask, reason, detail):
        m = mask.fillna(False).astype(bool) & self.reason.isna()
        self.reason[m] = reason
        if isinstance(detail, pd.Series):
            self.detail[m] = detail[m]
        else:
            self.detail[m] = detail


def _split(df, r, source_table, key_col, fallback_prefix):
    bad = r.reason.notna()
    keys = df[key_col].where(df[key_col].notna(), pd.Series([f"{fallback_prefix}{i + 2}" for i in df.index], index=df.index))
    rejects = build_rejects(source_table, keys[bad], r.reason[bad], r.detail[bad]) if bad.any() else empty_rejects()
    return df[~bad].copy(), rejects


def check_tickets(df, closed_status):
    """Thứ tự: ticket_id_trong, ticket_id_trung, ngay_dong_khong_doc_duoc, da_dong_thieu_closed_at."""
    r = _Reasons(df.index)
    r.mark(df["ticket_id"].isna(), "ticket_id_trong", "ticket_id để trống")
    r.mark(df["ticket_id"].notna() & df["ticket_id"].duplicated(keep="first"),
           "ticket_id_trung", "mã phiếu đã xuất hiện ở dòng trước")
    r.mark(df["closed_at_invalid"], "ngay_dong_khong_doc_duoc", "closed_at có giá trị nhưng không đọc được")
    r.mark((df["status"] == closed_status) & df["closed_at"].isna(),
           "da_dong_thieu_closed_at", "phiếu Đã đóng nhưng closed_at trống")
    return _split(df, r, "stg_ticket", "ticket_id", "dong_")


def check_surveys(df, tickets_ok, closed_status, rules):
    """df cần các cột: response_id, ticket_id, score_int, comment, responded_at, responded_at_invalid.
    Thứ tự: score_ngoai_1_5, nhan_xet_qua_dai, ngay_tra_loi_khong_doc_duoc, phieu_chua_dong,
    tra_loi_truoc_ngay_dong, trung_phan_hoi (QT-10)."""
    r = _Reasons(df.index)
    lo, hi, max_len = rules["min_score"], rules["max_score"], rules["max_comment_len"]
    s = df["score_int"]
    r.mark(s.isna() | (s < lo) | (s > hi), "score_ngoai_1_5", "điểm không phải số nguyên trong khoảng cho phép")
    r.mark(df["comment"].fillna("").str.len() > max_len, "nhan_xet_qua_dai", f"nhận xét dài hơn {max_len} ký tự")
    r.mark(df["responded_at_invalid"], "ngay_tra_loi_khong_doc_duoc", "responded_at không đọc được")
    closed = tickets_ok[tickets_ok["status"] == closed_status].set_index("ticket_id")["closed_at"]
    r.mark(~df["ticket_id"].isin(closed.index), "phieu_chua_dong", "phiếu không tồn tại hoặc chưa đóng")
    closed_at = df["ticket_id"].map(closed)
    # So sánh theo NGÀY: nguồn có định dạng chỉ có ngày (dd/mm/yyyy), trả lời cùng ngày đóng là hợp lệ.
    r.mark(df["responded_at"].notna() & closed_at.notna()
           & (df["responded_at"].dt.normalize() < closed_at.dt.normalize()),
           "tra_loi_truoc_ngay_dong", "ngày trả lời sớm hơn ngày đóng phiếu")
    ok = r.reason.isna()
    dup = pd.Series(False, index=df.index)
    dup[ok] = df.loc[ok, "ticket_id"].duplicated(keep="first")
    r.mark(dup, "trung_phan_hoi", "phiếu đã có phản hồi trước đó (QT-10)")
    return _split(df, r, "stg_survey_response", "response_id", "dong_")

