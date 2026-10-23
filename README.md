# Smart CRM Mekong Mobile – Khảo sát hài lòng CSAT (L8, Track DA)

Sinh viên: MOONLASING Moulita · MSSV 237480201IS02 · GVHD: ThS. Nguyễn Minh Tân

## 1. Giới thiệu

Pipeline dữ liệu cho luồng L8: đọc `tickets_history.csv` và `survey_responses.csv`, chuẩn hóa, kiểm tra chất lượng, rồi nạp vào kho dữ liệu dạng star schema (`fact_survey` và 3 bảng dimension) để tính CSAT theo trung tâm, kỹ thuật viên và tháng. Sprint 2 bổ sung nạp dimension theo khoá nghiệp vụ, nạp fact theo lô ngày, dashboard 2 biểu đồ và 17 unit test. Thiết kế chi tiết nằm trong báo cáo Bài tập 1; các thay đổi thiết kế nằm trong `docs/thay-doi-thiet-ke.md`.

## 2. Môi trường
Python 3.11+ (đã chạy trên 3.12). Thư viện: xem `requirements.txt`. Không cần cài DBMS (dùng SQLite).

## 3. Các bước dựng hệ thống (mỗi bước một lệnh)
1. `git clone https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sathai-long.git`
2. `cd smartcrm-237480201IS02-khao-sathai-long`
3. `python -m venv .venv`
4. Kích hoạt môi trường — Windows: `.venv\Scripts\activate` · macOS/Linux: `source .venv/bin/activate`
5. `pip install -r requirements.txt`
6. Đặt hai file CSV thật vào `data/raw/` (tên `tickets_history.csv`, `survey_responses.csv`).
   Chưa có CSV thật thì sinh dữ liệu mẫu để thử: `python -m scripts.make_sample_data`
7. `python -m src.pipeline --config config/config.yaml`
   → tạo `data/csat.db` và `reports/chatluong-<ngày>.md`; dòng cuối phải in `ĐẠT` ở mục `[reconcile]`.
8. `python -m src.pipeline --config config/config.yaml` (chạy lần hai — số dòng `fact_survey` phải giữ nguyên)
9. `python -m pytest -q` → phải hiện `17 passed`
10. `streamlit run src/dashboard/app.py` → mở http://localhost:8501
11. `python -m scripts.export_charts` → ghi 2 biểu đồ vào `docs/` (dùng làm minh chứng)

Nếu CSV thật có tên cột hoặc định dạng ngày khác: sửa `config/config.yaml` (`columns`, `date_formats`), không sửa code.

## 4. Cấu trúc mã nguồn
| Đường dẫn | Vai trò |
|---|---|
| `src/extract/reader.py` | Đọc CSV, kiểm tra cột bắt buộc, thống kê ô trống |
| `src/transform/normalize.py` | Chuẩn hoá ngày (8 định dạng), ép điểm về số nguyên |
| `src/quality/rules.py`, `rejects.py` | Quy tắc chất lượng, bảng `reject_rows` (mỗi dòng một lý do) |
| `src/load/sqlite_loader.py` | Staging, dimension theo khoá nghiệp vụ (+ dòng “Không xác định”), fact theo lô ngày |
| `src/report.py` | Đối chiếu số dòng và báo cáo chất lượng markdown |
| `src/dashboard/queries.py` | Báo cáo Q1–Q5 (trung tâm×tháng · kỹ thuật viên · xu hướng · điểm thấp · tỉ lệ phản hồi) |
| `src/dashboard/charts.py`, `app.py` | 2 biểu đồ và dashboard Streamlit (đang tải · rỗng · lỗi) |
| `db/star_schema.sql` | DDL 1 fact + 3 dimension + `reject_rows` + `etl_run` |
| `docs/` | Nhật ký thay đổi thiết kế, sơ đồ, yêu cầu dữ liệu, ảnh minh chứng, khai báo AI |
| `tests/` | 17 unit test cho lớp nghiệp vụ |

## 5. Kiểm thử
`python -m pytest -q` chạy 17 test, gồm: luồng đúng (3 định dạng ngày → cùng một ngày; CSAT tính đúng), giá trị biên
(điểm 1/5 hợp lệ – 0/6 bị loại; nhận xét 500/501 ký tự; mẫu nhỏ 9 so với 10 phản hồi), dữ liệu sai (ngày không đọc được,
trùng mã phiếu, phản hồi cho phiếu chưa đóng, kỳ không có phản hồi).

## 6. Điều chỉnh thiết kế và phạm vi đã cắt trong Sprint 2
- **Đối chiếu staging ↔ fact:** `stg_ticket = fact_survey + phiếu bị loại + phiếu chưa đóng`. Fact có grain là phiếu Đã đóng nên ít dòng hơn staging.
- **Quy tắc “trả lời trước ngày đóng” so theo NGÀY:** nguồn có định dạng chỉ có ngày (`dd/mm/yyyy`); trả lời cùng ngày đóng là hợp lệ.
- **Phiếu thiếu khoá dimension** vào dòng “Không xác định” (key = −1) thay vì bị JOIN loại mất.
- **Đã cắt/hoãn (ghi nhận theo CLO5):** bảng `customer`, `survey_invitation`, xuất Excel (FR9), nhắc lần 2 (FR8), số điện thoại trong danh sách điểm thấp
  (chưa có `customers.csv`), phân tích cảm xúc (WON'T). Lý do: ưu tiên luồng end-to-end, test và README.
- Hạn chế đã biết: dòng bị xoá khỏi CSV nguồn không bị xoá khỏi fact ở lần nạp sau (chỉ upsert).
