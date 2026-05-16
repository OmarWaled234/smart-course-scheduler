"""FastAPI backend for the Smart Course Scheduler mobile app."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

import database as db
from models import DAYS_OF_WEEK, PRIORITIES, TASK_TYPES
from scheduler import flag_overdue_tasks, generate_schedule
from utils import hours_between


app = FastAPI(title="Smart Course Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CoursePayload(BaseModel):
    name: str = Field(min_length=1)
    instructor: str = ""
    color: str = "#4C78A8"


class TaskPayload(BaseModel):
    title: str = Field(min_length=1)
    course_id: int
    task_type: str
    due_date: date
    estimated_hours: float = Field(gt=0)
    completed_hours: float = Field(default=0, ge=0)
    priority: str
    completed: bool = False

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, value: str) -> str:
        if value not in TASK_TYPES:
            raise ValueError(f"task_type must be one of {TASK_TYPES}")
        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        if value not in PRIORITIES:
            raise ValueError(f"priority must be one of {PRIORITIES}")
        return value


class StudyBlockPayload(BaseModel):
    day_of_week: str
    start_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    completed: bool = False

    @field_validator("day_of_week")
    @classmethod
    def validate_day(cls, value: str) -> str:
        if value not in DAYS_OF_WEEK:
            raise ValueError(f"day_of_week must be one of {DAYS_OF_WEEK}")
        return value


class LogHoursPayload(BaseModel):
    hours: float = Field(gt=0)


def records(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert pandas rows into JSON-safe dictionaries."""
    if dataframe.empty:
        return []
    clean = dataframe.where(pd.notna(dataframe), None)
    return clean.to_dict(orient="records")


def ensure_course_exists(course_id: int) -> None:
    courses = db.get_courses()
    if courses.empty or course_id not in set(courses["id"].astype(int)):
        raise HTTPException(status_code=404, detail="Course not found")


def ensure_task_exists(task_id: int) -> None:
    tasks = db.get_tasks()
    if tasks.empty or task_id not in set(tasks["id"].astype(int)):
        raise HTTPException(status_code=404, detail="Task not found")


def ensure_block_exists(block_id: int) -> None:
    blocks = db.get_study_blocks()
    if blocks.empty or block_id not in set(blocks["id"].astype(int)):
        raise HTTPException(status_code=404, detail="Study block not found")


@app.on_event("startup")
def startup() -> None:
    db.init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/constants")
def constants() -> dict[str, list[str]]:
    return {
        "days_of_week": DAYS_OF_WEEK,
        "priorities": PRIORITIES,
        "task_types": TASK_TYPES,
    }


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    tasks = flag_overdue_tasks(db.get_tasks())
    blocks = db.get_study_blocks()
    if tasks.empty:
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "overdue_tasks": 0,
            "upcoming_tasks": 0,
            "remaining_hours": 0,
            "tasks_by_course": [],
            "hours_by_course": [],
        }

    tasks["remaining_hours"] = (
        tasks["estimated_hours"].astype(float) - tasks["completed_hours"].astype(float)
    ).clip(lower=0)
    unfinished = tasks[tasks["completed"] == 0]
    today = date.today()
    upcoming = unfinished[pd.to_datetime(unfinished["due_date"]).dt.date >= today]
    return {
        "total_tasks": int(len(tasks)),
        "completed_tasks": int((tasks["completed"] == 1).sum()),
        "overdue_tasks": int(tasks["is_overdue"].sum()),
        "upcoming_tasks": int(len(upcoming)),
        "remaining_hours": round(float(unfinished["remaining_hours"].sum()), 2),
        "study_blocks": int(len(blocks)),
        "tasks_by_course": records(tasks.groupby("course_name").size().reset_index(name="count")),
        "hours_by_course": records(
            tasks.groupby("course_name")["remaining_hours"].sum().reset_index(name="hours")
        ),
    }


@app.get("/api/courses")
def list_courses() -> list[dict[str, Any]]:
    return records(db.get_courses())


@app.post("/api/courses", status_code=201)
def create_course(payload: CoursePayload) -> dict[str, str]:
    try:
        db.add_course(payload.name, payload.instructor, payload.color)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "created"}


