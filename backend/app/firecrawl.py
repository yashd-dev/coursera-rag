"""Complementary public web context, never academic-paper metadata or proof a PDF was read."""

import json, hashlib
from urllib.parse import urlparse
import httpx
from . import config, db


def _headers():
    return {"Authorization": "Bearer " + config.FIRECRAWL_API_KEY}


def reserve(cost):
    if (
        not config.FIRECRAWL_CALLS
        or not config.FIRECRAWL_FREE_VERIFIED
        or not config.FIRECRAWL_API_KEY
    ):
        raise ValueError("Firecrawl disabled or free-credit scope unverified.")
    r = httpx.get(
        "https://api.firecrawl.dev/v2/team/credit-usage", headers=_headers(), timeout=15
    )
    r.raise_for_status()
    remaining = r.json().get("data", {}).get("remainingCredits")
    if not isinstance(remaining, (int, float)) or remaining < cost + 10:
        raise ValueError("Insufficient verified Firecrawl credit headroom.")
    with db.conn().transaction():
        db.conn().execute(
            "SELECT pg_advisory_xact_lock(hashtextextended('firecrawl_budget',0))"
        )
        if (
            db.meta_get("firecrawl_credits_reserved") + cost
            > config.FIRECRAWL_CREDIT_CAP
        ):
            raise ValueError("Firecrawl app credit cap reached.")
        db.meta_add("firecrawl_credits_reserved", cost)


def search(query):
    reserve(2)
    r = httpx.post(
        "https://api.firecrawl.dev/v2/search",
        headers=_headers(),
        json={
            "query": query,
            "limit": 3,
            "sources": ["web"],
            "domainTools": False,
            "safe": True,
        },
        timeout=60,
    )
    r.raise_for_status()
    body = r.json()
    if not body.get("success"):
        raise ValueError("Firecrawl search failed; not automatically retried.")
    return [
        {
            "title": d.get("title", ""),
            "url": d.get("url", ""),
            "description": d.get("description", ""),
            "kind": "web_context_not_paper",
        }
        for d in body.get("data", {}).get("web", [])
    ]


def scrape(url):
    p = urlparse(url)
    if (
        p.scheme != "https"
        or not p.hostname
        or p.hostname in ("localhost", "127.0.0.1")
        or p.path.lower().endswith(".pdf")
    ):
        raise ValueError(
            "Firecrawl web context accepts HTTPS public webpages, not PDF ingestion."
        )
    # No social-profile enrichment or expensive third-party provider routes.
    if any(
        p.hostname == d or p.hostname.endswith("." + d)
        for d in ("linkedin.com", "x.com", "twitter.com")
    ):
        raise ValueError("Social/enrichment URLs excluded.")
    reserve(1)
    r = httpx.post(
        "https://api.firecrawl.dev/v2/scrape",
        headers=_headers(),
        json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
        timeout=60,
    )
    r.raise_for_status()
    j = r.json()
    if not j.get("success"):
        raise ValueError("Firecrawl scrape failed; not automatically retried.")
    return {
        "url": url,
        "kind": "web_context_not_paper",
        "markdown": j.get("data", {}).get("markdown", "")[:16000],
    }


def context(topic, root):
    key = "web_context:" + hashlib.sha256(topic.encode()).hexdigest()
    old = db.q("SELECT value FROM meta WHERE key=%s", (key,))
    if old:
        return json.loads(old[0]["value"])
    hits = search(topic + " research paper publisher project")
    pages = []
    for hit in hits[:2]:
        try:
            pages.append(scrape(hit["url"]))
        except (ValueError, httpx.HTTPError):
            continue
    result = {"kind": "web_context_not_paper", "search_results": hits, "pages": pages}
    db.x(
        "INSERT INTO meta(key,value) VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value",
        (key, json.dumps(result)),
    )
    (root / "web-context.json").write_text(json.dumps(result, indent=2))
    return result
