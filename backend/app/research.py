"""Source discovery (arXiv + OpenAlex), open-access PDF download, page-wise text extraction."""

import re, subprocess, time, unicodedata
import xml.etree.ElementTree as ET
import httpx
from . import config

UA = {"User-Agent": f"PaperForge/0.2 (mailto:{config.CONTACT})"}
ATOM = {"a": "http://www.w3.org/2005/Atom"}


def _norm(t):
    return re.sub(
        r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", t or "").lower()
    ).strip()


def _key(authors, year, title):
    sur = (
        _norm(
            (authors or "anon").split(",")[0].split()[-1] if authors else "anon"
        ).replace(" ", "")
        or "anon"
    )
    word = next(
        (
            w
            for w in _norm(title).split()
            if len(w) > 3
            and w not in {"with", "from", "that", "this", "using", "towards", "toward"}
        ),
        "paper",
    )
    return f"{sur}{year or 'nd'}{word}"


def arxiv_query(query):
    # arXiv query grammar does not scope a whole unquoted natural-language sentence after all:.
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9-]*", query)
    stop = {
        "a",
        "an",
        "the",
        "of",
        "for",
        "and",
        "or",
        "in",
        "on",
        "with",
        "to",
        "by",
        "from",
        "literature",
        "comparison",
        "survey",
        "review",
        "evaluation",
        "models",
        "model",
    }
    terms = [w for w in words if w.lower() not in stop][:8]
    return " AND ".join('all:"' + w + '"' for w in terms)


def search_arxiv(query, n=10, recent=False):
    r = httpx.get(
        "https://export.arxiv.org/api/query",
        headers=UA,
        timeout=30,
        follow_redirects=True,
        params={
            "search_query": arxiv_query(query),
            "max_results": n,
            "sortBy": "submittedDate" if recent else "relevance",
            "sortOrder": "descending",
        },
    )
    r.raise_for_status()
    out = []
    for e in ET.fromstring(r.text).findall("a:entry", ATOM):
        t = re.sub(r"\s+", " ", e.findtext("a:title", "", ATOM)).strip()
        aid = e.findtext("a:id", "", ATOM).rsplit("/abs/", 1)[-1]
        auth = ", ".join(
            a.findtext("a:name", "", ATOM) for a in e.findall("a:author", ATOM)
        )
        year = int((e.findtext("a:published", "", ATOM) or "0")[:4]) or None
        out.append(
            dict(
                title=t,
                authors=auth,
                year=year,
                venue="arXiv",
                doi=None,
                url=f"https://arxiv.org/abs/{aid}",
                pdf_url=f"https://arxiv.org/pdf/{aid}",
                abstract=re.sub(r"\s+", " ", e.findtext("a:summary", "", ATOM)).strip(),
                cited_by=0,
                origin="arxiv",
            )
        )
    return out


def _abstract(inv):
    if not inv:
        return ""
    pos = {}
    for w, ps in inv.items():
        for p in ps:
            pos[p] = w
    return " ".join(pos[i] for i in sorted(pos))


def search_openalex(query, n=10, recent=False):
    if not config.OPENALEX_CALLS:
        raise ValueError(
            "OpenAlex calls disabled; explicitly enable only within verified free allowance."
        )
    headers = dict(UA)
    if config.OPENALEX_API_KEY:
        headers["Authorization"] = "Bearer " + config.OPENALEX_API_KEY
        quota = httpx.get(
            "https://api.openalex.org/rate-limit", headers=headers, timeout=15
        )
        quota.raise_for_status()
        limits = quota.json().get("rate_limit", {})
        # Never consume prepaid balance. Reject unknown quota schema instead of guessing.
        daily = limits.get("daily_budget_usd")
        used = limits.get("daily_used_usd")
        cost = limits.get("endpoint_costs_usd", {}).get("search")
        if not all(isinstance(v, (int, float)) for v in (daily, used, cost)) or min(
            daily, 1.0
        ) - used < max(cost, 0.002):
            raise ValueError(
                "Verified OpenAlex free daily allowance unavailable or nearly exhausted."
            )
    params = {
        "search": query,
        "per_page": min(n, 100),
        "filter": "open_access.is_oa:true,type:article|preprint",
        "mailto": config.CONTACT,
    }
    if recent:
        params["sort"] = "publication_date:desc"
    r = httpx.get(
        "https://api.openalex.org/works", headers=headers, timeout=30, params=params
    )
    r.raise_for_status()
    out = []
    for w in r.json().get("results", []):
        loc = w.get("best_oa_location") or {}
        pdf = loc.get("pdf_url")
        if not pdf:
            continue
        auth = ", ".join(a["author"]["display_name"] for a in w.get("authorships", []))
        out.append(
            dict(
                title=w.get("title") or "",
                authors=auth,
                year=w.get("publication_year"),
                venue=((w.get("primary_location") or {}).get("source") or {}).get(
                    "display_name"
                )
                or "",
                doi=(w.get("doi") or "").replace("https://doi.org/", "") or None,
                url=w.get("doi") or w.get("id"),
                pdf_url=pdf,
                abstract=_abstract(w.get("abstract_inverted_index")),
                cited_by=w.get("cited_by_count") or 0,
                origin="openalex",
            )
        )
    return out


