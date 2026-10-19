import pandas as pd

from src.pipeline import load_config
from src.quality.rules import check_responses, check_tickets

CFG = load_config("config/config.yaml")
T = pd.Timestamp


def _tickets():
    return pd.DataFrame(
        {
            "ticket_id": pd.array([1, 2, 3, 3], dtype="Int64"),
            "center_id": pd.array([1, 1, 2, 2], dtype="Int64"),
            "technician_id": pd.array([1, 1, 2, 2], dtype="Int64"),
            "status": ["DA_DONG", "DANG_XU_LY", "DA_DONG", "DA_DONG"],
            "closed_at": [T("2026-09-01"), pd.NaT, pd.NaT, T("2026-09-02")],
        }
    )


def test_phieu_da_dong_thieu_closed_at_va_trung_ma():
    valid, rejects = check_tickets(_tickets(), CFG)
    assert valid["ticket_id"].tolist() == [1, 2]
    assert set(rejects["reason"]) == {"ticket_id_trung", "da_dong_thieu_closed_at"}


def _responses(rows):
    return pd.DataFrame(
        rows, columns=["response_id", "ticket_id", "score", "comment", "responded_at"]
    ).astype({"response_id": "Int64", "ticket_id": "Int64", "score": "Int64"})


def test_cac_quy_tac_phan_hoi():
    tickets, _ = check_tickets(_tickets(), CFG)
    resp = _responses(
        [
            (1, 1, 5, None, T("2026-09-03")),        # hợp lệ
            (2, 1, 4, None, T("2026-09-04")),        # trùng phiếu 1 (QT-10)
            (3, 2, 4, None, T("2026-09-03")),        # phiếu chưa đóng
            (4, 99, 4, None, T("2026-09-03")),       # phiếu không tồn tại
            (5, 1, 9, None, T("2026-09-03")),        # điểm ngoài 1-5
            (6, 1, 4, "x" * 501, T("2026-09-03")),   # nhận xét quá 500 ký tự
            (7, 1, 4, None, T("2026-08-30")),        # trả lời trước ngày đóng
        ]
    )
    valid, rejects = check_responses(resp, tickets, CFG)
    assert valid["response_id"].tolist() == [1]
    reasons = dict(zip(rejects["record_key"], rejects["reason"]))
    assert reasons == {
        "2": "ticket_id_trung_phan_hoi",
        "3": "phieu_chua_da_dong",
        "4": "ticket_khong_ton_tai",
        "5": "score_ngoai_khoang",
        "6": "nhan_xet_qua_dai",
        "7": "phan_hoi_truoc_ngay_dong",
    }
