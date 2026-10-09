# Yêu cầu dữ liệu – Luồng L8: Khảo sát hài lòng (CSAT) – Track DA

**Học phần:** Chuyên đề tốt nghiệp 1 – Bài tập 1
**Case study:** khảo sát hài lòng · **Sinh viên:** MOONLASING Moulita – 237480201IS02

Tài liệu này là đặc tả dữ liệu cho Track DA, đi kèm `srs.md`, `erd.drawio` (lược đồ kho dữ liệu) và `wireframe.png`. Thuật ngữ dùng theo Bảng thuật ngữ ở Mục 1 của SRS: **phiếu bảo hành**, **khảo sát hài lòng**, **phản hồi** (một bản ghi trả lời khảo sát), **kỹ thuật viên**, **trung tâm bảo hành**.

---

## 1. Mục tiêu dữ liệu

Cung cấp số liệu để trả lời 5 câu hỏi phân tích (mục 6) phục vụ Quản lý trung tâm, Marketing và Ban giám đốc, qua 3 khung dashboard. Không phân tích cảm xúc văn bản (WON'T, US9).

## 2. Nguồn dữ liệu

| Nguồn | Số dòng | Ghi chú |
|---|---|---|
| `tickets_history.csv` | 7.800 phiếu bảo hành (6.350 phiếu Đã đóng, 1.450 phiếu chưa đóng) | Lịch sử phiếu bảo hành |
| `survey_responses.csv` | 2.600 phản hồi | Phản hồi khảo sát hài lòng |
| `technicians.csv` | Chưa có | Cần để kiểm tra khóa ngoại `technician_id` |

Số liệu đo trên dữ liệu mẫu:

- Tỉ lệ phản hồi: 2.600 / 6.350 ≈ **40,9%**.
- Phản hồi trải 25 tháng (09/2024 – 09/2026), trung bình **104 phản hồi/tháng** (thấp nhất 13, cao nhất 135).
- Điểm hài lòng trung bình **3,92**; tỉ lệ CSAT (điểm 4–5) = 1.819 / 2.600 ≈ **70,0%**.
- Phân bố điểm 1 đến 5: 142 / 233 / 406 / 719 / 1.100. Có **375** phản hồi điểm ≤ 2.
- Khách trả lời sau 1–5 ngày (trung bình ≈ 3 ngày) nên hạn liên kết 7 ngày bao phủ toàn bộ dữ liệu mẫu.
- Mỗi kỹ thuật viên trung bình ≈ 3 phản hồi/tháng (nhiều nhất 17), nên cần cảnh báo "mẫu nhỏ" (< 10 phản hồi) theo FR5.

## 3. Luồng dữ liệu (data flow)

```
tickets_history.csv ─┐
                     ├─► Staging (SQLite) ─► Làm sạch & ghép (ETL) ─► Kho dữ liệu (SQLite) ─► Báo cáo CSAT
survey_responses.csv ┘   stg_ticket,           lọc DA_DONG, kiểm       fact_survey +           theo trung tâm,
                         stg_survey_response   tra, LEFT JOIN          3 bảng dimension        kỹ thuật viên, tháng
```

Các bước ETL:

1. Nạp 2 file CSV vào bảng staging `stg_ticket`, `stg_survey_response`.
2. Chỉ giữ phiếu có `status = 'DA_DONG'`; kiểm tra các quy tắc chất lượng ở mục 7.
3. `LEFT JOIN` phiếu Đã đóng với phản hồi theo `ticket_id` (phiếu không có phản hồi vẫn giữ lại với `has_response = 0`).
4. Nạp `dim_date`, `dim_center`, `dim_technician`, sau đó nạp `fact_survey`.
5. Chạy hằng ngày, hoàn tất trước 06:00 (job ≤ 30 phút) – theo NFR4.

## 4. Lược đồ kho dữ liệu (star schema)

**GRAIN của `fact_survey`: một dòng = một phiếu bảo hành đã đóng (`status = DA_DONG`).**

```
dim_date ◄── closed_date_key ───┐
dim_date ◄── responded_date_key ┤
dim_center ◄── center_key ──────┼── fact_survey
dim_technician ◄─ technician_key┘
```

`dim_date` được dùng hai lần (role-playing): ngày đóng phiếu và ngày trả lời.

## 5. Từ điển dữ liệu

### 5.1. Bảng kho dữ liệu

**fact_survey** (grain: một phiếu bảo hành đã đóng)

| Cột | Kiểu | Khóa | Mô tả | Cho phép NULL |
|---|---|---|---|---|
| ticket_id | BIGINT | PK | Mã phiếu bảo hành | Không |
| closed_date_key | INT | FK → dim_date | Ngày đóng phiếu (dạng YYYYMMDD) | Không |
| responded_date_key | INT | FK → dim_date | Ngày khách trả lời; NULL nếu chưa có phản hồi | Có |
| center_key | INT | FK → dim_center | Trung tâm bảo hành xử lý phiếu | Không |
| technician_key | INT | FK → dim_technician | Kỹ thuật viên xử lý phiếu | Không |
| has_response | SMALLINT | | 1 nếu phiếu có phản hồi, 0 nếu không | Không |
| score | SMALLINT | | Điểm hài lòng 1–5; NULL nếu chưa có phản hồi | Có |
| is_satisfied | SMALLINT | | 1 nếu score ≥ 4, 0 nếu score ≤ 3; NULL nếu chưa có phản hồi | Có |
| response_delay_days | SMALLINT | | Số ngày từ lúc đóng phiếu đến lúc trả lời; NULL nếu chưa có phản hồi | Có |
| comment | TEXT | | Nhận xét của khách (≤ 500 ký tự), tùy chọn | Có |
| responded_at *(bổ sung)* | TIMESTAMP | | Thời điểm trả lời đầy đủ giờ phút – wireframe hiển thị cột "Thời điểm trả lời" | Có |
| customer_phone *(bổ sung)* | VARCHAR(15) | | Số điện thoại khách, lưu đầy đủ; chỉ hiển thị theo quy tắc QT-15 | Có |

**dim_date**

| Cột | Kiểu | Khóa | Mô tả |
|---|---|---|---|
| date_key | INT | PK | Khóa ngày dạng YYYYMMDD |
| full_date | DATE | | Ngày đầy đủ |
| month | SMALLINT | | Tháng (1–12) |
| quarter | SMALLINT | | Quý (1–4) |
| year | SMALLINT | | Năm |
| year_month | CHAR(7) | | Năm-tháng dạng YYYY-MM, dùng cho biểu đồ xu hướng |

**dim_center**

| Cột | Kiểu | Khóa | Mô tả |
|---|---|---|---|
| center_key | INT | PK | Khóa thay thế của trung tâm bảo hành |
| center_id | INT | | Mã trung tâm bảo hành ở hệ thống nguồn (1–6) |
| center_name | VARCHAR(100) | | Tên trung tâm bảo hành |

**dim_technician**

| Cột | Kiểu | Khóa | Mô tả |
|---|---|---|---|
| technician_key | INT | PK | Khóa thay thế của kỹ thuật viên |
| technician_id | INT | | Mã kỹ thuật viên ở hệ thống nguồn (1–38) |
| center_id | INT | | Trung tâm bảo hành kỹ thuật viên thuộc về |

### 5.2. Bảng nguồn (staging)

**stg_survey_response** (từ `survey_responses.csv`)

| Cột | Kiểu | Mô tả | Giá trị hợp lệ | Tỉ lệ thiếu (2.600 dòng) |
|---|---|---|---|---|
| response_id | BIGINT | Khóa chính phản hồi | Duy nhất | 0% |
| ticket_id | BIGINT | Phiếu được khảo sát | Tồn tại trong ticket, duy nhất | 0% |
| score | SMALLINT | Điểm hài lòng | 1–5 | 0% |
| comment | TEXT | Nhận xét | Tùy chọn, ≤ 500 ký tự | 27,54% (716 dòng) |
| responded_at | TIMESTAMP | Thời điểm trả lời | ≥ closed_at của phiếu | 0% |

**stg_ticket** (các cột L8 sử dụng, từ `tickets_history.csv`, 7.800 dòng)

| Cột | Kiểu | Mô tả | Giá trị hợp lệ | Tỉ lệ thiếu |
|---|---|---|---|---|
| ticket_id | BIGINT | Khóa chính phiếu bảo hành | Duy nhất | 0% |
| center_id | INT | Trung tâm bảo hành | 1–6 | 0% |
| technician_id | INT | Kỹ thuật viên | 1–38 | 0% |
| status | VARCHAR(20) | Trạng thái phiếu | DA_PHAN_CONG, DANG_XU_LY, CHO_LINH_KIEN, HOAN_TAT, DA_DONG | 0% |
| closed_at | TIMESTAMP | Thời điểm đóng phiếu | Bắt buộc có khi status = DA_DONG | 18,6% (1.450 dòng, đều là phiếu chưa đóng nên hợp lệ) |

## 6. Câu hỏi phân tích và chỉ số

### 6.1. Câu hỏi phân tích

| Mã | Câu hỏi | Mức chi tiết | Truy về |
|---|---|---|---|
| Q1 | CSAT từng trung tâm bảo hành tháng này là bao nhiêu? | Theo trung tâm, theo tháng | US3, FR4 |
| Q2 | Kỹ thuật viên nào có điểm thấp kéo dài? | Theo kỹ thuật viên, theo quý | US4, FR5 |
| Q3 | CSAT toàn công ty tăng hay giảm so với 12 tháng qua? | Theo tháng | US5, FR6 |
| Q4 | Những phiếu nào bị chấm ≤ 2 trong 7 ngày qua? | Theo phiếu | US6, FR7 |
| Q5 | Tỉ lệ phản hồi (phản hồi / phiếu đã đóng) là bao nhiêu? | Theo trung tâm, theo tháng | US1, US2, FR4 |

### 6.2. Định nghĩa chỉ số

Kỳ báo cáo được xác định theo **tháng đóng phiếu** (`closed_date_key`).

| Chỉ số | Tên kỹ thuật | Công thức |
|---|---|---|
| Điểm hài lòng trung bình | avg_score | `AVG(score)` trên các dòng có `has_response = 1` |
| Tỉ lệ CSAT | csat_rate | `SUM(is_satisfied) / SUM(has_response)` (điểm 4–5 chia tổng số phản hồi) |
| Số phản hồi | response_count | `SUM(has_response)` |
| Tỉ lệ phản hồi | response_rate | `SUM(has_response) / COUNT(*)` (số phản hồi chia số phiếu Đã đóng) |

Quy tắc hiển thị:

- Kỳ không có phản hồi: hiển thị "Chưa có dữ liệu", **không** hiển thị 0 điểm (FR4).
- Kỹ thuật viên có dưới 10 phản hồi trong kỳ: gắn nhãn "mẫu nhỏ" (FR5).

## 7. Quy tắc chất lượng dữ liệu

| Quy tắc | Ngưỡng | Kết quả đo | Đạt |
|---|---|---|---|
| Completeness của score | ≥ 99% | 100% (0 / 2.600 dòng thiếu) | Đạt |
| score thuộc 1–5 | 100% | 100% | Đạt |
| Không trùng ticket_id trong phản hồi | 100% | 0 dòng trùng | Đạt |
| Phản hồi gắn với phiếu có trạng thái Đã đóng | 100% | 2.600 / 2.600 | Đạt |
| responded_at ≥ closed_at | 100% | 2.600 / 2.600 | Đạt |
| ticket_id khớp bảng phiếu (khóa ngoại) | ≥ 99% | 100% (2.600 / 2.600) | Đạt |
| Nhận xét tối đa 500 ký tự | 100% | 100% (dài nhất 36 ký tự) | Đạt |
| Phiếu DA_DONG đều có closed_at | 100% | 6.350 / 6.350 | Đạt |
| technician_id nằm trong 1–38 | 100% | 100%, đủ 38 mã khác nhau | Đạt (kiểm tra gián tiếp) |

**Chưa kiểm tra:** khóa ngoại `technician_id` với `technicians.csv`, vì chưa có file này. Cần kiểm tra lại khi nhận được file. Dữ liệu mẫu rất sạch; các kết quả trên chưa phản ánh dữ liệu thực tế có lỗi.

## 8. Truy vết wireframe → dữ liệu

| Khung dashboard (wireframe) | Trường hiển thị | Nguồn trong kho dữ liệu |
|---|---|---|
| Khung 1 – Thẻ chỉ số | Điểm hài lòng TB, Tỉ lệ CSAT, Số phản hồi, Tỉ lệ phản hồi | `fact_survey` (score, is_satisfied, has_response) lọc theo `dim_center`, `dim_date` |
| Khung 2 – Xu hướng CSAT 12 tháng và bảng theo kỹ thuật viên | Tháng, CSAT, kỹ thuật viên, số phản hồi, điểm TB, nhãn "mẫu nhỏ" | `fact_survey` + `dim_date.year_month` + `dim_technician` |
| Khung 3 – Phản hồi điểm thấp | Mã phiếu, trung tâm, điểm, nhận xét, thời điểm trả lời, số điện thoại | `fact_survey` (ticket_id, score, comment, responded_at, customer_phone) + `dim_center.center_name`; số điện thoại che theo QT-15 |

## 9. Điểm cần xác nhận

- Hai cột đánh dấu *(bổ sung)* (`responded_at`, `customer_phone`) cần có trong nguồn dữ liệu; nếu `tickets_history.csv` không có số điện thoại thì phải sửa wireframe hoặc bổ sung nguồn.
- Cập nhật `erd.drawio` cho khớp với bảng ở mục 5.1 (ví dụ nhãn bảng bên trái phải là `dim_center`).
- Quy tắc che số điện thoại của Marketing và Quản lý trung tâm (QT-15) phải thống nhất giữa SRS và wireframe.

## 10. Ngoài phạm vi

Phân tích cảm xúc nhận xét, thang NPS 0–10, dữ liệu bán hàng và tồn kho, triển khai hạ tầng.
