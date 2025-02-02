import streamlit as st
import tomllib


def load_settings():
    return tomllib.load(open("settings.toml", "rb"))


if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
settings = st.session_state.settings
