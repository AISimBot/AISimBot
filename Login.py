import streamlit as st
import hmac
from Settings import settings


def check_password():
    st.session_state.allow_text_chat = settings["allow_text_chat"]
    if st.session_state.password in st.secrets["passwords"]:
        st.session_state.role = "student"
        if "Chat" in st.session_state.password:
            st.session_state.allow_text_chat = True
    elif hmac.compare_digest(st.session_state.password, st.secrets["admin_password"]):
        st.session_state.role = "admin"
        st.session_state.allow_text_chat = True
    else:
        return False

    del st.session_state["password"]
    return True


st.set_page_config(
    page_title="Login | " + settings["title"],
    page_icon=":material/login:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Login | " + settings["title"])

if "passwords" in st.secrets:
    st.sidebar.header("Access Code")
    with st.sidebar.container(border=True):
        with st.form("Credentials"):
            st.text_input("Access Code", type="password", key="password")
            if st.form_submit_button("Login"):
                if check_password():
                    st.switch_page("Test-Sound.py")
                else:
                    st.error("😕 Invalid Code")
    with st.container(border=True):
        st.markdown(settings["intro"])
else:
    with st.container(border=True):
        st.markdown(settings["unavailable"])
