"""Streamlit UI for the Smart Course Scheduler app."""

from __future__ import annotations

import json
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import database as db
from models import DAYS_OF_WEEK, PRIORITIES, TASK_TYPES
from scheduler import flag_overdue_tasks, generate_schedule
from utils import dataframe_to_csv, format_date, format_time, hours_between


REQUIRED = ":red[*]"

THEMES = {
    "Light": {
        "background": "#F7F9FC",
        "surface": "#FFFFFF",
        "surface_alt": "#EEF3F8",
        "text": "#172033",
        "muted": "#5B677A",
        "accent": "#2563EB",
        "accent_alt": "#14B8A6",
        "success": "#16A34A",
        "warning": "#F59E0B",
        "danger": "#DC2626",
        "border": "#D8E0EA",
    },
    "Dark": {
        "background": "#0E1117",
        "surface": "#171B24",
        "surface_alt": "#222938",
        "text": "#F2F5FA",
        "muted": "#A8B3C7",
        "accent": "#60A5FA",
        "accent_alt": "#34D399",
        "success": "#4ADE80",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "border": "#2D3748",
    },
    "Ocean": {
        "background": "#F1FAFB",
        "surface": "#FFFFFF",
        "surface_alt": "#DDF3F2",
        "text": "#102A43",
        "muted": "#486581",
        "accent": "#0284C7",
        "accent_alt": "#0F766E",
        "success": "#059669",
        "warning": "#D97706",
        "danger": "#E11D48",
        "border": "#B7DDE0",
    },
    "Forest": {
        "background": "#F5F8F2",
        "surface": "#FFFFFF",
        "surface_alt": "#E5EDDC",
        "text": "#1F2A1F",
        "muted": "#5F6F52",
        "accent": "#3F7D20",
        "accent_alt": "#B7791F",
        "success": "#2F855A",
        "warning": "#C05621",
        "danger": "#C53030",
        "border": "#D5DEC8",
    },
    "Sunset": {
        "background": "#FFF7F0",
        "surface": "#FFFFFF",
        "surface_alt": "#FDE7D7",
        "text": "#2D1B18",
        "muted": "#7C5E57",
        "accent": "#EA580C",
        "accent_alt": "#DB2777",
        "success": "#15803D",
        "warning": "#CA8A04",
        "danger": "#BE123C",
        "border": "#F5CDB9",
    },
}

LAYOUTS = {
    "Comfortable": {"dashboard_columns": 3, "gap": "1rem", "font_size": "1rem", "chart_height": 3.0},
    "Compact": {"dashboard_columns": 5, "gap": "0.45rem", "font_size": "0.92rem", "chart_height": 2.55},
    "Focus": {"dashboard_columns": 1, "gap": "1.25rem", "font_size": "1.03rem", "chart_height": 3.4},
}


st.set_page_config(
    page_title="Smart Course Scheduler",
    layout="wide",
)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return db.get_courses(), db.get_tasks(), db.get_study_blocks()


