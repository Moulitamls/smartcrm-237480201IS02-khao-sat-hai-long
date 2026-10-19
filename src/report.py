"""Ghi báo cáo chất lượng dữ liệu (markdown) sau mỗi lần chạy pipeline."""
from datetime import datetime
from pathlib import Path


def write_report(report_dir, stats):
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    path = Path(report_dir) / f"chat-luong-{datetime.now():%Y%m%d}.md"
    lines = [
        f"# Báo cáo chất lượng dữ liệu CSAT ({datetime.now():%d/%m/%Y %H:%M})",
        "",
        "## Số dòng trước và sau",
        "",
        "| Bảng | Dòng đọc | Dòng bị loại | Dòng hợp lệ |",
        "|---|---|---|---|",
    ]
    for t in stats["tables"]:
        lines.append(f"| {t['name']} | {t['read']} | {t['rejected']} | {t['valid']} |")
    lines += [
        "",
        f"Tỉ lệ phản hồi: {stats['responses_valid']} / {stats['closed_tickets']} "
        f"phiếu đã đóng = {stats['response_rate']:.1f}%",
        f"fact_survey: {stats['fact_rows']} dòng",
        "",
        "## Lý do bị loại",
        "",
    ]
    if stats["reject_by_reason"]:
        lines += ["| Bảng | Lý do | Số dòng |", "|---|---|---|"]
        lines += [f"| {s} | {r} | {n} |" for (s, r), n in stats["reject_by_reason"].items()]
    else:
        lines.append("Không có dòng nào bị loại.")
    lines += ["", "## Tỉ lệ ô trống từng cột (dữ liệu nguồn)", ""]
    for prof in stats["profiles"]:
        lines += [f"### {prof['name']} ({prof['rows']} dòng, {prof['cols']} cột)", "",
                  "| Cột | Số ô trống | Tỉ lệ (%) |", "|---|---|---|"]
        for _, r in prof["profile"].iterrows():
            lines.append(f"| {r['cot']} | {r['so_o_trong']} | {r['ti_le_trong_pct']} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
