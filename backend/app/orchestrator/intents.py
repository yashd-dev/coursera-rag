"""Deterministic guards around the model's intent. The model proposes; these rules decide what is allowed to start."""

import re

FIND_RE = re.compile(
    r"(?i)\b(find|search(?:\s+for)?|look\s+(?:for|up)|suggest|recommend|show\s+me|get\s+me|list)\b[^.?!]{0,60}\b(papers?|articles?|studies|literature|references|sources|surveys?)\b"
)
# Only verbs that ask for the paper itself count as explicit write intent.
WRITE_RE = re.compile(
    r"(?i)\b(write|draft|generate|compose|produce|create|prepare)\b[^.?!]{0,50}\b(a|an|the|my|this)?\s*(literature\s+review|review\s+paper|research\s+paper|paper|survey|manuscript|article)\b"
)
YES_RE = re.compile(r"(?i)^\s*(yes|y|yeah|yep|ok|okay|sure|go|go ahead|proceed|do it|start|write it|confirm)\b")
NO_RE = re.compile(r"(?i)^\s*(no|n|nope|cancel|stop|don'?t|do not|never ?mind|not now)\b")

INTENTS = ("find_papers", "ask", "write_paper", "clarify")


def guard(text, model_intent):
    """Return (intent, explicit). A search phrase never becomes a write; a write needs explicit paper-writing words.

    explicit=True means the user's own words ask for a paper to be written, so no extra confirmation is shown.
    A model-only write_paper (no such words) is returned with explicit=False and the graph asks first."""
    t = text.strip()
    low = t.lower()
    if low.startswith("/find"):
        return "find_papers", False
    if low.startswith("/write"):
        return "write_paper", True
    if low.startswith("/ask"):
        return "ask", False
    writes = bool(WRITE_RE.search(t))
    finds = bool(FIND_RE.search(t))
    if finds and not writes:
        return "find_papers", False
    if writes and not finds:
        return "write_paper", True
    if writes and finds:
        # "find papers and write a review": the write verb is explicit, but the mix is worth one confirmation.
        return "write_paper", False
    if model_intent == "write_paper":
        return "write_paper", False
    if model_intent in INTENTS:
        return model_intent, False
    return "clarify", False


def consent_decision(text):
    if YES_RE.search(text):
        return "yes"
    if NO_RE.search(text):
        return "no"
    return "other"
