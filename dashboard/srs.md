# BÁO CÁO BUỔI 4 – SRS LUỒNG L8

**Luồng L8 – Khảo sát hài lòng CSAT · Track DA**
**Họ tên:** MOONLASING Moulita  **MSSV:** 237480201IS02
**Dự án:** Smart CRM – Mekong Mobile (doanh nghiệp mô phỏng)
**Sơ đồ Use Case:** `L8.drawio` (cùng thư mục commit)

> Ghi chú phạm vi: luồng này chỉ làm CSAT thang 1–5. NPS (thang 0–10) nằm ngoài phạm vi vì dữ liệu chỉ có thang 1–5.

---

## 1. User Story

Phạm vi: hệ thống tự gửi khảo sát cho phiếu bảo hành ở trạng thái **Đã đóng**, ghi nhận điểm 1–5 kèm nhận xét của khách hàng, và tổng hợp chỉ số CSAT theo trung tâm, kỹ thuật viên và thời gian.

### 1.1 Danh sách User Story (9 story: 3 MUST, 3 SHOULD, 2 COULD, 1 WON'T)

| Mã | User Story | Nối với | MoSCoW |
| --- | --- | --- | --- |
| US1 | Là Marketing, tôi muốn hệ thống tự gửi khảo sát hài lòng cho khách ngay khi phiếu bảo hành chuyển sang Đã đóng, để biết khách có hài lòng không mà không phải gọi từng người. | V7 | MUST |
| US2 | Là khách hàng, tôi muốn chấm điểm 1–5 và viết nhận xét ngắn sau khi bảo hành xong, để phản ánh trải nghiệm trực tiếp cho công ty thay vì đăng lên mạng xã hội. | V7 | MUST |
| US3 | Là Quản lý trung tâm bảo hành, tôi muốn xem điểm hài lòng trung bình và tỉ lệ CSAT của trung tâm tôi theo tháng, để biết chất lượng dịch vụ mà không phải tổng hợp tay. | V4, V7 | MUST |
| US4 | Là Quản lý trung tâm, tôi muốn xem điểm hài lòng theo từng kỹ thuật viên, để nhận ra ai cần hỗ trợ hoặc ghi nhận. | V7 | SHOULD |
| US5 | Là Ban giám đốc, tôi muốn xem xu hướng CSAT toàn công ty theo tháng, để biết chất lượng dịch vụ đang tăng hay giảm. | V4, V7 | SHOULD |
| US6 | Là Marketing, tôi muốn xem danh sách phản hồi điểm ≤ 2 kèm nhận xét, để gọi chăm sóc khách không hài lòng trước khi họ lên mạng xã hội. | V7 | SHOULD |
| US7 | Là Marketing, tôi muốn hệ thống nhắc khách lần 2 nếu sau 3 ngày chưa trả lời, để tăng tỉ lệ phản hồi. | V7 | COULD |
| US8 | Là Ban giám đốc, tôi muốn xuất báo cáo CSAT ra Excel, để đưa vào báo cáo họp tháng. | V4 | COULD |
| US9 | Là Marketing, tôi muốn hệ thống tự phân tích cảm xúc của nhận xét văn bản, để biết nguyên nhân chung gây không hài lòng. | V7, V8 | WON'T (đợt này) |

### 1.2 Tiêu chí chấp nhận Given–When–Then cho story MUST (8 tiêu chí, trong đó 4 ngoại lệ)

Vòng đời trạng thái phiếu: Đã phân công → Đang xử lý / Chờ linh kiện → **Hoàn tất** → **Đã đóng**. Khảo sát chỉ gửi khi phiếu sang Đã đóng.

**US1**

1. **Given** phiếu đang ở trạng thái Hoàn tất. **When** phiếu chuyển sang Đã đóng. **Then** hệ thống gửi khảo sát cho khách trong vòng 15 phút.
2. *(Ngoại lệ)* **Given** phiếu đang ở trạng thái Đang xử lý. **When** đến lượt quét gửi khảo sát. **Then** hệ thống không gửi (QT-10).
3. *(Ngoại lệ)* **Given** phiếu đã gửi khảo sát hoặc đã có phản hồi. **When** phiếu được xét lại. **Then** hệ thống không gửi lần nữa (QT-10).

