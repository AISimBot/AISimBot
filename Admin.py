import streamlit as st
from Session import get_active_user_count, push_session_log
from Settings import settings
from Logger import log
import json
from Utils import load_prompt
from pathlib import Path


def save_prompt(prompt):
    Path("prompts.toml").open("wb").write(prompt)


st.set_page_config(
    page_title="Admin | " + settings["title"],
    page_icon=":material/admin_panel_settings:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Admin | " + settings["title"])
if "role" not in st.session_state:
    st.switch_page("Login.py")

if st.sidebar.button(f"🟢 Active Users: {get_active_user_count()}"):
    st.rerun()

if "messages" not in st.session_state:
    load_prompt()

efforts = ["minimal", "low", "medium", "high"]
feedback_reasoning_effort = st.sidebar.selectbox(
    "Reasoning Effort for Feedback",
    efforts,
    index=efforts.index(settings["parameters"]["feedback_reasoning_effort"]),
)
settings["parameters"]["feedback_reasoning_effort"] = feedback_reasoning_effort

debrief_reasoning_effort = st.sidebar.selectbox(
    "Reasoning Effort for Debrief",
    efforts,
    index=efforts.index(settings["parameters"]["debrief_reasoning_effort"]),
)
settings["parameters"]["debrief_reasoning_effort"] = debrief_reasoning_effort


def toggle_display_reasoning():
    st.session_state.display_reasoning = not st.session_state.display_reasoning


st.session_state.setdefault("display_reasoning", False)
st.sidebar.toggle(
    "Display Reasoning",
    value=st.session_state.display_reasoning,
    on_change=toggle_display_reasoning,
)

st.sidebar.download_button(
    label="Download Prompt",
    data=open("prompts.toml", "rb").read(),
    file_name="prompts.toml",
    mime="text/plain",
)

prompt_file = st.sidebar.file_uploader("Load Prompt", type="toml")
if prompt_file:
    try:
        prompt = prompt_file.getvalue()
        save_prompt(prompt)
        load_prompt()
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
    prompt_text = Path("prompts.toml").open("r", encoding="utf-8").read()
    prompt = st.text_area("Temporary Prompt", prompt_text)
    if st.form_submit_button("Save"):
        save_prompt(prompt.encode("utf-8"))
        load_prompt()

    if (
        "GITHUB_TOKEN" in st.secrets
        and "GITHUB_REPOSITORY" in st.secrets
        and st.form_submit_button("Commit")
    ):
        save_prompt(prompt)
        load_prompt()
        push_session_log()
