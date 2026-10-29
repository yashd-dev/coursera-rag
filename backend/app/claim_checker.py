"""Optional experimental claim checker (Laya, convaiinnovations/laya). Opt-in: PAPERFORGE_CLAIM_CHECKER=laya.

Contract: assess(claim, passages) -> {"checker": "laya", "p_support": float, "label": "model_assessment_supported" |
"model_assessment_not_supported", "verified": False, "note": str}. The result is a model assessment, never
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


def assess(claim, passages):
    """Highest p(support) over passage windows. Returns None when disabled or the package is unavailable;
    callers must treat None as 'no assessment', never as support."""
    if not enabled() and _agent is None:
        return None
    try:
        agent = _load()
    except Exception as e:  # not installed, no weights, out of memory: the app keeps working without it
        return {"checker": "laya", "error": f"{type(e).__name__}: {str(e)[:120]}", "verified": False}
    best = None
    for passage in passages:
        for w in _windows(passage):
            state = f"Claim: {claim}\n\nEvidence passage from the cited source: {w}"
            try:
                p = float(agent.predict(state, QUESTION)["answers"]["support"]["noul"])
            except Exception as e:
                return {"checker": "laya", "error": f"{type(e).__name__}: {str(e)[:120]}", "verified": False}
            best = p if best is None else max(best, p)
    if best is None:
        return None
    return {
        "checker": "laya",
        "p_support": round(best, 3),
        "label": "model_assessment_supported" if best >= THRESHOLD else "model_assessment_not_supported",
        "verified": False,
        "note": "Model assessment, not verification: no quote or page evidence, and it can accept claims that stitch separate facts.",
    }
