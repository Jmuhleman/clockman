from __future__ import annotations

"""
Simple password gate for Streamlit apps.

Security notes:
- We use bcrypt because it is a slow, adaptive password hashing algorithm designed
  for securely storing password verifiers.
- We store ONLY the bcrypt hash in Streamlit secrets, never the plaintext password.
- Authentication is persisted per-browser-session using st.session_state.
"""

import logging
from typing import Final

import bcrypt
import streamlit as st

logger = logging.getLogger(__name__)

_AUTH_KEY: Final[str] = "authenticated"
_PASSWORD_INPUT_KEY: Final[str] = "auth_password"
_CLEAR_PASSWORD_FLAG: Final[str] = "_auth_clear_password"


def logout() -> None:
    """Clear authentication state and rerun."""
    st.session_state[_AUTH_KEY] = False
    # Safely clear any typed password still in memory for this session.
    # Important: do NOT assign to a widget-bound key after it has been instantiated
    # in the same run. Use pop + rerun-safe flag instead.
    st.session_state.pop(_PASSWORD_INPUT_KEY, None)
    st.session_state[_CLEAR_PASSWORD_FLAG] = True
    st.rerun()


def _is_authenticated() -> bool:
    return bool(st.session_state.get(_AUTH_KEY, False))


def _get_password_hash_from_secrets() -> str:
    try:
        value = st.secrets["PASSWORD_HASH"]
    except KeyError as exc:
        raise ValueError(
            "Missing PASSWORD_HASH in .streamlit/secrets.toml. "
            "Add a bcrypt hash like: PASSWORD_HASH = \"$2b$12$...\""
        ) from exc
    if not isinstance(value, str) or not value.strip():
        raise ValueError("PASSWORD_HASH in secrets must be a non-empty string.")
    return value.strip()


def _clear_password_widget_state_if_requested() -> None:
    """
    Clear the password input widget state BEFORE it is instantiated.

    Streamlit raises if you modify st.session_state[key] for a widget key after the
    widget has been created during the same script run.
    """
    if st.session_state.pop(_CLEAR_PASSWORD_FLAG, False):
        st.session_state.pop(_PASSWORD_INPUT_KEY, None)


def check_password() -> None:
    """
    Enforce authentication. Call this at the very top of the app.

    If unauthenticated:
    - shows a password input
    - validates entered password vs stored bcrypt hash
    - denies access using st.stop()
    """
    if _is_authenticated():
        # Provide logout in the sidebar for authenticated users.
        with st.sidebar:
            st.button("Logout", on_click=logout)
        return

    st.set_page_config(page_title="Timesheet Management System", layout="wide")
    st.title("Timesheet Management System")

    st.info("This app is protected. Please enter the password to continue.")
    _clear_password_widget_state_if_requested()

    # Use a form so ENTER submits naturally.
    with st.form("login_form", clear_on_submit=False):
        password = st.text_input("Password", type="password", key=_PASSWORD_INPUT_KEY)
        submitted = st.form_submit_button("Sign in", type="primary")

    if submitted:
        try:
            stored_hash = _get_password_hash_from_secrets()
            ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        except ValueError:
            # Configuration error; show safe message (never show hash).
            st.error("Authentication is not configured correctly. Contact the administrator.")
            logger.exception("Auth misconfiguration (PASSWORD_HASH missing/invalid).")
            st.stop()
        except Exception:
            st.error("Authentication failed due to an internal error.")
            logger.exception("Unexpected authentication error.")
            st.stop()

        if ok:
            st.session_state[_AUTH_KEY] = True
            # Schedule password clearing for the NEXT run (before the widget is created).
            st.session_state[_CLEAR_PASSWORD_FLAG] = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    # Hard stop: nothing below should execute unless authenticated.
    st.stop()

