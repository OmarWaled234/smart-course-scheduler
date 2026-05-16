"""Data models and constants for Smart Course Scheduler."""

from dataclasses import dataclass
from datetime import date, time


TASK_TYPES = ["assignment", "exam", "quiz", "project", "reading", "other"]
PRIORITIES = ["low", "medium", "high"]
DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


@dataclass
class Course:
    """Represents a course a student wants to track."""

    name: str
    instructor: str = ""
    color: str = "#4C78A8"
    id: int | None = None


@dataclass
class Task:
    """Represents an academic task with workload and deadline data."""

    title: str
    course_id: int
    task_type: str
    due_date: date
    estimated_hours: float
    priority: str
    completed_hours: float = 0
    completed: bool = False
    id: int | None = None


@dataclass
class StudyBlock:
    """Represents a weekly block of available study time."""

    day_of_week: str
    start_time: time
    end_time: time
    id: int | None = None
