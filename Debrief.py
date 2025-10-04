import streamlit as st
from Settings import settings
from Logger import log
from Utils import elapsed, load_audio, autoplay_audio, local_css, run_js
from Session import get_session
from UI_Utils import show_messages, handle_audio_input, process_user_query

if settings["parameters"]["model"].startswith("claude"):
    from AnthropicClient import get_response
else:
    from OpenAIClient import get_response, stream_response


# Session Initialization
def generate_Feedback():
    st.session_state.messages[0] = {
        "role": "system",
        "content": st.session_state.prompts["prompt2"],
    }
    st.session_state.messages.append(
        {"role": "system", "content": st.session_state.prompts["trigger1"]}
    )
    response = stream_response(
        st.session_state.messages,
        model=settings["parameters"]["feedback_model"],
        reasoning={"effort": "medium", "summary": "auto"},
    )
    with st.empty():
        try:
            while True:
                s = next(response)
                st.markdown(s.strip().split("\n")[0])
        except StopIteration as e:
            response = e.value
    st.session_state.messages[0] = {
        "role": "system",
        "content": st.session_state.prompts["prompt3"],
    }
    st.session_state.messages[-1] = {
        "role": "system",
        "content": st.session_state.prompts["trigger2"] + response,
    }
    st.session_state.feedback_generated = True


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
    page_title="Debrief | " + settings["title"],
    page_icon=":material/feedback:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Chat | " + settings["title"])
if "role" not in st.session_state:
    st.switch_page("Login.py")

# Inject CSS for custom styles
local_css("style.css")
run_js("scrol.js")
container1, container3, container4 = setup_sidebar()
load_audio("assets/audio/Send.mp3")
load_audio("assets/audio/Receive.mp3")
if st.session_state.audio:
    autoplay_audio(st.session_state.audio, container4)
    st.session_state.audio = None

col1, col2 = st.columns([0.3, 0.7])

with col1.container(height=600, border=False):
    img = settings["assistant_feedback"]
    st.image(img)

with col2.container(height=600, border=True):

    if not st.session_state.allow_text_chat:
        st.markdown(
            "When you finish the debriefiing with Dr. Casey, click the **Next** button to download the transcript or click the **Start Over** button in the left panel."
        )

    if st.session_state.allow_text_chat and not st.session_state.text_chat_enabled:
        st.markdown(
            "If you experience issues with voice chat, click the **Enable Text Chat** button in the left panel."
        )

    chatbox = st.container(border=True, key="chatbox")

    if not st.session_state.get("feedback_generated", False):
        with st.spinner(
            "📋 Reviewing your interaction and compiling insights for debriefing… Please wait and stay on this page. This may take up to a few minutes. Thank you for your patience."
        ):
            generate_Feedback()
            process_user_query(
                chatbox,
                model=settings["parameters"]["model"],
                voice=settings["parameters"]["feedback_voice"],
                instruction=settings["parameters"]["feedback_voice_instruction"],
            )

    show_messages(chatbox)

    user_query = ""
    input_placeholder = st.empty()
    if st.session_state.text_chat_enabled:
        user_query = input_placeholder.chat_input(
            "When you finish the debriefiing with Dr. Casey, click the 'Next' button to download the transcript or click the 'Start Over' in the left panel.",
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
            voice=settings["parameters"]["feedback_voice"],
            instruction=settings["parameters"]["feedback_voice_instruction"],
        )

# Handle end session
if len(st.session_state.messages) > 2 and container3.button(
    "Next",
    icon=":material/navigate_next:",
):
    log.info(f"Session end: {elapsed(st.session_state.start_time)} {get_session()}")
    st.switch_page("Download.py")

if container3.button("Start Over", icon=":material/restart_alt:"):
    del st.session_state["text_chat_enabled"]
    del st.session_state["messages"]
    st.switch_page("Chat.py")
