import streamlit as st
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
import json
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
            model="gpt-transcribe",
            response_format="json",
            file=audio_bio,
            languages=["en"],
        )
        st.session_state.processed_audio = id
        st.session_state.latency.append(("stt", time() - start))
        log.debug(f"STT usage: {transcript.usage.model_dump() if transcript.usage else None}")
        return transcript.text
    except Exception as e:
        log.exception("")


def text_to_speech(text, voice, instructions):
    """Yield the speech as base64 Ogg Opus chunks while it is generated."""
    start = time()
    first = None
    try:
        if st.session_state.get("display_reasoning", False):
            text = re.sub(r"<details>.*?</details>", "", text, flags=re.DOTALL)
        log.debug(f"TTS: {voice}, {instructions}\n{text}")
        # SSE returns the opus file in base64 chunks, and the final event carries usage.
        usage = None
        with get_client().audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts-2025-03-20",
            # gpt-4o-mini-tts-2025-03-20
            voice=voice,
            input=text,
            instructions=instructions,
            response_format="opus",
            stream_format="sse",
        ) as response:
            for line in response.iter_lines():
                if not line.startswith("data:") or line[5:].strip() == "[DONE]":
                    continue
                event = json.loads(line[5:])
                if event.get("type") == "speech.audio.delta":
                    if first is None:
                        first = time() - start
                    yield event["audio"]
                elif event.get("type") == "speech.audio.done":
                    usage = event.get("usage")
        log.debug(f"TTS usage: {usage}")
        st.session_state.latency.append(("tts", time() - start))
        total = sum([l[1] for l in st.session_state.latency])
        st.session_state.latency.append(("total", total))
        st.session_state.latency.append(("tts_first", first or 0))
        latency = [f"{l[0]} {l[1]:.2f}" for l in st.session_state.latency]
        latency = ", ".join(latency)
        latency = f"Latency: {latency}"
        st.session_state.last_latency = latency
        log.debug(f"{latency}")
        del st.session_state.latency
    except Exception as e:
        log.exception("")


# Send prompt to OpenAI and get response
def get_response(
    messages,
    model,
    reasoning={"effort": "none", "summary": "auto"},
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
            text={"verbosity":"low"},
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
        log.debug(f"Usage: {response.usage.model_dump()}")
        st.session_state.latency.append(("text", time() - start))
        if reasoning and st.session_state.get("display_reasoning", False):
            completion_text = f"<details><summary><strong>Reasoning</strong></summary>{reasoning}</details>{completion_text}"
        return completion_text
    except Exception as e:
        log.exception("")


def stream_response(
    messages,
    model,
    reasoning={"effort": "none", "summary": "auto"},
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
            text={"verbosity":"low"},
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
        log.debug(f"Usage: {event.response.usage.model_dump()}")
        st.session_state.latency.append(("text_stream", time() - start))
        if reasoning and st.session_state.get("display_reasoning", False):
            completion_text = f"<details><summary><strong>Reasoning</strong></summary>{reasoning}</details>{completion_text}"
        return completion_text
    except Exception as e:
        log.exception("")
