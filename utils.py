"""Small helper functions shared by the Streamlit UI and scheduler."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from io import StringIO

import pandas as pd


PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
DAY_ORDER = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


def parse_date(value: str | date) -> date:
    """Convert a database date string into a date object."""
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_time(value: str | time) -> time:
    """Convert a database time string into a time object."""
    if isinstance(value, time):
        return value
    return datetime.strptime(value, "%H:%M").time()


def format_date(value: str | date) -> str:
    return parse_date(value).strftime("%b %d, %Y")


def format_time(value: str | time) -> str:
    return parse_time(value).strftime("%I:%M %p")


def hours_between(start: str | time, end: str | time) -> float:
    """Return the number of hours in a study block."""
    start_time = parse_time(start)
    end_time = parse_time(end)
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    if end_dt <= start_dt:
        return 0.0
    return round((end_dt - start_dt).total_seconds() / 3600, 2)


def priority_score(priority: str) -> int:
    return PRIORITY_SCORES.get(priority.lower(), 1)


def urgency_score(due_date: str | date, today: date | None = None) -> float:
    """Give nearer due dates a higher score, while keeping overdue tasks urgent."""
    today = today or date.today()
    days_until_due = (parse_date(due_date) - today).days
    if days_until_due < 0:
        return 12.0
    if days_until_due == 0:
        return 10.0
    return max(1.0, 10.0 / (days_until_due + 1))


def task_score(task: dict, today: date | None = None) -> float:
    """Combine priority and urgency into one sortable scheduling score."""
    return round(priority_score(task["priority"]) * 2 + urgency_score(task["due_date"], today), 2)


def week_start(reference_date: date | None = None) -> date:
    reference_date = reference_date or date.today()
    return reference_date - timedelta(days=reference_date.weekday())


def day_to_date(day_name: str, reference_date: date | None = None) -> date:
    return week_start(reference_date) + timedelta(days=DAY_ORDER[day_name])


def dataframe_to_csv(dataframe: pd.DataFrame) -> str:
    """Return CSV text suitable for Streamlit download buttons."""
    buffer = StringIO()
    dataframe.to_csv(buffer, index=False)
    return buffer.getvalue()
