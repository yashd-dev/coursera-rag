"""Resolve explicit section references and enforce byte-exact preservation elsewhere."""

import re


class SectionError(ValueError):
    pass


def locate(tex, request):
    heads = list(
        re.finditer(r"\\(section|subsection|subsubsection)(\*?)\{([^{}]+)\}", tex)
    )
    counters = [0, 0, 0]
    items = []
    for i, m in enumerate(heads):
        level = {"section": 0, "subsection": 1, "subsubsection": 2}[m[1]]
        if not m[2]:
            counters[level] += 1
        for j in range(level + 1, 3):
            counters[j] = 0
        number = ".".join(str(x) for x in counters[: level + 1])
        aliases = {number, m[3].lower()}
        if level == 1 and 1 <= counters[1] <= 26:
            aliases.add(str(counters[0]) + chr(96 + counters[1]))
        end = next(
            (
                h.start()
                for h in heads[i + 1 :]
                if {"section": 0, "subsection": 1, "subsubsection": 2}[h[1]] <= level
            ),
            len(tex),
        )
        boundary = re.search(
            r"\\(?:bibliographystyle|bibliography|end\{document)", tex[m.end() : end]
        )
        if boundary:
            end = m.end() + boundary.start()
        items.append(
            {"title": m[3], "aliases": aliases, "start": m.start(), "end": end}
        )
    refs = re.findall(
        r"\bsection\s+([0-9]+(?:\.[0-9]+)*(?:[a-z]|\s+[a-z]\b)?)\b", request, re.I
    )
    matches = []
    for ref in refs:
        norm = re.sub(r"\s+", "", ref.lower())
        found = [s for s in items if norm in s["aliases"]]
        if len(found) != 1:
            raise SectionError(
                "Section "
                + ref
                + " is missing or ambiguous. Use an exact existing section title."
            )
        matches.extend(found)
    if not refs:
        matches = [
            s
            for s in items
            if re.search(r"(?<!\w)" + re.escape(s["title"]) + r"(?!\w)", request, re.I)
        ]
    # Parent/child titles both mentioned may be ambiguous. Never silently choose.
    unique = {s["start"]: s for s in matches}
    if len(unique) > 1:
        raise SectionError(
            "More than one section matches. Name one exact section to change."
        )
    return next(iter(unique.values()), None)


def apply(before, patches, target=None):
    revised = before
    for p in patches:
        old, new = p.get("old"), p.get("new")
        if (
            not isinstance(old, str)
            or not old
            or revised.count(old) != 1
            or not isinstance(new, str)
        ):
            raise SectionError("Edit span mismatch")
        if target:
            at = revised.index(old)
            end = len(revised) - (len(before) - target["end"])
            if at < target["start"] or at + len(old) > end:
                raise SectionError("Patch changes text outside the requested section")
        revised = revised.replace(old, new, 1)
    if target:
        assert_preserved(before, revised, target)
    return revised


def assert_preserved(before, after, target):
    prefix = before[: target["start"]]
    suffix = before[target["end"] :]
    if not after.startswith(prefix) or (suffix and not after.endswith(suffix)):
        raise SectionError("Protected text outside the requested section changed")
