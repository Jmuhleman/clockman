# Timesheet Management System

A production-ready, offline Timesheet Management System built with Streamlit and Python. It supports daily time entry, per-session project assignment, automatic time calculations, equal project allocation, and CSV persistence compatible with Excel, LibreOffice, and Google Sheets.

## Features
1. Morning and afternoon session tracking with validation.
2. Project management page with active project selection.
3. Automatic session and daily hour calculations.
4. Equal allocation of time across projects.
5. Editable summary grid with validation and safe CSV persistence.
6. Aggregated summaries by project and by date + project.

## Architecture
The codebase is organized into clear layers:
1. **UI layer**: `streamlit_app.py` renders the Streamlit interface.
2. **Validation layer**: `app/validators/` handles input validation rules.
3. **Business logic**: `app/services/` computes durations, allocations, and rows.
4. **Persistence layer**: `app/services/csv_persistence.py` manages CSV I/O.
5. **Project services**: `app/services/project_service.py` manages projects.
6. **Summary services**: aggregation and editable persistence in `app/services/`.
7. **Models and utilities**: `app/models/` and `app/utils/` provide typed data models and helpers.

## Folder Structure
```
project_root/
├── app/
│   ├── config/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── validators/
├── data/
│   └── timesheets.csv
│   └── projects.csv
├── tests/
├── requirements.txt
├── README.md
├── .gitignore
└── streamlit_app.py
```

## Installation
```bash
pip install -r requirements.txt
```

## Run the App
```bash
streamlit run streamlit_app.py
```

## CSV Schema
| Column | Description |
| --- | --- |
| Date | Entry date (YYYY-MM-DD) |
| Session | Morning or Afternoon |
| Check-in | HH:MM (24h) |
| Check-out | HH:MM (24h) |
| Session Duration | Hours for the session |
| Project Number | Project identifier |
| Allocated Time | Allocated hours per project |
| Daily Total | Total hours for the day |

## Projects CSV Schema
| Column | Description |
| --- | --- |
| project_code | Project identifier used in timesheets |
| project_name | Human-readable project name |
| active_status | True/False flag for availability |

## Summary Editing
- Use the **Summary** page to edit existing rows in-place.
- Click **Save Summary Changes** to validate and persist updates.
- Aggregated tables update automatically from saved data.

## Migration Notes
- Create `data/projects.csv` using the schema above to enable project selection.
- Existing `timesheets.csv` files remain compatible and editable.

## Example Screenshots
1. `docs/screenshots/daily-entry.png`
2. `docs/screenshots/summary.png`

## Testing
```bash
pytest
```

## Future Improvements
1. Weekly and monthly summaries.
2. Project analytics dashboards.
3. Editable past entries and audit history.
4. SQLite persistence and user authentication.
