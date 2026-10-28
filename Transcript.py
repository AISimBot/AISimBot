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


def _phase_seconds(phase):
    start = st.session_state.get(f"{phase}_start_time")
    end = st.session_state.get(f"{phase}_end_time")
    return end - start if start and end else None


def _format_minutes(seconds):
    if seconds is None:
        return "Not recorded"
    hours, minutes = divmod(round(seconds / 60), 60)
    return f"{hours}h{minutes}m" if hours else f"{minutes}m"


def _nurse_turns(messages):
    # The feedback system message separates the interview from the debrief.
    turns = [0, 0]
    phase = 0
    for msg in messages[1:]:
        if msg["role"] == "system":
            phase = 1
        elif msg["role"] == "user":
            turns[phase] += 1
    return turns


def create_transcript_markdown(messages):
    interview_turns, debrief_turns = _nurse_turns(messages)
    interview_seconds = _phase_seconds("patient_interview")
    debrief_seconds = _phase_seconds("debrief")
    total_seconds = (
        interview_seconds + debrief_seconds
        if interview_seconds and debrief_seconds
        else None
    )
    md_lines = [
        "# Conversation Transcript",
        "",
        "| Phase | Duration | Turns |",
        "|---|---|---|",
        f"| Patient Interview | {_format_minutes(interview_seconds)} | {interview_turns} |",
        f"| Debriefing | {_format_minutes(debrief_seconds)} | {debrief_turns} |",
        f"| Total | {_format_minutes(total_seconds)} | {interview_turns + debrief_turns} |",
        "",
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
            # Drop the debrief model instruction in front of the feedback report.
            md_lines.append(content.removeprefix(st.session_state.prompts["trigger2"]))
            md_lines.append("")  # blank line -> new paragraph
            md_lines.append(f"---\n\n# Debrief\n")
            continue
        if debrief and msg["role"] == "assistant":
            speaker = settings["debrief_name"]

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
    # fpdf draws <hr> at the current y, right against the content above.
    # <br> moves it clear of text; after a table an empty <p> is enough.
    html = html.replace("<hr />", "<br><hr />")
    html = html.replace("</table>\n<br><hr />", "</table>\n<p></p><hr />")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans.ttf")
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans-Bold.ttf", style="B")
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans-Oblique.ttf", style="I")
    pdf.add_font("DejaVuSans", fname="assets/fonts/DejaVuSans-BoldOblique.ttf", style="BI")
    pdf.set_font("DejaVuSans", size=12)
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
