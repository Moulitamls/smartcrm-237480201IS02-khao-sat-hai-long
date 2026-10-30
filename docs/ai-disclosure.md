# Phụ lục – Bảng khai báo sử dụng công cụ AI (BT2)

**Học phần:** Chuyên đề tốt nghiệp 1 – Bài tập 2: Hiện thực hoá Module Cốt lõi
**Luồng nghiệp vụ:** L8 – Khảo sát hài lòng khách hàng sau bảo hành (CSAT) · **Track:** DA
**Sinh viên:** MOONLASING Moulita · **MSSV:** 237480201IS02
**Repo / tag:** https://github.com/Moulitamls/smartcrm-237480201IS02-khao-sat-hai-long · `v0.2`

## 1. Bảng khai báo (BT2)

| Công cụ | Dùng vào việc gì | Áp dụng ở tệp / hàm nào | Em đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Rà soát repo đối chiếu đề BT2 và bảng tiêu chí C1–C7, D1–D4; chỉ liệt kê điểm thiếu, không sửa mã ở bước này | Toàn repo (không sinh mã ở bước này) | Em tự kiểm tra từng điểm Claude nêu: `git tag -l` rỗng; `src/config.demo.yaml` và `docs/data-dictionary.md` không có trong repo; `docs/ai-disclosure.md` còn là bản BT1; chạy `python -m pytest -q src` và chạy pipeline hai lần để xác nhận số dòng không nhân đôi |
| Claude (Anthropic) | Soạn 8 hàm kiểm chất lượng CL1–CL8, mỗi hàm trả số dòng lỗi, tổng dòng, tỉ lệ lỗi và kết quả so với ngưỡng; soạn hàm `run_all` gọi cả 8 hàm | `src/quality/metrics.py`: `cl1_ticket_id_hop_le` … `cl8_moi_phieu_mot_phan_hoi`, `run_all` | Em đã đọc từng hàm và giải thích được từng điều kiện; tự tính tay một ca (4 phiếu, 1 mã trùng → CL1 = 1/4 = 25%) rồi so với kết quả chạy; chạy pipeline trên dữ liệu thật được CL1–CL8 đều 0 lỗi; chạy với `config.demo.yaml` được số lỗi khớp số dòng chèn lỗi trong `make_sample_data.py` |
| Claude (Anthropic) | Soạn 5 test cho các hàm CL: dữ liệu sạch (0 lỗi), biên điểm 1/5 hợp lệ và 0/6 lỗi (CL4 = 2/4), biên nhận xét 500/501 ký tự, dữ liệu sai nhiều loại, bảng rỗng không chia cho 0 | `src/test_metrics.py` | Em chạy `python -m pytest -q src`, kết quả `23 passed` (18 test cũ + 5 test mới); em sửa lại một kỳ vọng sai ở `test_du_lieu_sai_nhieu_loai_moi_phep_dem_dung` (CL3 đếm cả phiếu thiếu `closed_at` lẫn phiếu có `closed_at` không đọc được, nên đúng là 2 chứ không phải 1) |
| Claude (Anthropic) | Nối CL1–CL8 vào luồng chạy và báo cáo; thêm ngưỡng `max_error_rate` vào cấu hình | `src/pipeline.py` (import `metrics`, gọi `qm.run_all`, in 8 dòng `[quality]`); `src/report.py` (mục 3 của báo cáo chất lượng); `src/config.yaml` (`rules.max_error_rate`) | Em chạy pipeline hai lần: `fact_survey` giữ 6350 dòng, `[reconcile]` vẫn `ĐẠT`; mở `reports/chatluong-<ngày>.md` thấy bảng CL1–CL8 có cột tỉ lệ lỗi; `check_tickets` / `check_surveys` và bảng `reject_rows` không bị sửa |
| Claude (Anthropic) | Soạn tệp cấu hình cho dữ liệu mẫu có lỗi chủ ý và từ điển cột | `src/config.demo.yaml`; `docs/data-dictionary.md` | Chạy `python -m src.make_sample_data` rồi `python -m src.pipeline --config src/config.demo.yaml`: `reject_rows` có 8 loại lý do, chạy lần hai `fact_survey` vẫn 6343 dòng; đối chiếu từng cột của từ điển với `src/star_schema.sql` và `src/load/sqlite_loader.py` |
| Claude (Anthropic) | Cập nhật tài liệu theo thay đổi ở trên; thêm gói con Python | `README.md` (số test, bảng cấu trúc, kết quả đúng); `docs/thay-doi-thiet-ke.md` (TD-22); `.gitignore` (`reports/`); `src/__init__.py` và `__init__.py` của 4 gói con | Em đọc lại từng dòng đã sửa; làm đúng README trong thư mục trống (`git clone --branch v0.2`) và không phải gõ thêm lệnh nào |
| Claude (Anthropic) | Tra mã commit sửa từng lỗi để điền vào bug log (dùng `git log -S`) | `docs/bug-log.md`, dòng "Commit" của BUG-01 đến BUG-06 | Em chạy `git show <mã>` cho từng commit để xác nhận commit đó thật sự chứa thay đổi sửa lỗi tương ứng |

## 2. Các phần em tự làm hoàn toàn

*[SV xác nhận trước khi nộp: các phần không nằm trong bảng ở mục 1 do em tự làm, gồm `src/extract/`, `src/transform/`, `src/quality/rules.py`, `src/quality/rejects.py`, `src/load/`, `src/queries.py`, `src/charts.py`, `src/app.py`, `src/export_charts.py`, 18 test đã có trước đó, sơ đồ và ảnh minh chứng. Nếu có phần nào em từng dùng AI hỗ trợ (kể cả gợi ý hàm, giải thích lỗi, soát văn phong), phải thêm vào bảng ở mục 1; nếu không dùng thì giữ nguyên câu này và xoá ngoặc vuông.]*

## 3. Bảng khai báo của BT1 (giữ lại để truy vết)

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Rà soát bản DOCX BT1 so với đề bài, liệt kê điểm còn thiếu so với 11 mục kiểm chứng | Báo cáo BT1 (DOCX) | Đối chiếu từng điểm Claude nêu với file đề bài PDF, tự sửa nội dung trong tài liệu, chạy lại Ctrl+F kiểm tra thuật ngữ |

## 4. Cam kết

**Tôi xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung này.**

- Họ tên: **MOONLASING Moulita**
- MSSV: **237480201IS02**
- Ngày: *[30/10/2026]*