**US2**

4. **Given** khách mở liên kết khảo sát hợp lệ. **When** khách chọn điểm 4 và gửi. **Then** hệ thống lưu điểm, thời điểm trả lời và hiển thị lời cảm ơn.
5. **Given** khách đang ở form khảo sát. **When** khách chọn điểm 2 và nhập nhận xét "sửa lâu quá". **Then** hệ thống lưu cả điểm và nhận xét.
6. *(Ngoại lệ)* **Given** phiếu đã có phản hồi. **When** khách mở lại liên kết và gửi lần nữa. **Then** hệ thống từ chối và báo "Bạn đã gửi khảo sát cho phiếu này" (QT-10).

**US3**

7. **Given** trung tâm Quận 10 có 40 phản hồi trong tháng 9. **When** Quản lý trung tâm Quận 10 mở báo cáo tháng 9. **Then** hiển thị điểm trung bình, tỉ lệ CSAT và số phản hồi của đúng trung tâm này (QT-14).
8. *(Ngoại lệ)* **Given** trung tâm chưa có phản hồi nào trong tháng được chọn. **When** mở báo cáo. **Then** hiển thị "Chưa có dữ liệu", không hiển thị 0 điểm.

---

## 2. Use Case

Sơ đồ (file `L8.drawio`) có **6 actor** (Khách hàng, Marketing, Quản lý trung tâm bảo hành, Ban giám đốc, Bộ lập lịch, Kênh gửi tin nhắn) và **8 use case**. US9 là WON'T nên không vẽ.

### 2.1 Danh sách use case

| Mã | Use case | Actor | User Story | MoSCoW |
| --- | --- | --- | --- | --- |
| UC1 | Gửi khảo sát hài lòng cho phiếu đã đóng | Bộ lập lịch, Kênh gửi tin nhắn | US1 | MUST |
| UC2 | Trả lời khảo sát hài lòng | Khách hàng | US2 | MUST |
| UC3 | Xem CSAT theo trung tâm | Quản lý trung tâm, Ban giám đốc | US3 | MUST |
| UC4 | Xem CSAT theo kỹ thuật viên | Quản lý trung tâm | US4 | SHOULD |
| UC5 | Xem xu hướng CSAT theo thời gian | Ban giám đốc | US5 | SHOULD |
| UC6 | Xem danh sách phản hồi điểm thấp | Marketing, Quản lý trung tâm | US6 | SHOULD |
| UC7 | Gửi nhắc khảo sát lần 2 (`<<extend>>` UC1) | Bộ lập lịch, Kênh gửi tin nhắn | US7 | COULD |
| UC8 | Xuất báo cáo CSAT ra Excel (`<<extend>>` UC3, UC5) | Ban giám đốc | US8 | COULD |

Marketing là người hưởng lợi của UC1 và UC7 (US1, US7) nhưng không thao tác trực tiếp; hệ thống chạy tự động qua Bộ lập lịch.

### 2.2 Đặc tả UC2 – Trả lời khảo sát hài lòng (5 luồng ngoại lệ)

- **Actor:** Khách hàng
- **Điều kiện trước:** Phiếu ở trạng thái Đã đóng; khách đã nhận liên kết khảo sát; phiếu chưa có phản hồi.
- **Điều kiện sau:** Phản hồi (điểm, nhận xét, thời điểm trả lời) được lưu gắn với đúng phiếu; liên kết không dùng lại được.

**Luồng chính**

1. Khách mở liên kết khảo sát.
2. Hệ thống kiểm tra phiếu hợp lệ (Đã đóng, chưa khảo sát, liên kết còn hạn).
3. Hệ thống hiển thị form: thang điểm 1–5 và ô nhận xét tùy chọn.
4. Khách chọn điểm, có thể nhập nhận xét, rồi bấm Gửi.
5. Hệ thống kiểm tra dữ liệu hợp lệ.
6. Hệ thống lưu phản hồi và thời điểm trả lời.
7. Hệ thống hiển thị lời cảm ơn.

**Luồng ngoại lệ**

