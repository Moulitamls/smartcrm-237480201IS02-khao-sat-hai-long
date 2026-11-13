# Ảnh chụp minh chứng (mục 7 của PDF)

Chụp ngay khi chạy, thấy rõ **lệnh** và **kết quả**. Che secret trước khi chụp (dự án này không có secret). Đặt tên đúng như dưới đây.

| Tệp | Chụp gì | Lệnh |
|---|---|---|
| `bt3-01-test-pass.png` | Bộ test PASS trong container: `19 passed` | `docker compose run --rm pipeline python -m pytest -q src` |
| `bt3-02-compose-ps.png` | `dashboard` healthy, `pipeline` Exited (0) | `docker compose ps -a` |
| `bt3-03-health-dashboard.png` | `ok` và trang dashboard có 4 thẻ, 2 biểu đồ | `curl -s http://localhost:8501/_stcore/health`, mở trình duyệt |
| `bt3-04-white-machine.png` | Phép thử máy trắng: `down -v` → clone theo tag v1.0 vào thư mục trống → 2 lệnh → ps → test | xem `docs/deployment-guide.md` mục 5 |
| `bt3-05-second-run.png` | Chạy pipeline lần hai vẫn `fact_survey = 6350` | `docker compose run --rm pipeline` |
| `sec-1.png`, `sec-6.png`, `TC-12.png` | Kết quả lệnh của checklist mục 1, 6 và test TC-12 | xem `docs/checklist-bao-mat.md` |
