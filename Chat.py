import streamlit as st
from Settings import settings
from Utils import autoplay_audio, local_css, run_js
from UI_Utils import init_session, show_messages, handle_audio_input, process_user_query
from Session import update_active_users
import warnings


warnings.filterwarnings("ignore", category=DeprecationWarning)


def setup_sidebar():
    st.sidebar.header("Chat with " + settings["assistant_name"])
    # Show Profile
    with st.sidebar.container(border=True):
        for key, val in settings["sidebar"].items():
            st.subheader(f"{key.replace("_", " ")}: {val}")

    container = st.sidebar.container(border=True)
    con1 = container.container()
    con3 = container.container()
    con4 = container.empty()
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
run_js("scrol.js")
if "start_time" not in st.session_state:
    init_session()
update_active_users()
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

    chatbox = st.container(border=True, key="chatbox")

    if len(st.session_state.messages) == 1:
        with st.spinner("🧑‍⚕️ Preparing Jordan for the interview… Please wait."):
            process_user_query(
                chatbox,
                model=settings["parameters"]["model"],
                voice=settings["parameters"]["voice"],
                instruction=settings["parameters"]["voice_instruction"],
            )

    show_messages(chatbox)

    user_query = ""
    input_placeholder = st.empty()
    if st.session_state.allow_text_chat:
        user_query = input_placeholder.chat_input(
            "When you have completed the CRAFFT screening with Jordan, click the 'Next' button in the left panel to move onto a debriefing session.",
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
            voice=settings["parameters"]["voice"],
            instruction=settings["parameters"]["voice_instruction"],
        )

# Handle end session
if len(st.session_state.messages) > 2 and container3.button(
    "Next",
    icon=":material/navigate_next:",
):
    st.session_state.feedback_generated = False
    st.switch_page("Debrief.py")