- **2a.** Phiếu chưa ở trạng thái Đã đóng → báo "Khảo sát chưa khả dụng", kết thúc.
- **2b.** Phiếu đã có phản hồi (QT-10) → báo "Bạn đã gửi khảo sát cho phiếu này", không lưu thêm, kết thúc.
- **2c.** Liên kết quá hạn 7 ngày hoặc không hợp lệ → báo hết hạn, kết thúc.
- **5a.** Chưa chọn điểm hoặc điểm ngoài 1–5 → báo lỗi, quay lại bước 4.
- **5b.** Nhận xét dài quá 500 ký tự → báo lỗi, quay lại bước 4.

---

## 3. SRS rút gọn (6 mục)

### 3.1 Giới thiệu

Đặc tả yêu cầu cho luồng L8 của Smart CRM – Mekong Mobile, giải quyết vấn đề **V7**: sau bảo hành không có kênh thu phản hồi.

**Ngoài phạm vi:** phân tích văn bản nhận xét (US9); NPS thang 0–10; tạo hay sửa phiếu bảo hành.

| Thuật ngữ | Định nghĩa |
| --- | --- |
| Phiếu bảo hành | Yêu cầu bảo hành hoặc sửa chữa có mã duy nhất và vòng đời trạng thái |
| Khảo sát hài lòng | Phản hồi của khách sau khi phiếu được đóng, thang điểm 1–5 kèm nhận xét |
| Kỹ thuật viên | Nhân viên thực hiện sửa chữa |
| Điểm hài lòng trung bình | Trung bình cộng điểm 1–5 của các phản hồi trong kỳ |
| Tỉ lệ CSAT | Số phản hồi chấm 4–5 chia tổng số phản hồi trong kỳ (định nghĩa đề xuất) |
| Tỉ lệ phản hồi | Số phản hồi chia số phiếu Đã đóng trong kỳ |

### 3.2 Mô tả tổng quan

- **Người dùng:** Khách hàng, Marketing, Quản lý trung tâm, Ban giám đốc. Hệ thống ngoài: Bộ lập lịch, Kênh gửi tin nhắn.
- **Giả định:** Hệ thống phiếu (L2) đã có; khách có số điện thoại hợp lệ để nhận tin.
- **Ràng buộc:** Làm độc lập theo luồng; dùng dữ liệu mẫu `survey_responses.csv` và `tickets_history.csv`.

### 3.3 Yêu cầu chức năng

| Mã | Yêu cầu |
| --- | --- |
| FR1 | Hệ thống tự gửi khảo sát cho phiếu khi chuyển sang trạng thái Đã đóng. |
| FR2 | Mỗi phiếu chỉ được gửi khảo sát và ghi nhận phản hồi một lần. |
| FR3 | Cho phép khách chấm điểm nguyên 1–5 và nhập nhận xét tùy chọn tối đa 500 ký tự. |
| FR4 | Tổng hợp điểm trung bình, tỉ lệ CSAT, số phản hồi và tỉ lệ phản hồi theo trung tâm và theo tháng; kỳ không có phản hồi thì hiển thị "Chưa có dữ liệu", không hiển thị 0 điểm. |
| FR5 | Tổng hợp các chỉ số trên theo kỹ thuật viên, theo tháng và theo quý; cảnh báo "mẫu nhỏ" khi kỹ thuật viên có dưới 10 phản hồi trong kỳ (ngưỡng đề xuất). |
| FR6 | Hiển thị xu hướng CSAT theo tháng toàn công ty (12 tháng gần nhất). |
| FR7 | Liệt kê phản hồi điểm ≤ 2 kèm nhận xét, mã phiếu và trung tâm, có bộ lọc theo khoảng ngày (ví dụ 7 ngày qua). |
| FR8 | Gửi nhắc lần 2 nếu sau 3 ngày chưa có phản hồi. |
| FR9 | Xuất báo cáo CSAT ra file Excel. |
| FR10 | Phân quyền xem theo trung tâm / toàn công ty và che số điện thoại theo vai trò. |
| FR11 | Liên kết khảo sát hết hạn sau 7 ngày kể từ lúc gửi; liên kết hết hạn hoặc không hợp lệ thì từ chối và báo hết hạn. |

### 3.4 Yêu cầu phi chức năng

