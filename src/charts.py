"""Hai biểu đồ, mỗi biểu đồ gắn một câu hỏi phân tích; có mốc tham chiếu, nguồn và thời điểm dữ liệu."""
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

EMPTY_MESSAGE = ("Không có dữ liệu cho bộ lọc đã chọn. Hãy mở rộng khoảng ngày hoặc chọn thêm trung tâm; "
                 "tháng/kỹ thuật viên chưa có phản hồi được hiển thị là 'Chưa có dữ liệu', không phải 0 điểm.")


def _footer(fig, source, stamp):
    fig.text(0.01, 0.01, f"{source} · Dữ liệu cập nhật lúc {stamp}", fontsize=7, color="#555")


def chart_trend(df, ref_value, source, stamp):
    """Câu hỏi: Tỉ lệ CSAT toàn công ty theo tháng đang tăng hay giảm so với mức chung cả kỳ?"""
    d = df.dropna(subset=["csat_rate"])
    if d.empty:
        return None
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(d["year_month"], d["csat_rate"] * 100, marker="o", color="#1f6feb", label="CSAT theo tháng")
    if ref_value == ref_value and ref_value is not None:
        ax.axhline(ref_value * 100, ls="--", color="gray", label=f"Mốc tham chiếu: CSAT cả kỳ {ref_value * 100:.1f}%")
    ax.set_ylim(0, 100); ax.set_ylabel("Tỉ lệ CSAT (%) — điểm 4–5 / tổng phản hồi")
    ax.set_title("CSAT toàn công ty theo tháng có tăng hay giảm so với mức chung?", fontsize=10)
    ax.tick_params(axis="x", rotation=45); ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout(rect=(0, 0.04, 1, 1)); _footer(fig, source, stamp)
    return fig


def chart_technician(df, ref_value, source, stamp):
    """Câu hỏi: Kỹ thuật viên nào có điểm trung bình thấp hơn mức chung, và kết luận đó có đủ mẫu không?"""
    d = df.dropna(subset=["avg_score"])
    if d.empty:
        return None
    fig, ax = plt.subplots(figsize=(9, 4.4))
    colors = ["#b0b0b0" if s else "#1f6feb" for s in d["small_sample"]]
    ax.bar(range(len(d)), d["avg_score"], color=colors)
    ax.set_xticks(range(len(d))); ax.set_xticklabels([n.replace("Kỹ thuật viên ", "KTV ") for n in d["technician_name"]],
                                                       rotation=90, fontsize=7)
    if ref_value == ref_value and ref_value is not None:
        ax.axhline(ref_value, ls="--", color="red", label=f"Mốc tham chiếu: điểm TB toàn công ty {ref_value:.2f}")
    ax.set_ylim(0, 5); ax.set_ylabel("Điểm hài lòng trung bình (1–5)")
    ax.set_title("Kỹ thuật viên nào thấp hơn mức chung? (xám = mẫu nhỏ, kết luận kém chắc)", fontsize=10)
    h, _ = ax.get_legend_handles_labels()
    ax.legend(handles=h + [Patch(color="#b0b0b0", label="Mẫu nhỏ (dưới ngưỡng phản hồi)"),
                           Patch(color="#1f6feb", label="Đủ mẫu")], fontsize=8, loc="lower right")
    fig.tight_layout(rect=(0, 0.04, 1, 1)); _footer(fig, source, stamp)
    return fig


