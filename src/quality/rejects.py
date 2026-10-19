"""Cấu trúc chung của bảng reject_rows: dòng nào bị loại, từ bảng nào, vì lý do gì."""
import pandas as pd

REJECT_COLUMNS = ["source_table", "record_key", "reason", "detail"]


def empty_rejects():
    return pd.DataFrame(columns=REJECT_COLUMNS)


def build_rejects(rows, source_table, key_col, reason, detail_col=None):
    """Tạo bảng reject từ các dòng bị loại (rows là DataFrame gốc, chưa chuẩn hóa)."""
    if rows is None or len(rows) == 0:
        return empty_rejects()
    detail = rows[detail_col].astype("string") if detail_col else pd.Series(pd.NA, index=rows.index, dtype="string")
    return pd.DataFrame(
        {
            "source_table": source_table,
            "record_key": rows[key_col].astype("string").values,
            "reason": reason,
            "detail": detail.values,
        }
    )
