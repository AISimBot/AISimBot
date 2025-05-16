import streamlit as st
from io import BytesIO
from streamlit_mic_recorder import mic_recorder
import re
import warnings
import io
import time
import codecs
from Logger import log
from Utils import get_uuid, elapsed, autoplay_audio, local_css, get_prompt
from Session import (
    get_session,
    update_active_users,
    get_active_user_count,
    log_session,
    push_session_log,
)
from OpenAIClient import speech_to_text, text_to_speech
from Settings import settings

if settings["parameters"]["model"].startswith("claude"):
    from AnthropicClient import get_response
else:
    from OpenAIClient import get_response

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Session Initialization
def init_session():
    st.session_state["start_time"] = time.time()
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": get_prompt()}]
    # Cache large prompt to cut down first response time.
    get_response(st.session_state.messages)
    st.session_state["manual_input"] = None
    st.session_state["text_chat_enabled"] = False
    st.session_state.stage = 1
    st.session_state.audio = None
    autoplay_audio(open("assets/unlock.mp3", "rb").read())
    update_active_users()
    log.info(
        f"Session Start: {time.time()-st.session_state.start_time:.2f} seconds, {get_session()}"
    )


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
    con2.toggle(
        ":material/keyboard: Enable Text Chat",
        value=st.session_state.text_chat_enabled,
        on_change=toggle_text_chat,
    )
    return con1, con3, con4


def show_messages(chatbox):
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        name = (
            settings["user_name"]
            if message["role"] == "user"
            else settings["assistant_name"]
        )
        avatar = (
            settings["user_avatar"]
            if message["role"] == "user"
            else settings["assistant_avatar"]
        )
        with chatbox.chat_message(name, avatar=avatar):
            st.markdown(message["content"])


def handle_audio_input(container):
    with container:
        if audio := mic_recorder(
            start_prompt="🎙 Record",
            stop_prompt="📤 Stop",
            just_once=True,
            use_container_width=True,
            format="wav",
            key="recorder",
        ):
            return speech_to_text(audio)


def process_user_query(chatbox):
    message = st.session_state.messages[-1]
    # Display the user's query
    if st.session_state.text_chat_enabled and message["role"] == "user":
        with chatbox.chat_message(
            settings["user_name"],
            avatar=settings["user_avatar"],
        ):
            st.markdown(message["content"])
    if st.session_state.manual_input:
        response = get_response(
            st.session_state.messages,
            settings["parameters"]["feedback_model"],
            settings["parameters"]["feedback_temperature"],
        )
        response = "Use the following feedback for debriefing.\n" + response
        st.session_state.messages.append({"role": "system", "content": response})
        response = get_response(
            st.session_state.messages,
            temperature=settings["parameters"]["feedback_temperature"],
        )
        st.session_state.manual_input = None
    elif st.session_state.stage == 2:
        response = get_response(
            st.session_state.messages,
            temperature=settings["parameters"]["feedback_temperature"],
        )
    else:
        response = get_response(st.session_state.messages)
    response = response.strip()
    st.session_state.messages.append({"role": "assistant", "content": response})

    voice = (
        settings["parameters"]["voice"]
        if st.session_state.stage == 1
        else settings["parameters"]["feedback_voice"]
    )
    instruction = (
        settings["parameters"]["voice_instruction"]
        if st.session_state.stage == 1
        else settings["parameters"]["feedback_voice_instruction"]
    )
    log_session()
    if audio := text_to_speech(response, voice=voice, instructions=instruction):
        st.session_state.audio = audio
        st.rerun()


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
    img = (
        settings["assistant_interview"]
        if st.session_state.stage == 1
        else settings["assistant_feedback"]
    )
    st.image(img)

with col2.container(height=600, border=True):
    chatbox = st.container(border=True)
    if st.session_state.text_chat_enabled:
        show_messages(chatbox)
    else:
        st.markdown(
            """
            You are in voice chat-only mode, which disables text input and hides the conversation history.

            When you are ready, click **🎙 Record**, allow microphone access if prompted, speak when the button changes to **📤 Stop**, then click **📤 Stop** when you are done speaking.

            If you experience issues with voice chat, click **Enable Text Chat** in the left panel.
        """
        )

    # Check if there's a manual input and process it
    if st.session_state.manual_input:
        container3.button(
            "🤔 Preparing for Your Debriefing Session...",
            icon=":material/feedback:",
            disabled=True,
        )
        process_user_query(chatbox)

    if st.session_state.stage == 1:
        user_query = st.chat_input(
            "Click 'Next' Button in the Left Panel to move onto a debriefing session.",
            disabled=not st.session_state.text_chat_enabled,
        )
    elif st.session_state.stage == 2:
        user_query = st.chat_input(
            "Ask questions about your feedback below or click 'Start Over' in the left panel.",
            disabled=not st.session_state.text_chat_enabled,
        )

    if transcript := handle_audio_input(container1):
        user_query = transcript

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query.strip()})
        process_user_query(chatbox)

# Handle end session
if st.session_state.stage == 1:
    if len(st.session_state.messages) > 1 and container3.button(
        "Next",
        icon=":material/navigate_next:",
        disabled=(st.session_state.stage == 2),
    ):
        st.session_state.stage = 2
        st.session_state.messages.append({"role": "system", "content": "Please provide a feedback."})
        st.session_state.manual_input = "Feedback"
        process_user_query(chatbox)
elif st.session_state.stage == 2:
    if container3.button("Start Over", icon=":material/restart_alt:"):
        del st.session_state["text_chat_enabled"]
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    if container3.button(
        "Next",
        icon=":material/navigate_next:",
    ):
        log.info(f"Session end: {elapsed(st.session_state.start_time)} {get_session()}")
        st.switch_page("Download.py")
