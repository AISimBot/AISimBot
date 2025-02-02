import streamlit as st
from io import BytesIO
from streamlit_mic_recorder import mic_recorder
import re
from docx import Document
import warnings
import io
import time
import codecs
from Logger import log
from Utils import get_uuid, elapsed, autoplay_audio
from Session import get_session, update_active_users
from OpenAIClient import speech_to_text, text_to_speech
from Settings import settings

if settings["parameters"]["model"].startswith("claude"):
    from AnthropicClient import get_response
else:
    from OpenAIClient import get_response

warnings.filterwarnings("ignore", category=DeprecationWarning)


@st.cache_data
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def get_prompt():
    return codecs.open("prompt.txt", "r", "utf-8").read()


def show_download():
    document = create_transcript_document()
    col1, col2 = st.columns([1, 1])
    # Button to download the full conversation transcript
    with col1:
        st.download_button(
            label="📥 Download Transcript",
            data=document,
            file_name="Transcript.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )


def create_transcript_document():
    doc = Document()
    doc.add_heading("Conversation Transcript\n", level=1)

    for message in st.session_state.messages[1:]:
        if message["role"] == "user":
            p = doc.add_paragraph()
            p.add_run(settings["user_name"] + ": ").bold = True
            p.add_run(message["content"])
        else:
            p = doc.add_paragraph()
            p.add_run(settings["assistant_name"] + ": ").bold = True
            p.add_run(message["content"])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# Session Initialization
def init_session():
    defaults = {
        "chat_active": True,
        "messages": [{"role": "system", "content": get_prompt()}],
        "processed_audio": None,
        "manual_input": None,
        "end_session_button_clicked": False,
        "download_transcript": False,
        "start_time": time.time(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    autoplay_audio(open("assets/unlock.mp3", "rb").read())
    log.info(f"Session Start: {get_session()}")
    update_active_users()


def setup_sidebar():
    st.sidebar.header("Chat with " + settings["assistant_name"])
    # Show Profile
    with st.sidebar.container(border=True):
        for key, val in settings["sidebar"].items():
            if re.search(r"(jpg|png|webp)$", val):
                st.image(val)
            else:
                st.subheader(f"{key.replace("_", " ")}: {val}")


def show_messages():
    for message in st.session_state.messages[1:]:
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
        with st.chat_message(name, avatar=avatar):
            st.markdown(message["content"])


def handle_audio_input():
    with st.sidebar.container(border=True):
        audio = mic_recorder(
            start_prompt="🎙 Record",
            stop_prompt="📤 Stop",
            just_once=False,
            use_container_width=True,
            format="wav",
            key="recorder",
        )
    # Check if there is a new audio recording and it has not been processed yet
    if audio and audio["id"] != st.session_state.processed_audio:
        return speech_to_text(audio)


def process_user_query(user_query):
    # Display the user's query
    with st.chat_message(
        settings["user_name"],
        avatar=settings["user_avatar"],
    ):
        st.markdown(user_query)

    # Store the user's query into the history
    st.session_state.messages.append({"role": "user", "content": user_query.strip()})

    response = get_response(st.session_state.messages)
    response = response.strip()
    if not st.session_state.end_session_button_clicked:
        if audio := text_to_speech(response):
            autoplay_audio(audio)

    with st.chat_message(
        settings["assistant_name"],
        avatar=settings["assistant_avatar"],
    ):
        st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


st.set_page_config(
    page_title="AI SimBot | Chat",
    page_icon=":material/chat:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS for custom styles
local_css("style.css")
if "chat_active" not in st.session_state:
    init_session()
st.title(settings["title"])
setup_sidebar()
show_messages()

# Check if there's a manual input and process it
if st.session_state.manual_input:
    user_query = st.session_state.manual_input
else:
    if st.session_state.end_session_button_clicked:
        user_query = st.chat_input("Questions about your feedback? Ask them here.")
    else:
        user_query = st.chat_input(
            "Click 'End Session' Button to Receive Feedback and Download Transcript."
        )
        if transcript := handle_audio_input():
            user_query = transcript

if user_query:
    process_user_query(user_query)
    if st.session_state.manual_input:
        st.session_state.manual_input = None
        st.rerun()

# Handle end session
if (
    not st.session_state.end_session_button_clicked
    and len(st.session_state.messages) > 1
):
    if st.button("End Session"):
        st.session_state.end_session_button_clicked = True
        log.info(f"Session end: {elapsed(st.session_state.start_time)} {get_session()}")
        st.session_state.download_transcript = True
        st.session_state["manual_input"] = "Goodbye. Thank you for coming."
        # Trigger the manual input immediately
        st.rerun()

# Show the download button
if st.session_state.download_transcript:
    show_download()
