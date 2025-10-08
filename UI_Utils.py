import streamlit as st
from streamlit_mic_recorder import mic_recorder
from Settings import settings
from OpenAIClient import speech_to_text, text_to_speech
from Session import log_session

if settings["parameters"]["model"].startswith("claude"):
    from AnthropicClient import get_response
else:
    from OpenAIClient import get_response


def show_messages(chatbox):
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        name = (
            settings["user_name"]
            if message["role"] == "user"
            else settings["assistant_name"]
        )
        avatar = (
            settings["user_avatar"]
            if message["role"] == "user"
            else settings["assistant_avatar"]
        )
        with chatbox.chat_message(name, avatar=avatar):
            st.markdown(message["content"], unsafe_allow_html=True)


def handle_audio_input(container):
    format = "aac" if "Safari" in st.session_state.client_info["browser"] else "webm"
    with container:
        if audio := mic_recorder(
            start_prompt="🎙 Record",
            stop_prompt="📤 Stop",
            just_once=True,
            use_container_width=True,
            format=format,
            key="recorder",
        ):
            return speech_to_text(audio)


def process_user_query(
    chatbox,
    model,
    voice,
    instruction,
    reasoning={"effort": "minimal", "summary": "detailed"},
):
    message = st.session_state.messages[-1]
    # Display the user's query
    if message["role"] == "user":
        with chatbox.chat_message(
            settings["user_name"],
            avatar=settings["user_avatar"],
        ):
            st.markdown(message["content"], unsafe_allow_html=True)
    response = get_response(
        st.session_state.messages,
        model=model,
        reasoning=reasoning,
    )
    response = response.strip()
    st.session_state.messages.append({"role": "assistant", "content": response})
    log_session()
    if audio := text_to_speech(response, voice=voice, instructions=instruction):
        st.session_state.audio = audio
        st.rerun()
