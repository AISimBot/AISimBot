import streamlit as st
from Session import get_active_user_count, push_session_log
from Settings import settings
from Logger import log
import json
from Utils import get_prompt
import codecs

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
    st.session_state["messages"] = [
        {"role": "system", "content": get_prompt()["prompt1"]}
    ]

st.sidebar.download_button(
    label="Download Prompt",
    data=st.session_state.messages[0]["content"].encode("utf-8"),
    file_name="prompt.txt",
    mime="text/plain",
)

prompt_file = st.sidebar.file_uploader("Load Prompt", type="txt")
if prompt_file:
    try:
        prompt = prompt_file.getvalue().decode("utf-8")
        st.session_state.messages[0]["content"] = prompt
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
        st.switch_page("Chat.py")

    if (
        "GITHUB_TOKEN" in st.secrets
        and "GITHUB_REPOSITORY" in st.secrets
        and st.form_submit_button("Commit")
    ):
        st.session_state.messages[0]["content"] = prompt
        codecs.open("prompt.txt", "w", "utf-8").write(
            st.session_state.messages[0]["content"]
        )
        push_session_log()
        st.switch_page("Chat.py")
