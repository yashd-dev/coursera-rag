"""Optional experimental claim checker (Laya, convaiinnovations/laya). Opt-in: PAPERFORGE_CLAIM_CHECKER=laya.

Contract: assess(claim, passages) -> {"checker": "laya", "label": window_supported_single_part | window_level_only |
no_window_supported, "max_window_score", "window_scores", "verified": False, "note"}. Window-level labels only. The result is a model assessment, never
verification: it gives no quote or page evidence and it is not used to mark a span verified. On a 44-case
single-reader benchmark it accepted two stitched false claims at p=0.91 and 0.97 and rejected supported ones, so
it is shown as an assessment only. Imports are lazy: without the opt-in, the laya/torch packages are never loaded.
"""
import os
import re

ENABLED_VALUE = "laya"
QUESTION = {
    "support": {
        "type": "noul",
        "instructions": "Does the evidence passage fully support every part of the claim?",
    }
}
THRESHOLD = 0.5
MAX_PASSAGE_CHARS = 1100  # the English checkpoint has a 512-token context; claim + passage must fit
_agent = None


def enabled():
    return os.environ.get("PAPERFORGE_CLAIM_CHECKER", "") == ENABLED_VALUE


def _load():
    global _agent
    if _agent is None:
        import laya  # lazy, optional dependency (pip install laya; ~843 MB weights on first use)

        _agent = laya.load("convaiinnovations/laya")
    return _agent


def set_agent(agent):
    """Test hook."""
    global _agent
    _agent = agent


def _windows(passage):
    passage = re.sub(r"\s+", " ", passage).strip()
    if len(passage) <= MAX_PASSAGE_CHARS:
        return [passage] if passage else []
    step = MAX_PASSAGE_CHARS // 2
    return [passage[i : i + MAX_PASSAGE_CHARS] for i in range(0, max(1, len(passage) - step), step)]


MULTI_RE = re.compile(r"(;|\bwhile\b|\bwhereas\b|\band\b[^.]*\band\b|,[^,.]*,[^,.]*,|\.\s+[A-Z])", re.I)


def multi_clause(claim):
    return bool(MULTI_RE.search(claim))


def assess(claim, passages):
    """Per-window assessment. The benchmarked prompt asks whether ONE passage supports the claim, so a high score on
    one window cannot mean the whole claim is supported when it has several parts or the passage was split. The label
    therefore says what was actually assessed:
      window_supported_single_part   one window scored >= threshold and the claim has one part and fit in one window
      window_level_only              a window scored >= threshold but the claim has several parts or was windowed:
                                     says nothing about the claim as a whole
      no_window_supported            no window scored >= threshold
    Returns None when disabled or the package is unavailable; callers must treat None as 'no assessment'.
    Scores are model outputs, not calibrated probabilities."""
    if not enabled() and _agent is None:
        return None
    try:
        agent = _load()
    except Exception as e:  # not installed, no weights, out of memory: the app keeps working without it
        return {"checker": "laya", "error": f"{type(e).__name__}: {str(e)[:120]}", "verified": False}
    windows = []
    for passage in passages:
        windows.extend(_windows(passage))
    scores = []
    for w in windows:
        state = f"Claim: {claim}\n\nEvidence passage from the cited source: {w}"
        try:
            scores.append(round(float(agent.predict(state, QUESTION)["answers"]["support"]["noul"]), 3))
        except Exception as e:
            return {"checker": "laya", "error": f"{type(e).__name__}: {str(e)[:120]}", "verified": False}
    if not scores:
        return None
    best = max(scores)
    multi = multi_clause(claim)
    if best < THRESHOLD:
        label = "no_window_supported"
    elif multi or len(windows) > 1:
        label = "window_level_only"
    else:
        label = "window_supported_single_part"
    return {
        "checker": "laya",
        "label": label,
        "max_window_score": best,
        "window_scores": scores,
        "windows": len(windows),
        "multi_clause": multi,
        "verified": False,
        "note": "Model assessment of single passage windows, not verification and not a calibrated probability. "
        "No quote or page evidence. A window score says nothing about claim parts that need other passages; "
        "it accepted stitched false claims in a small benchmark.",
    }
