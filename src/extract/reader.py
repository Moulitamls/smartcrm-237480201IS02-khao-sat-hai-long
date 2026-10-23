"""Đọc nguồn CSV, kiểm tra cột bắt buộc, thống kê ô trống."""
import pandas as pd


class MissingColumnsError(ValueError):
    pass


def read_csv(path, required, name="csv"):
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise MissingColumnsError(
            f"{name}: thiếu cột bắt buộc {missing}; file có các cột {list(df.columns)}")
    for c in df.columns:
        df[c] = df[c].str.strip().replace("", pd.NA)
    return df


def profile(df, name):
    return {"name": name, "rows": len(df), "cols": df.shape[1],
            "null_pct": (df.isna().mean() * 100).round(2).to_dict()}


def print_profile(p):
    print(f"[extract] {p['name']}: {p['rows']} dòng, {p['cols']} cột")
    for col, pct in p["null_pct"].items():
        if pct > 0:
            print(f"          ô trống {col}: {pct}%")

