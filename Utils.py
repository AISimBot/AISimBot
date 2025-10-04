import streamlit as st
import uuid
import time
from datetime import datetime, timedelta
import base64
import codecs
import shlex
import subprocess
from Logger import log
import tomllib
from browser_detection import browser_detection_engine
import streamlit.components.v1 as components


def get_browser():
    info = "Unknown Browser"
    try:
        browser = browser_detection_engine()
        info = f"{browser['name']} {browser['version']} on {browser['platform']}"
        tags = []
        if browser["isAndroid"]:
            tags.append("Android")
        if browser["isTablet"]:
            tags.append("Tablet")
        if browser["isMobile"]:
            tags.append("Mobile")
        if browser["isDesktop"]:
            tags.append("Desktop")
        if browser["isWebkit"]:
            tags.append("Webkit")
        if browser["isIE"]:
            tags.append("IE")
        if browser["isChrome"]:
            tags.append("Chrome")
        if browser["isFireFox"]:
            tags.append("FireFox")
        if browser["isSafari"]:
            tags.append("Safari")
        if browser["isOpera"]:
            tags.append("Opera")
        if browser["isEdge"]:
            tags.append("Edge")
        tags = ", ".join(tags)
        info = info + ", " + tags
    except Exception as e:
        log.exception(e)
    return info


def run_command(command, cwd="."):
    log.info(f"Command: {command}")
    command_args = shlex.split(command)
    process = subprocess.Popen(
        command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
    )
    stdout, stderr = process.communicate()
    log.info(f"Out: {stdout}")
    if stderr:
        log.info(f"Error: {stderr}")
    return stdout, stderr


def get_uuid():
    timestamp = time.time()
    id = uuid.uuid4()
    id = f"{id}-{timestamp}"
    id = base64.urlsafe_b64encode(id.encode("utf-8")).decode("utf-8")
    return id[:8]


def elapsed(start):
    duration = time.time() - start
    td = timedelta(seconds=duration)

    days = td.days
    hours, rem = divmod(td.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    microseconds = td.microseconds

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if seconds or microseconds:
        if microseconds:
            parts.append(f"{seconds + microseconds / 1_000_000:.3f} seconds")
        else:
            parts.append(f"{seconds} seconds")

    return " ".join(parts) or "0 seconds"


@st.cache_data(show_spinner=False)
def load_audio(file, controls=False):
    b64 = base64.b64encode(_load_file(file)).decode("utf-8")
    id = file[file.rindex("/") + 1 : file.rindex(".")]
    if controls:
        html_str = f'<audio id="{id}" controls>'
    else:
        html_str = f'<audio id="{id}">'
    html_str += f"""
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.html(html_str)


def autoplay_audio(audio_data, container=None, controls=False):
    b64 = base64.b64encode(audio_data).decode("utf-8")
    if controls:
        html_str = '<audio id="audio_player" autoplay controls>'
    else:
        html_str = '<audio id="audio_player" autoplay>'
    html_str += f"""
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    if container == None:
        container = st.empty()
    with container:
        st.html(html_str)


@st.cache_data(show_spinner=False)
def _load_file(file):
    with open(file, "rb") as f:
        return f.read()


@st.cache_data(show_spinner=False)
def _read_file(file_name: str) -> str:
    with open(file_name, encoding="utf-8") as f:
        return f.read()


@st.cache_data(show_spinner=False)
def local_css(file_name: str):
    css = _read_file(file_name)
    st.html(f"<style>{css}</style>")


def run_js(file_name: str):
    js = _read_file(file_name)
    # st.markdown(js, unsafe_allow_html=True)
    components.html(js, width=0, height=0)


@st.cache_data
def get_prompt():
    return tomllib.load(open("prompts.toml", "rb"))