@app.put("/api/courses/{course_id}")
def update_course(course_id: int, payload: CoursePayload) -> dict[str, str]:
    ensure_course_exists(course_id)
    db.update_course(course_id, payload.name, payload.instructor, payload.color)
    return {"status": "updated"}


@app.delete("/api/courses/{course_id}", status_code=204)
def delete_course(course_id: int) -> Response:
    ensure_course_exists(course_id)
    db.delete_course(course_id)
    return Response(status_code=204)


@app.get("/api/tasks")
def list_tasks() -> list[dict[str, Any]]:
    tasks = db.get_tasks()
    if tasks.empty:
        return []
    flagged = flag_overdue_tasks(tasks)
    flagged["remaining_hours"] = (
        flagged["estimated_hours"].astype(float) - flagged["completed_hours"].astype(float)
    ).clip(lower=0)
    flagged["due_date"] = flagged["due_date"].astype(str)
    return records(flagged)


@app.post("/api/tasks", status_code=201)
def create_task(payload: TaskPayload) -> dict[str, str]:
    ensure_course_exists(payload.course_id)
    db.add_task(
        payload.title,
        payload.course_id,
        payload.task_type,
        payload.due_date.isoformat(),
        payload.estimated_hours,
        payload.priority,
        payload.completed,
    )
    if payload.completed_hours > 0:
        tasks = db.get_tasks()
        task_id = int(tasks.sort_values("id").iloc[-1]["id"])
        db.log_task_hours(task_id, payload.completed_hours)
    return {"status": "created"}


@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, payload: TaskPayload) -> dict[str, str]:
    ensure_task_exists(task_id)
    ensure_course_exists(payload.course_id)
    db.update_task(
        task_id,
        payload.title,
        payload.course_id,
        payload.task_type,
        payload.due_date.isoformat(),
        payload.estimated_hours,
        payload.completed_hours,
        payload.priority,
        payload.completed,
    )
    return {"status": "updated"}


@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: int, completed: bool = True) -> dict[str, str]:
    ensure_task_exists(task_id)
    db.set_task_completed(task_id, completed)
    return {"status": "updated"}


@app.post("/api/tasks/{task_id}/log-hours")
def log_task_hours(task_id: int, payload: LogHoursPayload) -> dict[str, str]:
    ensure_task_exists(task_id)
    db.log_task_hours(task_id, payload.hours)
    return {"status": "updated"}


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> Response:
    ensure_task_exists(task_id)
    db.delete_task(task_id)
    return Response(status_code=204)


@app.get("/api/study-blocks")
def list_study_blocks() -> list[dict[str, Any]]:
    blocks = db.get_study_blocks()
    if blocks.empty:
        return []
    blocks = blocks.copy()
    blocks["duration_hours"] = blocks.apply(
        lambda row: hours_between(row["start_time"], row["end_time"]),
        axis=1,
    )
    return records(blocks)


@app.post("/api/study-blocks", status_code=201)
def create_study_block(payload: StudyBlockPayload) -> dict[str, str]:
    if hours_between(payload.start_time, payload.end_time) <= 0:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    db.add_study_block(payload.day_of_week, payload.start_time, payload.end_time)
    return {"status": "created"}


@app.put("/api/study-blocks/{block_id}")
def update_study_block(block_id: int, payload: StudyBlockPayload) -> dict[str, str]:
    ensure_block_exists(block_id)
    if hours_between(payload.start_time, payload.end_time) <= 0:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    db.update_study_block(
        block_id,
        payload.day_of_week,
        payload.start_time,
        payload.end_time,
        payload.completed,
    )
    return {"status": "updated"}


@app.post("/api/study-blocks/{block_id}/complete")
def complete_study_block(block_id: int, completed: bool = True) -> dict[str, str]:
    ensure_block_exists(block_id)
    db.set_study_block_completed(block_id, completed)
    return {"status": "updated"}


@app.delete("/api/study-blocks/{block_id}", status_code=204)
def delete_study_block(block_id: int) -> Response:
    ensure_block_exists(block_id)
    db.delete_study_block(block_id)
    return Response(status_code=204)


@app.get("/api/schedule")
def weekly_schedule() -> list[dict[str, Any]]:
    return records(generate_schedule(db.get_tasks(), db.get_study_blocks()))


@app.post("/api/demo-data", status_code=201)
def load_demo_data() -> dict[str, str]:
    db.add_demo_data()
    return {"status": "created"}
