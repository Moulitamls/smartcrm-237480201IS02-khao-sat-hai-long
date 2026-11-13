# Test Plan rút gọn — Smart CRM CSAT (L8, track DA), tag v1.0

## 1. Phạm vi và mục tiêu
Kiểm chứng rằng pipeline đọc 2 tệp CSV, làm sạch, nạp kho star schema và dashboard hiển thị đúng 4 chỉ số, 2 biểu đồ, 3 trạng thái (đang tải · rỗng · lỗi). **Trong phạm vi:** `src/` (extract, transform, quality, load, report, queries, app), gói Docker. **Ngoài phạm vi:** giao diện đồ hoạ chi tiết (chỉ kiểm trạng thái lỗi bằng Streamlit AppTest), hiệu năng tải lớn, kiểm thử xâm nhập, các chức năng đã hoãn (TD-15).

## 2. Chiến lược và loại kiểm thử
Năm loại test case: **luồng đúng**, **giá trị biên**, **dữ liệu sai**, **ngoại lệ nghiệp vụ**, **bảo mật**. Công cụ: `pytest` (19 test tự động trên dữ liệu nhỏ do test tự dựng, không phụ thuộc CSV thật), chạy pipeline trên CSV thật và trên dữ liệu mẫu có lỗi chủ ý (`config.demo.yaml`), `streamlit.testing.AppTest` cho trạng thái lỗi của dashboard. Mỗi test case ở `docs/test-report.md` ghi lệnh chạy lại và kết quả thực tế.

## 3. Môi trường và dữ liệu kiểm thử
Chạy trong Docker (`python:3.11-slim`, thư viện ghim `==`) theo Deployment Guide; lệnh test một dòng: `docker compose run --rm pipeline python -m pytest -q src`. Dữ liệu: CSV thật 7.800 phiếu + 2.600 phản hồi trong `data/raw/`; dữ liệu mẫu lỗi sinh bằng `python -m src.make_sample_data` (seed cố định, 30 dòng lỗi chủ ý).

## 4. Tiêu chí đạt, vai trò, rủi ro
- **Đạt:** toàn bộ 19 test PASS bằng một lệnh; pipeline in `ĐẠT` ở cả hai công thức đối chiếu; chạy lần hai không đổi số dòng fact (6.350); không còn bug mức Critical/Major chưa xử lý.
- **Dừng/không đạt:** có test FAIL chưa có mục trong Bug Log, hoặc đối chiếu in `LỆCH`.
- **Vai trò:** MOONLASING Moulita viết test, chạy, ghi Bug Log; GVHD kiểm bằng phép thử máy trắng ở buổi 16.
- **Rủi ro:** quy tắc `ticket_id_trong` và `ngay_tra_loi_khong_doc_duoc` chưa có test riêng; test giao diện chỉ bao phủ trạng thái lỗi; Docker chưa chạy trên máy GV khác hệ điều hành.
