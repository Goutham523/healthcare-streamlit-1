import streamlit as st
from src.ui_core.chats_view import render_chat

from pages.update_prompts import render_update_prompts

st.set_page_config(page_title="Healthcare AI Admin", layout="wide")

page = st.sidebar.radio("Menu", ["Chat", "Update prompts"])

if page == "Chat":
    render_chat()
else:
    render_update_prompts()
