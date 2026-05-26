PROJECTS_TABLE = "projects"
TIMESHEETS_TABLE = "timesheet_entries"

TIME_FORMAT = "%H:%M"
DECIMAL_PLACES = 2
TIME_INTERVAL_MINUTES = 15

DEFAULT_SESSION_TIMES = {
    "morning": {"check_in": "08:00", "check_out": "12:00"},
    "afternoon": {"check_in": "12:45", "check_out": "17:00"},
}

SESSION_LABELS = {
    "morning": "Morning",
    "afternoon": "Afternoon",
}

TIMESHEET_COLUMNS = [
    "Date",
    "Session",
    "Check-in",
    "Check-out",
    "Session Duration",
    "Project Number",
    "Allocated Time",
    "Daily Total",
]

PROJECT_COLUMNS = [
    "project_code",
    "project_name",
    "active_status",
]
