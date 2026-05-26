# Timesheet Management System

A production-ready Timesheet Management System built with Streamlit and Python. It supports daily time entry, per-session project assignment, automatic time calculations, equal project allocation, and Supabase persistence.

## Features
1. Morning and afternoon session tracking with validation.
2. Project management page with active project selection.
3. Automatic session and daily hour calculations.
4. Equal allocation of time across projects with optional manual override.
5. Editable summary grid with validation and Supabase persistence.
6. Aggregated summaries by project and by date + project.

## Architecture
The codebase is organized into clear layers:
1. **UI layer**: `streamlit_app.py` renders the Streamlit interface.
2. **Validation layer**: `app/validators/` handles input validation rules.
3. **Business logic**: `app/services/` computes durations, allocations, and rows.
4. **Persistence layer**: `app/database/` (Supabase client + repositories) with `app/services/timesheet_persistence.py` as the DataFrame adapter.
5. **Project services**: `app/services/project_service.py` manages projects.
6. **Summary services**: aggregation and editable persistence in `app/services/`.
7. **Models and utilities**: `app/models/` and `app/utils/` provide typed data models and helpers.

## Folder Structure
```
project_root/
├── app/
│   ├── config/
│   ├── database/
│   │   ├── repositories/
│   │   └── supabase_client.py
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── validators/
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

## Supabase Setup
Create `.streamlit/secrets.toml` using the example file:
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-service-role-or-anon-key"
```

Required tables (already provisioned in your Supabase project):
- `projects` — `project_code`, `project_name`, `active_status`, `created_at`
- `timesheet_entries` — `work_date`, `session`, `check_in`, `check_out`, `session_duration`, `project_code`, `allocated_time`, `daily_total`, `created_at`

## Streamlit Deployment
- Add `SUPABASE_URL` and `SUPABASE_KEY` to Streamlit Cloud secrets (or use `.streamlit/secrets.toml` locally).
- Ensure the `projects` and `timesheet_entries` tables exist in Supabase.

## Run the App
```bash
streamlit run streamlit_app.py
```

## Timesheet Display Columns
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

## Summary Editing
- Use the **Summary** page to edit existing rows in-place.
- Click **Save Summary Changes** to validate and persist updates.
- Aggregated tables update automatically from saved data.
- Delete rows in the editor to remove entries, then save.

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
