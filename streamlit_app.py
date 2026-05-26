from __future__ import annotations

import csv
from datetime import date

import pandas as pd
import streamlit as st

from app.config.settings import (
    CSV_FILE,
    DECIMAL_PLACES,
    DEFAULT_SESSION_TIMES,
    PROJECTS_FILE,
    SESSION_LABELS,
    TIME_FORMAT,
    TIME_INTERVAL_MINUTES,
)
from app.services.csv_persistence import append_timesheet_rows, load_timesheets, write_timesheets
from app.services.editable_summary_service import validate_and_prepare_edits
from app.services.project_service import get_active_projects, load_projects, save_projects
from app.services.summary_aggregation_service import aggregate_by_date_project, aggregate_by_project
from app.services.time_calculator import compute_daily_total, compute_session_duration
from app.services.timesheet_service import build_timesheet_rows
from app.utils.time_options import generate_time_options, with_empty_option
from app.utils.time_utils import format_decimal
from app.validators.timesheet_validator import validate_daily_inputs


def _init_session_state() -> None:
    for key in SESSION_LABELS:
        defaults = DEFAULT_SESSION_TIMES.get(key, {})
        for field in ("check_in", "check_out"):
            state_key = f"{key}_{field}"
            if state_key not in st.session_state and field in defaults:
                st.session_state[state_key] = defaults[field]


@st.cache_data
def _time_options() -> list[str]:
    return with_empty_option(generate_time_options(TIME_INTERVAL_MINUTES))


def _default_time_index(options: list[str], default_value: str) -> int:
    if default_value in options:
        return options.index(default_value)
    return 0


def _render_time_inputs(label: str, key_prefix: str) -> tuple[str, str]:
    options = _time_options()
    defaults = DEFAULT_SESSION_TIMES.get(key_prefix, {})
    col1, col2 = st.columns(2)
    with col1:
        check_in = st.selectbox(
            f"{label} Check-in",
            options,
            key=f"{key_prefix}_check_in",
            index=_default_time_index(options, defaults.get("check_in", "")),
            format_func=lambda value: value if value else "—",
        )
    with col2:
        check_out = st.selectbox(
            f"{label} Check-out",
            options,
            key=f"{key_prefix}_check_out",
            index=_default_time_index(options, defaults.get("check_out", "")),
            format_func=lambda value: value if value else "—",
        )
    return check_in, check_out


def _render_project_select(
    label: str,
    key_prefix: str,
    project_options: list[str],
    project_labels: dict[str, str],
) -> list[str]:
    return st.multiselect(
        f"{label} Projects",
        project_options,
        key=f"{key_prefix}_projects",
        format_func=lambda value: project_labels.get(value, value),
    )


def _display_hours(value) -> str:
    return format_decimal(value, DECIMAL_PLACES) if value is not None else "N/A"


