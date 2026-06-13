from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = timezone.utc


def now_utc_naive() -> datetime:
    """Current UTC time stored as timezone-naive datetime for SQLite compatibility."""
    return datetime.now(UTC).replace(tzinfo=None)


def ensure_utc_naive(dt: datetime) -> datetime:
    """Normalize any datetime to UTC-naive for internal storage/calculation."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(UTC).replace(tzinfo=None)


def utc_naive_to_et(dt: datetime) -> datetime:
    """Convert UTC-naive internal datetime to timezone-aware US Eastern datetime."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(ET)


def format_et(dt: datetime, with_seconds: bool = False) -> str:
    """Format datetime in US Eastern Time with weekday."""
    if dt is None:
        return ""
    et = utc_naive_to_et(dt)
    fmt = "%a %Y-%m-%d %H:%M:%S %Z" if with_seconds else "%a %Y-%m-%d %H:%M %Z"
    return et.strftime(fmt)
