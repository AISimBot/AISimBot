import streamlit as st
from io import BytesIO
from Settings import settings
from mistletoe import markdown
from fpdf import FPDF
from fpdf.enums import AccessPermission
from html2docx import html2docx
from pathlib import Path
from unicodedata import normalize
from unidecode import unidecode
from zoneinfo import ZoneInfo
from datetime import datetime


def _format_timestamp(timestamp):
    if not timestamp:
        return "Not recorded"
    tz = ZoneInfo(settings.get("timezone", "UTC"))
    return datetime.fromtimestamp(timestamp, tz).strftime("%Y-%m-%d %H:%M:%S")


def _phase_timing_line(label, start_key, end_key, elapsed_key):
    start = st.session_state.get(start_key)
    end = st.session_state.get(end_key)
    elapsed = st.session_state.get(elapsed_key, "Not recorded")
    return (
        f"{label}: Start: {_format_timestamp(start)}, "
        f"End: {_format_timestamp(end)}, Elapsed: {elapsed}"
    )


def create_transcript_markdown(messages):
    md_lines = [
        "# Conversation Transcript",
        "",
        "---",
        _phase_timing_line(
            "Patient Interview",
            "patient_interview_start_time",
            "patient_interview_end_time",
            "patient_interview_elapsed_time",
        ),
        "",
        _phase_timing_line(
            "Debriefing",
            "debrief_start_time",
            "debrief_end_time",
            "debrief_elapsed_time",
        ),
        "---",
        "",
    ]
    debrief = False
    for msg in messages[1:]:
        speaker = (
            settings["user_name"]
            if msg["role"] == "user"
            else settings["assistant_name"]
        )
        content = msg["content"]
        if msg["role"] == "system":
            debrief = True
            md_lines.append(f"---\n\n# Feedback\n")
            speaker = "Instructor"
            md_lines.append(f"**{speaker}:** {content}")
            md_lines.append("")  # blank line -> new paragraph
            md_lines.append(f"---\n\n# Debrief\n")
            continue
        if debrief and msg["role"] == "assistant":
            speaker = "Instructor"

        md_lines.append(f"**{speaker}:** {content}")
        md_lines.append("")  # blank line -> new paragraph

    md_text = "\n".join(md_lines)
    md_text = unidecode(normalize("NFC", md_text))
    return md_text


def create_transcript_html(messages):
    md = create_transcript_markdown(messages)
    html = markdown(md)
    return html


def create_transcript_pdf():
    html = create_transcript_html(st.session_state.messages)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans.ttf")
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans-Bold.ttf", style="B")
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans-Oblique.ttf", style="I")
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans-BoldOblique.ttf", style="BI")
    pdf.set_font("DejaVuSans", size=16)
    pdf.add_page()
    pdf.set_encryption(owner_password="drkim@32", permissions=AccessPermission.none())
    pdf.write_html(html, ul_bullet_char="\u2022")
    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf


def create_transcript_document():
    html = create_transcript_html(st.session_state.messages)
    buf = html2docx(html, title="Transcript")
    file = Path(f"sessions/{st.session_state.id}.docx")
    file.parent.mkdir(parents=True, exist_ok=True)
    file.open("wb").write(buf.getvalue())
