# Phụ lục – Bảng khai báo sử dụng công cụ AI

**Học phần:** Chuyên đề tốt nghiệp 1 – Bài tập 1: Phân tích và Thiết kế
**Luồng nghiệp vụ:** L8 – Khảo sát hài lòng khách hàng sau bảo hành (CSAT) · **Track:** DA
**Sinh viên:** MOONLASING Moulita · **MSSV:** 237480201IS02

## 1. Bảng khai báo

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | liệt kê điểm còn thiếu hoặc sai so với 11 mục kiểm chứng | Bản DOCX của Bài tập 1 | Đối chiếu từng điểm Claude nêu với file đề bài PDF và tự sửa nội dung trong tài liệu; chạy lại Ctrl+F kiểm tra thuật ngữ |


## 2. Các phần em tự làm hoàn toàn

*Mục 1 phân tích yêu cầu nghiệp vụ và User Story; Use Case Diagram và đặc tả UC2; sơ đồ kiến trúc và 3 câu lập luận; sơ đồ data flow và lược đồ kho dữ liệu; wireframe trên Figma; đo số liệu trên dữ liệu mẫu.*

## 3. Cam kết

Tôi xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

- Họ tên: **MOONLASING Moulita**
- MSSV: **237480201IS02**
- Ngày: 09/10/2026

---

# Phụ lục – Bảng khai báo sử dụng công cụ AI (Giai đoạn 3 – Bài tập 3)

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Soạn bản nháp `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `src/config.docker.yaml`; sửa `src/app.py` (đọc `CSAT_CONFIG`, thông báo lỗi chung) và viết `test_dashboard_error.py`; soạn Test Plan, Test Report, checklist bảo mật, Deployment Guide, Pipeline doc, Data dictionary, mục TD-23 đến TD-27; chạy thử pipeline, pytest, `pip-audit` và các lệnh `grep` trong môi trường của công cụ để lấy log và số liệu |  Chạy lại toàn bộ lệnh trong tài liệu: `pytest` 19 passed, pipeline 6.350 dòng và ĐẠT, chạy lần hai không đổi, `pip-audit` không có lỗ hổng đã biết; test BUG-07 FAIL trên mã cũ và PASS sau sửa; từ điển cột kiểm đủ cột bằng script. Em đã tự chạy phép thử máy trắng bằng Docker 28.1.1 trên Windows ngày 13/11/2026 (clone vào thư mục trống, hai lệnh, `docker compose ps` healthy, 19 passed, chạy pipeline lần hai vẫn 6.350 dòng), đối chiếu số liệu trong Guide với kết quả thực tế, và đọc, sửa từng tài liệu. |