def wants_recent(topic):
    return bool(
        re.search(
            r"\b(latest|recent|current|newest|state.of.the.art|advancements)\b",
            topic,
            re.I,
        )
    )


def discover(queries, per_query=8, checkpoint=None, recent=False):
    """Returns deduplicated candidates ranked by how many queries surfaced them, then citation count."""
    import json

    pool = {}
    errors = []
    try:
        cache = json.loads(checkpoint.read_text()) if checkpoint else {}
    except (OSError, ValueError):
        cache = {}

    throttle_file = config.DATA_DIR / "arxiv-backoff.json"
    try:
        global_retry = json.loads(throttle_file.read_text()).get("retry_after", 0)
    except (OSError, ValueError):
        global_retry = 0
    arxiv_throttled = max(cache.get("arxiv_retry_after", 0), global_retry) > time.time()
    for qi, query in enumerate(queries):
        for fn in (search_arxiv, search_openalex):
            key = (
                fn.__name__
                + ("recent:" if recent and qi < max(1, len(queries) - 1) else ":")
                + query
            )
            if fn == search_arxiv and arxiv_throttled and key not in cache:
                errors.append("arXiv rate limited; remaining queries deferred")
                continue
            try:
                if key in cache:
                    res = cache[key]
                else:
                    res = (
                        fn(query, per_query, recent=True)
                        if recent and qi < max(1, len(queries) - 1)
                        else fn(query, per_query)
                    )
                    cache[key] = res
                    if checkpoint:
                        checkpoint.write_text(json.dumps(cache))
            except Exception as e:
                if (
                    fn == search_arxiv
                    and isinstance(e, httpx.HTTPStatusError)
                    and e.response.status_code == 429
                ):
                    arxiv_throttled = True
                    cache["arxiv_retry_after"] = time.time() + 3600
                    throttle_file.write_text(
                        json.dumps({"retry_after": cache["arxiv_retry_after"]})
                    )
                    if checkpoint:
                        checkpoint.write_text(json.dumps(cache))
                errors.append(f"{fn.__name__}({query!r}): {e}")
                continue
            time.sleep(0.4)
            for rank, c in enumerate(res):
                k = _norm(c["title"])
                if not k or len(c["title"]) < 8:
                    continue
                if k in pool:
                    pool[k]["hits"] += 1
                    pool[k]["rank"] += rank
                    for f in ("doi", "venue", "abstract"):
                        if not pool[k].get(f) and c.get(f):
                            pool[k][f] = c[f]
                    pool[k]["cited_by"] = max(pool[k]["cited_by"], c["cited_by"])
                    if c["origin"] == "arxiv":
                        pool[k]["pdf_url"] = c["pdf_url"]
                else:
                    pool[k] = dict(c, hits=1, rank=rank)
    ranked = sorted(
        pool.values(),
        key=lambda c: (-c["hits"], c["rank"] - min(c["cited_by"], 5000) / 1000),
    )
    return ranked, errors


