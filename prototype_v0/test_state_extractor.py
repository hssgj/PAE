from state_extractor import _extract_json_object, _normalize_state


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
