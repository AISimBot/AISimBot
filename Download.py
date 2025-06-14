import streamlit as st
from io import BytesIO
from Session import get_session, push_session_log
from Utils import local_css
from Settings import settings
from mistletoe import markdown
from fpdf import FPDF
from fpdf.enums import AccessPermission
from html2docx import html2docx
from pathlib import Path
from unicodedata import normalize
from unidecode import unidecode


def create_transcript_html(messages):
    md_lines = ["# Conversation Transcript", ""]
    debrief = False
    for msg in messages[1:]:
        speaker = (
            settings["user_name"]
            if msg["role"] == "user"
            else settings["assistant_name"]
        )
        if msg["role"] == "system":
            if not debrief:
                md_lines.append(f"---\n\n# Debrief\n\n")
            debrief = True
            speaker = "Instructor"
        if debrief and msg["role"] == "assistant":
            speaker = "Instructor"
        md_lines.append(f"**{speaker}:** {msg['content']}")
        md_lines.append("")  # blank line -> new paragraph

    md_text = "\n".join(md_lines)
    md_text = unidecode(normalize("NFC", md_text))
    html = markdown(md_text)
    return html


def create_transcript_pdf():
    html = create_transcript_html(st.session_state.messages)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font(
        "DejaVuSans", fname="assets/fonts/DejaVuSans-Bold.ttf", style="B", uni=True
    )
    pdf.set_font("DejaVuSans", size=16)
    pdf.add_page()
    pdf.set_encryption(owner_password="drkim@32", permissions=AccessPermission.none())
    pdf.write_html(html)
    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf


def create_transcript_document():
    html = create_transcript_html(st.session_state.messages)
    buf = html2docx(html, title="Transcript")
    file = Path("sessions/" + get_session() + ".docx")
    file.parent.mkdir(parents=True, exist_ok=True)
    file.open("wb").write(buf.getvalue())


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
    create_transcript_document()
    push_session_log()

document = create_transcript_pdf()
st.download_button(
    label="Download Transcript",
    icon=":material/download:",
    data=document,
    file_name="Transcript.pdf",
    mime="application/pdf",
)
