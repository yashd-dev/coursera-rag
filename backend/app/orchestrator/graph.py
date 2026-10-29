"""StateGraph for one chat turn.

  START -> fast_route -+-> scope | resume | edit | ask            (slash commands, resume, questions: no model call)
                       +-> classify -> find_agent <-> find_tools -> find_report   (search only: never writes)
                                    -> consent -> write_paper      (interrupt before any paper is written)
                                    -> clarify

Side effects (writing files, indexing, review) live only in nodes after the consent interrupt and each guards on
threads.phase, so a replayed node cannot start a second run. threads.phase stays the source of truth; the checkpoint
holds the pending consent question and routing state."""

import threading
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .. import db, jobs, pipeline
from . import intents, llm
from .tools import make_tools

MAX_TOOL_ROUNDS = 2


class State(TypedDict, total=False):
    tid: str
    text: str
    template: str
    kind: str
    note: str
    intent: str
    explicit: bool
    messages: list
    rounds: int
    candidates: str


def _job(state):
    return jobs.RUNNING[state["tid"]]


@tool
def Intent(intent: str, confidence: float) -> str:
    """Classify the user's message. intent is one of: find_papers (user wants to see or search for papers, nothing is
    written), ask (a question about the indexed sources), write_paper (the user explicitly wants a paper written),
    clarify (unclear). confidence is 0 to 1."""
    return intent


# ---- nodes
def fast_route(state):
    thread = db.get_thread(state["tid"])
    kind, note = pipeline.route(state["text"], thread)
    return {"kind": kind, "note": note or ""}


def pick_after_route(state):
    k = state["kind"]
    if k == "create":
        return "classify"
    return k  # scope | resume | edit | ask


def classify(state):
    text = state["text"]
    model_intent = None
    try:
        m = llm.chat_model().bind_tools([Intent], tool_choice="Intent")
        msg = m.invoke(
            [
                SystemMessage(
                    content="Classify the user's message for a research-paper assistant. Call Intent once. Searching or listing papers is find_papers, not write_paper."
                ),
                HumanMessage(content=text),
            ]
        )
        calls = getattr(msg, "tool_calls", None) or []
        if calls:
            args = calls[0]["args"]
            if float(args.get("confidence", 0) or 0) >= 0.6:
                model_intent = args.get("intent")
    except Exception:  # hosted calls disabled, rate limit, malformed output: fall back to rules, never to a write
        model_intent = None
    intent, explicit = intents.guard(text, model_intent)
    return {"intent": intent, "explicit": explicit}


def pick_after_classify(state):
    i = state["intent"]
    if i == "write_paper":
        return "write_paper" if state.get("explicit") else "ask_consent"
    return {"find_papers": "find_agent", "ask": "ask"}.get(i, "clarify")


def find_agent(state):
    msgs = state.get("messages")
    tools = make_tools(state["tid"])
    if not msgs:
        msgs = [
            SystemMessage(
                content="Find candidate papers for the user's topic with the search tools (at most two calls). Then stop calling tools. You only search; you never write a paper."
            ),
            HumanMessage(content=state["text"]),
        ]
    if state.get("rounds", 0) >= MAX_TOOL_ROUNDS:
        return {"messages": msgs}
    try:
        reply = llm.chat_model().bind_tools(tools).invoke(msgs)
    except Exception:
        if state.get("rounds", 0) == 0:
            # No model: run the search tools directly on the user's words. Still read-only.
            out = tools[0].invoke({"query": state["text"]})
            return {"messages": msgs, "candidates": out, "rounds": MAX_TOOL_ROUNDS}
        return {"messages": msgs, "rounds": MAX_TOOL_ROUNDS}
    return {"messages": msgs + [reply]}


def after_find_agent(state):
    msgs = state["messages"]
    last = msgs[-1]
    if getattr(last, "tool_calls", None) and state.get("rounds", 0) < MAX_TOOL_ROUNDS:
        return "find_tools"
    return "find_report"


def find_tools(state):
    tools = {t.name: t for t in make_tools(state["tid"])}
    last = state["messages"][-1]
    out = []
    for c in last.tool_calls:
        t = tools.get(c["name"])
        res = t.invoke(c["args"]) if t else '{"error":"unknown tool"}'
        out.append(ToolMessage(content=res, tool_call_id=c["id"]))
    return {"messages": state["messages"] + out, "rounds": state.get("rounds", 0) + 1}


def find_report(state):
    import json

    job = _job(state)
    raw = state.get("candidates")
    if raw is None:
        parts = [m.content for m in state["messages"] if isinstance(m, ToolMessage)]
        raw = "[" + ",".join(p.strip("[]") for p in parts if p.strip("[]")) + "]"
    try:
        items = json.loads(raw)
    except ValueError:
        items = []
    items = [i for i in items if isinstance(i, dict) and i.get("title")]
    seen, rows = set(), []
    for i in items:
        k = i["title"].lower()
        if k in seen:
            continue
        seen.add(k)
        rows.append(i)
    if not rows:
        job.text("I couldn't find candidate papers for that (search returned nothing or failed). Nothing was downloaded or written.")
    else:
        lines = [
            f"- {i['title']} ({i.get('year') or 'n.d.'}, {i.get('venue') or i.get('origin')})" + (f" {i['url']}" if i.get("url") else "")
            for i in rows[:10]
        ]
        job.text(
            "Candidate papers:\n\n" + "\n".join(lines) +
            "\n\nI only searched. Nothing was downloaded, indexed or written. Ask me to write a paper on this topic when you want one."
        )
    job.finish()
    return {}