def _render_daily_entry() -> None:
    st.subheader("Daily Timesheet Entry")
    entry_date = st.date_input("Date", value=date.today())

    try:
        active_projects = get_active_projects(PROJECTS_FILE)
    except ValueError as exc:
        st.error(str(exc))
        active_projects = []
    project_options = [project.code for project in active_projects]
    project_labels = {
        project.code: f"{project.code} — {project.name}" if project.name else project.code
        for project in active_projects
    }
    if not project_options:
        st.warning("No active projects found. Add projects in the Projects page.")

    st.markdown("### Morning Session")
    morning_in, morning_out = _render_time_inputs("Morning", "morning")
    morning_projects = _render_project_select(
        "Morning", "morning", project_options, project_labels
    )

    st.markdown("### Afternoon Session")
    afternoon_in, afternoon_out = _render_time_inputs("Afternoon", "afternoon")
    afternoon_projects = _render_project_select(
        "Afternoon", "afternoon", project_options, project_labels
    )

    validation = validate_daily_inputs(
        entry_date,
        morning_in,
        morning_out,
        morning_projects,
        afternoon_in,
        afternoon_out,
        afternoon_projects,
        TIME_FORMAT,
    )

    for session_key, session_validation in validation.sessions.items():
        if session_validation.errors:
            label = SESSION_LABELS[session_key]
            st.error(f"{label}: " + " ".join(session_validation.errors))

    cross_errors = [
        error
        for error in validation.errors
        if "Morning session must finish" in error
    ]
    for error in cross_errors:
        st.error(error)

    morning_duration = (
        compute_session_duration(
            validation.sessions["morning"].data.check_in,
            validation.sessions["morning"].data.check_out,
            DECIMAL_PLACES,
            entry_date,
        )
        if validation.sessions["morning"].time_valid
        else None
    )
    afternoon_duration = (
        compute_session_duration(
            validation.sessions["afternoon"].data.check_in,
            validation.sessions["afternoon"].data.check_out,
            DECIMAL_PLACES,
            entry_date,
        )
        if validation.sessions["afternoon"].time_valid
        else None
    )
    daily_total = compute_daily_total([morning_duration, afternoon_duration], DECIMAL_PLACES)

    st.markdown("### Daily Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Morning Duration (h)", _display_hours(morning_duration))
    col2.metric("Afternoon Duration (h)", _display_hours(afternoon_duration))
    col3.metric("Daily Total (h)", _display_hours(daily_total))

    rows = []
    if not validation.errors:
        rows, _, daily_total = build_timesheet_rows(
            entry_date,
            {
                "morning": validation.sessions["morning"].data,
                "afternoon": validation.sessions["afternoon"].data,
            },
            DECIMAL_PLACES,
        )

    with st.expander("Allocation Details", expanded=False):
        if rows:
            allocation_df = pd.DataFrame(
                [
                    {
                        "Session": row.session,
                        "Project Number": row.project_number,
                        "Allocated Time": format_decimal(row.allocated_time, DECIMAL_PLACES),
                    }
                    for row in rows
                ]
            )
            st.dataframe(allocation_df, use_container_width=True)
        else:
            st.info("No allocations to display yet.")

    if st.button("Commit Timesheet"):
        if validation.errors:
            st.error("Please fix validation errors before committing.")
            return
        rows, _, _ = build_timesheet_rows(
            entry_date,
            {
                "morning": validation.sessions["morning"].data,
                "afternoon": validation.sessions["afternoon"].data,
            },
            DECIMAL_PLACES,
        )
        try:
            append_timesheet_rows(CSV_FILE, rows)
        except (ValueError, OSError, csv.Error) as exc:
            st.error(f"Commit failed: {exc}")
        else:
            st.success("Timesheet committed successfully.")


def _render_summary() -> None:
    st.subheader("Timesheet Summary")
    try:
        df = load_timesheets(CSV_FILE)
    except ValueError as exc:
        st.error(str(exc))
        return

    if df.empty:
        st.info("No timesheet entries found yet.")
        return

    st.markdown("### Editable Timesheet Entries")
    editable_df = df.copy()
    editable_df["Date"] = pd.to_datetime(editable_df["Date"], errors="coerce")
    edited_df = st.data_editor(
        editable_df,
        use_container_width=True,
        num_rows="dynamic",
    )

    if st.button("Save Summary Changes"):
        result = validate_and_prepare_edits(edited_df)
        if result.errors:
            for error in result.errors:
                st.error(error)
        else:
            try:
                write_timesheets(CSV_FILE, result.cleaned, backup=True)
            except (ValueError, OSError) as exc:
                st.error(f"Failed to save changes: {exc}")
            else:
                st.success("Summary changes saved.")
                df = result.cleaned

    st.markdown("### Totals by Project")
    try:
        project_totals = aggregate_by_project(df)
        st.dataframe(project_totals, use_container_width=True)
    except ValueError as exc:
        st.error(str(exc))

    st.markdown("### Totals by Date and Project")
    try:
        date_project_totals = aggregate_by_date_project(df)
        st.dataframe(date_project_totals, use_container_width=True)
    except ValueError as exc:
        st.error(str(exc))


def _render_projects() -> None:
    st.subheader("Project Management")
    try:
        projects_df = load_projects(PROJECTS_FILE)
    except ValueError as exc:
        st.error(str(exc))
        return
    if projects_df.empty:
        st.info("No projects yet. Add your first project below.")

    edited_projects = st.data_editor(
        projects_df,
        use_container_width=True,
        num_rows="dynamic",
    )

    if st.button("Save Projects"):
        edited_projects = edited_projects.copy()
        if "active_status" in edited_projects.columns:
            edited_projects["active_status"] = edited_projects["active_status"].fillna(True)
        try:
            save_projects(PROJECTS_FILE, edited_projects)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success("Projects saved.")


def main() -> None:
    st.set_page_config(page_title="Timesheet Management System", layout="wide")
    _init_session_state()

    st.title("Timesheet Management System")
    page = st.sidebar.radio("Navigation", ["Daily Entry", "Summary", "Projects"])

    if page == "Daily Entry":
        _render_daily_entry()
    elif page == "Summary":
        _render_summary()
    else:
        _render_projects()


if __name__ == "__main__":
    main()
