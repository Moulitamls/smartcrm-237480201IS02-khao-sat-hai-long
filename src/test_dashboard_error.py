"""BUG-07: khi kho dữ liệu chưa sẵn sàng, dashboard không được lộ câu SQL / tên bảng / đường dẫn."""
from pathlib import Path
import yaml
from streamlit.testing.v1 import AppTest


def test_loi_dashboard_khong_lo_cau_truc_ben_trong(cfg, tmp_path, monkeypatch):    # bảo mật A10/A02
    cfg["paths"]["db"] = str(tmp_path / "chua_co_bang.db")            # SQLite tự tạo file rỗng, không có bảng
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    monkeypatch.setenv("CSAT_CONFIG", str(cfg_file))
    at = AppTest.from_file(str(Path(__file__).resolve().parent / "app.py"), default_timeout=30).run()
    assert len(at.error) == 1                                          # có hiện trạng thái lỗi
    msg = at.error[0].value.lower()
    for leak in ("select", "dim_center", "no such table", "sql", str(tmp_path).lower()):
        assert leak not in msg
