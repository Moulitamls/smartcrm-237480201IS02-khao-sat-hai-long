# Báo cáo chất lượng dữ liệu — 2026-10-30 14:54:27

## 1. Nguồn

| Nguồn | Số dòng | Số cột |
|---|---|---|
| tickets_history | 7805 | 6 |
| survey_responses | 2606 | 5 |

## 2. Đối chiếu staging ↔ fact

| Chỉ số | Giá trị |
|---|---|
| Dòng stg_ticket | 7805 |
| − Phiếu bị loại (reject_rows) | 12 |
| − Phiếu chưa đóng (không thuộc grain của fact) | 1450 |
| = Dòng fact_survey | 6343 |
| Khớp công thức | ĐẠT |
| Dòng stg_survey_response | 2606 |
| − Phản hồi bị loại | 18 |
| = Phản hồi nằm trong fact (has_response=1) | 2588 |
| Khớp công thức | ĐẠT |

## 3. Dòng bị loại theo lý do

| Bảng | Lý do | Số dòng |
|---|---|---|
| stg_survey_response | nhan_xet_qua_dai | 3 |
| stg_survey_response | phieu_chua_dong | 3 |
| stg_survey_response | score_ngoai_1_5 | 3 |
| stg_survey_response | tra_loi_truoc_ngay_dong | 4 |
| stg_survey_response | trung_phan_hoi | 5 |
| stg_ticket | da_dong_thieu_closed_at | 3 |
| stg_ticket | ngay_dong_khong_doc_duoc | 4 |
| stg_ticket | ticket_id_trung | 5 |

## 4. Lô nạp fact theo ngày

Số lô: 353; tổng dòng ghi: 6343.
