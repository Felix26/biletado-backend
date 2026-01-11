import uuid
from datetime import date, datetime, timezone


def _monkeypatch_auth(monkeypatch):
    # Make require_auth accept our fake tokens
    monkeypatch.setattr('app.auth.get_jwks_client', lambda: {
        "keys": [
            {"kid": "test-kid", "kty": "RSA", "use": "sig", "n": "test-modulus", "e": "AQAB"}
        ]
    })
    monkeypatch.setattr('app.auth.jwt.decode', lambda token, key, algorithms, options: {"sub": "user1"})
    monkeypatch.setattr('app.auth.jwt.get_unverified_header', lambda token: {"kid": "test-kid"})

# Simple proxy to avoid evaluating comparisons on class attributes
class AttrProxy:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self

    def __ne__(self, other):
        return self

    def __lt__(self, other):
        return self

    def __le__(self, other):
        return self

    def __gt__(self, other):
        return self

    def __ge__(self, other):
        return self


# Fake token used for Authorization header
fake_token = (
    "eyJhbGciOiJSUzI1NiIsImtpZCI6InRlc3Qta2lkIn0."
    "eyJzdWIiOiJ1c2VyMSJ9."
    "c2lnbmF0dXJl"
)

class DummyQuery:
    def __init__(self, items=None):
        self._items = items or []

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None

    def get(self, id_):
        for it in self._items:
            if str(it.id) == str(id_):
                return it
        return None


class DummyReservation:
    query = DummyQuery([])

    def __init__(self, room_id=None, start_date=None, end_date=None):
        self.id = uuid.uuid4()
        self.room_id = room_id or uuid.uuid4()
        self.start_date = start_date or date.today()
        self.end_date = end_date or date.today()
        self.deleted_at = None

    # class-level proxies to avoid runtime comparison errors
    room_id = AttrProxy('room_id')
    start_date = AttrProxy('start_date')
    end_date = AttrProxy('end_date')
    deleted_at = AttrProxy('deleted_at')
    id = AttrProxy('id')

    def to_dict(self):
        return {
            "id": str(self.id),
            "room_id": str(self.room_id),
            "from": self.start_date.isoformat(),
            "to": self.end_date.isoformat(),
        }


class DummyDBSession:
    def add(self, o):
        pass

    def commit(self):
        pass

    def delete(self, o):
        pass


class DummyDB:
    def __init__(self):
        self.session = DummyDBSession()


def test_get_reservations_empty(monkeypatch, client):
    from app import routes

    routes.Reservation.query = DummyQuery([])

    r = client.get('/api/v3/reservations/reservations')
    assert r.status_code == 200
    assert r.get_json() == {"reservations": []}


def test_create_reservation_bad_input_missing_fields(client):
    r = client.post('/api/v3/reservations/reservations', json={})
    assert r.status_code == 400


def test_create_reservation_from_after_to(client):
    # from same as to -> bad request
    payload = {"room_id": str(uuid.uuid4()), "from": "2025-01-02", "to": "2025-01-02"}
    r = client.post('/api/v3/reservations/reservations', json=payload)
    assert r.status_code == 400


def test_create_reservation_overlap(monkeypatch, client):
    from app import routes

    # Simulate overlap found
    existing = DummyReservation(start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))
    routes.Reservation.query = DummyQuery([existing])

    payload = {"room_id": str(existing.room_id), "from": "2025-01-02", "to": "2025-01-03"}
    r = client.post('/api/v3/reservations/reservations', json=payload)
    assert r.status_code == 400


def test_create_reservation_success(monkeypatch, client):
    from app import routes

    # No overlap
    routes.Reservation = DummyReservation
    routes.db = DummyDB()

    payload = {"room_id": str(uuid.uuid4()), "from": "2025-02-01", "to": "2025-02-03"}
    r = client.post('/api/v3/reservations/reservations', json=payload)
    assert r.status_code == 201
    assert 'Location' in r.headers


def test_get_reservation_invalid_uuid(monkeypatch, client):
    r = client.get('/api/v3/reservations/reservations/not-a-uuid')
    assert r.status_code == 404


def test_get_reservation_not_found(monkeypatch, client):
    from app import routes
    routes.Reservation = DummyReservation
    routes.Reservation.query = DummyQuery([])

    r = client.get(f'/api/v3/reservations/reservations/{uuid.uuid4()}')
    assert r.status_code == 404


def test_get_reservation_found(monkeypatch, client):
    from app import routes
    res = DummyReservation(start_date=date(2025, 3, 1), end_date=date(2025, 3, 2))
    routes.Reservation = DummyReservation
    routes.Reservation.query = DummyQuery([res])

    r = client.get(f'/api/v3/reservations/reservations/{res.id}')
    assert r.status_code == 200
    assert r.get_json()["id"] == str(res.id)


def test_delete_invalid_id_requires_auth(monkeypatch, client):
    _monkeypatch_auth(monkeypatch)
    r = client.delete('/api/v3/reservations/reservations/not-a-uuid', headers={"Authorization": f"Bearer {fake_token}"})
    # Auth decorator runs first; we provided auth so inner code runs and returns 400
    assert r.status_code == 400


def test_delete_not_found(monkeypatch, client):
    from app import routes
    _monkeypatch_auth(monkeypatch)
    routes.Reservation = DummyReservation
    routes.Reservation.query = DummyQuery([])

    r = client.delete(f'/api/v3/reservations/reservations/{uuid.uuid4()}', headers={"Authorization": f"Bearer {fake_token}"})
    assert r.status_code == 404


def test_delete_soft_and_permanent(monkeypatch, client):
    from app import routes
    _monkeypatch_auth(monkeypatch)

    # Soft-delete
    res = DummyReservation()
    routes.Reservation = DummyReservation
    routes.Reservation.query = DummyQuery([res])
    routes.db = DummyDB()
    # soft delete
    r = client.delete(f'/api/v3/reservations/reservations/{res.id}', headers={"Authorization": f"Bearer {fake_token}"})
    assert r.status_code == 204

    # Permanent delete
    res2 = DummyReservation()
    routes.Reservation.query = DummyQuery([res2])
    r2 = client.delete(f'/api/v3/reservations/reservations/{res2.id}?permanent=true', headers={"Authorization": f"Bearer {fake_token}"})
    assert r2.status_code == 204
