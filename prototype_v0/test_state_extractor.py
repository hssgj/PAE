from pathlib import Path
from tempfile import TemporaryDirectory

from provider import Provider
from sessions import SessionStore
from state_extractor import (
    _extract_json_object,
    _normalize_state,
    extract_state,
)


class FakeSemanticProvider(Provider):
    name = "fake-semantic"

    def chat(self, messages: list[dict[str, str]]) -> str:
        assert "Source material is authoritative" in messages[0]["content"]
        assert "Door is locked" in messages[1]["content"]
        return """{
  "canon": ["The archive door is locked."],
  "characters": [{"name": "Nell", "facts": ["Present at the door."]}],
  "current_scene": {
    "location": "UNKNOWN",
    "situation": "The group is waiting at a locked archive door.",
    "present_characters": ["Nell"]
  },
  "important_facts": ["Door is locked"],
  "unknowns": ["Exact archive location"]
}"""


def test_extract_json_object_accepts_fenced_json() -> None:
    raw = """```json
{"canon": ["A"], "characters": [], "current_scene": {}, "important_facts": []}
```"""
    data = _extract_json_object(raw)
    assert data["canon"] == ["A"]


def test_normalize_state_preserves_unknown() -> None:
    state = _normalize_state(
        {
            "canon": ["Known fact"],
            "characters": [{"name": "Nell", "facts": ["Present"]}],
            "current_scene": {"situation": "Waiting"},
            "important_facts": ["Door is locked"],
        }
    )

    assert state["current_scene"]["location"] == "UNKNOWN"
    assert state["current_scene"]["situation"] == "Waiting"
    assert state["canon"] == ["Known fact"]
    assert state["characters"][0]["name"] == "Nell"
    assert state["unknowns"] == []


def test_extract_state_persists_across_session_reload() -> None:
    provider = FakeSemanticProvider()
    sources = [
        {
            "name": "sample.md",
            "sha256": "abc123",
            "content": "Nell waits at the archive door. Door is locked.",
        }
    ]

    state = extract_state(provider, sources)

    assert state["current_scene"]["location"] == "UNKNOWN"
    assert state["characters"][0]["name"] == "Nell"
    assert state["important_facts"] == ["Door is locked"]

    with TemporaryDirectory() as tmp:
        store = SessionStore(Path(tmp))
        session = store.open_or_create("day2", system_prompt="test")
        store.set_derived_state(session, state)

        reopened = store.load("day2")
        assert reopened.derived_state == state
        assert reopened.derived_state["current_scene"]["location"] == "UNKNOWN"
