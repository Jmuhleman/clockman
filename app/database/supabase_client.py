from __future__ import annotations

import logging

import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except KeyError as exc:
        raise ValueError("Supabase credentials missing in .streamlit/secrets.toml.") from exc

    try:
        return create_client(url, key)
    except Exception as exc:  # pragma: no cover - defensive guard
        logging.exception("Failed to create Supabase client.")
        raise ValueError("Failed to initialize Supabase client.") from exc
