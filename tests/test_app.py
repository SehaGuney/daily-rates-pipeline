import json

import pytest

from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_latest_report_no_artifacts(client):
    resp = client.get("/latest-report")
    assert resp.status_code == 404


def test_latest_report_returns_newest(client, tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    old = {"date": "2026-09-24", "base": "EUR", "rates": {"USD": 1.10}}
    new = {"date": "2026-09-25", "base": "EUR", "rates": {"USD": 1.14}}
    (artifacts / "report_2026-09-24.json").write_text(json.dumps(old))
    (artifacts / "report_2026-09-25.json").write_text(json.dumps(new))

    resp = client.get("/latest-report")
    assert resp.status_code == 200
    assert resp.get_json() == new


def test_latest_report_invalid_json(client, tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "report_2026-09-25.json").write_text("not json")

    resp = client.get("/latest-report")
    assert resp.status_code == 500
