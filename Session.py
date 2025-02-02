import streamlit as st
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
import time


def get_session():
    runtime = get_instance()
    ctx = get_script_run_ctx()
    session_id = ctx.session_id
    session_info = runtime._instance.get_client(session_id)
    return session_id


@st.cache_resource
def get_active_users():
    return {}


def update_active_users(timeout=300):
    now = time.time()
    active_users = get_active_users()
    id = get_session()
    active_users[id] = now
    for user_id, last_active in list(active_users.items()):
        if now - last_active > timeout:
            del active_users[user_id]


def get_active_user_count():
    return len(get_active_users())
