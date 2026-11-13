# Nhật ký lỗi (bug log)

Mỗi lỗi theo bốn bước gỡ lỗi: tái lập → khoanh vùng → sửa nguyên nhân → xác nhận. Mức độ ghi ở tiêu đề. Link commit: /commit/<mã>.

## BUG-01 — [Major] Test không import được `tests.conftest`

- Triệu chứng: `python -m pytest -q src` báo `ModuleNotFoundError: No module named 'tests'` ở 4 file test (loader, pipeline, quality, queries); 0 test chạy.
- Tái lập: chạy `python -m pytest -q src` ở thư mục gốc repo.
- Khoanh vùng: dòng 1 của các file test là `from tests.conftest import ...`, trong khi `conftest.py` nằm phẳng trong `src/` (không có thư mục `tests/`). Đây là lỗi hợp đồng đường dẫn, không phải lỗi logic.
- Nguyên nhân gốc: mã viết cho cấu trúc cũ có thư mục `tests/`; cấu trúc phẳng (TD-16) không còn thư mục đó.
- Cách sửa: đổi thành `from src.conftest import T, S, run_pipeline`.
- Xác nhận: `python -m pytest -q src` hiện `17 passed`.
- Commit: [d419337](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/d419337), [540311a](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/540311a), [595f65c](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/595f65c), [578fce8](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/578fce8)

## BUG-02 — [Major] Dashboard không tìm thấy config sau khi gom file vào src/

- Triệu chứng: `streamlit run src/app.py` báo không tìm thấy `config.yaml` hoặc không import được `src.queries`.
- Tái lập: chạy dashboard khi `app.py` còn tính đường dẫn gốc dự án bằng `parents[2]`.
- Khoanh vùng: `app.py` nằm ở `src/app.py` nên thư mục gốc là `parents[1]`, không phải `parents[2]`.
- Nguyên nhân gốc: mã viết cho `src/dashboard/app.py` (sâu hơn một cấp).
- Cách sửa: dùng `Path(__file__).resolve().parents[1]` cho cả `sys.path` và đường dẫn config.
- Xác nhận: dashboard mở ở `localhost:8501` và hiện số liệu.
- Commit: [ea91f02](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/ea91f02)

## BUG-03 — [Major] Phản hồi cùng ngày đóng phiếu bị loại oan

- Triệu chứng: một số phản hồi hợp lệ bị ghi vào `reject_rows` với lý do `tra_loi_truoc_ngay_dong`.
- Tái lập: nguồn có định dạng chỉ có ngày (`dd/mm/yyyy`), phản hồi cùng ngày với `closed_at` có giờ.
- Khoanh vùng: ngày không có giờ được hiểu là 00:00 nên nhỏ hơn giờ đóng phiếu trong cùng ngày. Đây là lỗi logic (ý nghĩa dữ liệu), không phải lỗi hợp đồng.
- Nguyên nhân gốc: quy tắc so sánh theo thời điểm đầy đủ.
- Cách sửa: so sánh theo NGÀY bằng `dt.normalize()` trong `check_surveys` (TD-12).
- Xác nhận: test "trả lời cùng ngày đóng hợp lệ" trong `test_quality.py` PASS (TC-09).
- Commit: [1f6802f](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/1f6802f)

## BUG-04 — [Major] Số dòng fact ít hơn staging vì JOIN loại phiếu thiếu khoá

- Triệu chứng: `fact_survey` ít dòng hơn số phiếu đã đóng khi nguồn có phiếu thiếu trung tâm hoặc kỹ thuật viên.
- Tái lập: nạp phiếu đã đóng có `center_id` hoặc `technician_id` trống.
- Khoanh vùng: truy vấn phiếu staging không có khoá khớp dimension; phép nối bỏ các phiếu này.
- Nguyên nhân gốc: dimension không có dòng cho giá trị thiếu.
- Cách sửa: thêm dòng "Không xác định" (key = −1) vào dimension và ánh xạ khoá thiếu về −1 (TD-11).
- Xác nhận: công thức đối chiếu `stg_ticket = fact + loại + chưa đóng` in `ĐẠT`; test thiếu trung tâm hoặc kỹ thuật viên trong `test_loader.py` PASS (TC-11).
- Commit: [c02ea47](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/c02ea47)

