import datetime

import pytz


def days_hours_minutes(td):
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60


def calc_abs_time_delta(announcement_time):
    current_time = datetime.datetime.now(datetime.timezone.utc)
    announcement_time = pytz.UTC.normalize(announcement_time)
    abs_delta = abs(announcement_time - current_time)
    return abs_delta


def get_time_diff(announcement_time, interval):
    diff = calc_abs_time_delta(announcement_time)
    if diff.total_seconds() < (interval / 2):
        return "happening NOW!"
    else:
        days, hours, minutes = days_hours_minutes(diff)
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        return f"in {', '.join(parts)}"
