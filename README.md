# Smart CRM Mekong Mobile – Khảo sát hài lòng CSAT (L8, Track DA)

Sinh viên: MOONLASING Moulita · MSSV 237480201IS02 · GVHD: ThS. Nguyễn Minh Tân

## 1. Giới thiệu

Pipeline dữ liệu cho luồng L8: đọc `tickets_history.csv` và `survey_responses.csv`, chuẩn hóa, kiểm tra chất lượng, rồi nạp vào kho dữ liệu dạng star schema (`fact_survey` và 3 bảng dimension) để tính CSAT theo trung tâm, kỹ thuật viên và tháng. Thiết kế chi tiết nằm trong báo cáo Bài tập 1; các thay đổi thiết kế nằm trong `docs/thay-doi-thiet-ke.md`.

## 2. Yêu cầu môi trường

- Python 3.10 trở lên (đã chạy thử với Python 3.12)
- SQLite 3 (đi kèm Python, không cần cài thêm)
- Thư viện: pandas, PyYAML, pytest (xem `requirements.txt`)
- Dữ liệu nguồn: đặt `tickets_history.csv` và `survey_responses.csv` vào `data/raw/` (file CSV không đưa lên Git)

Cài đặt trong môi trường ảo (tránh lỗi `externally-managed-environment`):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Cách chạy

```bash
python -m src.pipeline --config config/config.yaml   # chạy toàn bộ pipeline bằng một lệnh
python -m pytest -q                                   # chạy unit test
```

Chạy từ thư mục gốc của repo. Kết quả: file `data/csat.db` (staging, kho dữ liệu, `reject_rows`) và báo cáo `reports/chat-luong-<ngày>.md`.

## 4. Cấu trúc thư mục

| Thư mục / file | Vai trò (khớp sơ đồ data flow, Chương 4) |
|---|---|
| `src/extract/` | Đọc 2 file CSV, thống kê số dòng, số cột, tỉ lệ ô trống |
| `src/transform/` | Chuẩn hóa kiểu dữ liệu và ngày (nhiều định dạng) |
| `src/quality/` | Kiểm tra quy tắc chất lượng; ghi dòng lỗi vào `reject_rows` kèm lý do |
| `src/load/` | Nạp staging, dựng `dim_date`, `dim_center`, `dim_technician`, `fact_survey` |
| `src/pipeline.py` | Điểm vào: chạy extract → transform → quality → load → báo cáo |
| `config/config.yaml` | Đường dẫn, tên cột, định dạng ngày, ngưỡng quy tắc |
| `db/star_schema.sql` | DDL kho dữ liệu (SQLite) |
| `tests/` | Unit test |
| `docs/` | Nhật ký thay đổi thiết kế, ảnh kết quả chạy |

## 5. Tài liệu

- Báo cáo Bài tập 1 (SRS, use case, kiến trúc, mô hình dữ liệu, wireframe)
- `docs/thay-doi-thiet-ke.md`: quyết định điều chỉnh thiết kế sau phản hồi BT1

## 6. Trạng thái hiện tại (buổi 8)

- [x] Cấu trúc `src/` gồm extract, transform, quality, load theo sơ đồ data flow
- [x] Đọc 2 file CSV, in số dòng, số cột, tỉ lệ ô trống từng cột
- [x] Hàm chuẩn hóa ngày (8 định dạng cấu hình được); dòng không quy đổi được vào bảng `reject_rows` kèm lý do
- [x] Kiểm tra quy tắc chất lượng: điểm 1–5, nhận xét ≤ 500 ký tự, phiếu đã đóng, trả lời sau ngày đóng, mỗi phiếu một phản hồi
- [x] Nạp staging và kho dữ liệu (`fact_survey` + 3 dimension) theo `db/star_schema.sql`; chạy lại nhiều lần cho cùng kết quả
- [x] 7 unit test đạt (dữ liệu nhỏ tự tạo trong test)
- [ ] Chạy trên 2 file CSV thật và chụp ảnh kết quả lưu vào `docs/`
- [ ] Đối chiếu số liệu chạy thật với Chương 4 (6.350 phiếu đã đóng, 2.600 phản hồi, tỉ lệ phản hồi 40,9%)
- [ ] Kiểm tra tên cột và định dạng ngày của file thật; sửa `config/config.yaml` nếu khác
- [ ] Tên trung tâm đang là tên tạm "Trung tâm n" vì dữ liệu nguồn chưa có tên
- [ ] Chưa làm: truy vấn báo cáo CSAT (Q1–Q5), bảng `customer` và `survey_invitation` (BT2)
- Ghi chú: dùng SQLite cho staging và kho dữ liệu ở giai đoạn này.
