from __future__ import annotations

import base64
import json
import os
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr, parsedate_to_datetime
from html.parser import HTMLParser
from urllib import error, parse, request
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tool_core import ToolError


GMAIL_API = "https://gmail.googleapis.com/gmail/v1"
TOKEN_URL = "https://oauth2.googleapis.com/token"
MAX_BODY_CHARS = 50_000
_cached_access_token = ""


class _PlainTextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def _html_to_text(value: str) -> str:
    parser = _PlainTextHTMLParser()
    parser.feed(value)
    return "\n".join(parser.parts)


def refresh_configured() -> bool:
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
    if not refresh_configured():
        if configured:
            return configured
        raise ToolError(
            "AUTH_REQUIRED: configure PAE_GMAIL_ACCESS_TOKEN, or the three refresh "
            "variables PAE_GMAIL_CLIENT_ID, PAE_GMAIL_CLIENT_SECRET and "
            "PAE_GMAIL_REFRESH_TOKEN."
        )
    form = parse.urlencode(
        {
            "client_id": os.environ["PAE_GMAIL_CLIENT_ID"].strip(),
            "client_secret": os.environ["PAE_GMAIL_CLIENT_SECRET"].strip(),
            "refresh_token": os.environ["PAE_GMAIL_REFRESH_TOKEN"].strip(),
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    req = request.Request(
        TOKEN_URL,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            payload = json.load(response)
    except error.HTTPError as exc:
        raise ToolError(f"AUTH_REQUIRED: Gmail token refresh failed (HTTP {exc.code})") from exc
    except error.URLError as exc:
        raise ToolError(f"NETWORK_UNAVAILABLE: Gmail token refresh failed: {exc.reason}") from exc
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise ToolError("AUTH_REQUIRED: Gmail token refresh returned no access token")
    _cached_access_token = token
    return token


def _api(
    path: str,
    params: list[tuple[str, str]] | None = None,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    query = "?" + parse.urlencode(params or []) if params else ""
    url = f"{GMAIL_API}{path}{query}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    for attempt in range(2):
        token = get_access_token(force_refresh=attempt == 1)
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=30) as response:
                raw = response.read()
            result = json.loads(raw) if raw else {}
            if not isinstance(result, dict):
                raise ToolError("GMAIL_ERROR: Gmail returned an invalid response")
            return result
        except error.HTTPError as exc:
            if exc.code == 401 and attempt == 0 and refresh_configured():
                continue
            prefix = "AUTH_REQUIRED" if exc.code == 401 else "AUTH_SCOPE_REQUIRED" if exc.code == 403 else "GMAIL_ERROR"
            raise ToolError(f"{prefix}: Gmail API failed (HTTP {exc.code})") from exc
        except error.URLError as exc:
            raise ToolError(f"NETWORK_UNAVAILABLE: Gmail cannot be reached: {exc.reason}") from exc
    raise ToolError("AUTH_REQUIRED: Gmail authorization failed after token refresh")


def verified_account() -> str:
    profile = _api("/users/me/profile")
    actual = str(profile.get("emailAddress", "")).strip().casefold()
    expected = os.getenv("PAE_GMAIL_ACCOUNT", "").strip().casefold()
    if not actual:
        raise ToolError("AUTH_REQUIRED: Gmail profile returned no account address")
    if expected and actual != expected:
        raise ToolError("AUTH_REQUIRED: Gmail account does not match PAE_GMAIL_ACCOUNT")
    return actual


def _headers(message: dict[str, object]) -> dict[str, str]:
    payload = message.get("payload")
    if not isinstance(payload, dict) or not isinstance(payload.get("headers"), list):
        return {}
    result: dict[str, str] = {}
    for item in payload["headers"]:
        if isinstance(item, dict):
            name, value = item.get("name"), item.get("value")
            if isinstance(name, str) and isinstance(value, str):
                result[name.casefold()] = value
    return result


def _decode_data(value: str) -> str:
    padded = value + "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")
    except (ValueError, UnicodeError):
        return ""


def _decode_body(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    body = payload.get("body")
    if isinstance(body, dict) and isinstance(body.get("data"), str):
        decoded = _decode_data(body["data"])
        return _html_to_text(decoded) if payload.get("mimeType") == "text/html" else decoded
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
        local_date = parsed.astimezone(ZoneInfo("Europe/Prague")).strftime("%d. %m. %Y %H:%M:%S %Z")
    except (TypeError, ValueError, OverflowError, ZoneInfoNotFoundError):
        pass
    return {
        "message_id": str(message.get("id", "")),
        "thread_id": str(message.get("threadId", "")),
        "sender": headers.get("from", ""),
        "sender_name": sender_name,
        "sender_email": sender_email,
        "to": headers.get("to", ""),
        "cc": headers.get("cc", ""),
        "subject": headers.get("subject", ""),
        "date": raw_date,
        "date_local": local_date,
        "rfc_message_id": headers.get("message-id", ""),
        "references": headers.get("references", ""),
        "snippet": str(message.get("snippet", ""))[:300],
    }


def search_messages(query: str = "in:inbox", limit: int = 5) -> dict[str, object]:
    account = verified_account()
    bounded_limit = max(1, min(limit, 10))
    refs = _api("/users/me/messages", [("q", query or "in:inbox"), ("maxResults", str(bounded_limit))]).get("messages", [])
    messages: list[dict[str, object]] = []
    if isinstance(refs, list):
        for ref in refs:
            if not isinstance(ref, dict) or not ref.get("id"):
                continue
            item = _api(
                f"/users/me/messages/{parse.quote(str(ref['id']), safe='')}",
                [("format", "metadata"), ("metadataHeaders", "From"), ("metadataHeaders", "To"),
                 ("metadataHeaders", "Cc"), ("metadataHeaders", "Subject"), ("metadataHeaders", "Date"),
                 ("metadataHeaders", "Message-ID"), ("metadataHeaders", "References")],
            )
            messages.append(_metadata(item))
    return {"status": "ok", "fresh": True, "account": account, "query": query or "in:inbox", "count": len(messages), "messages": messages}


def read_message(*, message_id: str = "", thread_id: str = "") -> dict[str, object]:
    account = verified_account()
    if bool(message_id) == bool(thread_id):
        raise ToolError("GMAIL_ARGUMENT_ERROR: provide exactly one of message_id or thread_id")
    if message_id:
        raw_messages = [_api(f"/users/me/messages/{parse.quote(message_id, safe='')}", [("format", "full")])]
    else:
        thread = _api(f"/users/me/threads/{parse.quote(thread_id, safe='')}", [("format", "full")])
        raw = thread.get("messages", [])
        raw_messages = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
    messages: list[dict[str, object]] = []
    for item in raw_messages:
        result = _metadata(item)
        content = _decode_body(item.get("payload"))
        result.update({"content": content[:MAX_BODY_CHARS], "truncated": len(content) > MAX_BODY_CHARS})
        messages.append(result)
    return {"status": "ok", "fresh": True, "account": account, "count": len(messages), "messages": messages}


def _validated_addresses(raw: str, field: str) -> list[str]:
    if "\r" in raw or "\n" in raw:
        raise ToolError(f"GMAIL_ARGUMENT_ERROR: {field} contains an invalid newline")
    addresses = [address for _, address in getaddresses([raw]) if "@" in address]
    if not addresses:
        raise ToolError(f"GMAIL_ARGUMENT_ERROR: {field} contains no valid email address")
    return addresses


def create_draft(
    *, to: str, cc: str, subject: str, body: str,
    thread_id: str = "", reply_to_message_id: str = "",
) -> dict[str, object]:
    account = verified_account()
    _validated_addresses(to, "to")
    if cc:
        _validated_addresses(cc, "cc")
    if "\n" in subject or "\r" in subject:
        raise ToolError("GMAIL_ARGUMENT_ERROR: subject contains an invalid newline")
    in_reply_to = ""
    references = ""
    resolved_thread = thread_id
    if reply_to_message_id:
        original = _api(f"/users/me/messages/{parse.quote(reply_to_message_id, safe='')}", [("format", "metadata")])
        original_meta = _metadata(original)
        resolved_thread = resolved_thread or str(original_meta.get("thread_id", ""))
        in_reply_to = str(original_meta.get("rfc_message_id", ""))
        references = " ".join(value for value in (str(original_meta.get("references", "")), in_reply_to) if value)
    message = EmailMessage()
    message["To"] = to
    if cc:
        message["Cc"] = cc
    message["Subject"] = subject
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
    if references:
        message["References"] = references
    message.set_content(body)
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii").rstrip("=")
    gmail_message: dict[str, object] = {"raw": encoded}
    if resolved_thread:
        gmail_message["threadId"] = resolved_thread
    created = _api("/users/me/drafts", method="POST", payload={"message": gmail_message})
    draft_id = str(created.get("id", ""))
    message_data = created.get("message")
    created_message_id = ""
    created_thread_id = resolved_thread
    if isinstance(message_data, dict):
        created_message_id = str(message_data.get("id", ""))
        created_thread_id = str(message_data.get("threadId", created_thread_id))
    if not draft_id:
        raise ToolError("GMAIL_ERROR: Gmail created no draft id")
    return {
        "status": "draft_created", "account": account, "draft_id": draft_id,
        "message_id": created_message_id, "thread_id": created_thread_id,
        "preview": {"to": to, "cc": cc, "subject": subject, "body": body},
        "sent": False, "confirmation_required": True,
    }


def send_draft(draft_id: str) -> dict[str, object]:
    account = verified_account()
    result = _api("/users/me/drafts/send", method="POST", payload={"id": draft_id})
    message_id = str(result.get("id", ""))
    if not message_id:
        raise ToolError("GMAIL_ERROR: Gmail returned no sent message id; message was NOT sent")
    return {
        "status": "sent", "account": account, "draft_id": draft_id,
        "message_id": message_id, "thread_id": str(result.get("threadId", "")), "sent": True,
    }
