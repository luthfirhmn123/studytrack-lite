from datetime import datetime, timedelta, timezone
from task_status import get_status, sort_key

NOW = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)


def iso(delta):
    return (NOW + delta).isoformat()


def test_due_in_23_hours_is_due_soon():
    assert get_status(iso(timedelta(hours=23)), False, NOW) == "due_soon"


def test_due_in_exactly_24_hours_is_upcoming():
    assert get_status(iso(timedelta(hours=24)), False, NOW) == "upcoming"


def test_due_in_3_days_is_upcoming():
    assert get_status(iso(timedelta(days=3)), False, NOW) == "upcoming"


def test_past_deadline_is_overdue():
    assert get_status(iso(timedelta(hours=-1)), False, NOW) == "overdue"


def test_completed_task_is_done_even_if_overdue():
    assert get_status(iso(timedelta(days=-5)), True, NOW) == "done"


def test_missing_deadline_is_no_deadline():
    assert get_status(None, False, NOW) == "no_deadline"


def test_due_right_now_is_due_soon():
    assert get_status(iso(timedelta(0)), False, NOW) == "due_soon"


def test_plain_date_is_treated_as_midnight_utc():
    assert get_status("2026-11-10", False, NOW) == "overdue"
    assert get_status("2026-11-11", False, NOW) == "due_soon"


def test_timestamp_with_offset_is_converted_to_utc():
    # 20:00 at +07:00 is 13:00 UTC, one hour after NOW
    assert get_status("2026-11-10T20:00:00+07:00", False, NOW) == "due_soon"


def test_sort_order():
    tasks = [
        {"id": 1, "due_at": iso(timedelta(days=3)), "status": "upcoming"},
        {"id": 2, "due_at": iso(timedelta(days=-1)), "status": "overdue"},
        {"id": 3, "due_at": iso(timedelta(hours=5)), "status": "due_soon"},
        {"id": 4, "due_at": iso(timedelta(days=2)), "status": "done"},
    ]
    tasks.sort(key=sort_key)
    assert [t["id"] for t in tasks] == [3, 2, 1, 4]