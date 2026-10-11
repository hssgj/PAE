"""Checks for terminal animation, cleanup and the provider boundary."""

import io
import time

import pytest

from busy_indicator import BusyProvider, LABEL, busy_indicator


class FakeTerminal(io.StringIO):
    def isatty(self) -> bool:
        return True


def test_tty_spinner_animates_and_clears_on_success() -> None:
    stream = FakeTerminal()
    with busy_indicator(stream=stream, interval=0.005):
        time.sleep(0.035)
    output = stream.getvalue()
    assert LABEL in output
    assert "|" in output and "/" in output
    assert output.endswith("\r\033[2K")


def test_tty_spinner_clears_on_failure() -> None:
    stream = FakeTerminal()
    with pytest.raises(RuntimeError, match="failed"):
        with busy_indicator(stream=stream, interval=0.005):
            raise RuntimeError("failed")
    assert stream.getvalue().endswith("\r\033[2K")


def test_non_tty_prints_single_plain_status() -> None:
    stream = io.StringIO()
    with busy_indicator(stream=stream, interval=0.005):
        pass
    assert stream.getvalue() == f"{LABEL}...\n"


def test_busy_provider_preserves_name_and_reply(capsys) -> None:
    class FakeProvider:
        name = "fake"

        def chat(self, messages):
            return messages[-1]["content"].upper()

    provider = BusyProvider(FakeProvider())
    assert provider.name == "fake"
    assert provider.chat([{"role": "user", "content": "hello"}]) == "HELLO"
    assert LABEL in capsys.readouterr().out
