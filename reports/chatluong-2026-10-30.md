# Báo cáo chất lượng dữ liệu — 2026-10-30 13:51:59

## 1. Nguồn

| Nguồn | Số dòng | Số cột |
|---|---|---|
| tickets_history | 7800 | 15 |
| survey_responses | 2600 | 5 |

## 2. Đối chiếu staging ↔ fact

| Chỉ số | Giá trị |
|---|---|
| Dòng stg_ticket | 7800 |
| − Phiếu bị loại (reject_rows) | 0 |
| − Phiếu chưa đóng (không thuộc grain của fact) | 1450 |
| = Dòng fact_survey | 6350 |
| Khớp công thức | ĐẠT |
| Dòng stg_survey_response | 2600 |
| − Phản hồi bị loại | 0 |
| = Phản hồi nằm trong fact (has_response=1) | 2600 |
| Khớp công thức | ĐẠT |

## 3. Dòng bị loại theo lý do

| Bảng | Lý do | Số dòng |
|---|---|---|
| — | không có dòng bị loại | 0 |

## 4. Lô nạp fact theo ngày

Số lô: 734; tổng dòng ghi: 6350.
