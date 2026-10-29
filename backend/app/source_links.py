"""Explicit user-link ingestion. Public academic PDFs only, with chat-scoped checkpoints."""

import hashlib, ipaddress, json, re, socket
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin, unquote
from pathlib import Path
import httpx
from . import db, research, rag, config


class LinkError(ValueError):
    pass


def links(text):
    return list(
        dict.fromkeys(
            u.rstrip(".,;:)") for u in re.findall(r'https?://[^\s<>"{}]+', text)
        )
    )


def public_url(url):
    p = urlparse(url)
    if (
        p.scheme != "https"
        or not p.hostname
        or p.username
        or p.password
        or p.port not in (None, 443)
    ):
        raise LinkError(
            "Use an HTTPS public paper URL without credentials or a custom port."
        )
    try:
        addresses = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
    except OSError:
        raise LinkError("Paper hostname could not be resolved.")
    if not addresses or any(
        not ipaddress.ip_address(a[4][0]).is_global for a in addresses
    ):
        raise LinkError("Private/local network links are not paper sources.")
    return url


def fetch(url, limit=40_000_000):
    """Validate each redirect, rather than following an untrusted location implicitly."""
    for _ in range(5):
        public_url(url)
        with httpx.stream(
            "GET", url, headers=research.UA, timeout=45, follow_redirects=False
        ) as r:
            if r.status_code in (301, 302, 303, 307, 308):
                url = urljoin(url, r.headers.get("location", ""))
                continue
            if r.status_code != 200:
                raise LinkError(
                    f"Paper URL returned HTTP {r.status_code}. No bypass or paid access attempted."
                )
            data = bytearray()
            for chunk in r.iter_bytes():
                data += chunk
                if len(data) > limit:
                    raise LinkError("Paper download exceeds the size limit.")
            return url, bytes(data)
    raise LinkError("Too many redirects in paper URL.")


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.title = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key and a.get("content"):
                self.meta.setdefault(key, []).append(a["content"])
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, text):
        if self.in_title:
            self.title.append(text)

    def first(self, *names):
        return next((self.meta[n][0] for n in names if self.meta.get(n)), None)


def resolve(url, root):
    """Landing citation metadata or a direct PDF. Never substitute web prose for a paper."""
    requested = url
    u = urlparse(url)
    # Read citation metadata on arXiv abstract pages before fetching the PDF.
    if u.hostname in ("arxiv.org", "www.arxiv.org") and u.path.startswith("/pdf/"):
        url = "https://arxiv.org/abs/" + u.path[len("/pdf/") :].removesuffix(".pdf")
    final, data = fetch(url)
    meta = None
    if not data.startswith(b"%PDF"):
        if len(data) > 2_000_000:
            raise LinkError("Landing page too large; provide the direct PDF link.")
        meta = Metadata()
        meta.feed(data.decode("utf-8", "replace"))
        pdf = meta.first("citation_pdf_url")
        if not pdf:
            raise LinkError(
                "No open-access PDF link in the page metadata. Provide its direct academic PDF URL."
            )
        final, data = fetch(urljoin(final, pdf))
        if not data.startswith(b"%PDF"):
            raise LinkError("Linked file is not a PDF.")
    digest = hashlib.sha256(data).hexdigest()
    pdf = root / "sources" / (digest + ".pdf")
    pdf.parent.mkdir(exist_ok=True)
    pdf.write_bytes(data)
    from pypdf import PdfReader

    try:
        reader = PdfReader(str(pdf))
        pm = reader.metadata or {}
        pages = len(reader.pages)
        if pages < 1 or pages > config.UNSTRUCTURED_MAX_PAGES_PER_RUN:
            raise LinkError("Paper page count outside the configured bound.")
    except LinkError:
        raise
    except Exception:
        raise LinkError("Downloaded PDF could not be parsed.")
    title = (
        meta.first("citation_title", "dc.title", "og:title") if meta else None
    ) or pm.get("/Title")
    title = re.sub(r"\s+", " ", str(title or "")).strip()
    # Unknown metadata is not a license to invent author/year/title.
    if len(title) < 8 or title.lower() in ("untitled", "microsoft word"):
        raise LinkError(
            "PDF lacks a usable title. Provide its publisher/arXiv landing URL with citation metadata."
        )

    def natural_name(value):
        parts = [x.strip() for x in value.split(",")]
        return " ".join(parts[1:] + parts[:1]) if len(parts) == 2 else value.strip()

    authors = (
        ", ".join(natural_name(x) for x in meta.meta.get("citation_author", []))
        if meta
        else ""
    )
    authors = authors or str(pm.get("/Author") or "Unknown author")
    date = (
        meta.first("citation_publication_date", "citation_date", "dc.date")
        if meta
        else None
    )
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", date or "")
    year = int(year_match[0]) if year_match else None
    row = dict(
        title=title,
        authors=authors,
        year=year,
        venue=(
            meta.first("citation_journal_title", "citation_conference_title")
            if meta
            else ""
        ),
        doi=meta.first("citation_doi") if meta else None,
        url=requested,
        pdf_url=final,
        abstract="",
        cited_by=0,
        origin="user_link",
    )
    return row, pdf, digest, pages


