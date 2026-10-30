# Nhật ký lỗi (bug log) — Giai đoạn 2

Mỗi lỗi theo bốn bước gỡ lỗi: tái lập → khoanh vùng → sửa nguyên nhân → xác nhận. Điền mã commit sửa lỗi (từ `git log --oneline`) vào dòng "Commit".

## BUG-01 — Test không import được `tests.conftest`

- Triệu chứng: `python -m pytest -q src` báo `ModuleNotFoundError: No module named 'tests'` ở 4 file test (loader, pipeline, quality, queries); 0 test chạy.
- Tái lập: chạy `python -m pytest -q src` ở thư mục gốc repo.
- Khoanh vùng: dòng 1 của các file test là `from tests.conftest import ...`, trong khi `conftest.py` nằm phẳng trong `src/` (không có thư mục `tests/`). Đây là lỗi hợp đồng đường dẫn, không phải lỗi logic.
- Nguyên nhân gốc: mã viết cho cấu trúc cũ có thư mục `tests/`; cấu trúc phẳng (TD-16) không còn thư mục đó.
- Cách sửa: đổi thành `from src.conftest import T, S, run_pipeline`.
- Xác nhận: `python -m pytest -q src` hiện `17 passed`.
- Commit: `<d419337, 540311a, 595f65c, 578fce8>`

## BUG-02 — Dashboard không tìm thấy config sau khi gom file vào src/

- Triệu chứng: `streamlit run src/app.py` báo không tìm thấy `config.yaml` hoặc không import được `src.queries`.
- Tái lập: chạy dashboard khi `app.py` còn tính đường dẫn gốc dự án bằng `parents[2]`.
- Khoanh vùng: `app.py` nằm ở `src/app.py` nên thư mục gốc là `parents[1]`, không phải `parents[2]`.
- Nguyên nhân gốc: mã viết cho `src/dashboard/app.py` (sâu hơn một cấp).
- Cách sửa: dùng `Path(__file__).resolve().parents[1]` cho cả `sys.path` và đường dẫn config.
- Xác nhận: dashboard mở ở `localhost:8501` và hiện số liệu.
- Commit: `<ea91f02>`

## BUG-03 — Phản hồi cùng ngày đóng phiếu bị loại oan

- Triệu chứng: một số phản hồi hợp lệ bị ghi vào `reject_rows` với lý do `tra_loi_truoc_ngay_dong`.
- Tái lập: nguồn có định dạng chỉ có ngày (`dd/mm/yyyy`), phản hồi cùng ngày với `closed_at` có giờ.
- Khoanh vùng: ngày không có giờ được hiểu là 00:00 nên nhỏ hơn giờ đóng phiếu trong cùng ngày. Đây là lỗi logic (ý nghĩa dữ liệu), không phải lỗi hợp đồng.
- Nguyên nhân gốc: quy tắc so sánh theo thời điểm đầy đủ.
- Cách sửa: so sánh theo NGÀY bằng `dt.normalize()` trong `check_surveys` (TD-12).
- Xác nhận: test "trả lời cùng ngày đóng hợp lệ" trong `test_quality.py` PASS.
- Commit: `<1f6802f>`

## BUG-04 — Số dòng fact ít hơn staging vì JOIN loại phiếu thiếu khoá

- Triệu chứng: `fact_survey` ít dòng hơn số phiếu đã đóng khi nguồn có phiếu thiếu trung tâm hoặc kỹ thuật viên.
- Tái lập: nạp phiếu đã đóng có `center_id` hoặc `technician_id` trống.
- Khoanh vùng: truy vấn phiếu staging không có khoá khớp dimension; phép nối bỏ các phiếu này.
- Nguyên nhân gốc: dimension không có dòng cho giá trị thiếu.
- Cách sửa: thêm dòng "Không xác định" (key = −1) vào dimension và ánh xạ khoá thiếu về −1 (TD-11).
- Xác nhận: công thức đối chiếu `stg_ticket = fact + loại + chưa đóng` in `ĐẠT`; test thiếu trung tâm hoặc kỹ thuật viên trong `test_loader.py` PASS.
- Commit: `<c02ea47>`

## BUG-05 — README trỏ sai đường dẫn và link repo

- Triệu chứng: làm đúng README trên máy sạch thì lệnh báo `FileNotFoundError`; link clone bị đứt chữ (`khao-sathai-long`).
- Tái lập: clone repo vào thư mục mới và chạy từng bước README.
- Khoanh vùng: README ghi `config/config.yaml`, `db/star_schema.sql`, `src/dashboard/app.py`, `scripts/...`, `tests/`, trong khi các file thật nằm phẳng trong `src/`. Lệnh sinh dữ liệu mẫu cũng trỏ `scripts.make_sample_data`.
- Nguyên nhân gốc: README viết trước khi gom file theo yêu cầu giảng viên (TD-16) và không được chạy lại trên bản clone mới.
- Cách sửa: viết lại README theo cấu trúc phẳng, sửa link, thêm bước clone theo tag `v0.2` (TD-21).
- Xác nhận: clone `--branch v0.2` vào thư mục mới, chạy đủ các bước README, pipeline `ĐẠT` và `18 passed`.
- Commit: `<25e4a12>`

## BUG-06 — Tạo lỗi trạng thái "lỗi" làm sinh ra file csat.db rỗng

- Triệu chứng: đổi tên `data/csat.db` thành `csat.db.bak` rồi mở dashboard thì lỗi `no such table: dim_center`; sau khi đổi tên ngược lại báo trùng tên.
- Tái lập: đổi tên `data/csat.db`, chạy `python -m streamlit run src/app.py`.
- Khoanh vùng: `sqlite3.connect` tự tạo file `data/csat.db` rỗng khi file không tồn tại, nên dashboard mở được một kho không có bảng.
- Nguyên nhân gốc: hành vi mặc định của SQLite; đây là cách giả lập lỗi, không phải lỗi mã.
- Cách sửa: trước khi đổi tên `csat.db.bak` về `csat.db`, xoá file `csat.db` rỗng. Đã ghi vào README.
- Xác nhận: sau khi xoá file rỗng và đổi tên lại, dashboard hiện số liệu bình thường.
- Commit: `<25e4a12>`