def download_pdf(url, dest):
    """Download and validate a PDF. Raises ValueError with a human-readable reason when inaccessible."""
    with httpx.stream("GET", url, headers=UA, timeout=60, follow_redirects=True) as r:
        if r.status_code != 200:
            raise ValueError(f"HTTP {r.status_code}")
        buf = bytearray()
        for ch in r.iter_bytes():
            buf += ch
            if len(buf) > 40_000_000:
                raise ValueError("larger than 40 MB")
    if not buf.startswith(b"%PDF"):
        raise ValueError("not a PDF (landing page or paywall)")
    dest.write_bytes(bytes(buf))
    return len(buf)


def extract_pages(pdf_path):
    txt = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf_path), "-"],
        capture_output=True,
        timeout=120,
    ).stdout.decode("utf-8", "replace")
    pages = txt.split("\f")
    return [(i + 1, p) for i, p in enumerate(pages) if p.strip()]


def make_key(c, used):
    base = _key(c["authors"], c["year"], c["title"])
    k = base
    i = 2
    while k in used:
        k = f"{base}{i}"
        i += 1
    used.add(k)
    return k


def relevant_candidates(topic, cands):
    """Cheap topical guard before paid embeddings. Require multiple distinctive topic terms."""
    stop = {
        "a",
        "an",
        "the",
        "of",
        "for",
        "and",
        "or",
        "in",
        "on",
        "with",
        "to",
        "by",
        "from",
        "literature",
        "comparison",
        "survey",
        "review",
        "evaluation",
        "paper",
        "research",
        "make",
        "write",
        "create",
    }
    terms = set(re.findall(r"[a-z0-9]+", topic.lower())) - stop
    if not terms:
        return []
    out = []
    for c in cands:
        words = set(
            re.findall(r"[a-z0-9]+", (c["title"] + " " + c.get("abstract", "")).lower())
        )
        if len(terms & words) >= min(3, len(terms)) and (
            "retrieval" not in terms or "retrieval" in words
        ):
            out.append(c)
    return out


def rank_by_relevance(topic, cands):
    """Blend semantic similarity of title+abstract to the topic with query agreement and (log) citation count."""
    import math
    from . import rag
    from datetime import datetime, timezone

    current_year = datetime.now(timezone.utc).year
    from .scope import candidate_scope

    cands = [
        c
        for c in relevant_candidates(topic, cands)
        if (not c.get("year") or c["year"] <= current_year)
        and candidate_scope(topic, c)[0]
    ]
    if not cands:
        return cands
    tv = rag.embed([topic], "query")[0]
    dv = rag.embed([f"{c['title']}. {c['abstract'][:600]}" for c in cands])
    for c, v in zip(cands, dv):
        sim = sum(a * b for a, b in zip(tv, v))
        c["relevance"] = round(sim, 4)
        c["score"] = (
            sim + 0.04 * min(c["hits"], 3) + 0.03 * math.log10(1 + c["cited_by"])
        )
        if wants_recent(topic):
            from datetime import datetime, timezone

            year = datetime.now(timezone.utc).year
            if c.get("year"):
                c["score"] += max(0, 0.12 - 0.025 * max(0, year - c["year"]))
    return sorted(cands, key=lambda c: -c["score"])


# ---------------- hosted OCR / layout parsing: Unstructured Partition endpoint ----------------
_us_pages = 0


def needs_ocr(pages, pdf_path):
    """True when the PDF has no usable text layer (scanned / image-only)."""
    import subprocess, re

    o = subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True
    ).stdout
    m = re.search(r"Pages:\s+(\d+)", o)
    n = int(m.group(1)) if m else len(pages) or 1
    chars = sum(len(t) for _, t in pages)
    return chars < 400 * min(n, 5) or len(pages) < max(1, n // 3)


def unstructured_pages(pdf_path, n_pages_hint=0):
    """Send the PDF to Unstructured's hosted API and return [(page_number, text)]. Raises ValueError with a clear reason."""
    global _us_pages
    if not config.UNSTRUCTURED_API_KEY:
        raise ValueError("scanned PDF and UNSTRUCTURED_API_KEY is not set")
    if not config.HOSTED_CALLS:
        raise ValueError(
            "hosted calls are disabled (PAPERFORGE_HOSTED_CALLS=enabled to allow Unstructured)"
        )
    from . import transform

    result = subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True
    ).stdout
    match = re.search(r"Pages:\s+(\d+)", result)
    if not match:
        raise ValueError("Cannot verify physical PDF page count before Transform call.")
    return transform.pages(pdf_path, int(match.group(1)))
