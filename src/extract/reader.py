"""Tầng extract: đọc file CSV nguồn và thống kê số dòng, số cột, tỉ lệ ô trống."""
from pathlib import Path

import pandas as pd


def read_csv(path, required_columns, name):
    """Đọc CSV dưới dạng chuỗi (chưa ép kiểu) để tầng transform tự chuẩn hóa."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {path} ({name}). Đặt file CSV vào data/raw/ "
            "hoặc sửa đường dẫn trong config/config.yaml."
        )
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"{name}: thiếu cột {missing}. Cột hiện có: {list(df.columns)}. "
            "Sửa mục 'columns' trong config/config.yaml cho khớp file thật."
        )
    for col in df.columns:
        df[col] = df[col].str.strip().replace("", pd.NA)
    return df


def profile(df):
    """Trả về bảng: cột, số ô trống, tỉ lệ ô trống (%)."""
    empty = df.isna().sum()
    return pd.DataFrame(
        {
            "cot": df.columns,
            "so_o_trong": empty.values,
            "ti_le_trong_pct": (empty / max(len(df), 1) * 100).round(2).values,
        }
    )


def describe(df, name):
    """Thông tin để in ra màn hình: số dòng, số cột, bảng tỉ lệ ô trống."""
    return {
        "name": name,
        "rows": int(len(df)),
        "cols": int(df.shape[1]),
        "profile": profile(df),
    }
