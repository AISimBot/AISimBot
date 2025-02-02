import streamlit as st
from Session import get_active_user_count


st.set_page_config(
    page_title="AI SimBot | Admin",
    page_icon=":material/admin_panel_settings:",
    layout="wide",
    initial_sidebar_state="expanded",
)

if st.sidebar.button(f"🟢 Active Users: {get_active_user_count()}"):
    st.rerun()

with st.form("Prompt"):
    prompt = st.text_area("Temporary Prompt", st.session_state.messages[0]["content"])
    if st.form_submit_button("Temporarily Change and Restart Chat"):
        st.session_state.messages = [{"role": "system", "content": prompt}]
        st.switch_page("Chat.py")
