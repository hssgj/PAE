from __future__ import annotations

from dataclasses import dataclass
import base64
from email import policy
from email.parser import BytesParser

import gmail_source
import runtime_tools
from agent_loop import ToolCall, required_tool_call, run_agent_turn
from sessions import SessionStore
from tool_core import ToolContext


@dataclass
class FakeProvider:
    replies: list[str]
    name: str = "fake"

    def chat(self, messages: list[dict[str, str]]) -> str:
        if not self.replies:
            raise AssertionError("provider was called too many times")
        return self.replies.pop(0)


def context(tmp_path):
    store = SessionStore(tmp_path)
    session = store.open_or_create("mobile-test", system_prompt="test")
    return ToolContext(store=store, session=session)


def latest_message_result():
    return {
        "status": "ok",
        "fresh": True,
        "account": "user@example.com",
        "query": "in:inbox",
        "count": 1,
        "messages": [
            {
                "message_id": "m1",
                "thread_id": "t1",
                "subject": "Latest subject",
                "sender": "Sender <sender@example.com>",
                "sender_name": "Sender",
                "sender_email": "sender@example.com",
                "date_local": "07. 10. 2026 18:00:00 CEST",
                "snippet": "hello",
            }
        ],
    }


def test_czech_latest_gmail_request_is_forced_to_live_search() -> None:
    messages = [{"role": "user", "content": "Přečti čas posledního e-mailu v Gmailu."}]
    assert required_tool_call(messages) == ToolCall(
        name="gmail_search", arguments={"query": "in:inbox", "limit": 1}
    )


def test_latest_gmail_returns_tool_evidence_not_model_promise(tmp_path, monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        runtime_tools,
        "search_messages",
        lambda query, limit: calls.append((query, limit)) or latest_message_result(),
    )
    messages = [{"role": "user", "content": "Check Gmail and tell me the time of my latest email."}]
    answer = run_agent_turn(
        FakeProvider(["I will check Gmail. Please wait."]),
        messages,
        registry=runtime_tools.build_tool_registry(),
        context=context(tmp_path),
    )
    assert calls == [("in:inbox", 1)]
    assert "Latest subject" in answer and "m1" in answer
    assert "Please wait" not in answer


def test_read_that_email_uses_last_reported_message_id() -> None:
    messages = [
        {"role": "assistant", "content": "Předmět: Test\nMessage ID: abc_123\nThread ID: t1"},
        {"role": "user", "content": "Teď mi přečti tu zprávu."},
    ]
    assert required_tool_call(messages) == ToolCall(
        name="gmail_read", arguments={"message_id": "abc_123", "thread_id": ""}
    )


def test_capability_honesty_blocks_unsupported_external_claim(tmp_path) -> None:
    answer = run_agent_turn(
        FakeProvider(["I opened your calendar and refreshed it."]),
        [{"role": "user", "content": "Open and refresh my Calendar."}],
        registry=runtime_tools.build_tool_registry(),
        context=context(tmp_path),
    )
    assert "Nemám úspěšný výsledek externího nástroje" in answer


def test_gmail_read_returns_plain_text_content(monkeypatch) -> None:
    encoded = "SGVsbG8gZnJvbSByZWFsIG1haWw"
    monkeypatch.setattr(gmail_source, "verified_account", lambda: "user@example.com")
    monkeypatch.setattr(
        gmail_source,
        "_api",
        lambda *args, **kwargs: {
            "id": "m1",
            "threadId": "t1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Sender <sender@example.com>"},
                    {"name": "To", "value": "user@example.com"},
                    {"name": "Subject", "value": "PAE TEST"},
                    {"name": "Date", "value": "Wed, 07 Oct 2026 18:00:00 +0200"},
                ],
                "parts": [{"mimeType": "text/plain", "body": {"data": encoded}}],
            },
        },
    )
    result = gmail_source.read_message(message_id="m1")
    assert result["messages"][0]["content"] == "Hello from real mail"
    assert result["messages"][0]["subject"] == "PAE TEST"