def clarify(state):
    job = _job(state)
    job.text(
        "I'm not sure what you want. I can find papers (search only), answer questions about the sources in this chat, or write a paper if you ask for one. Which one? Nothing has been started."
    )
    job.finish()
    return {}


def ask_consent(state):
    _job(state).text(
        "Do you want me to write a full paper on this? That downloads papers, indexes them and drafts a document, which takes a while. Reply yes to start, or no to stop. Nothing has been started."
    )
    return {}


def consent(state):
    answer = interrupt({"question": "write_paper", "text": state["text"]})
    return {"intent": "write_paper" if intents.consent_decision(str(answer)) == "yes" else "clarify", "explicit": True}


def pick_after_consent(state):
    return "write_paper" if state["intent"] == "write_paper" else "declined"


def declined(state):
    job = _job(state)
    job.text("OK, I did not start anything.")
    job.finish()
    return {}


def write_paper(state):
    tid, job = state["tid"], _job(state)
    thread = db.get_thread(tid)
    if thread["phase"] not in ("new", "failed_early"):
        job.text("This chat already has a paper in progress, so I did not start another. Use /resume or /edit.")
        job.finish()
        return {}
    from .. import scope

    if scope.clarify(state["text"]):
        pipeline.run_scope(job, tid, state["text"])
    else:
        pipeline.run_create(job, tid, state["text"], state["template"])
    return {}


def _wrap(fn):
    def node(state):
        fn(_job(state), state["tid"], state)
        return {}

    return node


def scope_node(state):
    pipeline.run_scope(_job(state), state["tid"], state["text"])
    return {}


def resume_node(state):
    t = db.get_thread(state["tid"])
    pipeline.run_create(_job(state), state["tid"], state["text"], t["template"])
    return {}


def edit_node(state):
    pipeline.run_edit(_job(state), state["tid"], state["text"])
    return {}


def ask_node(state):
    pipeline.run_ask(_job(state), state["tid"], state["text"], state.get("note") or None)
    return {}


def build(checkpointer):
    g = StateGraph(State)
    for name, fn in [
        ("fast_route", fast_route), ("classify", classify), ("find_agent", find_agent), ("find_tools", find_tools),
        ("find_report", find_report), ("clarify", clarify), ("ask_consent", ask_consent), ("consent", consent),
        ("declined", declined), ("write_paper", write_paper), ("scope", scope_node), ("resume", resume_node),
        ("edit", edit_node), ("ask", ask_node),
    ]:
        g.add_node(name, fn)
    g.add_edge(START, "fast_route")
    g.add_conditional_edges("fast_route", pick_after_route, ["classify", "scope", "resume", "edit", "ask"])
    g.add_conditional_edges("classify", pick_after_classify, ["write_paper", "ask_consent", "find_agent", "ask", "clarify"])
    g.add_conditional_edges("find_agent", after_find_agent, ["find_tools", "find_report"])
    g.add_edge("find_tools", "find_agent")
    g.add_edge("ask_consent", "consent")
    g.add_conditional_edges("consent", pick_after_consent, ["write_paper", "declined"])
    for n in ("find_report", "clarify", "declined", "write_paper", "scope", "resume", "edit", "ask"):
        g.add_edge(n, END)
    return g.compile(checkpointer=checkpointer)


_graph = None
_lock = threading.Lock()


def _postgres_saver():
    import psycopg
    from psycopg.rows import dict_row
    from langgraph.checkpoint.postgres import PostgresSaver
    from .. import config

    with psycopg.connect(config.DATABASE_URL, autocommit=True) as c:
        c.execute("CREATE SCHEMA IF NOT EXISTS paperforge_lg")
    conn = psycopg.connect(
        config.DATABASE_URL, autocommit=True, row_factory=dict_row, options="-c search_path=paperforge_lg"
    )
    saver = PostgresSaver(conn)
    saver.setup()
    return saver


def get_graph():
    global _graph
    with _lock:
        if _graph is None:
            _graph = build(_postgres_saver())
        return _graph


def set_graph(g):
    global _graph
    _graph = g


def run(job, tid, text, template):
    g = get_graph()
    cfg = {"configurable": {"thread_id": tid}}
    snap = g.get_state(cfg)
    if snap.next:
        # A consent question is pending. yes/no answers it; anything else cancels it and is handled as a new message.
        if intents.consent_decision(text) != "other":
            g.invoke(Command(resume=text), cfg)
            if not job.done:
                job.finish()
            return
        g.invoke(Command(resume="no"), cfg)
        job.parts.clear()
    g.invoke({"tid": tid, "text": text, "template": template, "messages": [], "rounds": 0, "candidates": None}, cfg)
    if not job.done:
        job.finish()
