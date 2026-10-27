import streamlit as st
import uuid
import json
import time
from datetime import datetime, timedelta
import base64
import codecs
import shlex
import subprocess
from Logger import log
import tomllib
from browser_detection import browser_detection_engine


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


def autoplay_audio(audio_data, container=None, controls=False):
    b64 = base64.b64encode(audio_data).decode("utf-8")
    src = f"data:audio/mp3;base64,{b64}"
    mime = "audio/mp3"

    if controls:
        html_str = '<audio id="audio_player" autoplay controls>'
    else:
        html_str = '<audio id="audio_player" autoplay>'
    html_str += f"""
    <source src="{src}" type="{mime}">
    </audio>
    """
    if container == None:
        container = st.spinner()
    with container:
        st.html(html_str)


def stream_audio(chunks):
    """Play base64 Ogg Opus chunks in the browser as they arrive (see tts-stream.js)."""
    reply = uuid.uuid4().hex
    items = []
    with st.container(key="tts_player"):
        run_js("tts-stream.js")
        for chunk in chunks:
            items.append([reply, len(items), chunk])
            _push_audio(items[-1:])
        items.append([reply, len(items), None])
        _push_audio(items[-1:])
    # Streamlit drops messages that haven't reached the browser when the next run
    # starts, so the caller's rerun can cut off the end of the reply.
    # resend_audio() sends every chunk again in the next run; the player skips the ones it has.
    st.session_state.audio = items
    time.sleep(0.3)


def copy_audio_log_button(container):
    """A button that copies the TTS player's event log (window.__ttsLog) to the clipboard."""
    html = """
    <button id="tts_copy_log" style="width:100%;padding:0.4rem;border-radius:0.5rem;border:1px solid #ccc;background:white;cursor:pointer">Copy audio log</button>
    <script>
    (function () {
      const b = document.getElementById("tts_copy_log");
      if (!b || b.dataset.ready) return;
      b.dataset.ready = "1";
      b.addEventListener("click", async () => {
        const text = JSON.stringify(window.__ttsLog || []);
        try {
          await navigator.clipboard.writeText(text);
        } catch (_) {
          // The clipboard API needs https or localhost, so fall back to a hidden text box.
          const t = document.createElement("textarea");
          t.value = text;
          document.body.appendChild(t);
          t.select();
          document.execCommand("copy");
          t.remove();
        }
        b.textContent = `Copied ${(window.__ttsLog || []).length} events`;
        setTimeout(() => (b.textContent = "Copy audio log"), 2000);
      });
    })();
    </script>
    """
    with container:
        st.html(html, unsafe_allow_javascript=True)


def resend_audio(items):
    with st.container(key="tts_resend"):
        _push_audio(items)


def _push_audio(items):
    js = f"<script>(window.__ttsQueue = window.__ttsQueue || []).push(...{json.dumps(items)}); window.__tts && window.__tts.drain();</script>"
    st.html(js, width=1, unsafe_allow_javascript=True)


@st.cache_data(show_spinner=False)
def _read_file(file_name):
    with open(file_name, encoding="utf-8") as f:
        return f.read()


def local_css(file_name: str):
    css = _read_file(file_name)
    st.html(f"<style>{css}</style>")


def run_js(file_name: str):
    js = _read_file(file_name)
    st.html(js, width=1, unsafe_allow_javascript=True)


def load_prompt(prompt="prompt1"):
    st.session_state.prompts = tomllib.load(open("prompts.toml", "rb"))
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": st.session_state.prompts[prompt]}
        ]
    else:
        st.session_state["messages"][0] = {
            "role": "system",
            "content": st.session_state.prompts[prompt],
        }
