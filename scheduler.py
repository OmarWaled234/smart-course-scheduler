"""Scheduling algorithm for turning tasks and study blocks into a weekly plan."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd

from utils import DAY_ORDER, day_to_date, hours_between, parse_time, task_score


SESSION_CHUNK_HOURS = 1.5


def _block_start_datetime(day_name: str, start_time: str, reference_date: date) -> datetime:
    block_date = day_to_date(day_name, reference_date)
    return datetime.combine(block_date, parse_time(start_time))


def flag_overdue_tasks(tasks: pd.DataFrame, today: date | None = None) -> pd.DataFrame:
    """Add an overdue flag for unfinished tasks past their due date."""
    today = today or date.today()
    if tasks.empty:
        return tasks.copy()
    flagged = tasks.copy()
    flagged["due_date"] = pd.to_datetime(flagged["due_date"]).dt.date
    flagged["is_overdue"] = (flagged["due_date"] < today) & (flagged["completed"] == 0)
    return flagged


def generate_schedule(
    tasks: pd.DataFrame,
    study_blocks: pd.DataFrame,
    reference_date: date | None = None,
) -> pd.DataFrame:
    """Generate study sessions from unfinished tasks and available study blocks.

    The algorithm is intentionally simple and readable:
    1. Remove completed tasks.
    2. Score each task using priority and due-date urgency.
    3. Sort tasks by score so urgent/high-priority work is scheduled first.
    4. Fill weekly study blocks, splitting larger tasks into smaller sessions.
    """
    reference_date = reference_date or date.today()
    if tasks.empty or study_blocks.empty:
        return pd.DataFrame(
            columns=[
                "day",
                "date",
                "start_time",
                "end_time",
                "course",
                "task",
                "task_type",
                "priority",
                "session_hours",
                "due_date",
                "overdue",
                "score",
            ]
        )

    active_tasks = flag_overdue_tasks(tasks, reference_date)
    active_tasks = active_tasks[active_tasks["completed"] == 0].copy()
    if active_tasks.empty:
        return pd.DataFrame()

    active_tasks["score"] = active_tasks.apply(lambda row: task_score(row.to_dict(), reference_date), axis=1)
    if "completed_hours" not in active_tasks.columns:
        active_tasks["completed_hours"] = 0
    active_tasks["remaining_hours"] = (
        active_tasks["estimated_hours"].astype(float) - active_tasks["completed_hours"].astype(float)
    ).clip(lower=0)
    active_tasks = active_tasks[active_tasks["remaining_hours"] > 0.05].copy()
    if active_tasks.empty:
        return pd.DataFrame()
    active_tasks = active_tasks.sort_values(
        by=["score", "due_date", "remaining_hours"],
        ascending=[False, True, False],
    )

    blocks = study_blocks.copy()
    if "completed" in blocks.columns:
        blocks = blocks[blocks["completed"] == 0].copy()
    blocks["day_order"] = blocks["day_of_week"].map(DAY_ORDER)
    blocks["duration_hours"] = blocks.apply(
        lambda row: hours_between(row["start_time"], row["end_time"]),
        axis=1,
    )
    blocks = blocks[blocks["duration_hours"] > 0].sort_values(by=["day_order", "start_time"])

    schedule_rows: list[dict] = []

    for _, block in blocks.iterrows():
        block_remaining = float(block["duration_hours"])
        cursor = _block_start_datetime(block["day_of_week"], block["start_time"], reference_date)

        while block_remaining > 0.05 and (active_tasks["remaining_hours"] > 0.05).any():
            available_tasks = active_tasks[active_tasks["remaining_hours"] > 0.05]
            task_index = available_tasks.index[0]
            task = active_tasks.loc[task_index]

            session_hours = min(float(task["remaining_hours"]), block_remaining, SESSION_CHUNK_HOURS)
            session_end = cursor + timedelta(hours=session_hours)
            schedule_rows.append(
                {
                    "day": block["day_of_week"],
                    "date": cursor.date().isoformat(),
                    "start_time": cursor.strftime("%H:%M"),
                    "end_time": session_end.strftime("%H:%M"),
                    "course": task["course_name"],
                    "task": task["title"],
                    "task_type": task["task_type"],
                    "priority": task["priority"],
                    "session_hours": round(session_hours, 2),
                    "due_date": task["due_date"].isoformat(),
                    "overdue": bool(task["is_overdue"]),
                    "score": task["score"],
                }
            )

            active_tasks.loc[task_index, "remaining_hours"] = round(
                float(task["remaining_hours"]) - session_hours,
                2,
            )
            block_remaining = round(block_remaining - session_hours, 2)
            cursor = session_end

    return pd.DataFrame(schedule_rows)
