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
        if os.environ.get("PAPERFORGE_LAYA_LOW_RAM") == "1":
            from . import laya_lowram

            laya_lowram.apply()
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


# ---------------------------------------------------------------- pipeline integration (PAPERFORGE_CLAIM_CHECKER=laya)
import hashlib
import json

SUMMARY_FILE = "claim-assessment.json"


def _plain_claim(block):
    from . import span_review

    t = re.sub(r"\\cite(?:\[[^]]*\])?\{[^}]+\}", "", block)
    t = span_review.tex_plain(t)
    return re.sub(r"\s+", " ", t.replace("\\\\", " ").replace("&", " | ")).strip()


def review_claims_laya(job, tid, root):
    """Assess every sentence/table row of the draft against its retrieved source pages with Laya and save the summary.
    Returns True when the assessment ran, False when it could not (missing laya/weights/memory): the caller then
    pauses review and the draft downloads stay available. Sentences with no supporting window are flagged, not
    removed, and do not stop the export. Nothing is called verified."""
    from . import db, span_review

    tex = (root / "paper/main.tex").read_text()
    sources = [s for s in db.sources(tid) if s["status"] == "indexed"]
    blocks = span_review.spans(tex)
    cache_file = root / "span-review" / "laya-assessments.json"
    cache_file.parent.mkdir(exist_ok=True)
    try:
        cache = json.loads(cache_file.read_text())
    except (OSError, ValueError):
        cache = {}
    tc = job.tool_start("assess_claims_laya", {"sentences": len(blocks), "checker": "laya", "model": "convaiinnovations/laya"})
    rows = []
    for i, block in enumerate(blocks, 1):
        ev = span_review.candidates(block, sources, [], 4)
        ev = ev[:6]  # best-ranked passages only: unattributed sentences can pull dozens, which makes CPU runs crawl
        passages = [e["quote"] for e in ev]
        claim = _plain_claim(block)
        key = hashlib.sha256(
            ("|".join(["laya-v1", "convaiinnovations/laya", str(THRESHOLD), str(MAX_PASSAGE_CHARS), claim])
             + "".join(passages)).encode()
        ).hexdigest()
        res = cache.get(key)
        if res is None:
            res = assess(claim, passages)
            if res is None:
                res = {"label": "no_window_supported", "max_window_score": 0.0, "window_scores": [], "windows": 0,
                       "multi_clause": multi_clause(claim), "verified": False, "note": "no retrieved passage"}
            if "error" in res:
                job.tool_done(tc, {"error": res["error"]}, error=True)
                write_summary(root, {"error": res["error"], "total": len(blocks)})
                return False
            cache[key] = res
            cache_file.write_text(json.dumps(cache))
            _free_memory()
        rows.append({"span": i, "text": claim[:220], "label": res["label"], "score": res["max_window_score"],
                     "pages": sorted({(e["source_key"], e["page"]) for e in ev})[:4] and
                              [f"{k} p.{p}" for k, p in sorted({(e["source_key"], e["page"]) for e in ev})[:4]]})
    counts = {k: sum(r["label"] == k for r in rows) for k in ("window_supported_single_part", "window_level_only", "no_window_supported")}
    summary = {"checker": "laya", "total": len(rows), "counts": counts, "rows": rows, "verified": False}
    write_summary(root, summary)
    job.tool_done(tc, {"checked": len(rows), **counts})
    return True


def write_summary(root, summary):
    (root / SUMMARY_FILE).write_text(json.dumps(summary, indent=1))


def summary_text(root):
    """Short user-facing label for the final message. Empty when the checker did not run."""
    try:
        s = json.loads((root / SUMMARY_FILE).read_text())
    except (OSError, ValueError):
        return ""
    if s.get("error"):
        return f"Claim check (Laya) did not run: {s['error']}. The draft was not claim-checked."
    c = s["counts"]
    lines = [
        f"**Claim check: model-assessed by Laya, not verified.** {s['total']} sentences/rows checked against their cited source pages: "
        f"{c['window_supported_single_part'] + c['window_level_only']} have a passage the model rates as supporting "
        f"({c['window_level_only']} of those are multi-part or long, so that is a partial check), "
        f"{c['no_window_supported']} flagged as having no supporting passage."
    ]
    flagged = [r for r in s["rows"] if r["label"] == "no_window_supported"][:5]
    for r in flagged:
        lines.append(f"- flagged: {r['text'][:140]}")
    return "\n".join(lines)


def _free_memory():
    """Keep the resident size flat on small machines: Laya runs on CPU and glibc otherwise keeps freed activations."""
    import gc

    gc.collect()
    try:
        import ctypes

        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except OSError:
        pass
