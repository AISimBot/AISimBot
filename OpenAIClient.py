import streamlit as st
from openai import OpenAI
import io
from Logger import log
from Settings import settings
from Utils import elapsed
from time import time


@st.cache_resource
def get_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def speech_to_text(audio):
    st.session_state.turn_start = time()
    start = time()
    try:
        id = audio["id"]
        log.debug(f"STT: {id}")
        audio_bio = io.BytesIO(audio["bytes"])
        audio_bio.name = "audio.wav"
        transcript = get_client().audio.transcriptions.create(
            model="gpt-4o-transcribe",
            language="en",
            response_format="text",
            file=audio_bio,
        )
        st.session_state.processed_audio = id
        log.debug(f"STT took: {elapsed(start)}")
        return transcript
    except Exception as e:
        log.exception("")


def text_to_speech(text, voice, instructions):
    start = time()
    try:
        log.debug(f"TTS: {voice}, {instructions}\n{text}")
        response = get_client().audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            instructions=instructions,
        )
        log.debug(f"TTS took: {elapsed(start)}")
        turn_duration = elapsed(st.session_state.turn_start)
        log.debug(f"Total took: {turn_duration}")
        st.session_state.messages[-1]["duration"] = turn_duration
        return response.content
    except Exception as e:
        log.exception("")


# Send prompt to OpenAI and get response
def get_response(
    messages,
    model=settings["parameters"]["model"],
    temperature=settings["parameters"]["temperature"],
):
    start = time()
    if not st.session_state.get("turn_start"):
        st.session_state.turn_start = time()
    try:
        log.debug(f"Sending text to {model}: {messages[-1]['content']}")
        if model.startswith("o"):
            temperature = None
        if temperature:
            response = get_client().chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
        else:
            response = get_client().chat.completions.create(
                model=model,
                messages=messages,
            )
        completion_text = response.choices[0].message.content.strip()
        tokens = [
            response.usage.prompt_tokens,
            response.usage.prompt_tokens_details.cached_tokens,
            response.usage.completion_tokens,
            response.usage.completion_tokens_details.reasoning_tokens,
        ]
        log.debug(f"Usage: {tokens}")
        log.debug(f"Text took: {elapsed(start)}")
        return completion_text
    except Exception as e:
        log.exception("")


def stream_response(
    messages,
    model=settings["parameters"]["model"],
    temperature=settings["parameters"]["temperature"],
):
    try:
        log.debug(f"Sending text to {model}: {messages[-1]['content']}")
        if model.startswith("o"):
            temperature = None
        if temperature:
            stream = get_client().chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True,
                stream_options={"include_usage": True},
            )
        else:
            stream = get_client().chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},
            )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        tokens = [
            chunk.usage.prompt_tokens,
            chunk.usage.prompt_tokens_details.cached_tokens,
            chunk.usage.completion_tokens,
            chunk.usage.completion_tokens_details.reasoning_tokens,
        ]
        log.debug(f"Usage: {tokens}")
    except Exception as e:
        log.exception("")
