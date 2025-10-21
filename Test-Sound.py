import streamlit as st
from streamlit_mic_recorder import mic_recorder
from Settings import settings
from Utils import autoplay_audio, local_css
from Session import get_active_user_count, setup_session_log
from Utils import get_browser
from Logger import log
import re

st.set_page_config(
    page_title="Test Microphone and Speaker | " + settings["title"],
    page_icon=":material/chat:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Test Sound | " + settings["title"])

if "role" not in st.session_state:
    st.switch_page("Login.py")

setup_session_log()
# Inject CSS for custom styles
local_css("style.css")
browser = get_browser()
st.session_state.client_info = {}
st.session_state.client_info["browser"] = browser

if st.secrets.get("testing") and st.session_state.role == "student":
    with st.container(border=True):
        st.markdown(settings["unavailable"])
else:
    st.markdown(
        """
    To test your microphone and speaker:

    1. Ensure you are in a quiet room with minimal background noise.
    2. Click **🎙 Record** in the left panel.
    3. If prompted, allow your browser to access your microphone.
    4. **Chrome on Mac** may default to using your iPhone’s microphone. When prompted to allow microphone access, choose your Mac’s built-in microphone from the dropdown menu before clicking allow.
    5. When the button changes to **📤 Stop**, begin speaking.
    6. Click **📤 Stop** when you're finished.
    7. Ensure you can clearly hear your recording.

    If you can't hear yourself, refer to the following guides:

    - **Windows**: [How to set up and test microphones in Windows](https://support.microsoft.com/en-us/windows/how-to-set-up-and-test-microphones-in-windows-ba9a4aab-35d1-12ee-5835-cccac7ee87a4)  
    - **Mac**: [Change the sound input settings on Mac](https://support.apple.com/guide/mac-help/change-the-sound-input-settings-mchlp2567/mac)  

    When you're done testing, click the **Next** button in the left panel to begin the session.
    """
    )

    st.sidebar.header("Test Microphone and Speaker")
    with st.sidebar:
        if st.session_state.role == "admin" and st.button(
            f"🟢 Active Users: {get_active_user_count()}"
        ):
            st.rerun()
        else:
            get_active_user_count()

        player_container = st.empty()
        format = "aac" if "Safari" in browser else "webm"
        if audio := mic_recorder(
            start_prompt="🎙 Record",
            stop_prompt="📤 Stop",
            just_once=True,
            use_container_width=True,
            format=format,
            key="recorder",
        ):
            autoplay_audio(audio["bytes"], player_container, controls=True)
        if st.button("Next", icon=":material/navigate_next:"):
            if "messages" in st.session_state:
                st.session_state.messages = st.session_state.messages[:1]
            st.switch_page("Chat.py")
