"""Extract user-authorized exact GitHub file reads from a request.

This is a narrow guard for explicit file paths, not a general natural-language
router or repository crawler.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


REPO_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?![A-Za-z0-9_./-])"
)
NUMBERED_LINE_RE = re.compile(r"^\s*\d+[.)]\s*")
READABLE_SUFFIXES = (".md", ".txt", ".json")
MAX_EXPLICIT_FILES = 3


@dataclass(frozen=True)
class GitHubReadScope:
    repo: str
    paths: tuple[str, ...]
    ref: str = "main"

    def allows(self, name: str, arguments: dict[str, object]) -> bool:
        return (
            name == "github_read"
            and arguments.get("repo") == self.repo
            and arguments.get("ref", "main") == self.ref
            and arguments.get("path") in self.paths
        )


def extract_github_read_scope(user_text: str) -> GitHubReadScope | None:
    """Identify explicit file-path requests scoped to exactly one repository."""
    matches = REPO_RE.findall(user_text)
    if not matches:
        return None

    paths: list[str] = []
    for raw_line in user_text.splitlines():
        line = NUMBERED_LINE_RE.sub("", raw_line.strip()).strip()
        if len(line) >= 2 and line[0] in {'"', "'", "“"} and line[-1] in {'"', "'", "”"}:
            line = line[1:-1].strip()

        if (
            "/" not in line
            or not line.lower().endswith(READABLE_SUFFIXES)
            or line.startswith(("http://", "https://", "/", "../", "./"))
            or "\x00" in line
            or any(part in {"", ".", ".."} for part in line.split("/"))
        ):
            continue
        if line not in paths:
            paths.append(line)

    if not paths:
        return None

    # The user's first explicit repo is authoritative. Do not silently pick PAE.
    # NOTE: other slash-containing strings may occur within paths, after the repo.
    repos = [match for match in matches if match not in paths]
    if not repos:
        return None

    ref_match = re.search(
        r"\b(?:branch|ref|větev)\s*[:=]?\s*[\"'“]?([A-Za-z0-9_.\-/]+)",
        user_text, flags=re.IGNORECASE,
    )
    ref = ref_match.group(1) if ref_match else "main"
    if not (1 <= len(paths) <= MAX_EXPLICIT_FILES):
        return None
    return GitHubReadScope(repo=repos[0], paths=tuple(paths), ref=ref)
