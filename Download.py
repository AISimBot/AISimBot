import streamlit as st
from Session import get_active_users, push_session_log, remove_session
from Utils import elapsed, local_css
from Logger import log
from Settings import settings
from Transcript import create_transcript_pdf

st.set_page_config(
    page_title="Download | " + settings["title"],
    page_icon=":material/download:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Download | " + settings["title"])
# Inject CSS for custom styles
local_css("style.css")

# st.markdown(settings["agreement"])

# if st.checkbox("I agree to participate in the research."):
#    create_transcript_document()
#    push_session_log()

if st.download_button(
    label="Download Transcript",
    icon=":material/download:",
    data=create_transcript_pdf(),
    file_name="Transcript.pdf",
    mime="application/pdf",
):
    log.info(
        f"Session end: {elapsed(st.session_state.start_time)}, {st.session_state.id}"
    )
    remove_session(st.session_state.id)