def test_create_draft_builds_bounded_mime_and_does_not_send(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(gmail_source, "verified_account", lambda: "user@example.com")

    def fake_api(path, params=None, *, method="GET", payload=None):
        calls.append((path, method, payload))
        return {"id": "d1", "message": {"id": "dm1", "threadId": "t1"}}

    monkeypatch.setattr(gmail_source, "_api", fake_api)
    result = gmail_source.create_draft(
        to="person@example.com", cc="", subject="PAE TEST", body="PAE mobile Gmail test"
    )
    assert result["sent"] is False and result["confirmation_required"] is True
    assert calls[0][0:2] == ("/users/me/drafts", "POST")
    raw = calls[0][2]["message"]["raw"]
    decoded = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    message = BytesParser(policy=policy.default).parsebytes(decoded)
    assert message["To"] == "person@example.com"
    assert message["Subject"] == "PAE TEST"
    assert message.get_body(preferencelist=("plain",)).get_content().strip() == "PAE mobile Gmail test"


def test_draft_requires_separate_explicit_confirmation(tmp_path, monkeypatch) -> None:
    sent = []
    monkeypatch.setattr(
        runtime_tools,
        "create_draft",
        lambda **kwargs: {
            "status": "draft_created",
            "draft_id": "d1",
            "message_id": "dm1",
            "thread_id": "t1",
            "preview": {
                "to": kwargs["to"], "cc": kwargs["cc"],
                "subject": kwargs["subject"], "body": kwargs["body"],
            },
            "sent": False,
            "confirmation_required": True,
        },
    )
    monkeypatch.setattr(
        runtime_tools,
        "send_draft",
        lambda draft_id: sent.append(draft_id) or {
            "status": "sent", "draft_id": draft_id, "message_id": "sent1",
            "thread_id": "t1", "sent": True,
        },
    )
    ctx = context(tmp_path)
    registry = runtime_tools.build_tool_registry()
    draft = registry.execute(
        "gmail_create_draft",
        {"to": "person@example.com", "subject": "PAE TEST", "body": "PAE mobile Gmail test"},
        context=ctx,
    )
    assert draft["sent"] is False
    assert ctx.session.pending_actions["gmail_send"]["draft_id"] == "d1"

    vague = run_agent_turn(
        FakeProvider(['{"type":"tool_call","name":"gmail_send","arguments":{"draft_id":"d1"}}']),
        [{"role": "user", "content": "ok"}],
        registry=registry,
        context=ctx,
    )
    assert "nebyl odeslán" in vague
    assert sent == []

    confirmed = run_agent_turn(
        FakeProvider([]),
        [{"role": "user", "content": "Send it."}],
        registry=registry,
        context=ctx,
    )
    assert sent == ["d1"]
    assert "sent1" in confirmed
    assert "gmail_send" not in ctx.session.pending_actions


def test_pending_confirmation_survives_session_reload(tmp_path) -> None:
    ctx = context(tmp_path)
    ctx.session.pending_actions["gmail_send"] = {
        "draft_id": "d1", "preview": {"to": "person@example.com"}, "approved": False
    }
    ctx.store.save(ctx.session)
    loaded = ctx.store.load("mobile-test")
    assert loaded.pending_actions["gmail_send"]["draft_id"] == "d1"


def test_reply_search_is_live_and_uses_gmail_query(tmp_path, monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        runtime_tools,
        "search_messages",
        lambda query, limit: calls.append((query, limit)) or {
            "status": "ok", "fresh": True, "account": "user@example.com",
            "query": query, "count": 0, "messages": [],
        },
    )
    registry = runtime_tools.build_tool_registry()
    result = registry.execute(
        "gmail_search",
        {"query": 'subject:"PAE TEST" newer_than:1d', "limit": 10},
        context=context(tmp_path),
    )
    assert result["fresh"] is True
    assert calls == [('subject:"PAE TEST" newer_than:1d', 10)]
