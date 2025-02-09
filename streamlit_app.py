import streamlit as st
from Utils import get_uuid
from Settings import settings
from Logger import log


def main():
    login_page = st.Page("Login.py", title="Login", icon=":material/login:")
    chat_page = st.Page("Chat.py", title="Chat", icon=":material/chat:")
    test_page = st.Page("Test-Sound.py", title="Test Sound", icon="👂")
    admin_page = st.Page(
        "Admin.py", title="Admin", icon=":material/admin_panel_settings:"
    )
    if "role" not in st.session_state:
        pg = st.navigation([login_page, chat_page], position="hidden")
    elif st.session_state.role == "student":
        pg = st.navigation([chat_page, test_page])
    elif st.session_state.role == "admin":
        pg = st.navigation([chat_page, test_page, admin_page])
    pg.run()
    st.sidebar.header("Content Warning")
    st.sidebar.markdown(f":material/warning: :orange[{settings["warning"]}]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        id = get_uuid()
        log.exception(f"Unhandled exception: {id}")
        st.error(f"{settings['error_message']}\n\n**Reference id: {id}**")
