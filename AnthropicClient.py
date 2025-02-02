import streamlit as st
import anthropic
from Logger import log
from Settings import settings


@st.cache_resource
def get_client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def get_response(messages):
    try:
        log.debug(f"Sending text request to Anthropic: {messages[-1]['content']}")
        response = get_client().messages.create(
            model=settings["parameters"]["model"],
            messages=messages[1:],
            max_tokens=1000,
            system=messages[0]["content"],
            temperature=settings["parameters"]["temperature"],
        )
        return response.content[0].text
    except Exception as e:
        log.exception("")


def stream_response(messages):
    try:
        log.debug(f"Sending text request to Anthropic: {messages[-1]['content']}")
        stream = get_client().messages.create(
            model=settings["parameters"]["model"],
            messages=messages[1:],
            max_tokens=1000,
            system=messages[0]["content"],
            temperature=settings["parameters"]["temperature"],
            stream=True,
        )
        for chunk in stream:
            if isinstance(
                chunk,
                anthropic.types.raw_content_block_delta_event.RawContentBlockDeltaEvent,
            ):
                yield chunk.delta.text
    except Exception as e:
        log.exception("")