def apply_theme(theme: dict[str, str], layout: dict[str, str | float]) -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --app-bg: {theme["background"]};
                --app-surface: {theme["surface"]};
                --app-surface-alt: {theme["surface_alt"]};
                --app-text: {theme["text"]};
                --app-muted: {theme["muted"]};
                --app-accent: {theme["accent"]};
                --app-accent-alt: {theme["accent_alt"]};
                --app-border: {theme["border"]};
                --app-gap: {layout["gap"]};
                --app-font-size: {layout["font_size"]};
            }}

            .stApp {{
                background: var(--app-bg);
                color: var(--app-text);
                font-size: var(--app-font-size);
            }}

            [data-testid="stSidebar"], [data-testid="stHeader"] {{
                background: var(--app-surface);
                border-color: var(--app-border);
            }}

            [data-testid="stMetric"], div[data-testid="stDataFrame"],
            div[data-testid="stAlert"], div[data-testid="stForm"] {{
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                border-radius: 8px;
                padding: 0.65rem;
            }}

            h1, h2, h3, h4, h5, h6, p, label, span {{
                color: var(--app-text);
            }}

            .stCaption, [data-testid="stCaptionContainer"], small {{
                color: var(--app-muted);
            }}

            .stButton > button, .stDownloadButton > button,
            div[data-baseweb="select"] > div, input, textarea {{
                background: var(--app-surface) !important;
                border-color: var(--app-border);
                border-radius: 8px;
                color: var(--app-text) !important;
            }}

            div[data-baseweb="select"] span,
            div[data-baseweb="select"] svg,
            div[data-baseweb="select"] input {{
                color: var(--app-text) !important;
                fill: var(--app-text) !important;
            }}

            [data-testid="stDataFrame"] button,
            [data-testid="stDataFrame"] [role="button"],
            [data-testid="stElementToolbar"],
            [data-testid="stToolbar"],
            [data-baseweb="popover"],
            [data-baseweb="popover"] ul,
            [data-baseweb="popover"] li,
            [data-baseweb="menu"],
            [data-baseweb="menu"] ul,
            [data-baseweb="menu"] li,
            [role="menu"] {{
                background: var(--app-surface-alt) !important;
                color: var(--app-text) !important;
                border-color: var(--app-border) !important;
            }}

            [data-testid="stDataFrame"] svg,
            [data-testid="stElementToolbar"] svg,
            [data-testid="stToolbar"] svg,
            [data-baseweb="popover"] svg {{
                color: var(--app-text) !important;
                fill: var(--app-text) !important;
            }}

            [data-baseweb="menu"] li,
            [data-baseweb="menu"] li span,
            [data-baseweb="menu"] li div,
            [role="option"],
            [role="option"] span,
            [role="option"] div,
            [role="menuitem"],
            [data-baseweb="popover"] div {{
                color: var(--app-text) !important;
            }}

            [role="option"]:hover,
            [data-baseweb="menu"] li:hover {{
                background: var(--app-surface) !important;
            }}

            [aria-selected="true"],
            [data-baseweb="menu"] li[aria-selected="true"] {{
                background: var(--app-accent) !important;
                color: white !important;
            }}

            [aria-selected="true"] div,
            [aria-selected="true"] span {{
                color: white !important;
            }}

            .stButton > button[kind="primary"], .stDownloadButton > button {{
                background: var(--app-accent);
                color: white;
                border-color: var(--app-accent);
            }}

            hr {{
                border-color: var(--app-border);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_appearance_settings() -> dict:
    raw_settings = db.get_setting("appearance")
    if not raw_settings:
        return {}

    try:
        settings = json.loads(raw_settings)
    except json.JSONDecodeError:
        return {}

    return settings if isinstance(settings, dict) else {}


def save_appearance_settings(theme_name: str, theme: dict[str, str], layout_name: str) -> None:
    db.save_setting(
        "appearance",
        json.dumps(
            {
                "theme_name": theme_name,
                "theme": theme,
                "layout_name": layout_name,
            }
        ),
    )


def appearance_controls() -> tuple[dict[str, str], dict[str, str | float], str]:
    saved_settings = load_appearance_settings()
    saved_theme_name = saved_settings.get("theme_name", "Light")
    if saved_theme_name not in [*THEMES.keys(), "Custom"]:
        saved_theme_name = "Light"

    saved_layout_name = saved_settings.get("layout_name", "Comfortable")
    if saved_layout_name not in LAYOUTS:
        saved_layout_name = "Comfortable"

    st.header("Appearance")
    theme_options = ["Light", "Dark", "Ocean", "Forest", "Sunset", "Custom"]
    theme_name = st.selectbox(
        "Theme",
        theme_options,
        index=theme_options.index(saved_theme_name),
        help="Choose a ready-made color palette or build your own.",
    )

    if theme_name == "Custom":
        base = saved_settings.get("theme", THEMES["Light"])
        theme = {
            "background": st.color_picker("Page background", base.get("background", THEMES["Light"]["background"])),
            "surface": st.color_picker("Panel color", base.get("surface", THEMES["Light"]["surface"])),
            "surface_alt": st.color_picker("Soft panel color", base.get("surface_alt", THEMES["Light"]["surface_alt"])),
            "text": st.color_picker("Text color", base.get("text", THEMES["Light"]["text"])),
            "muted": st.color_picker("Muted text", base.get("muted", THEMES["Light"]["muted"])),
            "accent": st.color_picker("Primary accent", base.get("accent", THEMES["Light"]["accent"])),
            "accent_alt": st.color_picker("Secondary accent", base.get("accent_alt", THEMES["Light"]["accent_alt"])),
            "success": st.color_picker("Success color", base.get("success", THEMES["Light"]["success"])),
            "warning": st.color_picker("Warning color", base.get("warning", THEMES["Light"]["warning"])),
            "danger": st.color_picker("Danger color", base.get("danger", THEMES["Light"]["danger"])),
            "border": st.color_picker("Border color", base.get("border", THEMES["Light"]["border"])),
        }
    else:
        theme = THEMES[theme_name]

    layout_options = list(LAYOUTS.keys())
    layout_name = st.radio(
        "Layout",
        layout_options,
        index=layout_options.index(saved_layout_name),
        horizontal=True,
        help="Adjust spacing and dashboard chart layout.",
    )
    save_appearance_settings(theme_name, theme, layout_name)
    return theme, LAYOUTS[layout_name], theme_name


def course_options(courses: pd.DataFrame) -> dict[str, int]:
    return dict(zip(courses["name"], courses["id"]))


def add_task_progress(tasks: pd.DataFrame) -> pd.DataFrame:
    if tasks.empty:
        return tasks.copy()

    progress = tasks.copy()
    if "completed_hours" not in progress.columns:
        progress["completed_hours"] = 0
    progress["completed_hours"] = progress["completed_hours"].fillna(0).astype(float)
    progress["estimated_hours"] = progress["estimated_hours"].astype(float)
    progress["remaining_hours"] = (progress["estimated_hours"] - progress["completed_hours"]).clip(lower=0)
    progress.loc[progress["completed"] == 1, "remaining_hours"] = 0
    progress["progress"] = progress.apply(
        lambda row: 100 if row["estimated_hours"] <= 0 else min(100, round(row["completed_hours"] / row["estimated_hours"] * 100)),
        axis=1,
    )
    return progress


def show_dashboard(tasks: pd.DataFrame, theme: dict[str, str], layout: dict[str, str | float]) -> None:
    st.subheader("Dashboard")
    flagged = add_task_progress(flag_overdue_tasks(tasks))

    total_tasks = len(flagged)
    completed_tasks = int(flagged["completed"].sum()) if not flagged.empty else 0
    overdue_tasks = int(flagged["is_overdue"].sum()) if not flagged.empty else 0
    upcoming_tasks = int(((flagged["completed"] == 0) & (~flagged["is_overdue"])).sum()) if not flagged.empty else 0
    remaining_hours = (
        flagged.loc[flagged["completed"] == 0, "remaining_hours"].sum()
        if not flagged.empty
        else 0
    )

    cols = st.columns(5)
    cols[0].metric("Total tasks", total_tasks)
    cols[1].metric("Completed", completed_tasks)
    cols[2].metric("Overdue", overdue_tasks)
    cols[3].metric("Upcoming", upcoming_tasks)
    cols[4].metric("Hours remaining", f"{remaining_hours:.1f}")

    if flagged.empty:
        st.info("Add tasks to see charts and progress.")
        return

    chart_columns = int(layout["dashboard_columns"])
    chart_cols = st.columns(chart_columns, gap="medium")
    with chart_cols[0 % chart_columns]:
        st.caption("Tasks by course")
        tasks_by_course = flagged.groupby("course_name")["id"].count()
        fig, ax = plt.subplots(figsize=(4, float(layout["chart_height"])))
        tasks_by_course.plot(kind="bar", ax=ax, color=theme["accent"])
        fig.patch.set_facecolor(theme["surface"])
        ax.set_facecolor(theme["surface"])
        ax.tick_params(colors=theme["text"])
        ax.set_xlabel("")
        ax.set_ylabel("Tasks")
        ax.yaxis.label.set_color(theme["muted"])
        st.pyplot(fig)

    with chart_cols[1 % chart_columns]:
        st.caption("Completed vs incomplete")
        completed_counts = pd.Series(
            {
                "Completed": int((flagged["completed"] == 1).sum()),
                "Incomplete": int((flagged["completed"] == 0).sum()),
            }
        )
        fig, ax = plt.subplots(figsize=(4, float(layout["chart_height"])))
        completed_counts.plot(
            kind="pie",
            ax=ax,
            autopct="%1.0f%%",
            colors=[theme["success"], theme["danger"]],
            textprops={"color": theme["text"]},
        )
        fig.patch.set_facecolor(theme["surface"])
        ax.set_facecolor(theme["surface"])
        ax.set_ylabel("")
        st.pyplot(fig)

    with chart_cols[2 % chart_columns]:
        st.caption("Hours remaining by course")
        remaining = flagged[flagged["completed"] == 0].groupby("course_name")["remaining_hours"].sum()
        fig, ax = plt.subplots(figsize=(4, float(layout["chart_height"])))
        remaining.plot(kind="bar", ax=ax, color=theme["accent_alt"])
        fig.patch.set_facecolor(theme["surface"])
        ax.set_facecolor(theme["surface"])
        ax.tick_params(colors=theme["text"])
        ax.set_xlabel("")
        ax.set_ylabel("Hours")
        ax.yaxis.label.set_color(theme["muted"])
        st.pyplot(fig)


def show_today_recommendation(schedule: pd.DataFrame, tasks: pd.DataFrame) -> None:
    st.subheader("What should I study today?")
    today_name = date.today().strftime("%A")
    todays_sessions = schedule[schedule["day"] == today_name] if not schedule.empty else pd.DataFrame()

    overdue = add_task_progress(flag_overdue_tasks(tasks))
    overdue = overdue[overdue["is_overdue"]] if not overdue.empty else pd.DataFrame()

    if not overdue.empty:
        st.warning("You have overdue unfinished tasks. Start with these before new work.")
        st.dataframe(
            overdue[["title", "course_name", "due_date", "priority", "remaining_hours"]],
            use_container_width=True,
            hide_index=True,
        )
    elif not todays_sessions.empty:
        st.success(f"Today is {today_name}. Here is your generated study plan.")
        st.dataframe(
            todays_sessions[["start_time", "end_time", "course", "task", "session_hours", "priority"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No study sessions are scheduled for today. Use the weekly plan or add more study blocks.")


def courses_page(courses: pd.DataFrame) -> None:
    st.subheader("Courses")
    with st.form("add_course", clear_on_submit=True):
        cols = st.columns([2, 2, 1])
        name = cols[0].text_input(f"Course name {REQUIRED}")
        instructor = cols[1].text_input("Instructor")
        color = cols[2].color_picker(f"Color {REQUIRED}", "#4C78A8")
        if st.form_submit_button("Add course"):
            if name.strip():
                try:
                    db.add_course(name, instructor, color)
                    st.success("Course added.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not add course: {exc}")
            else:
                st.error("Course name is required.")

    if courses.empty:
        st.info("No courses yet. Add one above or load demo data from the sidebar.")
        return

    st.dataframe(courses, use_container_width=True, hide_index=True)
    st.markdown("#### Edit or delete a course")
    selected_name = st.selectbox("Select course", courses["name"], key="course_edit_select")
    selected = courses[courses["name"] == selected_name].iloc[0]
    with st.form("edit_course"):
        cols = st.columns([2, 2, 1])
        new_name = cols[0].text_input(f"Course name {REQUIRED}", selected["name"])
        new_instructor = cols[1].text_input("Instructor", selected["instructor"])
        new_color = cols[2].color_picker(f"Color {REQUIRED}", selected["color"])
        save, delete = st.columns(2)
        if save.form_submit_button("Save course"):
            db.update_course(int(selected["id"]), new_name, new_instructor, new_color)
            st.success("Course updated.")
            st.rerun()
        if delete.form_submit_button("Delete course"):
            db.delete_course(int(selected["id"]))
            st.warning("Course deleted.")
            st.rerun()


def tasks_page(courses: pd.DataFrame, tasks: pd.DataFrame) -> None:
    st.subheader("Tasks")
    if courses.empty:
        st.info("Add a course before creating tasks.")
        return

    options = course_options(courses)
    with st.form("add_task", clear_on_submit=True):
        cols = st.columns([2, 1, 1])
        title = cols[0].text_input(f"Task title {REQUIRED}")
        course_name = cols[1].selectbox(f"Course {REQUIRED}", list(options.keys()))
        task_type = cols[2].selectbox(f"Type {REQUIRED}", TASK_TYPES)
        cols = st.columns([1, 1, 1, 1])
        due_date = cols[0].date_input(f"Due date {REQUIRED}", date.today())
        estimated_hours = cols[1].number_input(f"Estimated hours {REQUIRED}", min_value=0.25, value=1.0, step=0.25)
        priority = cols[2].selectbox(f"Priority {REQUIRED}", PRIORITIES, index=1)
        completed = cols[3].checkbox("Completed")
        if st.form_submit_button("Add task"):
            if title.strip():
                db.add_task(title, options[course_name], task_type, due_date.isoformat(), estimated_hours, priority, completed)
                st.success("Task added.")
                st.rerun()
            else:
                st.error("Task title is required.")

    if tasks.empty:
        st.info("No tasks yet.")
        return

    visible_tasks = add_task_progress(flag_overdue_tasks(tasks))
    visible_tasks["status"] = visible_tasks.apply(
        lambda row: "Complete" if row["completed"] else ("Overdue" if row["is_overdue"] else "Open"),
        axis=1,
    )
    st.dataframe(
        visible_tasks[
            [
                "title",
                "course_name",
                "task_type",
                "due_date",
                "estimated_hours",
                "completed_hours",
                "remaining_hours",
                "progress",
                "priority",
                "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Export tasks to CSV",
        dataframe_to_csv(visible_tasks),
        file_name="smart_course_tasks.csv",
        mime="text/csv",
    )

    open_tasks = visible_tasks[visible_tasks["completed"] == 0]
    if not open_tasks.empty:
        st.markdown("#### Log study hours")
        for task in open_tasks.itertuples():
            cols = st.columns([3, 1, 1])
            cols[0].write(
                f"{task.title} ({task.course_name}) - {task.completed_hours:.1f}/{task.estimated_hours:.1f} hours"
            )
            logged_hours = cols[1].number_input(
                "Hours",
                min_value=0.25,
                max_value=max(0.25, float(task.remaining_hours)),
                value=min(0.5, max(0.25, float(task.remaining_hours))),
                step=0.25,
                key=f"log_hours_{task.id}",
            )
            if cols[2].button("Log", key=f"log_task_{task.id}"):
                db.log_task_hours(int(task.id), float(logged_hours))
                st.success(f"Logged {logged_hours:.2f} hours for {task.title}.")
                st.rerun()

        st.markdown("#### Mark an assignment complete")
        for task in open_tasks.itertuples():
            cols = st.columns([3, 1, 1])
            cols[0].write(f"{task.title} ({task.course_name})")
            cols[1].caption(f"{task.remaining_hours:.1f}h left")
            if cols[2].button("Complete", key=f"complete_task_{task.id}"):
                db.set_task_completed(int(task.id), True)
                st.success(f"Marked {task.title} complete.")
                st.rerun()

    st.markdown("#### Edit or delete a task")
    selected_label = st.selectbox(
        "Select task",
        [f"{row.title} ({row.course_name})" for row in tasks.itertuples()],
    )
    selected_index = [f"{row.title} ({row.course_name})" for row in tasks.itertuples()].index(selected_label)
    selected = tasks.iloc[selected_index]
    with st.form("edit_task"):
        cols = st.columns([2, 1, 1])
        new_title = cols[0].text_input(f"Task title {REQUIRED}", selected["title"])
        course_names = list(options.keys())
        current_course_index = course_names.index(selected["course_name"])
        new_course = cols[1].selectbox(f"Course {REQUIRED}", course_names, index=current_course_index)
        new_type = cols[2].selectbox(f"Type {REQUIRED}", TASK_TYPES, index=TASK_TYPES.index(selected["task_type"]))
        cols = st.columns([1, 1, 1, 1])
        new_due = cols[0].date_input(f"Due date {REQUIRED}", pd.to_datetime(selected["due_date"]).date())
        new_hours = cols[1].number_input(
            f"Estimated hours {REQUIRED}",
            min_value=0.25,
            value=float(selected["estimated_hours"]),
            step=0.25,
        )
        new_priority = cols[2].selectbox(f"Priority {REQUIRED}", PRIORITIES, index=PRIORITIES.index(selected["priority"]))
        new_completed = cols[3].checkbox("Completed", bool(selected["completed"]))
        new_completed_hours = st.number_input(
            "Logged hours",
            min_value=0.0,
            max_value=float(new_hours),
            value=min(float(selected["completed_hours"]), float(new_hours)),
            step=0.25,
        )
        save, delete = st.columns(2)
        if save.form_submit_button("Save task"):
            db.update_task(
                int(selected["id"]),
                new_title,
                options[new_course],
                new_type,
                new_due.isoformat(),
                new_hours,
                new_completed_hours,
                new_priority,
                new_completed,
            )
            st.success("Task updated.")
            st.rerun()
        if delete.form_submit_button("Delete task"):
            db.delete_task(int(selected["id"]))
            st.warning("Task deleted.")
            st.rerun()


def study_blocks_page(blocks: pd.DataFrame) -> None:
    st.subheader("Available Study Blocks")
    with st.form("add_block", clear_on_submit=True):
        cols = st.columns(3)
        day = cols[0].selectbox(f"Day {REQUIRED}", DAYS_OF_WEEK)
        start_time = cols[1].time_input(f"Start time {REQUIRED}")
        end_time = cols[2].time_input(f"End time {REQUIRED}")
        if st.form_submit_button("Add study block"):
            duration = hours_between(start_time, end_time)
            if duration <= 0:
                st.error("End time must be after start time.")
            else:
                db.add_study_block(day, start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))
                st.success("Study block added.")
                st.rerun()

    if blocks.empty:
        st.info("No study blocks yet.")
        return

    display_blocks = blocks.copy()
    display_blocks["duration_hours"] = display_blocks.apply(
        lambda row: hours_between(row["start_time"], row["end_time"]),
        axis=1,
    )
    display_blocks["status"] = display_blocks["completed"].apply(lambda value: "Complete" if value else "Open")
    st.dataframe(display_blocks, use_container_width=True, hide_index=True)

    open_blocks = blocks[blocks["completed"] == 0]
    if not open_blocks.empty:
        st.markdown("#### Mark a study block complete")
        for block in open_blocks.itertuples():
            cols = st.columns([3, 1])
            cols[0].write(f"{block.day_of_week}: {format_time(block.start_time)} - {format_time(block.end_time)}")
            if cols[1].button("Complete", key=f"complete_block_{block.id}"):
                db.set_study_block_completed(int(block.id), True)
                st.success("Study block marked complete.")
                st.rerun()

    st.markdown("#### Edit or delete a study block")
    selected_label = st.selectbox(
        "Select study block",
        [f"{row.day_of_week}: {format_time(row.start_time)} - {format_time(row.end_time)}" for row in blocks.itertuples()],
    )
    selected_index = [
        f"{row.day_of_week}: {format_time(row.start_time)} - {format_time(row.end_time)}"
        for row in blocks.itertuples()
    ].index(selected_label)
    selected = blocks.iloc[selected_index]
    with st.form("edit_block"):
        cols = st.columns([1, 1, 1, 1])
        new_day = cols[0].selectbox(f"Day {REQUIRED}", DAYS_OF_WEEK, index=DAYS_OF_WEEK.index(selected["day_of_week"]))
        new_start = cols[1].time_input(f"Start time {REQUIRED}", value=pd.to_datetime(selected["start_time"]).time())
        new_end = cols[2].time_input(f"End time {REQUIRED}", value=pd.to_datetime(selected["end_time"]).time())
        new_completed = cols[3].checkbox("Completed", bool(selected["completed"]))
        save, delete = st.columns(2)
        if save.form_submit_button("Save study block"):
            if hours_between(new_start, new_end) <= 0:
                st.error("End time must be after start time.")
            else:
                db.update_study_block(
                    int(selected["id"]),
                    new_day,
                    new_start.strftime("%H:%M"),
                    new_end.strftime("%H:%M"),
                    new_completed,
                )
                st.success("Study block updated.")
                st.rerun()
        if delete.form_submit_button("Delete study block"):
            db.delete_study_block(int(selected["id"]))
            st.warning("Study block deleted.")
            st.rerun()


def schedule_page(tasks: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    st.subheader("Weekly Study Schedule")
    schedule = generate_schedule(tasks, blocks)
    if schedule.empty:
        st.info("Add unfinished tasks and study blocks to generate a schedule.")
        return schedule

    display_schedule = schedule.copy()
    display_schedule["time"] = display_schedule["start_time"].apply(format_time) + " - " + display_schedule["end_time"].apply(format_time)
    display_schedule["deadline"] = display_schedule["due_date"].apply(format_date)
    display_schedule["status"] = display_schedule["overdue"].apply(lambda value: "Overdue task" if value else "On track")
    st.dataframe(
        display_schedule[
            ["day", "date", "time", "course", "task", "task_type", "priority", "session_hours", "deadline", "status"]
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Export generated schedule to CSV",
        dataframe_to_csv(display_schedule),
        file_name="smart_course_weekly_schedule.csv",
        mime="text/csv",
    )
    return schedule


def grade_calculator_page() -> None:
    st.subheader("Grade Calculator")
    st.caption("Enter your numbers, then press Calculate.")

    input_cols = st.columns(2)
    current_grade = input_cols[0].number_input(
        f"Current grade (%) {REQUIRED}",
        min_value=0.0,
        max_value=150.0,
        value=80.0,
        step=0.5,
    )
    desired_grade = input_cols[1].number_input(
        f"Goal grade (%) {REQUIRED}",
        min_value=0.0,
        max_value=150.0,
        value=85.0,
        step=0.5,
    )

    final_cols = st.columns(2)
    final_weight = final_cols[0].number_input(
        f"Final exam / remaining weight (%) {REQUIRED}",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=0.5,
    )
    expected_final_grade = final_cols[1].number_input(
        "Expected final exam grade (%)",
        min_value=0.0,
        max_value=150.0,
        value=80.0,
        step=0.5,
    )

    if not st.button("Calculate", type="primary"):
        return

    completed_weight = 100.0 - final_weight
    projected_grade = (current_grade * completed_weight + expected_final_grade * final_weight) / 100.0

    result_cols = st.columns(2)
    result_cols[0].metric("Projected final grade", f"{projected_grade:.1f}%")

    if final_weight <= 0:
        result_cols[1].metric("Needed on final", "N/A")
        if current_grade >= desired_grade:
            st.success(f"You have already reached your goal with {current_grade:.1f}%.")
        else:
            st.error("Final exam weight is 0%, so your final grade cannot change.")
        return

    needed_on_final = (desired_grade * 100.0 - current_grade * completed_weight) / final_weight
    result_cols[1].metric("Needed on final", f"{needed_on_final:.1f}%")

    if needed_on_final <= 0:
        st.success(f"You can still reach {desired_grade:.1f}% even with 0% on the final.")
    elif needed_on_final > 100:
        st.error(f"You need {needed_on_final:.1f}% on the final to reach {desired_grade:.1f}%.")
    else:
        st.success(f"You need {needed_on_final:.1f}% on the final to reach {desired_grade:.1f}%.")


def main() -> None:
    db.init_db()

    st.title("Smart Course Scheduler")
    st.caption("Track academic deadlines and generate a weekly study plan from urgency, priority, workload, and availability.")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Courses", "Tasks", "Study Blocks", "Weekly Schedule", "Grade Calculator"],
        )
        st.divider()
        theme, layout, theme_name = appearance_controls()
        apply_theme(theme, layout)
        st.caption(f"Using {theme_name} theme with {next(name for name, value in LAYOUTS.items() if value == layout)} layout.")
        st.divider()
        if st.button("Load sample/demo data"):
            db.add_demo_data()
            st.success("Demo data loaded.")
            st.rerun()

    courses, tasks, blocks = load_data()
    generated_schedule = generate_schedule(tasks, blocks)

    if page == "Dashboard":
        show_dashboard(tasks, theme, layout)
        st.divider()
        show_today_recommendation(generated_schedule, tasks)
    elif page == "Courses":
        courses_page(courses)
    elif page == "Tasks":
        tasks_page(courses, tasks)
    elif page == "Study Blocks":
        study_blocks_page(blocks)
    elif page == "Weekly Schedule":
        schedule_page(tasks, blocks)
    elif page == "Grade Calculator":
        grade_calculator_page()


if __name__ == "__main__":
    main()
