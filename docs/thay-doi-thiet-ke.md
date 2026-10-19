# Nhật ký thay đổi thiết kế

Đề tài: Áp dụng mô hình Smart CRM vào công ty Mekong Mobile với luồng nghiệp vụ Khảo sát hài lòng CSAT (L8)
SVTH: MOONLASING Moulita · MSSV: 237480201IS02 · GVHD: ThS. Nguyễn Minh Tân

## Sau phản hồi Bài tập 1 (buổi 8, ngày 19/10/2026)

Điểm BT1: 6.5/10 (Đầy đủ 8.5 · Kỹ thuật 4.75 · Nhất quán 6 · Trình bày 5.5).

Bảng tóm tắt:

| Mã | Nội dung | Quyết định |
|---|---|---|
| TD-01 | Sửa bảng chiều trung tâm bị đặt tên `dim_date` thành `dim_center` | SỬA |
| TD-02 | Sửa lỗi chính tả và ký hiệu trên các sơ đồ | SỬA |
| TD-03 | Bổ sung kiểu dữ liệu và mô tả cho cột của fact và dimension | SỬA |
| TD-04 | Số điện thoại ở Màn hình 3 chưa có trong mô hình dữ liệu: thêm bảng nguồn `customer` | SỬA |
| TD-05 | Không đưa số điện thoại vào star schema (không thêm `dim_customer`) | GIỮ NGUYÊN |
| TD-06 | Viết lại câu lập luận kiến trúc số 3 theo NFR | SỬA |
| TD-07 | Thêm chú thích ký hiệu (legend) và dòng "Ngoài phạm vi" cho các sơ đồ | SỬA |
| TD-08 | Xóa các câu hướng dẫn của đề còn sót trong báo cáo | SỬA |
| TD-09 | Đặt link GitHub ở trang bìa, viết commit message rõ nội dung | SỬA |

---

### TD-01 Đổi tên bảng chiều trung tâm thành dim_center

- Phản hồi của GV: Star schema đặt tên bảng chiều trung tâm là `dim_date`, trùng với bảng chiều ngày.
- Quyết định: SỬA
- Lý do: Hai bảng khác nhau mang cùng tên làm sai lược đồ và gây lỗi khi viết script ETL ở BT2. Bảng này chứa `center_key`, `center_id`, `center_name` nên tên đúng là `dim_center`.
- Ảnh hưởng: Cập nhật sơ đồ star schema (file `.drawio`) và mục 2, Chương 4 của báo cáo; các script ETL dùng tên `dim_center`.

### TD-02 Sửa lỗi chính tả và ký hiệu trên sơ đồ

- Phản hồi của GV: Phần Nhất quán và Trình bày bị trừ điểm do lỗi chữ trên sơ đồ.
- Quyết định: SỬA
- Lý do: Tên cột và tên thành phần phải trùng với tên dùng trong mã và tài liệu, nếu sai thì không đối chiếu được.
- Ảnh hưởng: Sửa `FL center_key` thành `FK center_key`; `responded_dtae_key` thành `responded_date_key`; `Pk` thành `PK`; `RESET/JSON` thành `REST/JSON`; `Servey Service` thành `Survey Service`; `dashbord` thành `dashboard`; `survey_reponses.csv` thành `survey_responses.csv`. Cập nhật sơ đồ kiến trúc, data flow và star schema.

### TD-03 Bổ sung kiểu dữ liệu và mô tả cột cho fact_survey và các dim

- Phản hồi của GV: Các cột của fact và dimension chưa có kiểu dữ liệu và mô tả.
- Quyết định: SỬA
- Lý do: Bảng kiểu dữ liệu là đầu vào trực tiếp của script ETL và DDL ở BT2; thiếu bảng này thì không viết được bước load.
- Ảnh hưởng: Thêm mục "Đặc tả cột" vào Chương 4 cho `fact_survey`, `dim_date`, `dim_center`, `dim_technician` (cột, kiểu, khóa, cho phép NULL hay không, mô tả). `score`, `is_satisfied`, `responded_date_key`, `response_delay_days` và `comment` cho phép NULL vì phiếu chưa có phản hồi vẫn nằm trong fact (grain: một dòng = một phiếu đã đóng).

### TD-04 Thêm bảng nguồn customer để có số điện thoại cho UC6

- Phản hồi của GV: Màn hình 3 có cột số điện thoại nhưng mô hình dữ liệu không có cột này.
- Quyết định: SỬA
- Lý do: FR7 yêu cầu danh sách phản hồi điểm ≤ 2 hiển thị số điện thoại khách để Marketing chăm sóc, nên dữ liệu này phải có nguồn. Số điện thoại được lấy từ bảng nguồn `customer` (customer_id, full_name, phone), nối qua `ticket.customer_id`, và che theo vai trò khi truy vấn (QT-15, FR10). Marketing xem đầy đủ ở Màn hình 3 (ngoại lệ của QT-15); các màn hình và vai trò khác che dạng 090****567.
- Ảnh hưởng: Thêm `customer` và cột `ticket.customer_id` vào từ điển dữ liệu (mục 3.2, Chương 4). Ghi chú chưa có file `customers.csv` nên chưa kiểm tra được chất lượng cột này. Cập nhật Chương 5 theo kết luận trên, bỏ câu "phụ thuộc quyết định về mâu thuẫn QT-15 và US6".

