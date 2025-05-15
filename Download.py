import streamlit as st
from docx import Document
from io import BytesIO
from Session import push_session_log
from Utils import local_css
from Settings import settings


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


st.set_page_config(
    page_title="Download | " + settings["title"],
    page_icon=":material/download:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Download | " + settings["title"])
# Inject CSS for custom styles
local_css("style.css")

st.markdown(settings["agreement"])

if st.checkbox("I agree to participate in the research."):
    push_session_log()

document = create_transcript_document()
st.download_button(
    label="Download Transcript",
    icon=":material/download:",
    data=document,
    file_name="Transcript.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)
