"""LaTeX project preparation, build loop and Word export."""

import os, re, shutil, subprocess, zipfile, secrets, unicodedata
from pathlib import Path
from . import config, db

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
RAG_TOKEN = secrets.token_hex(
    16
)  # per-process secret so only local OpenCode runs can call the retrieval endpoint

RAG_CLI = '''#!/usr/bin/env python3
"""Evidence search for this paper's chat-scoped pgvector collection.
usage: python3 rag.py "question or claim to verify" [top_k] [source_key]"""
import json, sys, urllib.request
q = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
body = {"thread_id": "%(tid)s", "query": q, "k": k, "source_key": sys.argv[3] if len(sys.argv) > 3 else None}
req = urllib.request.Request("%(url)s/api/internal/retrieve", json.dumps(body).encode(),
                             {"Content-Type": "application/json", "X-Rag-Token": "%(token)s"})
for r in json.load(urllib.request.urlopen(req, timeout=300))["results"]:
    print(f"[{r['key']} p.{r['page']} score={r['score']}] {r['text']}\\n")
'''


def bibtex_escape(s):
    return (
        (s or "")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


def bib_entry(s):
    authors = " and ".join(
        a.strip() for a in (s["authors"] or "Anonymous").split(",") if a.strip()
    )
    f = {
        "author": authors,
        "title": "{" + bibtex_escape(s["title"]) + "}",
        "year": s["year"] or "",
    }
    arx = s["url"] and "arxiv.org" in s["url"]
    if arx:
        f["howpublished"] = "arXiv preprint " + s["url"].rsplit("/abs/", 1)[-1]
        kind = "misc"
    else:
        f["journal"] = bibtex_escape(s["venue"] or "Open-access publication")
        kind = "article"
    if s["doi"]:
        f["doi"] = s["doi"]
    if s["url"]:
        f["url"] = s["url"]
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in f.items() if v != "")
    return f"@{kind}{{{s['key']},\n{body}\n}}\n"


def prepare(tid, template):
    """Create project/paper (template + refs.bib), project/sources, project/notes and the rag.py evidence CLI."""
    root = db.thread_dir(tid)
    paper = root / "paper"
    if not paper.exists():
        shutil.copytree(TEMPLATE_DIR / config.TEMPLATES[template]["dir"], paper)
    # Existing projects may switch document templates during an explicit edit.
    for asset in (TEMPLATE_DIR / config.TEMPLATES[template]["dir"]).iterdir():
        if asset.suffix in (".cls", ".bst"):
            shutil.copy2(asset, paper / asset.name)
    (root / "sources").mkdir(exist_ok=True)
    (root / "notes").mkdir(exist_ok=True)
    (root / "rag.py").write_text(
        RAG_CLI % {"tid": tid, "url": config.PUBLIC_URL, "token": RAG_TOKEN}
    )
    return root


def write_bib(tid):
    root = db.thread_dir(tid)
    used = [s for s in db.sources(tid) if s["status"] == "indexed"]
    (root / "paper" / "refs.bib").write_text("\n".join(bib_entry(s) for s in used))
    return used


def _run(cmd, cwd, timeout=180):
    r = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        errors="replace",
        env={
            **{
                k: v
                for k, v in os.environ.items()
                if k in {"PATH", "HOME", "USER", "LANG", "LC_ALL", "TMPDIR"}
            },
            "openin_any": "p",
            "openout_any": "p",
        },
    )
    return r.returncode, r.stdout + r.stderr


def normalize_generated_tex(text):
    # PDF-extracted mathematical Latin symbols are unsupported by pdfLaTeX.
    # Preserve their letter and bold/italic/double-struck style without a model repair.
    def math_latin(match):
        char = match.group()
        name = unicodedata.name(char, "")
        base = unicodedata.normalize("NFKD", char)
        if not name.startswith("MATHEMATICAL ") or not re.fullmatch(
            r"[A-Za-z0-9]", base
        ):
            return char
        style = (
            "mathbb"
            if "DOUBLE-STRUCK" in name
            else (
                "boldsymbol"
                if "BOLD" in name and "ITALIC" in name
                else (
                    "mathbf"
                    if "BOLD" in name
                    else ("mathit" if "ITALIC" in name else "mathrm")
                )
            )
        )
        return chr(92) + "ensuremath{" + chr(92) + style + "{" + base + "}}"

    text = re.sub(r"[\U0001D400-\U0001D7FF]", math_latin, text)
    # A literal percentage in generated prose must not silently comment out the rest
    # of its line. Preserve genuine TeX comments and already escaped percentages.
    if r"\documentclass[runningheads]{llncs}" in text:
        if r"\institute{" not in text:
            text = text.replace(
                r"\maketitle", r"\institute{}" + "\n" + r"\maketitle", 1
            )
        if r"\titlerunning{" not in text:
            text = text.replace(
                r"\maketitle",
                r"\titlerunning{Literature Review}" + "\n" + r"\maketitle",
                1,
            )
        if r"\emergencystretch" not in text:
            text = text.replace(
                r"\begin{document}",
                r"\emergencystretch=2em" + "\n" + r"\begin{document}",
                1,
            )
    # Implement [H] without optional TeX packages unavailable on minimal installs.
    if r"\begin{table}[H]" in text:
        definition = r"\makeatletter\renewenvironment{table}[1][]{\par\noindent\begin{minipage}{\linewidth}\def\@captype{table}\footnotesize}{\end{minipage}\par}\makeatother"
        if definition not in text:
            text = text.replace(
                r"\begin{document}", definition + "\n" + r"\begin{document}"
            )
        text = text.replace(",float}", "}")
    return re.sub(r"(?<!\\)(?<=\d)%(?=\s|[.,;)\]}]|$)", r"\\%", text)


