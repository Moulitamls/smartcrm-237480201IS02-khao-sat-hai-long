# Smart CRM Mekong Mobile – Khảo sát hài lòng CSAT (L8, Track DA)

Sinh viên: MOONLASING Moulita · MSSV 237480201IS02 · GVHD: ThS. Nguyễn Minh Tân

## 1. Giới thiệu

Pipeline dữ liệu cho luồng L8: đọc `tickets_history.csv` và `survey_responses.csv`, chuẩn hóa, kiểm tra chất lượng, rồi nạp vào kho dữ liệu dạng star schema (`fact_survey` và 2 bảng dimension nghiệp vụ `dim_center`, `dim_technician` cùng `dim_date`) để tính CSAT theo trung tâm, kỹ thuật viên và tháng. Sprint 2 bổ sung nạp dimension theo khoá nghiệp vụ, nạp fact theo lô ngày, dashboard 2 biểu đồ và 17 unit test. Các thay đổi thiết kế nằm trong `docs/thay-doi-thiet-ke.md`.

## 2. Môi trường

Python 3.11 trở lên. Thư viện: xem `requirements.txt`. Không cần cài DBMS (dùng SQLite).

Toàn bộ mã nguồn nằm **phẳng trong `src/`** (theo yêu cầu của giảng viên, không tạo thư mục con). Mọi lệnh bên dưới chạy **từ thư mục gốc của repo**.

## 3. Các bước dựng hệ thống (mỗi bước một lệnh)

1. `git clone https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long.git`
2. `cd smartcrm-237480201IS02-khao-sat-hai-long`
3. `python -m venv .venv`
4. Kích hoạt môi trường. Windows: `.venv\Scripts\activate` · macOS/Linux: `source .venv/bin/activate`
   (Nếu PowerShell chặn script: chạy `Set-ExecutionPolicy -Scope Process Bypass` rồi kích hoạt lại.)
5. `pip install -r requirements.txt`
6. Đặt hai file CSV thật (`tickets_history.csv`, `survey_responses.csv`) vào đúng thư mục khai báo ở mục `paths` trong `src/config.yaml`.
7. `python -m src.pipeline --config src/config.yaml`
   → tạo `data/csat.db` và `reports/chatluong-<ngày>.md`; dòng `[reconcile]` phải in `ĐẠT`.
8. `python -m src.pipeline --config src/config.yaml` (chạy lần hai; số dòng `fact_survey` phải giữ nguyên 6350)
9. `python -m pytest -q src` → phải hiện `17 passed`
10. `python -m streamlit run src/app.py` → mở http://localhost:8501
11. `python -m src.export_charts` → ghi 2 biểu đồ vào `docs/` (`chart1_csat_trend.png`, `chart2_technician.png`)

Nếu CSV thật có tên cột hoặc định dạng ngày khác: sửa `src/config.yaml` (`columns`, `date_formats`), không sửa code.

## 4. Cấu trúc mã nguồn

| Đường dẫn | Vai trò |
|---|---|
| `src/__init__.py` | Đánh dấu `src` là package để chạy `python -m src.…` |
| `src/config.yaml` | Cấu hình: đường dẫn, tên cột, định dạng ngày, quy tắc, dashboard |
| `src/star_schema.sql` | DDL 1 fact + 3 dimension + `reject_rows` + `etl_run` |
| `src/pipeline.py` | Điểm vào: đọc → chuẩn hoá → kiểm tra chất lượng → nạp → đối chiếu → báo cáo |
| `src/extract`, `src/transform`, `src/quality`, `src/load` | Đọc CSV; chuẩn hoá ngày và điểm; quy tắc chất lượng và `reject_rows`; nạp staging, dimension (+ dòng “Không xác định”), fact theo lô ngày |
| `src/report.py` | Đối chiếu số dòng và báo cáo chất lượng markdown |
| `src/queries.py` | Báo cáo Q1–Q5 (trung tâm×tháng · kỹ thuật viên · xu hướng · điểm thấp · tỉ lệ phản hồi) |
| `src/charts.py`, `src/app.py` | 2 biểu đồ và dashboard Streamlit (đang tải · rỗng · lỗi) |
| `src/export_charts.py` | Xuất 2 biểu đồ thành ảnh PNG vào `docs/` |
| `src/test_*.py`, `src/conftest.py` | 17 unit test cho lớp nghiệp vụ |
| `docs/` | Nhật ký thay đổi thiết kế, sơ đồ, yêu cầu dữ liệu, ảnh minh chứng, khai báo AI |

## 5. Kiểm thử

`python -m pytest -q src` chạy 17 test, gồm: luồng đúng (3 định dạng ngày → cùng một ngày; CSAT tính đúng), giá trị biên (điểm 1/5 hợp lệ – 0/6 bị loại; nhận xét 500/501 ký tự; mẫu nhỏ 9 so với 10 phản hồi), dữ liệu sai (ngày không đọc được, trùng mã phiếu, phản hồi cho phiếu chưa đóng, kỳ không có phản hồi).

## 6. Điều chỉnh thiết kế và phạm vi đã cắt trong Sprint 2

- **Cấu trúc phẳng trong `src/` (TD-16):** giảng viên không cho tạo thư mục mới nên `config.yaml` và `star_schema.sql` nằm trong `src/`; import và đường dẫn đã chỉnh theo.
- **Đối chiếu staging ↔ fact:** `stg_ticket = fact_survey + phiếu bị loại + phiếu chưa đóng`. Fact có grain là phiếu Đã đóng nên ít dòng hơn staging.
- **Quy tắc “trả lời trước ngày đóng” so theo NGÀY:** nguồn có định dạng chỉ có ngày (`dd/mm/yyyy`); trả lời cùng ngày đóng là hợp lệ.
- **Phiếu thiếu khoá dimension** vào dòng “Không xác định” (key = −1) thay vì bị JOIN loại mất.
- **Đã cắt/hoãn (ghi nhận theo CLO5):** bảng `customer`, `survey_invitation`, xuất Excel (FR9), nhắc lần 2 (FR8), số điện thoại trong danh sách điểm thấp (chưa có `customers.csv`), phân tích cảm xúc (WON'T), biểu đồ thứ ba. Lý do: ưu tiên luồng end-to-end, test và README.
- Hạn chế đã biết: dòng bị xoá khỏi CSV nguồn không bị xoá khỏi fact ở lần nạp sau (chỉ upsert).
