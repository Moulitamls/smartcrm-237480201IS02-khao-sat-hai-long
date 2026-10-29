# Smart CRM Mekong Mobile – Khảo sát hài lòng CSAT (L8, Track DA)

Sinh viên: MOONLASING Moulita · MSSV 237480201IS02 · GVHD: ThS. Nguyễn Minh Tân
Repo: https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long 

## 1. Giới thiệu

Pipeline dữ liệu cho luồng L8: đọc `tickets_history.csv` và `survey_responses.csv`, chuẩn hoá, kiểm tra chất lượng, rồi nạp kho dữ liệu star schema (SQLite: `fact_survey` + 3 dimension) để tính CSAT theo trung tâm, kỹ thuật viên và tháng. Dashboard Streamlit hiển thị 4 chỉ số và 2 biểu đồ, mỗi khung có dòng ghi nguồn và thời điểm dữ liệu.

Cấu trúc thư mục phẳng trong `src/` theo yêu cầu của giảng viên (TD-16 trong `docs/thay-doi-thiet-ke.md`).

## 2. Môi trường

- Python 3.11 trở lên (đã chạy trên 3.11 và 3.12). Không cần cài DBMS (dùng SQLite).
- Thư viện ghim phiên bản trong `requirements.txt`. Không cần `.env` thật hay secret (xem `.env.example`).
- Mọi lệnh bên dưới chạy ở **thư mục gốc repo**. Ví dụ dùng PowerShell trên Windows.

## 3. Các bước dựng hệ thống (mỗi bước một lệnh)

1. `git clone --branch v0.2 https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long.git`
2. `cd smartcrm-237480201IS02-khao-sat-hai-long`
3. `python -m venv .venv`
4. Kích hoạt môi trường. Windows: `.venv\Scripts\activate` · macOS/Linux: `source .venv/bin/activate`
5. `pip install -r requirements.txt`
6. `dir data\raw` (macOS/Linux: `ls data/raw`). Phải thấy `tickets_history.csv` và `survey_responses.csv`; hai file này đã nằm sẵn trong repo.
7. `python -m src.pipeline --config src/config.yaml`
   Kết quả đúng: `[load] 734 lô ngày; fact_survey = 6350 dòng` và `[reconcile] ... -> ĐẠT`. Tạo `data/csat.db` và `reports/chatluong-<ngày>.md`.
8. `python -m src.pipeline --config src/config.yaml` (chạy lần hai: `fact_survey` vẫn 6350, không nhân đôi)
9. `python -m pytest -q src`
   Kết quả đúng: `18 passed`.
10. `python -m streamlit run src/app.py`
    Mở http://localhost:8501. Dừng bằng Ctrl+C.
11. `python -m src.export_charts` (ghi `docs/chart1_csat_trend.png`, `docs/chart2_technician.png`)
12. `python -m src.make_sample_data` rồi `python -m src.pipeline --config src/config.demo.yaml`
    Chạy trên dữ liệu mẫu có lỗi chủ ý để xem bảng `reject_rows` (`data/demo.db`). Không ghi đè dữ liệu thật.

## 4. Cấu trúc mã nguồn

| Đường dẫn | Vai trò |
|---|---|
| `src/extract/reader.py` | Đọc CSV, kiểm tra cột bắt buộc, thống kê ô trống |
| `src/transform/normalize.py` | Chuẩn hoá ngày (8 định dạng), ép điểm về số nguyên |
| `src/quality/rules.py`, `rejects.py` | Quy tắc chất lượng, bảng `reject_rows` (mỗi dòng một lý do) |
| `src/load/sqlite_loader.py` | Staging, dimension theo khoá nghiệp vụ (+ dòng "Không xác định"), fact theo lô ngày (upsert) |
| `src/report.py` | Đối chiếu staging ↔ fact và báo cáo chất lượng markdown |
| `src/pipeline.py` | Điều phối cả luồng bằng một lệnh |
| `src/queries.py` | Báo cáo Q1–Q5 (trung tâm×tháng · kỹ thuật viên · xu hướng · điểm thấp · tỉ lệ phản hồi) |
| `src/charts.py`, `src/app.py`, `src/export_charts.py` | 2 biểu đồ, dashboard (đang tải · rỗng · lỗi), xuất ảnh biểu đồ |
| `src/config.yaml`, `src/config.demo.yaml` | Cấu hình dữ liệu thật và dữ liệu mẫu (đường dẫn, cột, định dạng ngày, ngưỡng quy tắc) |
| `src/star_schema.sql` | DDL 1 fact + 3 dimension + `reject_rows` + `etl_run` |
| `src/test_*.py`, `src/conftest.py` | 18 unit test cho lớp nghiệp vụ (không test giao diện) |
| `data/raw/` | CSV nguồn (`tickets_history.csv`, `survey_responses.csv`) |
| `docs/` | Từ điển cột (`data-dictionary.md`), thay đổi thiết kế, bug-log, khai báo AI, sơ đồ, ảnh minh chứng |