def build(tid):
    """pdflatex -> bibtex -> pdflatex x2. Returns a dict describing the outcome and any errors the agent must fix."""
    paper = db.thread_dir(tid) / "paper"
    tex = paper / "main.tex"
    normalized = normalize_generated_tex(tex.read_text())
    # Generated documents must never read arbitrary local files or execute shell commands.
    dangerous = re.search(
        r"\\(?:input|include|openin|openout|read|write|immediate|write18|catcode|csname)\b",
        normalized,
    )
    if dangerous:
        return {
            "ok": False,
            "pages": 0,
            "errors": ["Unsafe generated TeX command: " + dangerous.group()],
            "undefined_citations": [],
            "bibtex_warnings": [],
            "overfull": 0,
            "log_tail": "",
        }
    tex.write_text(normalized)
    log = ""
    failed_commands = []
    for cmd in (
        [
            "pdflatex",
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-file-line-error",
            "main.tex",
        ],
        ["bibtex", "main"],
        [
            "pdflatex",
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-file-line-error",
            "main.tex",
        ],
        [
            "pdflatex",
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-file-line-error",
            "main.tex",
        ],
    ):
        try:
            rc, out = _run(cmd, paper)
            if rc:
                failed_commands.append(" ".join(cmd))
        except subprocess.TimeoutExpired:
            out = "TIMEOUT"
            failed_commands.append(" ".join(cmd))
        log += f"\n$ {' '.join(cmd)}\n{out}"
    tex_log = (
        (paper / "main.log").read_text(errors="replace")
        if (paper / "main.log").exists()
        else ""
    )
    errors = re.findall(
        r"^(?:\./)?main\.tex:\d+:.*(?:\n.*){0,3}", tex_log, re.M
    ) or re.findall(r"^!.*(?:\n.*){0,3}", tex_log, re.M)
    undefined = sorted(set(re.findall(r"Citation `([^']+)' .*undefined", tex_log)))
    bibwarn = re.findall(r"^Warning--.*", log, re.M)[:10]
    pdf = paper / "main.pdf"
    pages = 0
    if pdf.exists():
        _, o = _run(["pdfinfo", str(pdf)], paper)
        m = re.search(r"Pages:\s+(\d+)", o)
        pages = int(m.group(1)) if m else 0
    ok = pdf.exists() and not errors and not undefined and not failed_commands
    if failed_commands and not errors:
        errors = ["Failed build command: " + c for c in failed_commands]
    return {
        "ok": ok,
        "pages": pages,
        "errors": errors[:8],
        "undefined_citations": undefined,
        "bibtex_warnings": bibwarn,
        "overfull": len(re.findall(r"Overfull \\hbox", tex_log)),
        "log_tail": tex_log[-1500:],
    }


def source_zip(tid, name="paper-source.zip"):
    paper = db.thread_dir(tid) / "paper"
    out = db.thread_dir(tid) / name
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in paper.iterdir():
            if (
                f.suffix in {".tex", ".bib", ".cls", ".bst", ".png", ".jpg", ".pdf"}
                or f.name == "main.bbl"
            ):
                z.write(f, f.name)
    return out


# ---------- Word export ----------
def _balanced(s, start):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1 : i], i + 1
    return s[start + 1 :], len(s)


def _arg(src, cmd):
    m = re.search(r"\\" + cmd + r"\s*(?:\[[^\]]*\])?\s*\{", src)
    return _balanced(src, m.end() - 1)[0] if m else ""