| Mã | Yêu cầu (có ngưỡng số) |
| --- | --- |
| NFR1 | Khảo sát được gửi trong ≤ 15 phút kể từ lúc phiếu đóng, với ≥ 95% phiếu. |
| NFR2 | Form khảo sát tải xong trong ≤ 2 giây với 95% lượt truy cập. |
| NFR3 | Báo cáo CSAT 12 tháng hiển thị trong ≤ 3 giây. |
| NFR4 | Dữ liệu báo cáo cập nhật mỗi ngày, hoàn tất trước 06:00 (job chạy ≤ 30 phút). |
| NFR5 | Hệ thống khả dụng ≥ 99% trong giờ làm việc 08:00–18:00, thứ Hai đến thứ Bảy. |

### 3.5 Quy tắc nghiệp vụ áp dụng

- **QT-10:** Chỉ gửi khảo sát cho phiếu Đã đóng, mỗi phiếu một lần (FR1, FR2, FR11).
- **QT-13:** Không xóa vật lý phiếu hay phản hồi, chỉ đánh dấu ngừng sử dụng (FR2, FR3).
- **QT-14:** Nhân viên chỉ xem dữ liệu trung tâm mình; Ban giám đốc xem toàn công ty (FR4–FR7, FR10).
- **QT-15:** Số điện thoại che dạng 090****567 trừ Quản lý và Ban giám đốc (FR7, FR10).

### 3.6 Bảng truy vết (không còn ô trống)

| FR | US | Use Case | MoSCoW | NFR / QT liên quan |
| --- | --- | --- | --- | --- |
| FR1 | US1 | UC1 | MUST | NFR1, QT-10 |
| FR2 | US1, US2 | UC1, UC2 | MUST | QT-10, QT-13 |
| FR3 | US2 | UC2 | MUST | NFR2, QT-13 |
| FR4 | US3 | UC3 | MUST | NFR3, NFR4, QT-14 |
| FR5 | US4 | UC4 | SHOULD | NFR3, NFR4, QT-14 |
| FR6 | US5 | UC5 | SHOULD | NFR3, NFR4, QT-14 |
| FR7 | US6 | UC6 | SHOULD | QT-14, QT-15 |
| FR8 | US7 | UC7 | COULD | NFR5 |
| FR9 | US8 | UC8 | COULD | NFR3 |
| FR10 | US3, US4, US6 | UC3, UC4, UC6 | MUST | QT-14, QT-15 |
| FR11 | US2 | UC2 | MUST | QT-10 |

---

## 4. Data requirement specification (Track DA)

### 4.1 Nguồn dữ liệu (số liệu đo trên dữ liệu thật)

- `survey_responses.csv`: 2.600 phản hồi. `tickets_history.csv`: 7.800 phiếu, trong đó 6.350 phiếu Đã đóng.
- Tỉ lệ phản hồi: 2.600 / 6.350 ≈ **40,9%**.
- Phản hồi trải trên 25 tháng (09/2024 – 09/2026), trung bình **104 phản hồi/tháng** (thấp nhất 13, cao nhất 135). Phiếu đóng trải trên 26 tháng (từ 30/08/2024).
- Điểm trung bình toàn bộ: **3,92**. Tỉ lệ CSAT (điểm 4–5): 1.819 / 2.600 ≈ **70,0%**. Phân bố điểm 1 đến 5: 142 / 233 / 406 / 719 / 1.100. Có 375 phản hồi điểm ≤ 2 (cần cho UC6).
- Khách trả lời sau 1–5 ngày kể từ lúc đóng phiếu (trung bình khoảng 3 ngày), nên hạn liên kết 7 ngày bao phủ toàn bộ dữ liệu mẫu.
- Mỗi kỹ thuật viên trung bình chỉ có khoảng **3 phản hồi/tháng** (nhiều nhất 17), nên cần cảnh báo "mẫu nhỏ" khi hiển thị theo kỹ thuật viên (FR5).

### 4.2 Từ điển dữ liệu

**Bảng survey_response** (từ `survey_responses.csv`)

