# pages/chats.py  (or pages/1_Chat.py)
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

from src.ui_core.settings import load_settings


def _get_history(base_url: str, user_id: int) -> List[Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/api/ai_chat/chats/{user_id}"  # NOTE: ai_chat (singular) [file:1]
    r = requests.get(url, timeout=(5, 20))
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json()


def _post_chat(base_url: str, user_id: int, user_message: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/api/v1/health-assistant/chat"
    payload = {"user_id": user_id, "user_message": user_message}

    try:
        r = requests.post(url, json=payload, timeout=(5, 60))
        r.raise_for_status()
        response = r.json()

        # Ensure the response has the expected structure
        if not isinstance(response, dict):
            response = {"role": "assistant", "content": str(response), "type": "chat"}

        # Ensure required fields are present
        if "role" not in response:
            response["role"] = "assistant"
        if "content" not in response:
            response["content"] = "I received an empty response."
        if "type" not in response:
            response["type"] = "chat"

        return response

    except requests.exceptions.RequestException as e:
        return {
            "role": "assistant",
            "content": f"Sorry, I encountered an error: {str(e)}",
            "type": "error",
        }


def _submit_cardset(
    base_url: str, user_id: int, answers: Dict[str, str]
) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/api/v1/health-assistant/cardset/submit"
    payload = {"user_id": user_id, "answers": answers}

    try:
        r = requests.post(url, json=payload, timeout=(5, 60))
        r.raise_for_status()
        response = r.json()

        # Ensure the response has the expected structure
        if not isinstance(response, dict):
            response = {
                "status": "success",
                "message": "Cardset submitted successfully",
            }

        return response

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Failed to submit cardset: {str(e)}"}


def _try_parse_cardset(content: str) -> Optional[List[Dict[str, Any]]]:
    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, list) else None
    except Exception:
        return None


st.set_page_config(page_title="Chat", layout="wide")
st.header("Chat")

settings = load_settings()

if "user_id" not in st.session_state:
    st.session_state.user_id = 62
if "server_messages" not in st.session_state:
    st.session_state.server_messages = []
if "pending_cardset" not in st.session_state:
    st.session_state.pending_cardset = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None
if "last_api_response" not in st.session_state:
    st.session_state.last_api_response = None


with st.sidebar:
    st.subheader("Session")
    st.caption(f"BASE_URL: {settings.base_url}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Load history"):
            try:
                st.session_state.server_messages = _get_history(
                    settings.base_url, int(st.session_state.user_id)
                )
                st.session_state.pending_cardset = None
                for m in reversed(st.session_state.server_messages):
                    if m.get("role") == "assistant" and m.get("type") == "cardset":
                        cs = _try_parse_cardset(m.get("content", ""))
                        if cs:
                            st.session_state.pending_cardset = cs
                        break
            except Exception as e:
                st.session_state.last_error = str(e)

    with c2:
        if st.button("Clear UI"):
            st.session_state.server_messages = []
            st.session_state.pending_cardset = None
            st.session_state.last_error = None
            st.session_state.last_api_response = None


if st.session_state.last_error:
    st.error(st.session_state.last_error)

# Render messages
for msg in st.session_state.server_messages:
    role = msg.get("role", "assistant")
    mtype = msg.get("type", "chat")
    content = msg.get("content", "")

    with st.chat_message(role):
        if mtype == "cardset":
            st.write("Cardset was sent earlier. Fill the questions below (if shown).")
        else:
            st.write(content)

# Cardset form
if st.session_state.pending_cardset:
    st.divider()
    st.subheader("Quick questions")

    cardset = st.session_state.pending_cardset
    answers: Dict[str, str] = {}

    with st.form("cardset_form"):
        for idx, q in enumerate(cardset, start=1):
            q_text = q.get("question", f"Question {idx}")
            q_type = q.get("type", "mcq")
            options = q.get("options", []) or []
            key = f"q{idx}"

            if q_type == "text":
                answers[key] = st.text_input(q_text, key=f"card_{key}")
            else:
                if not options:
                    options = ["Not sure"]
                answers[key] = st.radio(q_text, options, key=f"card_{key}")

        if st.form_submit_button("Submit answers"):
            try:
                resp = _submit_cardset(
                    settings.base_url, int(st.session_state.user_id), answers
                )
                st.session_state.last_api_response = resp
                st.session_state.server_messages = _get_history(
                    settings.base_url, int(st.session_state.user_id)
                )
                st.session_state.pending_cardset = None
                st.rerun()
            except Exception as e:
                st.session_state.last_error = str(e)

# Chat input
prompt = st.chat_input("Type a message…")  # [web:26]
if prompt:
    try:
        resp = _post_chat(settings.base_url, int(st.session_state.user_id), prompt)
        st.session_state.last_api_response = resp

        # If API returned a cardset, show it immediately
        if resp.get("type") == "cardset":
            st.session_state.pending_cardset = resp.get("questions", [])

        # Refresh history from DB-backed endpoint so UI matches server truth
        st.session_state.server_messages = _get_history(
            settings.base_url, int(st.session_state.user_id)
        )
        st.rerun()
    except Exception as e:
        st.session_state.last_error = str(e)

with st.expander("Debug: last API response"):
    st.json(st.session_state.last_api_response)
