import datetime

from app.models import get_current_time


def test_get_current_time_is_aware():
    t = get_current_time()
    assert t.tzinfo is not None
    assert isinstance(t, datetime.datetime)
