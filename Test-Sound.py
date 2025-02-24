import streamlit as st
from streamlit_mic_recorder import mic_recorder
from Settings import settings
from Utils import autoplay_audio, local_css
from Session import get_active_user_count

st.set_page_config(
    page_title="Test Microphone and Speaker | " + settings["title"],
    page_icon=":material/chat:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Test Sound | " + settings["title"])

if "role" not in st.session_state:
    st.switch_page("Login.py")

# Inject CSS for custom styles
local_css("style.css")
st.markdown(
    """
To test your microphone and speaker:

1. Click **🎙 Record** in the left panel.
2. If prompted, allow your browser to access your microphone.
    - When granting microphone permission, Chrome allows you to select a microphone source when multiple options are available. ⚠ On macOS, it defaults to the iPhone microphone if accessible via the Continuity feature.
3. When the button changes to **📤 Stop**, begin speaking.
4. Click **📤 Stop** when you're finished.
5. Ensure you can clearly hear your recording.

If you can't hear yourself, refer to the following guides:

- **Windows**: [How to set up and test microphones in Windows](https://support.microsoft.com/en-us/windows/how-to-set-up-and-test-microphones-in-windows-ba9a4aab-35d1-12ee-5835-cccac7ee87a4)  
- **Mac**: [Change the sound input settings on Mac](https://support.apple.com/guide/mac-help/change-the-sound-input-settings-mchlp2567/mac)  

When you're done testing, click **Start Chat** below.
"""
)
if st.button("Start Chat"):
    if "messages" in st.session_state:
        st.session_state.messages = st.session_state.messages[:1]
    st.switch_page("Chat.py")

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
