from app import app
import json

def test_latest_report_no_file(tmp_path, monkeypatch):
    # artifacts klasörü yoksa 404 dönmeli
    monkeypatch.chdir(tmp_path)
    client = app.test_client()
    resp = client.get("/latest-report")
    assert resp.status_code == 404

def test_latest_report(tmp_path, monkeypatch):
    # bir rapor dosyası yarat
    report = {"date":"2025-07-16","min":0.5,"max":1.5,"avg":1.0}
    (tmp_path / "artifacts").mkdir()
    f = tmp_path / "artifacts" / "report_20250716.json"
    f.write_text(json.dumps(report))
    monkeypatch.chdir(tmp_path)
    client = app.test_client()
    resp = client.get("/latest-report")
    assert resp.status_code == 200
    assert json.loads(resp.data) == report
