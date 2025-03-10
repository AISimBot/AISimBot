import streamlit as st
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
import time
import os
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
    update_active_users()
    if should_log_session():
        file = f"sessions/{get_session()}.json"
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
    return session_id


@st.cache_resource
def get_active_users():
    return {}


def update_active_users():
    now = time.time()
    active_users = get_active_users()
    id = get_session()
    active_users[id] = now


def get_active_user_count(timeout=300):
    active_users = get_active_users()
    now = time.time()
    for user_id, last_active in list(active_users.items()):
        if now - last_active > timeout:
            del active_users[user_id]

    return len(get_active_users())