def ingest(job, tid, url, root):
    """Durable per-URL stage. Successful indexing is not repeated after /resume."""
    ledger = root / "link-ingestion"
    ledger.mkdir(exist_ok=True)
    checkpoint = ledger / (hashlib.sha256(url.encode()).hexdigest() + ".json")
    try:
        state = json.loads(checkpoint.read_text())
    except (OSError, ValueError):
        state = {}
    existing = db.sources(tid)
    if state.get("source_id"):
        old = next((s for s in existing if s["id"] == state["source_id"]), None)
        if old and old["status"] == "indexed":
            return old
    else:
        old = next(
            (s for s in existing if s.get("url") == url and s["status"] == "indexed"),
            None,
        )
        if old:
            return old
    tc = job.tool_start("ingest_link", {"url": url, "scope": tid})
    if not state.get("source_id"):
        row, pdf, digest, n = resolve(url, root)
        # Content hash avoids indexing identical PDFs supplied through different URLs.
        old = next(
            (
                s
                for s in existing
                if s["status"] == "indexed"
                and s.get("pdf_path")
                and Path(s["pdf_path"]).exists()
                and hashlib.sha256(Path(s["pdf_path"]).read_bytes()).hexdigest()
                == digest
            ),
            None,
        )
        if old:
            job.tool_done(tc, {"source_key": old["key"], "reused_existing_pdf": True})
            return old
        row["key"] = research.make_key(row, {s["key"] for s in existing})
        row["status"] = "pending"
        sid = db.add_source(tid, row)
        state = {
            "source_id": sid,
            "key": row["key"],
            "pdf_path": str(pdf),
            "sha256": digest,
            "pages": n,
        }
        checkpoint.write_text(json.dumps(state))
        db.update_source(sid, pdf_path=str(pdf), pages=n)
    sid = state["source_id"]
    pdf = Path(state["pdf_path"])
    key = state["key"]
    text = root / "sources" / (key + ".txt")
    if not text.exists():
        pages = research.extract_pages(pdf)
        if config.UNSTRUCTURED_MODE != "off" and (
            config.UNSTRUCTURED_MODE == "always" or research.needs_ocr(pages, pdf)
        ):
            pages = research.unstructured_pages(pdf, state["pages"])
        if sum(len(t) for _, t in pages) < 3000:
            raise LinkError(
                "No usable paper text. OCR or a text-layer PDF is required."
            )
        text.write_text("\n".join(f"=== PAGE {n} ===\n{t}" for n, t in pages))
    chunks = re.split(r"=== PAGE (\d+) ===\n", text.read_text())
    pages = [(int(chunks[i]), chunks[i + 1]) for i in range(1, len(chunks) - 1, 2)]
    n = rag.index_source(tid, sid, pages)
    if not n:
        raise LinkError("No page chunks could be indexed.")
    db.update_source(sid, status="indexed", text_path=str(text), pages=state["pages"])
    row = next(s for s in db.sources(tid) if s["id"] == sid)
    job.tool_done(
        tc,
        {
            "source_key": key,
            "pages": state["pages"],
            "chunks_embedded": n,
            "store": "PostgreSQL pgvector",
        },
    )
    return row
