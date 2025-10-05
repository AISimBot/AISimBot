import streamlit as st
from openai import OpenAI
from openai.types.responses import (
    ResponseTextDeltaEvent,
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseReasoningSummaryTextDoneEvent,
    ResponseTextDoneEvent,
    ResponseOutputItemDoneEvent,
    ResponseReasoningItem,
    ResponseOutputMessage,
)
import io
from Logger import log
from Settings import settings
from time import time
from Session import update_active_users


@st.cache_resource
def get_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def speech_to_text(audio):
    start = time()
    if not st.session_state.get("latency"):
        st.session_state.latency = []
    try:
        id = audio["id"]
        log.debug(f"STT: {id}")
        audio_bio = io.BytesIO(audio["bytes"])
        ext = ".m4a" if "Safari" in st.session_state.client_info["browser"] else ".webm"
        audio_bio.name = f"audio{ext}"
        transcript = get_client().audio.transcriptions.create(
            model="gpt-4o-transcribe",
            language="en",
            response_format="text",
            file=audio_bio,
        )
        st.session_state.processed_audio = id
        st.session_state.latency.append(("stt", time() - start))
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
        st.session_state.latency.append(("tts", time() - start))
        total = sum([l[1] for l in st.session_state.latency])
        st.session_state.latency.append(("total", total))
        latency = [f"{l[0]}: {l[1]:.2f}" for l in st.session_state.latency]
        latency = ", ".join(latency)
        log.debug(f"{latency}")
        del st.session_state.latency
        return response.content
    except Exception as e:
        log.exception("")


# Send prompt to OpenAI and get response
def get_response(
    messages,
    model,
    reasoning={"effort": "minimal", "summary": "auto"},
):
    start = time()
    if not st.session_state.get("latency"):
        st.session_state.latency = []
    try:
        update_active_users()
        log.debug(f"Sending text to {model}: {messages[-1]['content']}")
        response = get_client().responses.create(
            model=model,
            input=messages,
            reasoning=reasoning,
            max_output_tokens=10000,
            store=False,
        )
        completion_text = response.output_text.strip()
        tokens = [
            response.usage.input_tokens,
            response.usage.input_tokens_details.cached_tokens,
            response.usage.output_tokens,
            response.usage.output_tokens_details.reasoning_tokens,
        ]
        log.debug(f"Usage: {tokens}")
        st.session_state.latency.append(("text", time() - start))
        return completion_text
    except Exception as e:
        log.exception("")


def stream_response(
    messages,
    model,
    reasoning={"effort": "minimal", "summary": "auto"},
):
    start = time()
    if not st.session_state.get("latency"):
        st.session_state.latency = []
    try:
        update_active_users()
        log.debug(f"Sending text to {model}: {messages[-1]['content']}")
        response = get_client().responses.create(
            model=model,
            input=messages,
            reasoning=reasoning,
            max_output_tokens=10000,
            store=False,
            stream=True,
        )
        content = ""
        summary = ""
        for event in response:
            if isinstance(event, ResponseReasoningSummaryTextDeltaEvent):
                summary += event.delta
            elif isinstance(event, ResponseTextDeltaEvent):
                content += event.delta
            elif isinstance(event, ResponseReasoningSummaryTextDoneEvent):
                yield summary.strip()
                summary = ""
            elif isinstance(event, ResponseOutputItemDoneEvent) and isinstance(
                event.item, ResponseReasoningItem
            ):
                yield "Finalizing the feedback"
            elif isinstance(event, ResponseOutputItemDoneEvent) and isinstance(
                event.item, ResponseOutputMessage
            ):
                yield "Preparing the debriefer"
            else:
                pass
        completion_text = content.strip()
        usage = event.response.usage
        tokens = [
            usage.input_tokens,
            usage.input_tokens_details.cached_tokens,
            usage.output_tokens,
            usage.output_tokens_details.reasoning_tokens,
        ]
        log.debug(f"Usage: {tokens}")
        st.session_state.latency.append(("text_stream", time() - start))
        return completion_text
    except Exception as e:
        log.exception("")
