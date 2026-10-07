from __future__ import annotations

import base64
import json
import os
from datetime import datetime
from email.utils import parseaddr, parsedate_to_datetime
from urllib import error, parse, request
from zoneinfo import ZoneInfo

from tool_core import ToolError


GMAIL_API = "https://gmail.googleapis.com/gmail/v1"
TOKEN_URL = "https://oauth2.googleapis.com/token"
_cached_access_token = ""


def _refresh_configured() -> bool:
    return all(
        os.getenv(name, "").strip()
        for name in (
            "PAE_GMAIL_CLIENT_ID",
            "PAE_GMAIL_CLIENT_SECRET",
            "PAE_GMAIL_REFRESH_TOKEN",
        )
    )


def get_access_token(*, force_refresh: bool = False) -> str:
    global _cached_access_token
    if _cached_access_token and not force_refresh:
        return _cached_access_token

    configured = os.getenv("PAE_GMAIL_ACCESS_TOKEN", "").strip()
    if configured and not force_refresh:
        _cached_access_token = configured
        return configured

    if not _refresh_configured():
        if configured:
            return configured
        raise ToolError(
            "Gmail authorization is missing. Configure PAE_GMAIL_ACCESS_TOKEN or "
            "PAE_GMAIL_CLIENT_ID, PAE_GMAIL_CLIENT_SECRET and PAE_GMAIL_REFRESH_TOKEN."
        )

    body = parse.urlencode(
        {
            "client_id": os.environ["PAE_GMAIL_CLIENT_ID"].strip(),
            "client_secret": os.environ["PAE_GMAIL_CLIENT_SECRET"].strip(),
            "refresh_token": os.environ["PAE_GMAIL_REFRESH_TOKEN"].strip(),
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    req = request.Request(
        TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            payload = json.load(response)
    except error.HTTPError as exc:
        raise ToolError(f"Gmail token refresh failed (HTTP {exc.code})") from exc
    except error.URLError as exc:
        raise ToolError(f"Gmail token refresh connection failed: {exc.reason}") from exc

    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise ToolError("Gmail token refresh returned no access token")
    _cached_access_token = token
    return token


def _api(path: str, params: list[tuple[str, str]] | None = None) -> dict[str, object]:
    query = "?" + parse.urlencode(params or []) if params else ""
    url = f"{GMAIL_API}{path}{query}"

    for attempt in range(2):
        token = get_access_token(force_refresh=attempt == 1)
        req = request.Request(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                payload = json.load(response)
            if not isinstance(payload, dict):
                raise ToolError("Gmail returned an invalid response")
            return payload
        except error.HTTPError as exc:
            if exc.code == 401 and attempt == 0 and _refresh_configured():
                continue
            raise ToolError(f"Gmail API failed (HTTP {exc.code})") from exc
        except error.URLError as exc:
            raise ToolError(f"Gmail connection failed: {exc.reason}") from exc

    raise ToolError("Gmail authorization failed after token refresh")


def verified_account() -> str:
    profile = _api("/users/me/profile")
    actual = str(profile.get("emailAddress", "")).strip().casefold()
    expected = os.getenv("PAE_GMAIL_ACCOUNT", "").strip().casefold()
    if not actual:
        raise ToolError("Gmail profile did not return an account address")
    if expected and actual != expected:
        raise ToolError("Authorized Gmail account does not match PAE_GMAIL_ACCOUNT")
    return actual


def _headers(message: dict[str, object]) -> dict[str, str]:
    payload = message.get("payload")
    if not isinstance(payload, dict):
        return {}
    items = payload.get("headers")
    if not isinstance(items, list):
        return {}
    result: dict[str, str] = {}
    for item in items:
        if isinstance(item, dict):
            name = item.get("name")
            value = item.get("value")
            if isinstance(name, str) and isinstance(value, str):
                result[name.casefold()] = value
    return result


def _decode_body(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    body = payload.get("body")
    if isinstance(body, dict) and isinstance(body.get("data"), str):
        raw = body["data"]
        raw += "=" * (-len(raw) % 4)
        try:
            return base64.urlsafe_b64decode(raw).decode("utf-8", errors="replace")
        except (ValueError, UnicodeError):
            return ""
    parts = payload.get("parts")
    if not isinstance(parts, list):
        return ""
    plain = [part for part in parts if isinstance(part, dict) and part.get("mimeType") == "text/plain"]
    for part in plain + parts:
        decoded = _decode_body(part)
        if decoded:
            return decoded
    return ""


def _metadata(message: dict[str, object]) -> dict[str, object]:
    headers = _headers(message)
    sender_name, sender_email = parseaddr(headers.get("from", ""))
    raw_date = headers.get("date", "")
    local_date = raw_date
    try:
        parsed = parsedate_to_datetime(raw_date)
        if parsed.tzinfo is None:
            parsed = parsed.astimezone()
        local_date = parsed.astimezone(ZoneInfo("Europe/Prague")).strftime(
            "%d. %m. %Y %H:%M:%S %Z"
        )
    except (TypeError, ValueError, OverflowError):
        pass
    return {
        "message_id": str(message.get("id", "")),
        "thread_id": str(message.get("threadId", "")),
        "subject": headers.get("subject", ""),
        "sender": headers.get("from", ""),
        "sender_name": sender_name,
        "sender_email": sender_email,
        "date": raw_date,
        "date_local": local_date,
    }


def list_messages(limit: int = 5) -> dict[str, object]:
    account = verified_account()
    payload = _api(
        "/users/me/messages",
        [("labelIds", "INBOX"), ("maxResults", str(max(1, min(limit, 10))))],
    )
    refs = payload.get("messages", [])
    messages: list[dict[str, object]] = []
    if isinstance(refs, list):
        for ref in refs:
            if not isinstance(ref, dict) or not ref.get("id"):
                continue
            item = _api(
                f"/users/me/messages/{parse.quote(str(ref['id']))}",
                [
                    ("format", "metadata"),
                    ("metadataHeaders", "From"),
                    ("metadataHeaders", "Subject"),
                    ("metadataHeaders", "Date"),
                ],
            )
            messages.append(_metadata(item))
    return {"status": "ok", "account": account, "count": len(messages), "messages": messages}


def read_message(message_id: str) -> dict[str, object]:
    account = verified_account()
    message = _api(
        f"/users/me/messages/{parse.quote(message_id, safe='')}",
        [("format", "full")],
    )
    result = _metadata(message)
    content = _decode_body(message.get("payload"))
    result.update(
        {
            "status": "ok",
            "account": account,
            "content": content[:50_000],
            "truncated": len(content) > 50_000,
        }
    )
    return result


def latest_message() -> dict[str, object]:
    listed = list_messages(1)
    messages = listed["messages"]
    if not isinstance(messages, list) or not messages:
        raise ToolError("Gmail inbox contains no messages")
    result = dict(messages[0])
    result.update({"status": "ok", "account": listed["account"]})
    return result
