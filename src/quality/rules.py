"""Tầng quality: kiểm tra các quy tắc chất lượng ở Chương 4 (mục 3.3 của báo cáo).
Mỗi dòng chỉ bị ghi một lý do: lý do đầu tiên vi phạm theo thứ tự các quy tắc."""
import pandas as pd

from src.quality.rejects import build_rejects, empty_rejects


def _apply_reasons(df, rules):
    """rules: danh sách (tên lý do, mặt nạ vi phạm). Trả về Series lý do đầu tiên của từng dòng."""
    reason = pd.Series(pd.NA, index=df.index, dtype="string")
    for name, mask in rules:
        reason = reason.where(reason.notna(), pd.Series(name, index=df.index).where(mask))
    return reason


def check_tickets(tickets, cfg):
    """Trả về (phiếu hợp lệ, bảng reject)."""
    rules = cfg["rules"]
    dup = tickets["ticket_id"].duplicated(keep="first")
    closed_without_time = (tickets["status"] == rules["closed_status"]) & tickets["closed_at"].isna()
    reason = _apply_reasons(
        tickets,
        [("ticket_id_trung", dup), ("da_dong_thieu_closed_at", closed_without_time)],
    )
    bad = reason.notna()
    rejects = [empty_rejects()]
    for name in reason[bad].unique():
        rows = tickets[reason == name]
        rejects.append(build_rejects(rows, "ticket", "ticket_id", name))
    return tickets[~bad].reset_index(drop=True), pd.concat(rejects, ignore_index=True)


def check_responses(responses, tickets_valid, cfg):
    """Trả về (phản hồi hợp lệ, bảng reject). tickets_valid là phiếu đã qua check_tickets."""
    rules = cfg["rules"]
    info = tickets_valid.drop_duplicates("ticket_id").set_index("ticket_id")
    status = responses["ticket_id"].map(info["status"])
    closed_at = responses["ticket_id"].map(info["closed_at"])
    comment_len = responses["comment"].fillna("").str.len()

    rules_list = [
        ("score_ngoai_khoang", ~responses["score"].between(rules["score_min"], rules["score_max"])),
        ("nhan_xet_qua_dai", comment_len > rules["comment_max_len"]),
        ("ticket_khong_ton_tai", status.isna()),
        ("phieu_chua_da_dong", status.notna() & (status != rules["closed_status"])),
        ("phan_hoi_truoc_ngay_dong", closed_at.notna() & (responses["responded_at"] < closed_at)),
        ("response_id_trung", responses["response_id"].duplicated(keep="first")),
    ]
    reason = _apply_reasons(responses, rules_list)

    # Mỗi phiếu chỉ một phản hồi (QT-10): giữ phản hồi đến sớm nhất, loại các bản còn lại.
    ok = responses[reason.isna()].sort_values("responded_at")
    dup_ticket_idx = ok.index[ok["ticket_id"].duplicated(keep="first")]
    reason.loc[dup_ticket_idx] = "ticket_id_trung_phan_hoi"

    bad = reason.notna()
    rejects = [empty_rejects()]
    for name in reason[bad].unique():
        rows = responses[reason == name]
        rejects.append(build_rejects(rows, "survey_response", "response_id", name))
    valid = responses[~bad].reset_index(drop=True)
    return valid, pd.concat(rejects, ignore_index=True)
