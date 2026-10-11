"""Unit tests for opt-in PAE input + timing utilities; no Qwen needed."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from paste_input import read_user_message
from perf_log import TimedProvider, summarize


class FakeProvider:
    name = "fake"

    def chat(self, messages):
        return "mock answer"


def test_single_line_unchanged():
    with patch("builtins.input", return_value="hello"):
        assert read_user_message() == "hello"


def test_multiline_is_one_message():
    with patch(
        "builtins.input",
        side_effect=[
            "/paste",
            "Repo: hssgj/frostfire_concepts",
            '1. "Cook Guide/Clouds/01_RECIPE.md"',
            "Porovnej těsto.",
            "/end",
        ],
    ):
        message = read_user_message()
    assert message.count("\n") == 2
    assert "Porovnej těsto." in message
    assert message.startswith("Repo:")


def test_abort_on_eof_never_sends_partial():
    with patch("builtins.input", side_effect=["/paste", "not finished", EOFError]):
        assert read_user_message() == ""


def test_profiler_stores_only_metadata():
    with TemporaryDirectory() as temp:
        log = Path(temp) / "performance.jsonl"
        provider = TimedProvider(FakeProvider(), log)
        assert provider.name == "fake"
        assert provider.chat([{"role": "user", "content": "private text"}]) == "mock answer"
        records = [json.loads(line) for line in log.read_text().splitlines()]
        assert len(records) == 1
        assert records[0]["message_count"] == 1
        assert records[0]["input_characters"] == 12
        assert "private text" not in log.read_text()
        assert "Posledních 1" in summarize(log)