### TD-05 Giữ nguyên: không thêm dim_customer vào star schema

- Phản hồi của GV: Chưa có chỗ chứa số điện thoại trong mô hình dữ liệu (xem TD-04); có thể giải quyết bằng cách thêm vào kho dữ liệu.
- Quyết định: GIỮ NGUYÊN
- Lý do: Các câu hỏi phân tích Q1–Q5 chỉ cần chiều trung tâm, kỹ thuật viên và thời gian. Số điện thoại chỉ dùng cho danh sách UC6 theo từng phiếu, không dùng để tổng hợp. Đưa dữ liệu cá nhân vào kho báo cáo làm nặng mô hình và tăng rủi ro lộ thông tin, trong khi không phục vụ câu hỏi phân tích nào.
- Ảnh hưởng: Không. Star schema giữ 1 fact và 3 dimension. Ghi chú lý do vào mục 2, Chương 4.

### TD-06 Viết lại câu lập luận kiến trúc số 3 theo NFR

- Phản hồi của GV: Câu lập luận 3 dựa vào QT-10, không phải NFR; cần đủ 3 câu gắn mã NFR.
- Quyết định: SỬA
- Lý do: Phần lập luận kiến trúc phải chứng minh lựa chọn thiết kế đáp ứng yêu cầu phi chức năng đo được. Câu mới dựa trên NFR2 (form khảo sát tải xong trong ≤ 2 giây với 95% lượt truy cập): chọn kiểm tra token, phiếu và hạn liên kết bằng một truy vấn theo khóa duy nhất (index trên `token` và `ticket_id`), form React tải nhẹ và không gọi dịch vụ ngoài; đánh đổi là phải tạo và bảo trì index, token phải đủ ngẫu nhiên.
- Ảnh hưởng: Sửa mục 2, Chương 3. Ý về ràng buộc UNIQUE theo QT-10 được giữ lại làm câu bổ sung (câu 4) vì vẫn là lập luận đúng, chỉ không thuộc nhóm dựa NFR.

### TD-07 Thêm legend và dòng "Ngoài phạm vi" cho các sơ đồ

- Phản hồi của GV: Các sơ đồ chưa có chú thích ký hiệu; sơ đồ kiến trúc chưa có dòng NGOÀI PHẠM VI.
- Quyết định: SỬA
- Lý do: Người đọc cần hiểu màu và nét vẽ mà không phải đoán; dòng ngoài phạm vi giúp ranh giới đề tài rõ ràng.
- Ảnh hưởng: Use Case: màu xanh lá = MUST, xanh dương = SHOULD, vàng = COULD, nét đứt = `<<extend>>`, viền đậm = use case đặc tả chi tiết. Kiến trúc: chú thích loại mũi tên (REST/JSON, truy vấn SQL, gửi tin) và dòng "Ngoài phạm vi: xác thực SSO, phân tích cảm xúc văn bản, container hóa". Data flow và star schema: chú thích màu các tầng và ký hiệu PK, FK.

### TD-08 Xóa câu hướng dẫn của đề còn sót

- Phản hồi của GV: Bài còn sót các câu như "Mũi tên cần vẽ…", "vẽ cho khớp với lựa chọn đó".
- Quyết định: SỬA
- Lý do: Đó là văn bản hướng dẫn của đề, không phải nội dung báo cáo.
- Ảnh hưởng: Chương 3: xóa "Mũi tên cần vẽ…" và "Dòng chú thích dưới hình, ví dụ…", bỏ chữ "(vẽ thành khối)" ở tiêu đề cột. Chương 5: viết lại "Vẽ thêm các khung trạng thái…" và "vẽ cho khớp với lựa chọn đó" thành câu khẳng định. Phụ lục AI: viết lại ô "Dùng vào việc gì" bị lặp câu.

### TD-09 Link GitHub ở trang bìa và commit message rõ nội dung

- Phản hồi của GV: Link GitHub cần đặt ở trang bìa; commit không để "Add files via upload".
- Quyết định: SỬA
- Lý do: Giảng viên cần mở repo ngay từ trang bìa và đọc được lịch sử làm việc theo từng đơn vị công việc.
- Ảnh hưởng: Thêm link repo (nhánh chính, không trỏ vào một commit cụ thể) dưới dòng GVHD ở trang bìa. Từ buổi 8 dùng Conventional Commits, ví dụ: `docs: điều chỉnh thiết kế theo phản hồi BT1`, `chore: khung src/ theo sơ đồ kiến trúc`, `feat: ...`, `docs: README mục 2 và mục 6`.

---

*Ghi chú: các mục tiếp theo (sau phản hồi BT2, ở BT3) nối tiếp vào cuối file này với mã TD-10 trở đi.*
