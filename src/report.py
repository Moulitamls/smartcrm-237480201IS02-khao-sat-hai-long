"""Đối chiếu số dòng staging ↔ fact và ghi báo cáo chất lượng dạng markdown."""
from datetime import datetime
from pathlib import Path


def reconcile(stg_ticket, fact_rows, rejected_tickets, open_tickets, stg_survey, survey_in_fact, rejected_surveys):
    """stg_ticket = fact + phiếu bị loại + phiếu chưa đóng; stg_survey = phản hồi vào fact + phản hồi bị loại."""
    return {
        "stg_ticket": stg_ticket, "fact_rows": fact_rows,
        "rejected_tickets": rejected_tickets, "open_tickets": open_tickets,
        "ticket_check": stg_ticket == fact_rows + rejected_tickets + open_tickets,
        "stg_survey": stg_survey, "survey_in_fact": survey_in_fact,
        "rejected_surveys": rejected_surveys,
        "survey_check": stg_survey == survey_in_fact + rejected_surveys,
    }


def write_quality_report(summary, reports_dir, prefix="chatluong"):
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = Path(reports_dir) / f"{prefix}-{today}.md"
    rc = summary["reconcile"]
    L = [f"# Báo cáo chất lượng dữ liệu — {summary['finished_at']}", "",
         "## 1. Nguồn", "", "| Nguồn | Số dòng | Số cột |", "|---|---|---|"]
    for p in summary["profiles"]:
        L.append(f"| {p['name']} | {p['rows']} | {p['cols']} |")
    L += ["", "## 2. Đối chiếu staging ↔ fact", "",
          "| Chỉ số | Giá trị |", "|---|---|",
          f"| Dòng stg_ticket | {rc['stg_ticket']} |",
          f"| − Phiếu bị loại (reject_rows) | {rc['rejected_tickets']} |",
          f"| − Phiếu chưa đóng (không thuộc grain của fact) | {rc['open_tickets']} |",
          f"| = Dòng fact_survey | {rc['fact_rows']} |",
          f"| Khớp công thức | {'ĐẠT' if rc['ticket_check'] else 'LỆCH — cần điều tra'} |",
          f"| Dòng stg_survey_response | {rc['stg_survey']} |",
          f"| − Phản hồi bị loại | {rc['rejected_surveys']} |",
          f"| = Phản hồi nằm trong fact (has_response=1) | {rc['survey_in_fact']} |",
          f"| Khớp công thức | {'ĐẠT' if rc['survey_check'] else 'LỆCH — cần điều tra'} |",
          "", "## 3. Dòng bị loại theo lý do", "", "| Bảng | Lý do | Số dòng |", "|---|---|---|"]
    for (tbl, reason), n in summary["reject_counts"].items():
        L.append(f"| {tbl} | {reason} | {n} |")
    if not summary["reject_counts"]:
        L.append("| — | không có dòng bị loại | 0 |")
    L += ["", "## 4. Lô nạp fact theo ngày", "",
          f"Số lô: {len(summary['batches'])}; tổng dòng ghi: {sum(n for _, n in summary['batches'])}.", ""]
    path.write_text("\n".join(L), encoding="utf-8")
    return str(path)


