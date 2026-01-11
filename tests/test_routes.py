from app.helpers import Helpers


def test_get_status(client):
    resp = client.get("/api/v3/reservations/status")
    assert resp.status_code == 200
    j = resp.get_json()
    assert "api_version" in j


def test_liveness(client):
    resp = client.get("/api/v3/reservations/health/live")
    assert resp.status_code == 200
    assert resp.get_json() == {"live": True}


def test_readiness_ok(monkeypatch, client):
    monkeypatch.setattr(Helpers, "getDatabaseReady", staticmethod(lambda: (True, "")))
    resp = client.get("/api/v3/reservations/health/ready")
    assert resp.status_code == 200
    assert resp.get_json()["ready"] is True


def test_readiness_fail(monkeypatch, client):
    monkeypatch.setattr(Helpers, "getDatabaseReady", staticmethod(lambda: (False, "no db")))
    resp = client.get("/api/v3/reservations/health/ready")
    assert resp.status_code == 503
    data = resp.get_json()
    assert "errors" in data
