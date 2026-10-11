"""Conservative short *working excerpts* for dough-comparison tasks.

Never modifies full GitHub source stored in the session archive.
For unrelated queries returns None, meaning preserve existing tool result.
"""

from __future__ import annotations

import re
import unicodedata


DOUGH_QUESTION = ("test", "kyn", "livanc", "souffle", "sufle")
RELEVANT = (
    "test", "kyn", "kvask", "drozdi", "bilk", "sneh", "sleh",
    "mich", "preklap", "zaprac", "kyp", "odpo", "pec", "propec",
    "smaz", "panev", "poklic", "tepl", "textur", "nadych",
    "minut", "bublin", "hust", "piskot", "pruzn",
)
SECONDARY = ("vejce", "mouka", "tvaroh", "mleko", "zlutk", "stred", "povrch")
UNRELATED = ("karamel", "crumble", "shrapnel", "zmrzlin", "krem")


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def focus_source(text: str, question: str, limit: int = 1900) -> str | None:
    """Select useful source lines only for explicit dough/cooking questions.

    All excerpts retain source line numbers.  Unselected text stays archived;
    no claims should be made about omitted source material.
    """
    q = normalize(question)
    if not any(term in q for term in DOUGH_QUESTION):
        return None
    if len(text) <= limit:
        return text

    lines = text.splitlines()
    candidates: list[tuple[int, int, str]] = []

    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line or len(line) > 460:
            continue
        n = normalize(line)
        if any(term in n for term in UNRELATED):
            continue
        relevant_hits = sum(term in n for term in RELEVANT)
        secondary_hits = sum(term in n for term in SECONDARY)
        score = relevant_hits * 3 + secondary_hits
        if line.startswith("#") and relevant_hits:
            score += 3
        if score:
            candidates.append((score, index + 1, line))

    if not candidates:
        return text[:limit] + "\n[EXCERPT TRUNCATED]"

    # Select the highest-scoring source lines, then restore document order.
    candidates.sort(key=lambda x: (-x[0], x[1]))
    chosen = []
    total = 0
    for score, line_number, line in candidates:
        entry = f"L{line_number}: {line}\n"
        if len(entry) > 340:
            entry = entry[:337] + "...\n"
        if total + len(entry) > limit - 100:
            continue
        chosen.append((line_number, entry))
        total += len(entry)
    chosen.sort(key=lambda x: x[0])
    return (
        "[WORKING EXCERPT: selected source lines; full file saved in archive]\n"
        + "".join(entry for _, entry in chosen)
        + "[Other lines omitted from WORKING context.]"
    )
