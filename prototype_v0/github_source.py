from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from difflib import unified_diff
from urllib import error, parse, request


GITHUB_API_ROOT = "https://api.github.com"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MAX_LIST_ITEMS = 100
MAX_SEARCH_RESULTS = 10
MAX_TREE_ITEMS = 5_000
MAX_WRITE_CHARS = 100_000


class GitHubApiError(RuntimeError):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class GitHubTextFile:
    content: str
    blob_sha: str


@dataclass(frozen=True)
class GitHubTarget:
    repo: str
    ref: str
    path: str
    kind: str


def _token() -> str:
    return (os.getenv("PAE_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()


def github_configured() -> bool:
    return bool(_token())


def _validate_repo(repo: str) -> str:
    repo = repo.strip()
    if not REPO_RE.fullmatch(repo):
        raise ValueError("repo must be in owner/name form")
    return repo


def _validate_path(path: str, *, allow_root: bool = True) -> str:
    path = path.strip().strip("/")
    if not path and allow_root:
        return ""
    if not path or any(part in {"", ".", ".."} for part in path.split("/")):
        raise ValueError("invalid repository path")
    return path


def _github_api(
    api_path: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    require_auth: bool = False,
    timeout: int = 30,
) -> object:
    token = _token()
    if require_auth and not token:
        raise GitHubApiError(401, "AUTH_REQUIRED: PAE_GITHUB_TOKEN is not configured")
    headers = {
        "Accept": "application/vnd.github.text-match+json, application/vnd.github+json",
        "User-Agent": "PAE-prototype-v0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(f"{GITHUB_API_ROOT}{api_path}", data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
        return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        if exc.code == 401:
            prefix = "AUTH_REQUIRED"
        elif exc.code == 403:
            prefix = "AUTH_SCOPE_REQUIRED"
        elif exc.code == 404:
            prefix = "NOT_FOUND"
        else:
            prefix = "GITHUB_ERROR"
        raise GitHubApiError(exc.code, f"{prefix}: GitHub API failed (HTTP {exc.code})") from exc
    except error.URLError as exc:
        raise RuntimeError(f"NETWORK_UNAVAILABLE: GitHub cannot be reached: {exc.reason}") from exc


def parse_github_target(value: str) -> GitHubTarget:
    value = value.strip()
    if REPO_RE.fullmatch(value):
        return GitHubTarget(repo=value, ref="main", path="", kind="repo")
    parsed = parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.casefold() not in {
        "github.com", "www.github.com"
    }:
        raise ValueError("expected owner/name or a github.com repository URL")
    parts = [parse.unquote(part) for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("GitHub URL does not contain owner/repository")
    repo = _validate_repo(f"{parts[0]}/{parts[1].removesuffix('.git')}")
    if len(parts) == 2:
        return GitHubTarget(repo=repo, ref="main", path="", kind="repo")
    if len(parts) >= 4 and parts[2] in {"blob", "tree"}:
        kind = "file" if parts[2] == "blob" else "directory"
        return GitHubTarget(repo=repo, ref=parts[3], path="/".join(parts[4:]), kind=kind)
    raise ValueError("unsupported GitHub URL; use repository, /blob/ref/path or /tree/ref/path")


def list_github_path(repo: str, path: str = "", *, ref: str = "main", limit: int = 50) -> dict[str, object]:
    repo = _validate_repo(repo)
    path = _validate_path(path)
    limit = max(1, min(limit, MAX_LIST_ITEMS))
    encoded_path = "/".join(parse.quote(part, safe="") for part in path.split("/"))
    suffix = f"/{encoded_path}" if encoded_path else ""
    data = _github_api(f"/repos/{repo}/contents{suffix}?ref={parse.quote(ref, safe='')}")
    if isinstance(data, dict):
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        raise RuntimeError("GITHUB_ERROR: invalid contents response")
    compact = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        compact.append(
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "type": item.get("type"),
                "size": item.get("size"),
                "sha": item.get("sha"),
            }
        )
    return {"status": "ok", "repo": repo, "ref": ref, "path": path, "count": len(compact), "truncated": len(items) > limit, "items": compact}


def _search_terms(query: str) -> list[str]:
    return [term.casefold() for term in re.findall(r"[A-Za-z0-9_.-]{2,}", query)[:8]]


def search_github(repo: str, query: str, *, ref: str = "main", limit: int = 10) -> dict[str, object]:
    repo = _validate_repo(repo)
    query = query.strip()
    if not query:
        raise ValueError("query cannot be empty")
    limit = max(1, min(limit, MAX_SEARCH_RESULTS))
    token = _token()
    results: list[dict[str, object]] = []
    if token:
        encoded_q = parse.quote(f"{query} repo:{repo}", safe="")
        data = _github_api(f"/search/code?q={encoded_q}&per_page={limit}", require_auth=True)
        items = data.get("items", []) if isinstance(data, dict) else []
        if isinstance(items, list):
            for item in items[:limit]:
                if isinstance(item, dict):
                    matches = item.get("text_matches")
                    snippet = ""
                    if isinstance(matches, list) and matches and isinstance(matches[0], dict):
                        snippet = " ".join(str(matches[0].get("fragment", "")).split())[:320]
                    results.append({"path": item.get("path"), "name": item.get("name"), "sha": item.get("sha"), "snippet": snippet})
    else:
        tree_data = _github_api(f"/repos/{repo}/git/trees/{parse.quote(ref, safe='')}?recursive=1")
        tree = tree_data.get("tree", []) if isinstance(tree_data, dict) else []
        if not isinstance(tree, list):
            tree = []
        terms = _search_terms(query)
        blobs = [item for item in tree[:MAX_TREE_ITEMS] if isinstance(item, dict) and item.get("type") == "blob"]
        for item in blobs:
            path_value = str(item.get("path", ""))
            if any(term in path_value.casefold() for term in terms):
                results.append({"path": path_value, "name": path_value.rsplit("/", 1)[-1], "sha": item.get("sha"), "snippet": "filename match"})
                if len(results) >= limit:
                    break
        if len(results) < limit:
            text_candidates = [item for item in blobs if str(item.get("path", "")).casefold().endswith((".md", ".txt", ".json"))][:25]
            seen = {str(item["path"]) for item in results}
            for item in text_candidates:
                candidate_path = str(item.get("path", ""))
                if candidate_path in seen:
                    continue
                try:
                    content = fetch_github_file(repo, candidate_path, ref=ref).content
                except Exception:
                    continue
                lowered = content.casefold()
                matched = next((term for term in terms if term in lowered), "")
                if matched:
                    index = lowered.find(matched)
                    snippet = " ".join(content[max(0, index - 100):index + 220].split())
                    results.append({"path": candidate_path, "name": candidate_path.rsplit("/", 1)[-1], "sha": item.get("sha"), "snippet": snippet})
                    if len(results) >= limit:
                        break
    return {"status": "ok", "repo": repo, "ref": ref, "query": query, "count": len(results), "results": results, "authenticated": bool(token)}


def prepare_github_write(repo: str, path: str, content: str, *, branch: str = "main") -> dict[str, object]:
    repo = _validate_repo(repo)
    path = _validate_path(path, allow_root=False)
    if len(content) > MAX_WRITE_CHARS:
        raise ValueError(f"content exceeds {MAX_WRITE_CHARS} characters")
    existing = ""
    existing_sha = ""
    try:
        current = fetch_github_file(repo, path, ref=branch)
        existing, existing_sha = current.content, current.blob_sha
        operation = "update"
    except RuntimeError as exc:
        if "HTTP 404" not in str(exc):
            raise
        operation = "create"
    diff = "".join(
        unified_diff(
            existing.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f"a/{path}" if existing_sha else "/dev/null",
            tofile=f"b/{path}",
        )
    )
    return {
        "status": "prepared",
        "operation": operation,
        "repo": repo,
        "branch": branch,
        "path": path,
        "existing_sha": existing_sha,
        "content": content,
        "diff": diff[:20_000],
        "diff_truncated": len(diff) > 20_000,
        "confirmation_required": True,
        "applied": False,
    }


def apply_github_write(prepared: dict[str, object]) -> dict[str, object]:
    repo = _validate_repo(str(prepared["repo"]))
    path = _validate_path(str(prepared["path"]), allow_root=False)
    branch = str(prepared["branch"])
    content = str(prepared["content"])
    encoded_path = "/".join(parse.quote(part, safe="") for part in path.split("/"))
    payload: dict[str, object] = {
        "message": f"Update {path} via PAE Mobile",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    existing_sha = str(prepared.get("existing_sha", ""))
    if existing_sha:
        payload["sha"] = existing_sha
    result = _github_api(f"/repos/{repo}/contents/{encoded_path}", method="PUT", payload=payload, require_auth=True)
    if not isinstance(result, dict):
        raise RuntimeError("GITHUB_ERROR: invalid write response")
    commit = result.get("commit") if isinstance(result.get("commit"), dict) else {}
    written = result.get("content") if isinstance(result.get("content"), dict) else {}
    return {
        "status": "applied",
        "repo": repo,
        "branch": branch,
        "path": path,
        "commit_sha": commit.get("sha"),
        "content_sha": written.get("sha"),
        "applied": True,
    }


def fetch_github_file(
    repo: str,
    path: str,
    *,
    ref: str = "main",
    token: str | None = None,
    timeout: int = 30,
) -> GitHubTextFile:
    """Fetch one UTF-8 text file and its blob SHA from GitHub Contents API."""

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
    if not isinstance(data.get("sha"), str) or not data["sha"]:
        raise RuntimeError("GitHub response did not contain a blob SHA")

    try:
        raw = base64.b64decode(data["content"], validate=False)
        content = raw.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError("GitHub file is not valid UTF-8 text") from exc

    return GitHubTextFile(content=content, blob_sha=data["sha"])


def fetch_github_text(
    repo: str,
    path: str,
    *,
    ref: str = "main",
    token: str | None = None,
    timeout: int = 30,
) -> str:
    """Backward-compatible text-only wrapper."""
    return fetch_github_file(
        repo,
        path,
        ref=ref,
        token=token,
        timeout=timeout,
    ).content


def source_name(repo: str, path: str, *, ref: str = "main") -> str:
    return f"github:{repo}@{ref}:{path.lstrip('/')}"
