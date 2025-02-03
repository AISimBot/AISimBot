import streamlit as st
from Session import get_active_user_count
from Settings import settings
from Logger import log
import json

st.set_page_config(
    page_title="Admin | " + settings["title"],
    page_icon=":material/admin_panel_settings:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Admin | " + settings["title"])

if st.sidebar.button(f"🟢 Active Users: {get_active_user_count()}"):
    st.rerun()

st.sidebar.download_button(
    label="Download Prompt",
    data=st.session_state.messages[0]["content"].encode("utf-8"),
    file_name="prompt.txt",
    mime="text/plain",
)

prompt_file = st.sidebar.file_uploader("Load Prompt", type="txt")
if prompt_file:
    try:
        st.session_state.messages[0]["content"] = prompt_file.getvalue().decode("utf-8")
    except Exception as e:
        log.exception(f"{e}")

st.sidebar.download_button(
    label="Download Chat",
    data=json.dumps(st.session_state.messages, indent=4).encode("utf-8"),
    file_name="chat.json",
    mime="application/json",
)

chat_file = st.sidebar.file_uploader("Load Chat", type="json")
if chat_file:
    try:
        st.session_state.messages = json.load(chat_file)
    except Exception as e:
        log.exception(f"{e}")


if st.sidebar.button("Reset Chat"):
    st.session_state.messages = [st.session_state.messages[0]]

with st.form("Prompt"):
    prompt = st.text_area("Temporary Prompt", st.session_state.messages[0]["content"])
    if st.form_submit_button("Temporarily Change"):
        st.session_state.messages[0]["content"] = prompt
        st.rerun()
