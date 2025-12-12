# chats_view.py
import json
from typing import Any, Dict, List, Optional
import streamlit as st
from .api_client import APIClient, load_settings


def _try_parse_cardset(content: str) -> Optional[List[Dict[str, Any]]]:
    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, list) else None
    except Exception:
        return None


def render_chat() -> None:
    st.header("Chat")

    settings = load_settings()
    client = APIClient(settings)

    st.session_state.setdefault("user_id", 62)
    st.session_state.setdefault("server_messages", [])
    st.session_state.setdefault("pending_cardset", None)
    st.session_state.setdefault("last_error", None)
    st.session_state.setdefault("last_api_response", {})

    # Add this after session_state defaults
    st.session_state.setdefault("history_loaded", False)

    if not st.session_state.history_loaded:
        try:
            st.session_state.server_messages = client.get_history(
                int(st.session_state.user_id)
            )
            st.session_state.pending_cardset = None
        except Exception as e:
            st.session_state.last_error = str(e)
        finally:
            st.session_state.history_loaded = True

    st.subheader("Session")

    c_uid, c_actions = st.columns([1, 2], gap="small")

    with c_actions:
        c_a1, c_a2, c_a3 = st.columns(3, gap="small")
        with c_a1:
            load_clicked = st.button("Load", use_container_width=True)
        with c_a2:
            clear_clicked = st.button("Clear UI", use_container_width=True)
        with c_a3:
            delete_clicked = st.button(
                "Clear chat", type="primary", use_container_width=True
            )

    if load_clicked:
        st.session_state.server_messages = client.get_history(
            int(st.session_state.user_id)
        )

    if clear_clicked:
        st.session_state.server_messages = []
        st.session_state.pending_cardset = None
        st.session_state.last_error = None
        st.session_state.last_api_response = {}

    if delete_clicked:
        resp = client.delete_history(int(st.session_state.user_id))
        st.session_state.last_api_response = resp
        st.session_state.server_messages = []  # clear UI immediately
        st.session_state.pending_cardset = None
        st.success("Chat cleared on server.")
        st.rerun()

    # with st.expander("Debug: last API response"):
    #     if (
    #         isinstance(st.session_state.last_api_response, (dict, list))
    #         and st.session_state.last_api_response
    #     ):
    #         st.json(st.session_state.last_api_response)
    #     else:
    #         st.caption("No API response yet.")

    with st.sidebar:
        st.subheader("Session")
        st.caption(f"BASE_URL: {settings.base_url}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Load history"):
                try:
                    st.session_state.server_messages = client.get_history(
                        int(st.session_state.user_id)
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

    for msg in st.session_state.server_messages:
        role = msg.get("role", "assistant")
        mtype = msg.get("type", "chat")
        content = msg.get("content", "")
        with st.chat_message(role):
            if mtype == "cardset":
                st.write(
                    "Cardset was sent earlier. Fill the questions below (if shown)."
                )
            else:
                st.write(content)

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
                    answers[key] = st.radio(
                        q_text, options or ["Not sure"], key=f"card_{key}"
                    )

            if st.form_submit_button("Submit answers"):
                resp = client.submit_cardset(int(st.session_state.user_id), answers)
                st.session_state.last_api_response = resp
                st.session_state.server_messages = client.get_history(
                    int(st.session_state.user_id)
                )
                st.session_state.pending_cardset = None
                st.rerun()

    prompt = st.chat_input("Type a message…")
    if prompt:
        resp = client.post_chat(int(st.session_state.user_id), prompt)
        st.session_state.last_api_response = resp
        if resp.get("type") == "cardset":
            st.session_state.pending_cardset = resp.get("questions", [])
        st.session_state.server_messages = client.get_history(
            int(st.session_state.user_id)
        )
        st.rerun()

    with st.expander("Debug: last API response"):
        st.json(st.session_state.last_api_response)
