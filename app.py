"""Streamlit UI for the Smart Course Scheduler app."""

from __future__ import annotations

from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import database as db
from models import DAYS_OF_WEEK, PRIORITIES, TASK_TYPES
from scheduler import flag_overdue_tasks, generate_schedule
from utils import dataframe_to_csv, format_date, format_time, hours_between


st.set_page_config(
    page_title="Smart Course Scheduler",
    layout="wide",
)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return db.get_courses(), db.get_tasks(), db.get_study_blocks()


def course_options(courses: pd.DataFrame) -> dict[str, int]:
    return dict(zip(courses["name"], courses["id"]))


def show_dashboard(tasks: pd.DataFrame) -> None:
    st.subheader("Dashboard")
    flagged = flag_overdue_tasks(tasks)

    total_tasks = len(flagged)
    completed_tasks = int(flagged["completed"].sum()) if not flagged.empty else 0
    overdue_tasks = int(flagged["is_overdue"].sum()) if not flagged.empty else 0
    upcoming_tasks = int(((flagged["completed"] == 0) & (~flagged["is_overdue"])).sum()) if not flagged.empty else 0
    remaining_hours = (
        flagged.loc[flagged["completed"] == 0, "estimated_hours"].sum()
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

    chart_cols = st.columns(3)
    with chart_cols[0]:
        st.caption("Tasks by course")
        tasks_by_course = flagged.groupby("course_name")["id"].count()
        fig, ax = plt.subplots(figsize=(4, 3))
        tasks_by_course.plot(kind="bar", ax=ax, color="#4C78A8")
        ax.set_xlabel("")
        ax.set_ylabel("Tasks")
        st.pyplot(fig)

    with chart_cols[1]:
        st.caption("Completed vs incomplete")
        completed_counts = pd.Series(
            {
                "Completed": int((flagged["completed"] == 1).sum()),
                "Incomplete": int((flagged["completed"] == 0).sum()),
            }
        )
        fig, ax = plt.subplots(figsize=(4, 3))
        completed_counts.plot(kind="pie", ax=ax, autopct="%1.0f%%", colors=["#59A14F", "#E15759"])
        ax.set_ylabel("")
        st.pyplot(fig)

    with chart_cols[2]:
        st.caption("Hours remaining by course")
        remaining = flagged[flagged["completed"] == 0].groupby("course_name")["estimated_hours"].sum()
        fig, ax = plt.subplots(figsize=(4, 3))
        remaining.plot(kind="bar", ax=ax, color="#F28E2B")
        ax.set_xlabel("")
        ax.set_ylabel("Hours")
        st.pyplot(fig)


def show_today_recommendation(schedule: pd.DataFrame, tasks: pd.DataFrame) -> None:
    st.subheader("What should I study today?")
    today_name = date.today().strftime("%A")
    todays_sessions = schedule[schedule["day"] == today_name] if not schedule.empty else pd.DataFrame()

    overdue = flag_overdue_tasks(tasks)
    overdue = overdue[overdue["is_overdue"]] if not overdue.empty else pd.DataFrame()

    if not overdue.empty:
        st.warning("You have overdue unfinished tasks. Start with these before new work.")
        st.dataframe(
            overdue[["title", "course_name", "due_date", "priority", "estimated_hours"]],
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
        name = cols[0].text_input("Course name")
        instructor = cols[1].text_input("Instructor")
        color = cols[2].color_picker("Color", "#4C78A8")
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
        new_name = cols[0].text_input("Course name", selected["name"])
        new_instructor = cols[1].text_input("Instructor", selected["instructor"])
        new_color = cols[2].color_picker("Color", selected["color"])
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
        title = cols[0].text_input("Task title")
        course_name = cols[1].selectbox("Course", list(options.keys()))
        task_type = cols[2].selectbox("Type", TASK_TYPES)
        cols = st.columns([1, 1, 1, 1])
        due_date = cols[0].date_input("Due date", date.today())
        estimated_hours = cols[1].number_input("Estimated hours", min_value=0.25, value=1.0, step=0.25)
        priority = cols[2].selectbox("Priority", PRIORITIES, index=1)
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

    visible_tasks = flag_overdue_tasks(tasks)
    visible_tasks["status"] = visible_tasks.apply(
        lambda row: "Complete" if row["completed"] else ("Overdue" if row["is_overdue"] else "Open"),
        axis=1,
    )
    st.dataframe(
        visible_tasks[
            ["title", "course_name", "task_type", "due_date", "estimated_hours", "priority", "status"]
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

    st.markdown("#### Edit or delete a task")
    selected_label = st.selectbox(
        "Select task",
        [f"{row.title} ({row.course_name})" for row in tasks.itertuples()],
    )
    selected_index = [f"{row.title} ({row.course_name})" for row in tasks.itertuples()].index(selected_label)
    selected = tasks.iloc[selected_index]
    with st.form("edit_task"):
        cols = st.columns([2, 1, 1])
        new_title = cols[0].text_input("Task title", selected["title"])
        course_names = list(options.keys())
        current_course_index = course_names.index(selected["course_name"])
        new_course = cols[1].selectbox("Course", course_names, index=current_course_index)
        new_type = cols[2].selectbox("Type", TASK_TYPES, index=TASK_TYPES.index(selected["task_type"]))
        cols = st.columns([1, 1, 1, 1])
        new_due = cols[0].date_input("Due date", pd.to_datetime(selected["due_date"]).date())
        new_hours = cols[1].number_input(
            "Estimated hours",
            min_value=0.25,
            value=float(selected["estimated_hours"]),
            step=0.25,
        )
        new_priority = cols[2].selectbox("Priority", PRIORITIES, index=PRIORITIES.index(selected["priority"]))
        new_completed = cols[3].checkbox("Completed", bool(selected["completed"]))
        save, delete = st.columns(2)
        if save.form_submit_button("Save task"):
            db.update_task(
                int(selected["id"]),
                new_title,
                options[new_course],
                new_type,
                new_due.isoformat(),
                new_hours,
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
        day = cols[0].selectbox("Day", DAYS_OF_WEEK)
        start_time = cols[1].time_input("Start time")
        end_time = cols[2].time_input("End time")
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
    st.dataframe(display_blocks, use_container_width=True, hide_index=True)

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
        cols = st.columns(3)
        new_day = cols[0].selectbox("Day", DAYS_OF_WEEK, index=DAYS_OF_WEEK.index(selected["day_of_week"]))
        new_start = cols[1].time_input("Start time", value=pd.to_datetime(selected["start_time"]).time())
        new_end = cols[2].time_input("End time", value=pd.to_datetime(selected["end_time"]).time())
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


def main() -> None:
    db.init_db()

    st.title("Smart Course Scheduler")
    st.caption("Track academic deadlines and generate a weekly study plan from urgency, priority, workload, and availability.")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Courses", "Tasks", "Study Blocks", "Weekly Schedule"],
        )
        st.divider()
        if st.button("Load sample/demo data"):
            db.add_demo_data()
            st.success("Demo data loaded.")
            st.rerun()

    courses, tasks, blocks = load_data()
    generated_schedule = generate_schedule(tasks, blocks)

    if page == "Dashboard":
        show_dashboard(tasks)
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


if __name__ == "__main__":
    main()