| Cột | Kiểu | Ý nghĩa | Giá trị hợp lệ | Tỉ lệ thiếu (2.600 dòng) |
| --- | --- | --- | --- | --- |
| response_id | BIGINT | Khóa chính | Duy nhất | 0% (0 dòng) |
| ticket_id | BIGINT | Phiếu được khảo sát | Tồn tại trong ticket, duy nhất | 0% (0 dòng) |
| score | SMALLINT | Điểm hài lòng | 1–5 | 0% (0 dòng) |
| comment | TEXT | Nhận xét | Tùy chọn, ≤ 500 ký tự | 27,54% (716 dòng) |
| responded_at | TIMESTAMP | Thời điểm trả lời | ≥ closed_at của phiếu | 0% (0 dòng) |

**Bảng ticket – các cột L8 sử dụng** (từ `tickets_history.csv`, 7.800 dòng)

| Cột | Kiểu | Ý nghĩa | Giá trị hợp lệ | Tỉ lệ thiếu |
| --- | --- | --- | --- | --- |
| ticket_id | BIGINT | Khóa chính | Duy nhất | 0% |
| center_id | INT | Trung tâm bảo hành (dùng cho Q1, Q5) | 1–6 | 0% |
| technician_id | INT | Kỹ thuật viên (dùng cho Q2) | 1–38 | 0% |
| status | VARCHAR | Trạng thái phiếu | DA_PHAN_CONG, DANG_XU_LY, CHO_LINH_KIEN, HOAN_TAT, DA_DONG | 0% |
| closed_at | TIMESTAMP | Thời điểm đóng phiếu | Bắt buộc có khi status = DA_DONG | 18,6% (1.450 dòng, đều là phiếu chưa đóng nên hợp lệ) |

### 4.3 Quy tắc chất lượng dữ liệu

| Quy tắc | Ngưỡng | Kết quả đo | Đạt |
| --- | --- | --- | --- |
| Completeness của score | ≥ 99% | 100% (0 / 2.600 dòng thiếu) | Đạt |
| score thuộc 1–5 | 100% | 100% | Đạt |
| Không trùng ticket_id trong survey_response | 100% | 0 dòng trùng | Đạt |
| Phản hồi gắn với phiếu có trạng thái Đã đóng | 100% | 2.600 / 2.600 phiếu là DA_DONG | Đạt |
| responded_at ≥ closed_at | 100% | 2.600 / 2.600 dòng | Đạt |
| ticket_id khớp bảng phiếu (khóa ngoại) | ≥ 99% | 100% (2.600 / 2.600) | Đạt |
| Nhận xét tối đa 500 ký tự | 100% | 100% (dài nhất 36 ký tự) | Đạt |
| Phiếu DA_DONG đều có closed_at | 100% | 6.350 / 6.350 | Đạt |
| technician_id nằm trong 1–38 | 100% | 100%, đủ 38 mã khác nhau | Đạt (kiểm tra gián tiếp) |

**Chưa kiểm tra:** khóa ngoại technician_id với bảng `technicians.csv`, vì chưa có file này. Kiểm tra gián tiếp: `tickets_history.csv` có đúng 38 mã kỹ thuật viên liên tục từ 1 đến 38, khớp 38 kỹ thuật viên trong case study. Cần kiểm tra lại khi nhận được `technicians.csv`.

Dữ liệu mẫu rất sạch, nên khi báo cáo cần nói rõ các quy tắc trên đều đạt ở dữ liệu mẫu, chưa phản ánh dữ liệu thực tế có lỗi.

### 4.4 Câu hỏi phân tích

| Câu hỏi | Mức chi tiết | Truy về |
| --- | --- | --- |
| Q1: CSAT từng trung tâm tháng này là bao nhiêu? | Theo trung tâm, theo tháng | US3, FR4 |
| Q2: Kỹ thuật viên nào có điểm thấp kéo dài? | Theo kỹ thuật viên, theo quý | US4, FR5 |
| Q3: CSAT toàn công ty tăng hay giảm so với 12 tháng qua? | Theo tháng | US5, FR6 |
| Q4: Những phiếu nào bị chấm ≤ 2 trong 7 ngày qua? | Theo phiếu | US6, FR7 |
| Q5: Tỉ lệ phản hồi (phản hồi / phiếu đã đóng) là bao nhiêu? | Theo trung tâm, theo tháng | US1, US2, FR4 |
