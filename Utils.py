import streamlit as st
import uuid
import time
from datetime import datetime, timedelta
import base64
import codecs
import shlex
import subprocess


def run_command(command, cwd="."):
    command_args = shlex.split(command)
    process = subprocess.Popen(
        command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
    )
    stdout, stderr = process.communicate()
    return stdout, stderr


def get_uuid():
    timestamp = time.time()
    id = uuid.uuid4()
    id = f"{id}-{timestamp}"
    id = base64.urlsafe_b64encode(id.encode("utf-8")).decode("utf-8")
    return id[:8]


def elapsed(start):
    duration = time.time() - start
    duration_td = timedelta(seconds=duration)
    days = duration_td.days
    hours, remainder = divmod(duration_td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    dur_str = ""
    if days:
        dur_str = f"{days} days "
    if hours:
        dur_str += f"{hours} hours "
    if minutes:
        dur_str += f"{minutes} minutes "
    if seconds:
        dur_str += f"{seconds} seconds"
    return dur_str


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


@st.cache_data
def local_css(file_name):
    with open(file_name) as f:
        st.html(f"<style>{f.read()}</style>")


@st.cache_data
def get_prompt():
    return codecs.open("prompt.txt", "r", "utf-8").read()
