# update_prompts.py
import json
from types import SimpleNamespace
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

from src.ui_core.settings import load_settings  # if you keep settings.py at root


import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor


def must(name: str):
    if name not in st.secrets:
        raise RuntimeError(f"Missing secret: {name}")
    return st.secrets[name]


def load_settings_():
    return SimpleNamespace(
        db_host=must("HEALTHCARE_AI_DB_HOST"),
        db_port=int(st.secrets.get("HEALTHCARE_AI_DB_PORT", 5432)),
        db_name=must("HEALTHCARE_AI_DB_BASE"),
        db_user=must("HEALTHCARE_AI_DB_USER"),
        db_password=must("HEALTHCARE_AI_DB_PASS"),
        db_sslmode=st.secrets.get("HEALTHCARE_AI_DB_SSLMODE", "require"),
    )


def _get_conn():
    s = load_settings_()
    return psycopg2.connect(
        host=s.db_host,
        port=s.db_port,
        dbname=s.db_name,
        user=s.db_user,
        password=s.db_password,
        sslmode=getattr(s, "db_sslmode", "require"),
    )


def render_update_prompts():
    st.header("Update prompts")

    enable_writes = True  # keep as-is

    with _get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, name, updated_at FROM ai_prompts ORDER BY updated_at DESC"
            )
            rows = cur.fetchall()

    if not rows:
        st.info("No prompts found in ai_prompts table.")
        return

    names = [r["name"] for r in rows]
    name = st.selectbox("Select prompt", names)

    with _get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Removed meta from SELECT
            cur.execute(
                "SELECT id, name, prompt, updated_at FROM ai_prompts WHERE name = %s",
                (name,),
            )
            obj = cur.fetchone()

    if not obj:
        st.error("Prompt not found.")
        return

    prompt_text = st.text_area("Prompt", value=obj.get("prompt") or "", height=340)

    if st.button("Save", type="primary", disabled=not enable_writes):
        with _get_conn() as conn:
            with conn.cursor() as cur:
                # Update only prompt
                cur.execute(
                    "UPDATE ai_prompts SET prompt = %s WHERE name = %s",
                    (prompt_text, name),
                )
                conn.commit()

        st.success("Updated.")
        st.rerun()
