"""Model factory. Tests replace `factory`. Hosted calls stay behind the existing PAPERFORGE_ANSWER_CALLS switch."""

import os
from .. import config


class HostedCallsDisabled(RuntimeError):
    pass


def default_factory():
    if not config.ANSWER_CALLS:
        raise HostedCallsDisabled(
            "Hosted model calls are disabled (PAPERFORGE_ANSWER_CALLS)."
        )
    if not config.ANSWER_API_KEY:
        raise HostedCallsDisabled("NVIDIA_API_KEY is not set.")
    from langchain_nvidia_ai_endpoints import ChatNVIDIA

    # No max_retries: ChatNVIDIA forwards unknown kwargs to the API, which rejects them (verified against the
    # endpoint). with_structured_output is also rejected (guided_json), so structured output uses a forced tool call.
    return ChatNVIDIA(
        model=config.ANSWER_MODEL,
        base_url=config.ANSWER_BASE_URL,
        api_key=config.ANSWER_API_KEY,
        temperature=0,
        max_tokens=int(os.environ.get("PAPERFORGE_ORCH_MAX_TOKENS", "600")),
        timeout=int(os.environ.get("PAPERFORGE_ORCH_TIMEOUT", "60")),
        model_kwargs={"chat_template_kwargs": {"enable_thinking": False}},
    )


factory = default_factory


def chat_model():
    return factory()
