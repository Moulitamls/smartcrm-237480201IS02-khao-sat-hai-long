"""Cấu trúc bảng reject_rows: source_table, record_key, reason, detail."""
import pandas as pd

REJECT_COLUMNS = ["source_table", "record_key", "reason", "detail"]


def empty_rejects():
    return pd.DataFrame(columns=REJECT_COLUMNS)


def build_rejects(source_table, keys, reason, detail):
    out = pd.DataFrame({"source_table": source_table, "record_key": keys.astype(object),
                        "reason": reason, "detail": detail})
    return out[REJECT_COLUMNS].reset_index(drop=True)

