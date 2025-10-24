import streamlit as st
from pathlib import Path
from uuid import uuid4
from Session import update_active_users
from openai import OpenAI
from openai.types.responses import (
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseReasoningSummaryTextDoneEvent,
    ResponseReasoningSummaryPartDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseOutputItemDoneEvent,
    ResponseReasoningItem,
    ResponseOutputMessage,
    ResponseCompletedEvent,
)
import io
from Logger import log
from Settings import settings
from time import time
import re


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
        if st.session_state.get("display_reasoning", False):
            text = re.sub(r"<details>.*?</details>", "", text, flags=re.DOTALL)
        log.debug(f"TTS: {voice}, {instructions}\n{text}")
        file = f"static/{st.session_state.id}/{uuid4().hex}.opus"
        with get_client().audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            instructions=instructions,
            response_format="opus",
        ) as response:
            p = Path(file)
            p.parent.mkdir(parents=True, exist_ok=True)
            response.stream_to_file(p)
        st.session_state.latency.append(("tts", time() - start))
        total = sum([l[1] for l in st.session_state.latency])
        st.session_state.latency.append(("total", total))
        latency = [f"{l[0]} {l[1]:.2f}" for l in st.session_state.latency]
        latency = ", ".join(latency)
        latency = f"Latency: {latency}"
        st.session_state.last_latency = latency
        log.debug(f"{latency}")
        del st.session_state.latency
        return file
    except Exception as e:
        log.exception("")


# Send prompt to OpenAI and get response
def get_response(
    messages,
    model,
    reasoning={"effort": "minimal", "summary": "detailed"},
):
    start = time()
    update_active_users()
    if st.session_state.get("display_reasoning", False):
        for msg in messages:
            msg["content"] = re.sub(
                r"<details>.*?</details>", "", msg["content"], flags=re.DOTALL
            )
    if not st.session_state.get("latency"):
        st.session_state.latency = []
    try:
        log.debug(f"Sending text to {model}: {messages[-1]['content']}")
        response = get_client().responses.create(
            model=model,
            input=messages,
            reasoning=reasoning,
            max_output_tokens=10000,
            store=False,
        )
        completion_text = response.output_text.strip()
        reasoning = []
        for output in response.output:
            if isinstance(output, ResponseReasoningItem):
                for r in output.summary:
                    reasoning.append(r.text)

        reasoning = "\n\n".join(reasoning).strip()
        tokens = [
            response.usage.input_tokens,
            response.usage.input_tokens_details.cached_tokens,
            response.usage.output_tokens,
            response.usage.output_tokens_details.reasoning_tokens,
        ]
        log.debug(f"Usage: {tokens}")
        st.session_state.latency.append(("text", time() - start))
        if reasoning and st.session_state.get("display_reasoning", False):
            completion_text = f"<details><summary><strong>Reasoning</strong></summary>{reasoning}</details>{completion_text}"
        return completion_text
    except Exception as e:
        log.exception("")


def stream_response(
    messages,
    model,
    reasoning={"effort": "minimal", "summary": "detailed"},
):
    start = time()
    update_active_users()
    if st.session_state.get("display_reasoning", False):
        for msg in messages:
            msg["content"] = re.sub(
                r"<details>.*?</details>", "", msg["content"], flags=re.DOTALL
            )
    if not st.session_state.get("latency"):
        st.session_state.latency = []
    try:
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
        reasoning = []
        for event in response:
            if isinstance(event, ResponseReasoningSummaryTextDoneEvent):
                part = event.text.strip()
                yield part
                reasoning.append(part)
            elif isinstance(event, ResponseOutputItemDoneEvent) and isinstance(
                event.item, ResponseReasoningItem
            ):
                yield "Finalizing the feedback"
            elif isinstance(event, ResponseCompletedEvent):
                yield "Preparing the debriefer"
                content = event.response.output_text
            else:
                pass
        completion_text = content.strip()
        reasoning = "\n\n".join(reasoning).strip()
        usage = event.response.usage
        tokens = [
            usage.input_tokens,
            usage.input_tokens_details.cached_tokens,
            usage.output_tokens,
            usage.output_tokens_details.reasoning_tokens,
        ]
        log.debug(f"Usage: {tokens}")
        st.session_state.latency.append(("text_stream", time() - start))
        if reasoning and st.session_state.get("display_reasoning", False):
            completion_text = f"<details><summary><strong>Reasoning</strong></summary>{reasoning}</details>{completion_text}"
        return completion_text
    except Exception as e:
        log.exception("")
