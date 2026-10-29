"""Fail-closed validation of model review ledger against page-exact indexed source text."""

import json, re
from pathlib import Path
from . import db


def normalize(s):
    return re.sub(r"\s+", " ", s).strip()


def validate(tid, root):
    errors = []
    try:
        ledger = json.loads((root / "claim-review.json").read_text())
    except (OSError, ValueError):
        return ["Missing or invalid claim-review.json"]
    if not isinstance(ledger, dict):
        return ["Ledger must be an object with claims array, not a bare array"]
    if not ledger.get("claims") or not isinstance(ledger["claims"], list):
        return ["Empty claim ledger"]
    src = {s["key"]: s for s in db.sources(tid) if s["status"] == "indexed"}
    tex = (root / "paper/main.tex").read_text()
    cites = re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", tex)
    if not cites:
        errors.append("No processed-source citations in draft")
    for group in cites:
        for key in group.split(","):
            if key.strip() not in src:
                errors.append("Citation outside processed source set: " + key)
    # Bind evidence records to the current draft, not a stale or unrelated ledger.
    import hashlib

    if ledger.get("draft_sha256") != hashlib.sha256(tex.encode()).hexdigest():
        errors.append("Ledger draft_sha256 does not match the current TeX")
    if any(
        term in tex.lower()
        for term in (
            "not supported by the cited works",
            "claimed outcome links",
            "citations:",
        )
    ):
        errors.append(
            "Reviewer commentary leaked into paper: unsupported negative inference"
        )
    if not re.search(r"\\begin\{table\*?\}", tex):
        errors.append("Required source-comparison table is missing")
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if abstract:
        sentences = [
            normalize(x)
            for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", abstract.group(1))
            if len(x) > 40
        ]
        if len(sentences) != len(set(sentences)):
            errors.append("Repeated abstract sentence")
    if "Anonymous affiliation" in tex or "Anonymous email" in tex:
        errors.append("Invented anonymous affiliation/contact block")
    if len(re.findall(r"\\begin\{table\*?\}", tex)) > 1:
        errors.append("Duplicate comparison tables require review")
    covered = []
    for i, c in enumerate(ledger["claims"], 1):
        if not isinstance(c, dict):
            errors.append(f"Claim{i} must be an object")
            continue
        draft_quote = c.get("draft_quote")
        if (
            not isinstance(draft_quote, str)
            or len(draft_quote) < 20
            or normalize(draft_quote) not in normalize(tex)
        ):
            errors.append(f"Claim{i} lacks an exact draft_quote from current TeX")
        else:
            covered.append(normalize(draft_quote))
        key = c.get("source_key")
        page = c.get("page")
        quote = c.get("quote")
        statement = c.get("claim")
        if (
            key not in src
            or not isinstance(page, int)
            or not isinstance(quote, str)
            or len(quote) < 20
            or not isinstance(statement, str)
        ):
            errors.append(f"Claim{i} lacks exact source/page/quote")
            continue
        text = Path(src[key]["text_path"]).read_text()
        chunks = re.split(r"=== PAGE (\d+) ===\n", text)
        pages = {int(chunks[j]): chunks[j + 1] for j in range(1, len(chunks) - 1, 2)}
        if normalize(quote) not in normalize(pages.get(page, "")):
            errors.append(f"Claim{i} quote not on physical page{page}")
        # Numbers in numeric claims must appear in quoted evidence, not be inferred/derived.
        nums = re.findall(
            r"\b\d+(?:\.\d+)?%?",
            re.sub(
                r"\\cite(?:\[[^]]*\])?\{[^}]+\}",
                "",
                statement.split("&", 1)[-1] if "&" in statement else statement,
            ),
        )
        grouped = " ".join(
            x.get("quote", "")
            for x in ledger["claims"]
            if isinstance(x, dict) and x.get("draft_quote") == draft_quote
        )
        for n in nums:
            if n.rstrip("%") not in grouped:
                errors.append(f"Claim{i} number unsupported by quoted evidence")
        if c.get("status") != "supported":
            errors.append(f"Claim{i} not marked supported; revise/remove it first")
    # Every substantial prose block must be represented, including abstract/table.
    # This is a coverage guard, not a semantic-entailment proof.
    from .span_review import spans

    for block in spans(tex):
        if not any(normalize(block) == q for q in covered):
            errors.append("Uncovered prose block: " + normalize(block)[:100])
    return errors
