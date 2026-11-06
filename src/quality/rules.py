"""Quy tắc chất lượng. Mỗi quy tắc là MỘT hàm check_* trả về mặt nạ (Series True/False):
True = dòng vi phạm. Hai hàm điều phối check_tickets / check_surveys gọi các quy tắc theo thứ tự;
mỗi dòng chỉ bị ghi MỘT lý do: lý do đầu tiên vi phạm theo thứ tự."""
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


# ---------- Quy tắc cho bảng phiếu (tickets) ----------

def check_ticket_id_trong(df):
    """QT phiếu 1: ticket_id không được để trống."""
    return df["ticket_id"].isna()


def check_ticket_id_trung(df):
    """QT phiếu 2: ticket_id không được trùng (giữ dòng đầu, loại các dòng sau)."""
    return df["ticket_id"].notna() & df["ticket_id"].duplicated(keep="first")


def check_closed_at_doc_duoc(df):
    """QT phiếu 3: closed_at có giá trị thì phải đọc được thành ngày."""
    return df["closed_at_invalid"]


def check_da_dong_co_closed_at(df, closed_status):
    """QT phiếu 4: phiếu Đã đóng thì closed_at không được trống."""
    return (df["status"] == closed_status) & df["closed_at"].isna()


# ---------- Quy tắc cho bảng phản hồi (survey_responses) ----------

def check_score_trong_khoang(df, lo, hi):
    """QT phản hồi 1: điểm phải là số nguyên trong [lo, hi]."""
    s = df["score_int"]
    return s.isna() | (s < lo) | (s > hi)


def check_nhan_xet_khong_qua_dai(df, max_len):
    """QT phản hồi 2: nhận xét không dài quá max_len ký tự."""
    return df["comment"].fillna("").str.len() > max_len


def check_responded_at_doc_duoc(df):
    """QT phản hồi 3: responded_at có giá trị thì phải đọc được thành ngày."""
    return df["responded_at_invalid"]


def check_phieu_da_dong(df, closed_ids):
    """QT phản hồi 4: phản hồi phải thuộc một phiếu tồn tại và đã đóng."""
    return ~df["ticket_id"].isin(closed_ids)


def check_tra_loi_sau_ngay_dong(df, closed_at):
    """QT phản hồi 5: ngày trả lời không sớm hơn ngày đóng phiếu.
    So sánh theo NGÀY: nguồn có định dạng chỉ có ngày (dd/mm/yyyy), trả lời cùng ngày đóng là hợp lệ."""
    return (df["responded_at"].notna() & closed_at.notna()
            & (df["responded_at"].dt.normalize() < closed_at.dt.normalize()))


def check_moi_phieu_mot_phan_hoi(df, ok):
    """QT phản hồi 6 (QT-10): mỗi phiếu chỉ một phản hồi. Chỉ xét các dòng đã qua các quy tắc trước (ok)."""
    dup = pd.Series(False, index=df.index)
    dup[ok] = df.loc[ok, "ticket_id"].duplicated(keep="first")
    return dup


# ---------- Hai hàm điều phối (giữ nguyên tên và kết quả trả về) ----------

def check_tickets(df, closed_status):
    """Thứ tự: ticket_id_trong, ticket_id_trung, ngay_dong_khong_doc_duoc, da_dong_thieu_closed_at."""
    r = _Reasons(df.index)
    r.mark(check_ticket_id_trong(df), "ticket_id_trong", "ticket_id để trống")
    r.mark(check_ticket_id_trung(df), "ticket_id_trung", "mã phiếu đã xuất hiện ở dòng trước")
    r.mark(check_closed_at_doc_duoc(df), "ngay_dong_khong_doc_duoc", "closed_at có giá trị nhưng không đọc được")
    r.mark(check_da_dong_co_closed_at(df, closed_status),
           "da_dong_thieu_closed_at", "phiếu Đã đóng nhưng closed_at trống")
    return _split(df, r, "stg_ticket", "ticket_id", "dong_")


def check_surveys(df, tickets_ok, closed_status, rules):
    """df cần các cột: response_id, ticket_id, score_int, comment, responded_at, responded_at_invalid.
    Thứ tự: score_ngoai_1_5, nhan_xet_qua_dai, ngay_tra_loi_khong_doc_duoc, phieu_chua_dong,
    tra_loi_truoc_ngay_dong, trung_phan_hoi (QT-10)."""
    r = _Reasons(df.index)
    lo, hi, max_len = rules["min_score"], rules["max_score"], rules["max_comment_len"]
    r.mark(check_score_trong_khoang(df, lo, hi), "score_ngoai_1_5", "điểm không phải số nguyên trong khoảng cho phép")
    r.mark(check_nhan_xet_khong_qua_dai(df, max_len), "nhan_xet_qua_dai", f"nhận xét dài hơn {max_len} ký tự")
    r.mark(check_responded_at_doc_duoc(df), "ngay_tra_loi_khong_doc_duoc", "responded_at không đọc được")
    closed = tickets_ok[tickets_ok["status"] == closed_status].set_index("ticket_id")["closed_at"]
    r.mark(check_phieu_da_dong(df, closed.index), "phieu_chua_dong", "phiếu không tồn tại hoặc chưa đóng")
    r.mark(check_tra_loi_sau_ngay_dong(df, df["ticket_id"].map(closed)),
           "tra_loi_truoc_ngay_dong", "ngày trả lời sớm hơn ngày đóng phiếu")
    r.mark(check_moi_phieu_mot_phan_hoi(df, r.reason.isna()), "trung_phan_hoi", "phiếu đã có phản hồi trước đó (QT-10)")
    return _split(df, r, "stg_survey_response", "response_id", "dong_")