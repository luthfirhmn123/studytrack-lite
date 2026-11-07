from datetime import datetime, timedelta, timezone

DUE_SOON_WINDOW = timedelta(hours=24)
STATUS_ORDER = {"due_soon": 0, "overdue": 1, "upcoming": 2, "no_deadline": 3, "done": 4}


def parse_due(value):
    """Turn stored text (or a datetime) into a UTC datetime, or None."""
    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)  # no timezone given = UTC
    return value.astimezone(timezone.utc)


def get_status(due_at, is_done, now=None):
    if is_done:
        return "done"
    due = parse_due(due_at)
    if due is None:
        return "no_deadline"
    if now is None:
        now = datetime.now(timezone.utc)
    remaining = due - now
    if remaining < timedelta(0):
        return "overdue"
    if remaining < DUE_SOON_WINDOW:
        return "due_soon"
    return "upcoming"


def sort_key(task):
    due = parse_due(task["due_at"]) or datetime.max.replace(tzinfo=timezone.utc)
    return (STATUS_ORDER[task["status"]], due, task["id"])