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

---

## Sau phản hồi Bài tập 2 và các điều chỉnh Sprint 2 (buổi 10, 12)

Bảng tóm tắt:

| Mã | Nội dung | Quyết định |
|---|---|---|
| TD-10 | Dimension nạp theo khoá nghiệp vụ, fact nạp theo lô ngày bằng upsert, thay cho xoá và dựng lại bảng | SỬA |
| TD-11 | Thêm dòng "Không xác định" (key = −1) để phiếu thiếu trung tâm hoặc kỹ thuật viên không mất khỏi fact | SỬA |
| TD-12 | Quy tắc "trả lời trước ngày đóng" so theo ngày, không theo giờ | SỬA |
| TD-13 | Thêm đối chiếu staging và fact vào báo cáo chất lượng | THÊM |
| TD-14 | `fact_survey` giữ `comment_length`, `hours_to_respond` thay cho `comment` của từ điển BT1 | LỆCH SO VỚI TỪ ĐIỂN BT1, ghi nhận |
| TD-15 | Hoãn: bảng customer, survey_invitation, xuất Excel, nhắc lần 2, số điện thoại; không làm biểu đồ thứ ba và giao diện đẹp | HOÃN |
| TD-16 | Giữ cấu trúc phẳng trong `src/` (giảng viên không cho tạo thư mục mới); `star_schema.sql` và `config.yaml` nằm trong `src/` | SỬA |
| TD-17 | Hoàn thành từ điển cột cho fact, dimension và bảng hỗ trợ: `docs/data-dictionary.md` | SỬA |
| TD-18 | Vẽ lại lược đồ kho khớp DDL thật (`dim_center`, PK/FK, `technician_name`, bỏ `comment`) | SỬA |
| TD-19 | Dashboard: 4 thẻ chỉ số, dòng ghi nguồn cho từng khung, mặc định 12 tháng gần nhất | SỬA |
| TD-20 | Dữ liệu mẫu có lỗi chủ ý và `config.demo.yaml` để trình bày bảng `reject_rows` | THÊM |
| TD-21 | Đóng gói để chạy được trên máy sạch: CSV trong repo, `requirements.txt` ghim `==`, `.env.example`, `__init__.py`, test không phụ thuộc thư mục chạy | SỬA |

### TD-10 Nạp theo khoá nghiệp vụ và theo lô ngày

- Phản hồi của GV: Chạy nạp dimension bằng khoá nghiệp vụ, rồi nạp fact theo lô ngày; chạy lần hai không nhân đôi dòng.
- Quyết định: SỬA
- Lý do: Upsert (`ON CONFLICT(ticket_id) DO UPDATE`) giữ được dòng đã có và chạy lại không nhân đôi. Phương án xoá rồi nạp lại đơn giản hơn nhưng mất `loaded_at` của lần nạp trước.
- Ảnh hưởng: `src/load/sqlite_loader.py` (`load_dim_business_key`, `load_fact_by_day`); `test_loader.py` có test nạp lần hai. Hạn chế đã biết: dòng bị xoá khỏi CSV nguồn không bị xoá khỏi fact.

### TD-11 Dòng "Không xác định"

- Phản hồi của GV: Số dòng fact ít hơn staging khi JOIN loại dòng có khoá không khớp dimension (lỗi tích hợp thường gặp ở slide buổi 10).
- Quyết định: SỬA
- Lý do: Phiếu thiếu trung tâm hoặc kỹ thuật viên vẫn là phiếu đã đóng; bỏ khỏi fact làm sai CSAT và tỉ lệ phản hồi.
- Ảnh hưởng: Dimension có dòng key = −1; `test_loader.py` kiểm tra trường hợp này.

### TD-12 So sánh ngày trả lời theo NGÀY

- Phản hồi của GV: Không có (phát hiện khi chạy dữ liệu thật).
- Quyết định: SỬA
- Lý do: Nguồn có định dạng chỉ có ngày (dd/mm/yyyy) nên ngày được hiểu là 00:00; so theo giờ làm phản hồi cùng ngày bị loại oan.
- Ảnh hưởng: `src/quality/rules.py` (`check_surveys`) so `dt.normalize()`.

### TD-13 Đối chiếu staging và fact

- Phản hồi của GV: Đếm dòng staging và fact, giải thích chênh lệch.
- Quyết định: THÊM
- Lý do: Fact có grain là phiếu đã đóng nên ít dòng hơn staging; cần công thức để chứng minh chênh lệch có lý do.
- Ảnh hưởng: `src/report.py` (`reconcile`): stg_ticket = fact + phiếu bị loại + phiếu chưa đóng; pipeline in ĐẠT hoặc LỆCH.

### TD-14 Cột của fact lệch với từ điển BT1

- Phản hồi của GV: Không có (tự ghi nhận).
- Quyết định: LỆCH SO VỚI TỪ ĐIỂN BT1, ghi nhận
- Lý do: Nội dung nhận xét và `responded_at` nằm ở staging, phục vụ Q4; fact chỉ cần độ dài nhận xét và số giờ phản hồi để tổng hợp.
- Ảnh hưởng: Từ điển cột mới ở `docs/data-dictionary.md`; số điện thoại không nằm trong fact là đúng thiết kế (TD-05).

