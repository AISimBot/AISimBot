import streamlit as st
import hmac
from Settings import settings
from Utils import get_browser
from Logger import log


def check_password():
    if hmac.compare_digest(st.session_state.password, st.secrets["password"]):
        st.session_state.role = "student"
    elif hmac.compare_digest(st.session_state.password, st.secrets["admin_password"]):
        st.session_state.role = "admin"
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

if "password" in st.secrets:
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
        log.debug(get_browser())
        st.markdown(settings["intro"])
else:
    with st.container(border=True):
        st.markdown(settings["unavailable"])
