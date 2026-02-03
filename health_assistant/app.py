import streamlit as st
from src.ui_core.chats_view import render_chat
from pages.update_prompts import render_update_prompts

st.set_page_config(page_title="Healthcare AI Admin", layout="wide")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Chat", "Update Prompts"])

with tab1:
    render_chat()

with tab2:
    render_update_prompts()