## BUG-05 — [Major] README trỏ sai đường dẫn và link repo

- Triệu chứng: làm đúng README trên máy sạch thì lệnh báo `FileNotFoundError`; link clone bị đứt chữ (`khao-sathai-long`).
- Tái lập: clone repo vào thư mục mới và chạy từng bước README.
- Khoanh vùng: README ghi `config/config.yaml`, `db/star_schema.sql`, `src/dashboard/app.py`, `scripts/...`, `tests/`, trong khi các file thật nằm phẳng trong `src/`. Lệnh sinh dữ liệu mẫu cũng trỏ `scripts.make_sample_data`.
- Nguyên nhân gốc: README viết trước khi gom file theo yêu cầu giảng viên (TD-16) và không được chạy lại trên bản clone mới.
- Cách sửa: viết lại README theo cấu trúc phẳng, sửa link, thêm bước clone theo tag (TD-21).
- Xác nhận: clone `--branch v0.2` vào thư mục mới, chạy đủ các bước README, pipeline `ĐẠT` và `18 passed`.
- Commit: [25e4a12](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/25e4a12)

## BUG-06 — [Minor] Tạo lỗi trạng thái "lỗi" làm sinh ra file csat.db rỗng

- Triệu chứng: đổi tên `data/csat.db` thành `csat.db.bak` rồi mở dashboard thì lỗi `no such table: dim_center`; sau khi đổi tên ngược lại báo trùng tên.
- Tái lập: đổi tên `data/csat.db`, chạy `python -m streamlit run src/app.py`.
- Khoanh vùng: `sqlite3.connect` tự tạo file `data/csat.db` rỗng khi file không tồn tại, nên dashboard mở được một kho không có bảng.
- Nguyên nhân gốc: hành vi mặc định của SQLite; đây là cách giả lập lỗi, không phải lỗi mã.
- Cách sửa: trước khi đổi tên `csat.db.bak` về `csat.db`, xoá file `csat.db` rỗng. Đã ghi vào README.
- Xác nhận: sau khi xoá file rỗng và đổi tên lại, dashboard hiện số liệu bình thường.
- Commit: [25e4a12](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/25e4a12)

## BUG-07 — [Major] Dashboard hiện nguyên câu SQL và tên bảng khi tải dữ liệu lỗi (phát hiện khi điền checklist bảo mật mục 5)

- Triệu chứng: khi kho dữ liệu chưa có bảng, thông báo lỗi trên trang hiện `Execution failed on sql 'SELECT center_key, center_name FROM dim_center WHERE center_key>0 ORDER BY center_name': no such table: dim_center`.
- Tái lập: `AppTest.from_file("src/app.py").run()` với kho SQLite rỗng, hoặc đổi tên `data/csat.db` rồi mở dashboard (log: `docs/evidence/bug07-before-fix.txt`).
- Khoanh vùng: `src/app.py`, khối `except Exception as e` đưa nguyên `{e}` vào `st.error(...)`; không có lỗi ở `queries.py`. Đây là rò rỉ cấu trúc kho dữ liệu (OWASP A10/A02).
- Nguyên nhân gốc: dùng thông điệp ngoại lệ của thư viện làm thông báo cho người dùng cuối.
- Cách sửa: hiện câu chung, hướng dẫn kiểm tra pipeline; ghi chi tiết ngoại lệ vào log máy chủ bằng `logging.exception`. Thêm test `test_dashboard_error.py` (TD-25).
- Xác nhận: test mới FAIL trên mã cũ (`assert 'select' not in ...`) và PASS sau khi sửa; `python -m pytest -q src` → `19 passed`.
- Commit: [1978ba2](https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long/commit/1978ba2)
