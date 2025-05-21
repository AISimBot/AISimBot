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
st.session_state.browser = get_browser()
log.debug(st.session_state.browser)
if "Safari" in st.session_state.browser:
    version = re.search(r"\d+\.\d+", st.session_state.browser)[0]
    version = float(version)
    if version >= 18.4:
        st.error(
            "Safari 18.4, 18.5 is not supported. Please use [Google Chrome](https://www.google.com/chrome/) on your laptop or desktop.",
            icon=":material/stop:",
        )

st.markdown(
    """
To test your microphone and speaker:

1. Ensure you are in a quiet room with minimal background noise.
2. Click **🎙 Record** in the left panel.
3. If prompted, allow your browser to access your microphone.
4. When the button changes to **📤 Stop**, begin speaking.
5. Click **📤 Stop** when you're finished.
6. Ensure you can clearly hear your recording.

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

    player_container = st.empty()
    if audio := mic_recorder(
        start_prompt="🎙 Record",
        stop_prompt="📤 Stop",
        just_once=True,
        use_container_width=True,
        format="wav",
        key="recorder",
    ):
        autoplay_audio(audio["bytes"], player_container, controls=True)
    if st.button("Next", icon=":material/navigate_next:"):
        if "messages" in st.session_state:
            st.session_state.messages = st.session_state.messages[:1]
        st.switch_page("Chat.py")
