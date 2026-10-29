"""Unstructured Transform v2. Persist accepted jobs and never resubmit on a timeout."""

import hashlib, json, time
from urllib.parse import urljoin, urlparse
import httpx
from . import config, db


def pages(pdf_path, n_pages):
    base = config.UNSTRUCTURED_API_URL.rstrip("/")
    if base != "https://transform.unstructured.io/api/v2":
        raise ValueError("Expected the owner-selected Transform v2 API URL.")
    if n_pages < 1:
        raise ValueError(
            "Physical PDF page count required before Transform submission."
        )
    if not config.UNSTRUCTURED_FREE_PAGES_VERIFIED:
        raise ValueError("Transform free allowance not verified.")
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    key = "transform_job:" + digest
    old = db.q("SELECT value FROM meta WHERE key=%s", (key,))
    state = json.loads(old[0]["value"]) if old else {}

    def save():
        db.x(
            "INSERT INTO meta(key,value) VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value",
            (key, json.dumps(state)),
        )

    h = {"unstructured-api-key": config.UNSTRUCTURED_API_KEY}
    if not state:
        # Reserve BEFORE submission, including ambiguous/failed responses. No blind retries.
        with db.conn().transaction():
            db.conn().execute(
                "SELECT pg_advisory_xact_lock(hashtextextended('transform_page_budget',0))"
            )
            used = db.meta_get("transform_pages_reserved")
            if used + n_pages > config.UNSTRUCTURED_PAGE_CAP:
                raise ValueError("Transform one-time app page cap reached.")
            db.meta_add("transform_pages_reserved", n_pages)
            state = {"status": "submission_started", "pages_reserved": n_pages}
            save()
        with open(pdf_path, "rb") as f:
            r = httpx.post(
                base + "/parse",
                headers={**h, "Prefer": "wait=30"},
                data={"output": "elements", "profile": "balanced"},
                files={"input": (pdf_path.name, f, "application/pdf")},
                timeout=45,
            )
        if r.status_code not in (200, 202):
            raise ValueError(
                f"Transform HTTP{r.status_code}; submission not retried automatically."
            )
        body = r.json()
        state = {
            "status": body.get("status"),
            "id": body.get("id"),
            "pages_reserved": n_pages,
        }
        if r.status_code == 200:
            state["result"] = body
        else:
            ref = r.headers.get("Location") or body.get("poll_url")
            if not ref:
                raise ValueError(
                    "Transform accepted job lacks poll URL; retain job for manual recovery."
                )
            url = urljoin(base + "/", ref)
            parsed = urlparse(url)
            if (
                parsed.scheme != "https"
                or parsed.netloc != "transform.unstructured.io"
                or not parsed.path.startswith("/api/v2/jobs/")
            ):
                raise ValueError("Refusing untrusted Transform polling destination.")
            state["poll_url"] = url
        save()
    if "result" not in state and not state.get("poll_url"):
        raise ValueError(
            "Previous Transform submission state ambiguous; inspect account before retrying."
        )
    deadline = time.monotonic() + 90
    while "result" not in state and time.monotonic() < deadline:
        time.sleep(5)
        r = httpx.get(state["poll_url"], headers=h, timeout=30)
        if r.status_code != 200:
            raise ValueError(
                f"Transform poll HTTP{r.status_code}; existing job retained for resume."
            )
        body = r.json()
        state["status"] = body.get("status")
        if state["status"] in ("failed", "cancelled"):
            save()
            raise ValueError("Transform job ended without usable result.")
        if state["status"] in ("completed", "completed_with_warnings"):
            state["result"] = body.get("result")
        save()
    result = state.get("result")
    if not result:
        raise ValueError(
            "Transform job pending; resume existing job later, do not resubmit."
        )
    if result.get("warnings") or result.get("status") == "completed_with_warnings":
        raise ValueError("Transform warnings need review before indexing.")
    by = {}
    for el in result.get("elements", []):
        text = (el.get("text") or "").strip()
        page = (el.get("metadata") or {}).get("page_number")
        if text:
            if not isinstance(page, int) or page < 1:
                raise ValueError("Transform element lacks verified page provenance.")
            by.setdefault(page, []).append(text)
    if not by:
        raise ValueError("Transform returned no usable page elements.")
    return [(n, "\n\n".join(ts)) for n, ts in sorted(by.items())]
