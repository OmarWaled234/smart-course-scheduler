"""SQLite database setup and CRUD functions for Smart Course Scheduler."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd


DB_PATH = Path("smart_course_scheduler.db")


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with row dictionaries enabled."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create tables if they do not already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                instructor TEXT DEFAULT '',
                color TEXT DEFAULT '#4C78A8'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                course_id INTEGER NOT NULL,
                task_type TEXT NOT NULL,
                due_date TEXT NOT NULL,
                estimated_hours REAL NOT NULL,
                completed_hours REAL DEFAULT 0,
                priority TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS study_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_of_week TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(study_blocks)").fetchall()
        }
        if "completed" not in columns:
            conn.execute("ALTER TABLE study_blocks ADD COLUMN completed INTEGER DEFAULT 0")

        task_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(tasks)").fetchall()
        }
        if "completed_hours" not in task_columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN completed_hours REAL DEFAULT 0")
            conn.execute(
                """
                UPDATE tasks
                SET completed_hours = estimated_hours
                WHERE completed = 1
                """
            )


def fetch_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def get_setting(key: str) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def save_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO app_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )


def get_courses() -> pd.DataFrame:
    return fetch_dataframe("SELECT * FROM courses ORDER BY name")


def add_course(name: str, instructor: str, color: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO courses (name, instructor, color) VALUES (?, ?, ?)",
            (name.strip(), instructor.strip(), color),
        )


def update_course(course_id: int, name: str, instructor: str, color: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE courses SET name = ?, instructor = ?, color = ? WHERE id = ?",
            (name.strip(), instructor.strip(), color, course_id),
        )


def delete_course(course_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))


def get_tasks() -> pd.DataFrame:
    return fetch_dataframe(
        """
        SELECT
            tasks.*,
            courses.name AS course_name,
            courses.color AS course_color
        FROM tasks
        JOIN courses ON courses.id = tasks.course_id
        ORDER BY due_date ASC, priority DESC
        """
    )


def add_task(
    title: str,
    course_id: int,
    task_type: str,
    due_date: str,
    estimated_hours: float,
    priority: str,
    completed: bool,
) -> None:
    completed_hours = estimated_hours if completed else 0
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tasks
                (title, course_id, task_type, due_date, estimated_hours, completed_hours, priority, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title.strip(), course_id, task_type, due_date, estimated_hours, completed_hours, priority, int(completed)),
        )


def update_task(
    task_id: int,
    title: str,
    course_id: int,
    task_type: str,
    due_date: str,
    estimated_hours: float,
    completed_hours: float,
    priority: str,
    completed: bool,
) -> None:
    completed_hours = min(max(completed_hours, 0), estimated_hours)
    completed = completed or completed_hours >= estimated_hours
    if completed:
        completed_hours = estimated_hours
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, course_id = ?, task_type = ?, due_date = ?,
                estimated_hours = ?, completed_hours = ?, priority = ?, completed = ?
            WHERE id = ?
            """,
            (
                title.strip(),
                course_id,
                task_type,
                due_date,
                estimated_hours,
                completed_hours,
                priority,
                int(completed),
                task_id,
            ),
        )


def set_task_completed(task_id: int, completed: bool) -> None:
    with get_connection() as conn:
        if completed:
            conn.execute(
                """
                UPDATE tasks
                SET completed = 1, completed_hours = estimated_hours
                WHERE id = ?
                """,
                (task_id,),
            )
        else:
            conn.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))


def log_task_hours(task_id: int, hours: float) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET
                completed_hours = MIN(estimated_hours, completed_hours + ?),
                completed = CASE
                    WHEN completed_hours + ? >= estimated_hours THEN 1
                    ELSE 0
                END
            WHERE id = ?
            """,
            (hours, hours, task_id),
        )


def delete_task(task_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def get_study_blocks() -> pd.DataFrame:
    return fetch_dataframe(
        """
        SELECT * FROM study_blocks
        ORDER BY
            CASE day_of_week
                WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END,
            start_time
        """
    )


def add_study_block(day_of_week: str, start_time: str, end_time: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO study_blocks (day_of_week, start_time, end_time, completed) VALUES (?, ?, ?, 0)",
            (day_of_week, start_time, end_time),
        )


def update_study_block(block_id: int, day_of_week: str, start_time: str, end_time: str, completed: bool) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE study_blocks SET day_of_week = ?, start_time = ?, end_time = ?, completed = ? WHERE id = ?",
            (day_of_week, start_time, end_time, int(completed), block_id),
        )


def set_study_block_completed(block_id: int, completed: bool) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE study_blocks SET completed = ? WHERE id = ?", (int(completed), block_id))


def delete_study_block(block_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM study_blocks WHERE id = ?", (block_id,))


def add_demo_data() -> None:
    """Load sample courses, tasks, and blocks for quick testing."""
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM study_blocks")
        conn.execute("DELETE FROM courses")
        courses = [
            ("Calculus II", "Dr. Nguyen", "#4C78A8"),
            ("Computer Science", "Prof. Johnson", "#59A14F"),
            ("English Literature", "Dr. Rivera", "#F28E2B"),
            ("Biology", "Dr. Patel", "#E15759"),
        ]
        conn.executemany("INSERT INTO courses (name, instructor, color) VALUES (?, ?, ?)", courses)
        course_ids = {row["name"]: row["id"] for row in conn.execute("SELECT id, name FROM courses")}
        tasks = [
            ("Integration Practice Set", course_ids["Calculus II"], "assignment", "2026-05-08", 3.5, 1.0, "high", 0),
            ("Python DataFrames Lab", course_ids["Computer Science"], "project", "2026-05-12", 5.0, 2.0, "high", 0),
            ("Poetry Response Draft", course_ids["English Literature"], "assignment", "2026-05-10", 2.0, 0.5, "medium", 0),
            ("Cell Biology Quiz", course_ids["Biology"], "quiz", "2026-05-07", 1.5, 0, "high", 0),
            ("Read Chapter 9", course_ids["Biology"], "reading", "2026-05-14", 2.0, 0, "low", 0),
            ("Old Discussion Post", course_ids["English Literature"], "other", "2026-05-01", 1.0, 0, "medium", 0),
            ("Completed Recursion Notes", course_ids["Computer Science"], "reading", "2026-05-06", 1.0, 1.0, "low", 1),
        ]
        conn.executemany(
            """
            INSERT INTO tasks
                (title, course_id, task_type, due_date, estimated_hours, completed_hours, priority, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tasks,
        )
        blocks = [
            ("Monday", "16:00", "18:00", 0),
            ("Tuesday", "19:00", "21:00", 0),
            ("Wednesday", "15:30", "17:30", 0),
            ("Thursday", "18:00", "20:30", 0),
            ("Saturday", "10:00", "13:00", 0),
            ("Sunday", "14:00", "16:00", 0),
        ]
        conn.executemany(
            "INSERT INTO study_blocks (day_of_week, start_time, end_time, completed) VALUES (?, ?, ?, ?)",
            blocks,
        )
