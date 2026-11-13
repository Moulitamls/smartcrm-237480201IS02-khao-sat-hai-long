# Checklist bảo mật cơ bản — Smart CRM CSAT (L8, track DA)

Phạm vi: bảy việc cơ bản của CĐTN1, tự kiểm bằng lệnh. Không phải kiểm thử xâm nhập. Log lệnh đầy đủ: `docs/evidence/security-checks.txt` (chạy 11/11/2026, Linux, Python 3.12.3).
Tham chiếu OWASP Top 10:2025: A01 Broken Access Control · A02 Security Misconfiguration · A03 Software Supply Chain Failures · A04 Cryptographic Failures · A05 Injection · A07 Authentication Failures · A09 Security Logging and Alerting Failures · A10 Mishandling of Exceptional Conditions.

## 1. Không có secret nào trong repo (A02) — ĐÃ LÀM
Minh chứng: `grep -rniE "password|secret|api_key|token" src/` → rỗng; `grep` trên `.env.example`, `Dockerfile`, `docker-compose.yml` → rỗng; không có tệp `.env`; `.env` nằm trong `.gitignore` và `.dockerignore`. Dự án không dùng secret nào (xem `.env.example`).
Lịch sử Git: `git log --all --oneline -- .env` → `(rỗng)` — chạy ngày 13/11/2026 trên repo thật.
Ảnh: `docs/screenshots/sec-1.png`

## 2. Dữ liệu vào được kiểm ở tầng ứng dụng (A05) — ĐÃ LÀM
Minh chứng: (a) 10 quy tắc chất lượng chặn dữ liệu sai trước khi nạp: dữ liệu mẫu lỗi → 30 dòng vào `reject_rows` (TC-08 PASS), điểm 0/6 và nhận xét 501 ký tự bị loại (TC-04, TC-05 PASS). (b) Truy vấn dashboard dùng tham số `?` cho ngày và trung tâm (`src/queries.py`, hàm `_where`), ngưỡng điểm thấp ép `int()`. (c) `grep` các câu SQL ghép chuỗi: chỉ còn `{_metrics}`, `{_JOINS}`, `{w}` (chuỗi cố định trong mã) và tên bảng/cột truyền từ mã (`sqlite_loader.py`) — không có dữ liệu người dùng hay dữ liệu CSV trong câu SQL.
Giới hạn: dashboard không có ô nhập văn bản tự do; các ô nhập là lịch và danh sách chọn của Streamlit.

## 3. Kiểm soát truy cập theo chủ sở hữu (A01) — KHÔNG ÁP DỤNG
Lý do: dashboard không có đăng nhập, vai trò hay dữ liệu thuộc về từng người dùng (SSO nằm ngoài phạm vi, TD-07). Biện pháp thay thế đã làm: cổng dashboard chỉ gắn vào `127.0.0.1` (`docker-compose.yml`), không mở ra mạng; dữ liệu cá nhân (số điện thoại) không có trong kho (TD-05, TD-15).

## 4. Mật khẩu, dữ liệu nhạy cảm băm/mã hoá (A04, A07) — KHÔNG ÁP DỤNG
Lý do: hệ thống không lưu mật khẩu hay tài khoản. Dữ liệu khách chỉ là mã số giả danh (`customer_id` số, tên kỹ thuật viên dạng "Kỹ thuật viên N"); kiểm `regex` số điện thoại/e-mail: 0/1.884 nhận xét và 0/7.800 mô tả sự cố. Phân loại từng cột ở `docs/data-dictionary.md`. Hạn chế: SQLite không được mã hoá khi lưu (at rest).

## 5. Thông báo lỗi không lộ cấu trúc trong (A10, A02) — ĐÃ LÀM (sau khi sửa BUG-07)
Minh chứng: trước khi sửa, kho chưa có bảng làm dashboard in ra `Execution failed on sql 'SELECT center_key, center_name FROM dim_center ...': no such table: dim_center` (`docs/evidence/bug07-before-fix.txt`). Sau khi sửa, dashboard chỉ hiện câu chung và ghi chi tiết vào log máy chủ; test `test_loi_dashboard_khong_lo_cau_truc_ben_trong` PASS (TC-12). Pipeline là công cụ dòng lệnh cho người vận hành nên vẫn in traceback ra console.
Ảnh: `docs/screenshots/TC-12.png`

## 6. Nhật ký không ghi secret, dữ liệu cá nhân (A09) — ĐÃ LÀM
Minh chứng: `python -m src.pipeline 2>&1 | grep -iE "password|token|0[0-9]{9}"` → rỗng; log Streamlit khi chạy dashboard: 0 dòng khớp. Log của pipeline chỉ gồm số dòng; `reject_rows` chỉ lưu mã phiếu/phản hồi và lý do chung, không lưu nội dung dòng.
Trong Docker: `docker compose logs | grep -iE "password|token|0[0-9]{9}"` → `(rỗng)` — chạy ngày 13/11/2026 (PowerShell: `Select-String`)
Ảnh: `docs/screenshots/sec-6.png`

## 7. Phụ thuộc ghim phiên bản, đã kiểm lỗ hổng (A03) — ĐÃ LÀM (phụ thuộc trực tiếp)
Minh chứng: `requirements.txt` ghim `==` cả 5 gói; `pip-audit -r requirements.txt` → `No known vulnerabilities found` (11/11/2026); Dockerfile ghim `python:3.11-slim`.
Còn lại, CHƯA LÀM: phụ thuộc gián tiếp (numpy, tornado, …) chưa khoá bằng tệp lock, và ảnh Docker dùng thẻ `3.11-slim` không ghim digest. Kế hoạch: sinh tệp khoá bằng `pip freeze` sau khi nộp BT3.