## 5. Kiểm thử

`python -m pytest -q src` chạy 18 test, không cần CSV thật (test tự dựng dữ liệu nhỏ):

- Luồng đúng: 3 định dạng ngày ra cùng một ngày; CSAT và tỉ lệ phản hồi tính đúng; nạp lần hai không nhân đôi dòng; pipeline chạy trọn vẹn.
- Giá trị biên: điểm 1/5 hợp lệ, 0/6 bị loại; nhận xét 500/501 ký tự; kỹ thuật viên 9 so với 10 phản hồi; khoảng 12 tháng bắt đầu từ đầu tháng.
- Dữ liệu sai: ngày 31/02 và chuỗi rác; trùng mã phiếu; phản hồi cho phiếu chưa đóng; trả lời trước ngày đóng; hai phản hồi một phiếu; kỳ không có phản hồi không hiện 0 điểm.

## 6. Ba trạng thái của dashboard

- **Đang tải:** spinner khi truy vấn.
- **Rỗng:** đặt "Từ ngày" sau "Đến ngày" (hoặc chọn khoảng ngoài dữ liệu) thì hiện câu giải thích.
- **Lỗi:** đổi tên `data\csat.db` thành `csat.db.bak`, chạy lại dashboard để thấy thông báo lỗi và nút "Thử lại". **Trước khi đổi tên ngược lại, xoá file `csat.db` rỗng** do SQLite tự tạo (xem BUG-06 trong `docs/bug-log.md`).

Bộ lọc mặc định là "12 tháng gần nhất" (FR6); chọn "Toàn kỳ" để thấy số cả kỳ (điểm TB 3,92 · CSAT 70,0% · 2.600 phản hồi · tỉ lệ phản hồi 40,9%).

## 7. Lỗi thường gặp

| Thông báo | Cách xử lý |
|---|---|
| `FileNotFoundError: data/raw/...csv` | Chạy lệnh ở thư mục gốc repo; kiểm tra `data/raw/` (bước 6). |
| `ModuleNotFoundError: pandas` / `streamlit` | Chưa kích hoạt `.venv` hoặc chưa chạy `pip install -r requirements.txt`. |
| `database is locked` | Đóng `csat.db` trong DB Browser rồi chạy lại. |
| `streamlit` không nhận lệnh | Dùng `python -m streamlit run src/app.py`. |

## 8. Điều chỉnh thiết kế và phạm vi đã cắt

Xem chi tiết (TD-10 đến TD-21) ở `docs/thay-doi-thiet-ke.md`. Tóm tắt:

- **Đối chiếu staging ↔ fact:** `stg_ticket = fact_survey + phiếu bị loại + phiếu chưa đóng`; fact có grain là phiếu đã đóng nên ít dòng hơn staging.
- **Quy tắc "trả lời trước ngày đóng" so theo NGÀY**, vì nguồn có định dạng chỉ có ngày.
- **Phiếu thiếu khoá dimension** vào dòng "Không xác định" (key = −1) thay vì bị JOIN loại mất.
- **Đã cắt/hoãn (CLO5):** bảng `customer`, `survey_invitation`, xuất Excel (FR9), nhắc lần 2 (FR8), số điện thoại trong danh sách điểm thấp (chưa có `customers.csv`), biểu đồ thứ ba; phân tích cảm xúc nằm ngoài phạm vi.
- **Hạn chế đã biết:** dòng bị xoá khỏi CSV nguồn không bị xoá khỏi fact ở lần nạp sau (chỉ upsert).