def neutral_tex(main_tex):
    """Convert template-specific front matter (IEEEtran / llncs macros) to plain LaTeX pandoc understands."""
    title = _arg(main_tex, "title")
    author = _arg(main_tex, "author")
    author = re.sub(r"\\IEEEauthorblock[NA]\s*", "", author)
    author = re.sub(r"\\(?:and|AND|institute|email)\b", r"\\\\", author)
    author = re.sub(r"\\\\\s*(\\\\\s*)+", r"\\\\", author)
    author = author.replace("{", "").replace("}", "")
    abstract = ""
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main_tex, re.S)
    if m:
        abstract = re.sub(r"\\keywords\{.*?\}", "", m.group(1), flags=re.S).strip()
    kw = (
        _arg(main_tex, "keywords")
        or (
            re.search(
                r"\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}", main_tex, re.S
            )
            or [None, ""]
        )[1]
    )
    kw = kw.replace("\\and", ";").strip()
    body = main_tex.split("\\maketitle", 1)[-1]
    body = re.sub(r"\\begin\{abstract\}.*?\\end\{abstract\}", "", body, flags=re.S)
    body = re.sub(
        r"\\begin\{IEEEkeywords\}.*?\\end\{IEEEkeywords\}", "", body, flags=re.S
    )
    body = re.sub(
        r"\\bibliographystyle\{[^}]*\}|\\bibliography\{[^}]*\}|\\end\{document\}",
        "",
        body,
    )
    body += "\n\\section*{References}\n"
    return (
        r"\documentclass{article}\usepackage{amsmath,amssymb,graphicx,url}"
        + "\n\\title{"
        + title
        + "}\n\\author{"
        + author.strip()
        + "}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\n"
        + abstract
        + "\n\\end{abstract}\n"
        + (("\\noindent\\textbf{Keywords:} " + kw + "\n\n") if kw else "")
        + body
        + "\n\\end{document}\n"
    )


def export_docx(tid, template):
    paper = db.thread_dir(tid) / "paper"
    _, version = _run(["pandoc", "--version"], paper)
    match = re.search(r"pandoc (\d+)\.(\d+)", version)
    if not match or tuple(map(int, match.groups())) < (2, 11):
        return {
            "ok": False,
            "path": paper / "paper.docx",
            "log": "Pandoc 2.11+ with built-in citeproc is required.",
        }
    (paper / "word.tex").write_text(neutral_tex((paper / "main.tex").read_text()))
    out = paper / "paper.docx"
    cmd = [
        "pandoc",
        "word.tex",
        "-f",
        "latex",
        "-t",
        "docx",
        "-o",
        "paper.docx",
        "--citeproc",
        "--bibliography=refs.bib",
        f"--csl={TEMPLATE_DIR / config.TEMPLATES[template]['csl']}",
    ]
    rc, o = _run(cmd, paper)
    return {"ok": rc == 0 and out.exists(), "path": out, "log": o[-800:]}


def verify_docx(tid):
    """Independent check of the Word file: reconvert with LibreOffice, compare headings/citations/equations against the TeX."""
    paper = db.thread_dir(tid) / "paper"
    vdir = paper / "docx-check"
    shutil.rmtree(vdir, ignore_errors=True)
    vdir.mkdir()
    _run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(vdir),
            str(paper / "paper.docx"),
        ],
        paper,
        180,
    )
    pdf = vdir / "paper.pdf"
    _, text = _run(["pdftotext", str(pdf), "-"], paper) if pdf.exists() else (1, "")
    tex = (paper / "main.tex").read_text()
    heads = re.findall(r"\\(?:sub)*section\*?\{([^}]*)\}", tex)
    normal = lambda value: re.sub(r"\s+", "", value).lower()
    missing_heads = [h for h in heads if normal(h) not in normal(text)]
    cites = set(re.findall(r"\\cite[a-z]*(?:\[[^\]]*\])?\{([^}]*)\}", tex))
    cites = {c.strip() for g in cites for c in g.split(",")}
    unresolved = len(re.findall(r"\(\?\)|\?\?|@[A-Za-z]+\d{4}", text))
    n_eq = (
        len(re.findall(r"\\begin\{(?:equation|align)", tex))
        + len(re.findall(r"\$\$", tex)) // 2
    )
    pages = 0
    if pdf.exists():
        _, o = _run(["pdfinfo", str(pdf)], paper)
        m = re.search(r"Pages:\s+(\d+)", o)
        pages = int(m.group(1)) if m else 0
        _run(
            [
                "pdftoppm",
                "-r",
                "60",
                "-png",
                "-f",
                "1",
                "-l",
                "2",
                str(pdf),
                str(vdir / "page"),
            ],
            paper,
        )
    return {
        "rendered": pdf.exists(),
        "docx_pages": pages,
        "headings_in_tex": len(heads),
        "headings_missing_in_docx": missing_heads,
        "distinct_citations_in_tex": len(cites),
        "unresolved_citation_markers": unresolved,
        "display_equations_in_tex": n_eq,
        "word_count_docx": len(text.split()),
        "preview_dir": str(vdir),
    }
