"""Visible research-family clarification before source discovery, never a hidden scope choice."""

import re


def graph_family(text):
    s = text.lower()
    graph = bool(
        re.search(
            r"graph[ -]?(?:based[ -]?)?(?:rag|retrieval)|graph.rag|graph retrieval.augmented",
            s,
        )
    )
    if not graph:
        return None
    llm = bool(
        re.search(
            r"\bllms?\b|large language|knowledge.graph|question.answer|text corp|document corp|global summar",
            s,
        )
    )
    gfm = bool(
        re.search(
            r"graph foundation|node classification|link prediction|graph representation|graph tasks",
            s,
        )
    )
    if llm and not gfm:
        return "llm"
    if gfm and not llm:
        return "gfm"
    return "ambiguous"


def clarify(text):
    return graph_family(text) == "ambiguous"


def candidate_scope(topic, candidate):
    """Reject only an explicitly conflicting family. Other topicality is still ranked."""
    family = graph_family(topic)
    s = (candidate["title"] + " " + candidate.get("abstract", "")).lower()
    if (
        family == "llm"
        and re.search(
            r"graph foundation models?|node classification|link prediction", s
        )
        and not re.search(
            r"large language|\bllms?\b|question.answer|text corp|document corp", s
        )
    ):
        return (
            False,
            "Graph foundation/graph-prediction work does not match the explicit LLM/document GraphRAG scope.",
        )
    return True, None
