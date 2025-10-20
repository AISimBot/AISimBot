import streamlit as st
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
import time
import os
import shutil
from pathlib import Path
import json
import codecs
from Utils import run_command


def should_log_session():
    if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPOSITORY" in st.secrets:
        return True


@st.cache_resource
def setup_session_log():
    if not should_log_session():
        return
    try:
        os.mkdir("sessions")
    except:
        pass
    if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPOSITORY" in st.secrets:
        repo = st.secrets["GITHUB_REPOSITORY"]
        token = st.secrets["GITHUB_TOKEN"]
        run_command("git config --global user.name Streamlit")
        run_command("git config --global user.email streamlit@localhost")
        run_command(f"git remote set-url origin https://{token}@github.com/{repo}.git")


def log_session():
    if should_log_session():
        file = f"sessions/{st.session_state.id}.json"
        json.dump(st.session_state.messages, codecs.open(file, "w", "utf-8"), indent=4)


def push_session_log():
    if should_log_session():
        run_command("git add sessions")
        run_command("git commit -a -m 'session log'")
        run_command("git push origin")


def get_session():
    runtime = get_instance()
    ctx = get_script_run_ctx()
    session_id = ctx.session_id
    session_info = runtime._instance.get_client(session_id)
    st.session_state.id = session_id
    Path(f"static/{session_id}").mkdir(parents=True, exist_ok=True)
    return session_id


@st.cache_resource
def get_active_users():
    return {}


@st.fragment(run_every=60)
def update_active_users():
    now = time.time()
    active_users = get_active_users()
    active_users[st.session_state.id] = now


def clean_audio_cache():
    try:
        active_users = get_active_users().keys()
        for p in Path("static").glob("*"):
            if p.is_dir() and p.as_posix().replace("static/", "") not in active_users:
                shutil.rmtree(p)
    except:
        pass


def get_active_user_count(timeout=60):
    active_users = get_active_users()
    now = time.time()
    for user_id, last_active in list(active_users.items()):
        if now - last_active > timeout:
            del active_users[user_id]
    clean_audio_cache()
    return len(get_active_users())