### TD-15 Phạm vi đã cắt

- Phản hồi của GV: Slide buổi 10 cho phép cắt chức năng ngoài luồng chính nếu có ghi nhận.
- Quyết định: HOÃN
- Lý do: Ưu tiên luồng end-to-end, test và README (mục không được cắt). Chưa có `customers.csv`.
- Ảnh hưởng: Hoãn bảng `customer`, `survey_invitation`, xuất Excel (FR9), nhắc lần 2 (FR8), số điện thoại trong danh sách điểm thấp; không làm biểu đồ thứ ba. Phân tích cảm xúc nằm ngoài phạm vi (WON'T).

### TD-16 Cấu trúc phẳng trong src/

- Phản hồi của GV: Giảng viên không cho tạo thư mục mới.
- Quyết định: SỬA
- Lý do: Tuân thủ yêu cầu của giảng viên.
- Ảnh hưởng: BT1 ghi `db/star_schema.sql`, nay là `src/star_schema.sql`; `config.yaml` ở `src/`; dashboard ở `src/app.py`; lệnh chạy đã chỉnh trong README.

### TD-17 Từ điển cột cho fact và dimension

- Phản hồi của GV: Từ điển mới mô tả bảng nguồn; cột của fact và dimension chưa có kiểu và mô tả (còn nhắc lại ở BT2).
- Quyết định: SỬA
- Lý do: Từ điển cột là tài liệu đối chiếu giữa DDL, ETL và dashboard.
- Ảnh hưởng: Thêm `docs/data-dictionary.md` (cột, kiểu, khoá, NULL, mô tả) cho `fact_survey`, 3 dimension, `reject_rows`, `etl_run`, 2 bảng staging và danh sách lý do loại.

### TD-18 Lược đồ kho khớp DDL

- Phản hồi của GV: Hình lược đồ ghi nhầm tên bảng chiều trung tâm là `dim_date`.
- Quyết định: SỬA
- Lý do: Hình cũ còn lỗi `FL`, `responded_dtae_key`, `Pk`, `dim_technician` có `center_id`, fact có `comment`, không khớp DDL.
- Ảnh hưởng: Thay `docs/LuocDoKhoDuLieu.drawio.png` bằng hình khớp `src/star_schema.sql`, có legend PK/FK, grain và dòng ngoài phạm vi.

### TD-19 Dashboard có ghi nguồn cho từng khung

- Phản hồi của GV: Ở BT2 dựng dashboard có ghi chú nguồn dữ liệu cho từng khung.
- Quyết định: SỬA
- Lý do: Người xem phải biết số lấy từ bảng nào, công thức nào, cập nhật lúc nào. Wireframe M2 có 4 thẻ chỉ số và biểu đồ 12 tháng (FR6).
- Ảnh hưởng: `src/app.py` thêm thẻ "Số phản hồi", dòng nguồn cho nhóm thẻ, bảng điểm thấp và mỗi biểu đồ (chân hình); bộ lọc mặc định "12 tháng gần nhất", có lựa chọn "Toàn kỳ". Số trong Chương 4 (3,92 · 70,0% · 2.600 · 40,9%) là số của "Toàn kỳ".

### TD-20 Dữ liệu mẫu có lỗi chủ ý

- Phản hồi của GV: Slide buổi 12 kiểm bảng reject có lý do và hành vi khi nhập dữ liệu sai.
- Quyết định: THÊM
- Lý do: CSV thật không có dòng lỗi nên `reject_rows` trống, không chứng minh được các quy tắc chất lượng ở chế độ chạy thật.
- Ảnh hưởng: `src/make_sample_data.py` ghi `data/raw/demo_*.csv` (không ghi đè CSV thật); `src/config.demo.yaml` ghi `data/demo.db` và báo cáo `reports/chatluong-demo-<ngày>.md`.

### TD-21 Đóng gói chạy được trên máy sạch

- Phản hồi của GV: Giảng viên clone theo tag v0.2 và chạy theo README (mục C1).
- Quyết định: SỬA
- Lý do: README cũ trỏ đường dẫn không tồn tại (`config/`, `db/`, `src/dashboard/`, `scripts/`) và link repo bị đứt chữ; CSV bị `.gitignore` chặn nên máy sạch không có dữ liệu.
- Ảnh hưởng: Commit CSV vào `data/raw/`; `requirements.txt` ghim `==`; `.env.example` chỉ chứa biến thật sự dùng (`CSAT_CONFIG`); thêm `__init__.py` cho 4 gói con; `conftest.py` dùng đường dẫn tuyệt đối nên test chạy được từ mọi thư mục.

*Ghi chú: các mục tiếp theo (ở BT3) nối tiếp vào cuối file này với mã TD-22 trở đi.*
