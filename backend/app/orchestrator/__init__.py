"""LangGraph orchestration for the chat endpoint (opt-in: PAPERFORGE_ORCHESTRATOR=langgraph).

See graph.py for the node layout and README.md for the architecture. Imports are lazy so the legacy path
does not need the LangChain packages."""


def run(job, tid, text, template):
    from .graph import run as _run

    return _run(job, tid, text, template)
