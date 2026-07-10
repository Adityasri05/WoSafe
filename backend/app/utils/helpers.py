"""
WoSafe Utilities — Pagination, Geocoding, DateTime, Validators
"""

from datetime import UTC, datetime, timedelta
from math import asin, cos, radians, sin, sqrt


# ═══════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════

def paginate(total: int, page: int, page_size: int) -> dict:
    """Generate pagination metadata."""
    total_pages = max(1, (total + page_size - 1) // page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


# ═══════════════════════════════════════════
# GEOCODING
# ═══════════════════════════════════════════

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in kilometers (Haversine formula)."""
    R = 6371  # Earth's radius in km

    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))

    return R * c


def bounding_box(lat: float, lng: float, radius_km: float) -> tuple[float, float, float, float]:
    """Calculate bounding box for a given center point and radius."""
    delta_lat = radius_km / 111.0
    delta_lng = radius_km / (111.0 * cos(radians(lat)))

    return (
        lat - delta_lat,   # min_lat
        lng - delta_lng,   # min_lng
        lat + delta_lat,   # max_lat
        lng + delta_lng,   # max_lng
    )


def geohash_grid(lat: float, lng: float, precision: int = 4) -> str:
    """Generate a simple grid hash for heatmap bucketing."""
    lat_bucket = round(lat * (10 ** precision)) / (10 ** precision)
    lng_bucket = round(lng * (10 ** precision)) / (10 ** precision)
    return f"{lat_bucket}:{lng_bucket}"


# ═══════════════════════════════════════════
# DATETIME UTILITIES
# ═══════════════════════════════════════════

def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def time_ago(dt: datetime) -> str:
    """Convert a datetime to a human-readable 'time ago' string."""
    now = utc_now()
    if dt.tzinfo is not None and now.tzinfo is None:
        dt = dt.replace(tzinfo=None)
    elif dt.tzinfo is None and now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}m ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days}d ago"
    else:
        return dt.strftime("%b %d, %Y")


def time_of_day_category(hour: int) -> str:
    """Categorize the time of day for risk assessment."""
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    elif 21 <= hour or hour < 2:
        return "night"
    else:
        return "late_night"
