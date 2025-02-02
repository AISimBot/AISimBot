import streamlit as st
import uuid
import time
from datetime import datetime, timedelta
import base64


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


def autoplay_audio(audio_data):
    b64 = base64.b64encode(audio_data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
