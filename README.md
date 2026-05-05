# smart-course-scheduler
A Python-based Smart Course Scheduler that helps students manage courses, assignments, exams, and deadlines in one place. The app uses priority, urgency, workload, and available study blocks to automatically generate a weekly study plan, making it easier to stay organized and focus on the right tasks at the right time.

## Overview

Smart Course Scheduler is a Streamlit student productivity app that stores courses, tasks, and weekly study availability in SQLite. It generates a weekly study schedule by ranking unfinished work with deadline urgency, priority, and estimated workload.

Resume bullet:

> Built a Python-based smart study planner that tracks academic deadlines and automatically generates weekly study schedules using urgency, priority, and workload-based scheduling logic.

## Features

- Add, edit, delete, and view courses.
- Add, edit, delete, and view academic tasks.
- Track task type, due date, estimated hours, priority, and completion status.
- Add weekly study blocks with day, start time, and end time.
- Automatically generate a weekly study schedule.
- Split larger tasks across multiple study sessions.
- Exclude completed tasks from the generated schedule.
- Flag overdue unfinished tasks.
- Show a "What should I study today?" recommendation.
- Dashboard metrics for total tasks, completed tasks, overdue tasks, upcoming tasks, and remaining study hours.
- Charts for tasks by course, completed vs incomplete tasks, and hours remaining by course.
- Export tasks and generated schedules to CSV.
- Load sample/demo data for quick testing.

## Tech Stack

- Python
- Streamlit
- SQLite
- Pandas
- Matplotlib

## Project Structure

```text
smart-course-scheduler/
|-- app.py
|-- database.py
|-- scheduler.py
|-- models.py
|-- utils.py
|-- requirements.txt
|-- README.md
|-- LICENSE
`-- .gitignore
```

## Setup Instructions

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the Streamlit app:

```powershell
streamlit run app.py
```

The app creates a local SQLite database file named `smart_course_scheduler.db` when it starts.

## How the Scheduler Works

The scheduler first removes completed tasks. It then gives each unfinished task a score based on priority and urgency:

- High priority = 3
- Medium priority = 2
- Low priority = 1
- Tasks due sooner receive a higher urgency score.
- Overdue unfinished tasks are flagged and treated as highly urgent.

Tasks are sorted by the combined score, then placed into weekly study blocks in order. If a task needs more time than one block or session, it is split across multiple sessions until its estimated hours are covered or available study time runs out.

## Suggested Screenshots

Add screenshots for these views after running the app:

- Dashboard with metrics and charts.
- Courses page with sample courses.
- Tasks page showing open, complete, and overdue tasks.
- Study Blocks page with weekly availability.
- Weekly Schedule page with generated study sessions.
- CSV export buttons.

## Future Improvements

- Add user accounts for multi-student use.
- Add recurring study blocks.
- Add calendar export with `.ics` files.
- Add filters by course, priority, and due-date range.
- Add notifications or email reminders.
- Add smarter workload balancing across the week.
