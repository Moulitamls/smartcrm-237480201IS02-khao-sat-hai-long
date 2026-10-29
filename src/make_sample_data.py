"""Sinh dữ liệu MẪU (seed cố định) khi chưa có CSV thật: python -m src.make_sample_data
Quy mô theo Chương 4: 7.800 phiếu, 6.350 phiếu Đã đóng, ~2.600 phản hồi; có chủ ý chèn dòng lỗi
để kiểm tra bảng reject_rows. KHÔNG dùng để thay thế lần chạy trên CSV thật khi nộp bài.
Ghi ra data/raw/demo_tickets.csv và demo_survey.csv (KHÔNG ghi đè CSV thật); chạy bằng src/config.demo.yaml."""
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

random.seed(42)
OUT = Path("data/raw"); OUT.mkdir(parents=True, exist_ok=True)
N, N_CLOSED, N_RESP = 7800, 6350, 2600
STATUSES = ["DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN", "HOAN_TAT"]
LOW_COMMENTS = ["Sửa lâu quá", "Nhân viên thiếu nhiệt tình", "Máy vẫn còn lỗi", "Phải quay lại nhiều lần"]


def fmt(dt, style):
    return dt.strftime({0: "%Y-%m-%d %H:%M:%S", 1: "%d/%m/%Y", 2: "%d-%m-%Y"}[style])


def rnd_style():
    return random.choices([0, 1, 2], weights=[70, 20, 10])[0]


start = datetime(2025, 10, 1)
tech_w = [random.choice([1, 1, 2, 3, 6]) for _ in range(38)]      # có KTV ít phản hồi → "mẫu nhỏ"
for _k in (3, 17, 25, 33):
    tech_w[_k] = 0.05                                             # 4 KTV rất ít phiếu
tech_bias = [random.choice([-0.6, -0.3, 0, 0, 0.2]) for _ in range(38)]
rows, closed_ids = [], []
for i in range(1, N + 1):
    created = start + timedelta(days=random.randint(0, 340), hours=random.randint(7, 17), minutes=random.randint(0, 59))
    closed = i <= N_CLOSED
    tech = random.choices(range(1, 39), weights=tech_w)[0]
    tid = f"MK-{i:06d}/2026"
    cl = created + timedelta(days=random.randint(1, 14), hours=random.randint(0, 5)) if closed else None
    st = style = rnd_style()
    rows.append({"ticket_id": tid, "center_id": random.randint(1, 6), "technician_id": tech,
                 "status": "DA_DONG" if closed else random.choice(STATUSES),
                 "created_at": fmt(created, st), "closed_at": fmt(cl, style) if cl else ""})
    if closed:
        closed_ids.append((tid, cl, tech))
random.shuffle(rows)
tickets = pd.DataFrame(rows)

picked = random.sample(closed_ids, N_RESP)
resp = []
for k, (tid, cl, tech) in enumerate(picked, 1):
    base = random.choices([1, 2, 3, 4, 5], weights=[5, 8, 17, 35, 35])[0]
    score = min(5, max(1, round(base + tech_bias[tech - 1] + random.choice([0, 0, 1, -1]) * 0)))
    rt = cl + timedelta(days=random.randint(0, 7), hours=random.randint(1, 20))
    resp.append({"response_id": f"R{k:05d}", "ticket_id": tid, "score": str(score),
                 "comment": random.choice(LOW_COMMENTS) if score <= 2 else "", "responded_at": fmt(rt, rnd_style())})
survey = pd.DataFrame(resp)

# ---- chèn dòng lỗi có chủ ý ----
dup = tickets.sample(5, random_state=1).copy(); tickets = pd.concat([tickets, dup], ignore_index=True)
closed_idx = tickets.index[(tickets.status == "DA_DONG")][:3]; tickets.loc[closed_idx, "closed_at"] = ""
bad_idx = tickets.index[(tickets.status == "DA_DONG")][10:14]; tickets.loc[bad_idx, "closed_at"] = "31/02/2026"
survey.loc[survey.sample(3, random_state=2).index, "score"] = ["0", "7", "abc"]
survey.loc[survey.sample(3, random_state=3).index, "comment"] = "x" * 600
survey.loc[survey.sample(4, random_state=4).index, "responded_at"] = "2020-01-01"
survey = pd.concat([survey, survey.sample(5, random_state=5).assign(response_id=lambda d: "D" + d.response_id)], ignore_index=True)
open_ticket = tickets[tickets.status != "DA_DONG"].ticket_id.iloc[0]
survey = pd.concat([survey, pd.DataFrame([{"response_id": "X00001", "ticket_id": open_ticket, "score": "5",
                                           "comment": "", "responded_at": "2026-08-01"}])], ignore_index=True)

tickets.to_csv(OUT / "demo_tickets.csv", index=False, encoding="utf-8")
survey.to_csv(OUT / "demo_survey.csv", index=False, encoding="utf-8")
print(f"Đã sinh {len(tickets)} phiếu và {len(survey)} phản hồi (DỮ LIỆU MẪU) vào {OUT}/")

