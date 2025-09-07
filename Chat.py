import streamlit as st
from Settings import settings
import time
from Logger import log
from Utils import autoplay_audio, local_css, get_prompt
from Session import get_session
from UI_Utils import show_messages, handle_audio_input, process_user_query
import warnings


warnings.filterwarnings("ignore", category=DeprecationWarning)


# Session Initialization
def init_session():
    st.session_state["start_time"] = time.time()
    if "messages" not in st.session_state:
        st.session_state.prompts = get_prompt()
        st.session_state["messages"] = [
            {
                "role": "system",
                "content": st.session_state.prompts["prompt1"],
            }
        ]
    st.session_state["text_chat_enabled"] = False
    st.session_state.audio = None
    log.info(
        f"Session Start: {time.time()-st.session_state.start_time:.2f} seconds, {get_session()}"
    )
    if st.session_state.allow_text_chat:
        st.session_state.text_chat_enabled = True


def setup_sidebar():
    st.sidebar.header("Chat with " + settings["assistant_name"])
    # Show Profile
    with st.sidebar.container(border=True):
        for key, val in settings["sidebar"].items():
            st.subheader(f"{key.replace("_", " ")}: {val}")

    def toggle_text_chat():
        st.session_state.text_chat_enabled = not st.session_state.text_chat_enabled

    container = st.sidebar.container(border=True)
    con1 = container.container()
    con2 = container.container(border=True)
    con3 = container.container()
    con4 = container.empty()
    if st.session_state.allow_text_chat:
        con2.toggle(
            ":material/keyboard: Enable Text Chat",
            value=st.session_state.text_chat_enabled,
            on_change=toggle_text_chat,
        )
    return con1, con3, con4


st.set_page_config(
    page_title="Chat | " + settings["title"],
    page_icon=":material/chat:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Chat | " + settings["title"])
if "role" not in st.session_state:
    st.switch_page("Login.py")

# Inject CSS for custom styles
local_css("style.css")
if "text_chat_enabled" not in st.session_state:
    init_session()
container1, container3, container4 = setup_sidebar()
if st.session_state.audio:
    autoplay_audio(st.session_state.audio, container4)
    st.session_state.audio = None

col1, col2 = st.columns([0.3, 0.7])

with col1.container(height=600, border=False):
    st.image(settings["assistant_interview"])

with col2.container(height=600, border=True):

    if not st.session_state.allow_text_chat:
        st.markdown(
            "When you have completed the CRAFFT screening with Jordan, Click the **Next** Button in the Left Panel to move onto a debriefing session."
        )

    if st.session_state.allow_text_chat and not st.session_state.text_chat_enabled:
        st.markdown(
            "If you experience issues with voice chat, click the **Enable Text Chat** button in the left panel."
        )

    chatbox = st.container(border=True, key="chatbox")

    if len(st.session_state.messages) == 1:
        with st.spinner("🧑‍⚕️ Preparing Jordan for the interview… Please wait."):
            process_user_query(
                chatbox,
                model=settings["parameters"]["model"],
                temperature=settings["parameters"]["temperature"],
                voice=settings["parameters"]["voice"],
                instruction=settings["parameters"]["voice_instruction"],
            )

    show_messages(chatbox)

    user_query = ""
    input_placeholder = st.empty()
    if st.session_state.text_chat_enabled:
        user_query = input_placeholder.chat_input(
            "When you have completed the CRAFFT screening with Jordan, click the 'Next' button in the left panel to move onto a debriefing session.",
            disabled=not st.session_state.text_chat_enabled,
            key="chat_input_stage1",
        )

    if transcript := handle_audio_input(container1):
        user_query = transcript

    if user_query:
        st.session_state.messages.append(
            {"role": "user", "content": user_query.strip()}
        )
        process_user_query(
            chatbox,
            model=settings["parameters"]["model"],
            temperature=settings["parameters"]["temperature"],
            voice=settings["parameters"]["voice"],
            instruction=settings["parameters"]["voice_instruction"],
        )

# Handle end session
if len(st.session_state.messages) > 2 and container3.button(
    "Next",
    icon=":material/navigate_next:",
):
    st.switch_page("Debrief.py")

if container3.button("Start Over", icon=":material/restart_alt:"):
    del st.session_state["text_chat_enabled"]
    del st.session_state["messages"]
    st.rerun()
