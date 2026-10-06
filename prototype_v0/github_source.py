from __future__ import annotations

import base64
import json
import os
import re
from urllib import error, parse, request


GITHUB_API_ROOT = "https://api.github.com"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def fetch_github_text(
    repo: str,
    path: str,
    *,
    ref: str = "main",
    token: str | None = None,
    timeout: int = 30,
) -> str:
    """Fetch one UTF-8 text file from GitHub using the read-only Contents API."""

    repo = repo.strip()
    path = path.strip().lstrip("/")
    ref = ref.strip()

    if not REPO_RE.fullmatch(repo):
        raise ValueError("repo must be in owner/name form")
    if not path or any(part in {"", ".", ".."} for part in path.split("/")):
        raise ValueError("path must point to one repository file")
    if not ref:
        raise ValueError("ref cannot be empty")

    encoded_path = "/".join(parse.quote(part, safe="") for part in path.split("/"))
    encoded_ref = parse.quote(ref, safe="")
    url = f"{GITHUB_API_ROOT}/repos/{repo}/contents/{encoded_path}?ref={encoded_ref}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "PAE-prototype-v0",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    auth_token = token if token is not None else os.getenv("PAE_GITHUB_TOKEN", "")
    auth_token = auth_token.strip()
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    req = request.Request(url, headers=headers, method="GET")

    try:
        with request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub HTTP {exc.code} for {repo}:{path}@{ref}: {detail}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(f"GitHub connection failed: {exc}") from exc

    data = json.loads(body)

    if data.get("type") != "file":
        raise RuntimeError(f"GitHub path is not a file: {repo}:{path}@{ref}")
    if data.get("encoding") != "base64" or not isinstance(data.get("content"), str):
        raise RuntimeError("GitHub response did not contain base64 file content")

    try:
        raw = base64.b64decode(data["content"], validate=False)
        return raw.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError("GitHub file is not valid UTF-8 text") from exc


def source_name(repo: str, path: str, *, ref: str = "main") -> str:
    return f"github:{repo}@{ref}:{path.lstrip('/')}"
