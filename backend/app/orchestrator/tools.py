"""LangChain tools bound to the model in find_papers. The graph executes the model's tool calls."""

import json
from langchain_core.tools import tool
from .. import research, jobs

MAX_RESULTS = 8


def _brief(items):
    return json.dumps(
        [
            {
                "title": i.get("title"),
                "authors": (i.get("authors") or "")[:120],
                "year": i.get("year"),
                "venue": i.get("venue"),
                "url": i.get("url"),
                "open_access_pdf": bool(i.get("pdf_url")),
                "origin": i.get("origin"),
            }
            for i in items[:MAX_RESULTS]
        ]
    )


def make_tools(tid):
    def traced(name, query, fn):
        job = jobs.RUNNING.get(tid)
        tc = job.tool_start(name, {"query": query}) if job else None
        try:
            items = fn(query)
        except Exception as e:  # network or provider failure is reported, never papered over
            if job:
                job.tool_done(tc, {"error": f"{type(e).__name__}: {str(e)[:160]}"}, error=True)
            return json.dumps({"error": f"{name} failed: {type(e).__name__}"})
        if job:
            job.tool_done(tc, {"results": len(items)})
        return _brief(items)

    @tool
    def search_arxiv(query: str) -> str:
        """Search arXiv (open-access preprints) for papers on a topic. Returns title, authors, year, url."""
        return traced("search_arxiv", query, lambda q: research.search_arxiv(q, n=MAX_RESULTS))

    @tool
    def search_openalex(query: str) -> str:
        """Search OpenAlex for open-access papers on a topic. Returns title, authors, year, venue, url."""
        return traced("search_openalex", query, lambda q: research.search_openalex(q, n=MAX_RESULTS))

    return [search_arxiv, search_openalex]
