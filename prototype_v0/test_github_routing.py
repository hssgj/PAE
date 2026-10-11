"""Regression checks for wrong-repository fallbacks and copied list numbering."""

from dataclasses import dataclass, field

from agent_loop import run_agent_turn
from github_routing import extract_github_read_scope


USER_REQUEST = (
    'PAE, použij "github_read" pro 2 soubory z "hssgj/frostfire_concepts", branch "main":\n'
    '1. "Matthaels Cook Guide - Kitchen of Frost and Flame/Eryns_Dar_Na_Hrane_Leta/01_RECIPE.md"\n'
    '2. "Matthaels Cook Guide - Kitchen of Frost and Flame/Frostfire_Souffle_Clouds_Blackberry_Shrapnel/01_RECIPE.md"\n'
    'Porovnej technologii těsta. Odpověz stručně česky.'
)


@dataclass
class FakeSession:
    session_id: str = "test"
    sources: list = field(default_factory=list)
    messages: list = field(default_factory=list)
    pending_actions: dict = field(default_factory=dict)


@dataclass
class FakeContext:
    session: FakeSession = field(default_factory=FakeSession)


class FakeRegistry:
    def __init__(self, fail_path=None):
        self.calls = []
        self.fail_path = fail_path

    def specs(self):
        return [{"name": "github_read", "arguments": {"type": "object"}}]

    def execute(self, name, arguments, *, context):
        assert name == "github_read"
        self.calls.append(dict(arguments))
        if arguments["path"] == self.fail_path:
            raise RuntimeError("GitHub 404")
        return {"content": "Těsto: bílky; odpočinek; pečení.", "status": "loaded"}


class FakeProvider:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0
        self.seen_messages = []

    def chat(self, messages):
        self.seen_messages.append(messages)
        self.calls += 1
        return self.replies.pop(0)


def test_exact_paths_are_parsed_without_list_numbers_or_quotes():
    scope = extract_github_read_scope(USER_REQUEST)
    assert scope is not None
    assert scope.repo == "hssgj/frostfire_concepts"
    assert scope.ref == "main"
    assert len(scope.paths) == 2
    assert all(path.endswith("/01_RECIPE.md") for path in scope.paths)
    assert all(not path.startswith(("1.", "2.", '"')) for path in scope.paths)


def test_recipe_task_reads_only_two_files_and_never_dos_state():
    registry = FakeRegistry()
    provider = FakeProvider(["Hotové porovnání těsta."])
    result = run_agent_turn(
        provider,
        [
            {"role": "system", "content": "You are PAE."},
            {"role": "system", "content": "PERSISTENT SOURCE MATERIAL\nold DOS dump"},
            {"role": "assistant", "content": '"current_focus" "open_external_items"'},
            {"role": "user", "content": USER_REQUEST},
        ],
        registry=registry,
        context=FakeContext(),
    )
    assert result == "Hotové porovnání těsta."
    assert len(registry.calls) == 2
    assert all(call["repo"] == "hssgj/frostfire_concepts" for call in registry.calls)
    assert all("discipline_os" not in call["path"] for call in registry.calls)
    assert provider.calls == 1
    assert "old DOS dump" not in str(provider.seen_messages[0])


def test_404_reports_failure_without_fallback_or_model_call():
    scope = extract_github_read_scope(USER_REQUEST)
    registry = FakeRegistry(fail_path=scope.paths[0])
    provider = FakeProvider(["should not be called"])
    result = run_agent_turn(
        provider,
        [
            {"role": "system", "content": "You are PAE"},
            {"role": "user", "content": USER_REQUEST},
        ],
        registry=registry,
        context=FakeContext(),
    )
    assert "Nepodařilo se" in result
    assert len(registry.calls) == 2
    assert provider.calls == 0


def test_hallucinated_dos_call_is_blocked_and_reprompted():
    provider = FakeProvider([
        '{"type":"tool_call","name":"github_read","arguments":'
        '{"repo":"hssgj/PAE","path":"discipline_os/current_state.json","ref":"main"}}',
        "Srovnání těsta hotovo.",
    ])
    registry = FakeRegistry()
    result = run_agent_turn(
        provider,
        [
            {"role": "system", "content": "You are PAE"},
            {"role": "user", "content": USER_REQUEST},
        ],
        registry=registry,
        context=FakeContext(),
    )
    assert result == "Srovnání těsta hotovo."
    assert len(registry.calls) == 2
    assert provider.calls == 2


def test_dos_dump_in_final_is_blocked():
    registry = FakeRegistry()
    provider = FakeProvider(['Repo: hssgj/PAE\nCesta: discipline_os/current_state.json'])
    result = run_agent_turn(
        provider,
        [
            {"role": "system", "content": "You are PAE"},
            {"role": "user", "content": USER_REQUEST},
        ],
        registry=registry,
        context=FakeContext(),
    )
    assert "zablokována" in result


def test_regular_non_scoped_question_unchanged():
    assert extract_github_read_scope("Ahoj, co je PAE?") is None


def test_unrelated_current_status_does_not_force_pae_state():
    from agent_loop import required_tool_call
    messages = [
        {"role": "user", "content": "Zjisti aktuální stav jiného GitHub repozitáře."}
    ]
    assert required_tool_call(messages) is None


def test_unrelated_dos_read_is_blocked_even_without_exact_paths():
    provider = FakeProvider([
        '{"type":"tool_call","name":"github_read","arguments":'
        '{"repo":"hssgj/PAE","path":"discipline_os/current_state.json","ref":"main"}}',
        "Nemám podklady pro odpověď.",
    ])
    registry = FakeRegistry()
    result = run_agent_turn(
        provider,
        [
            {"role": "system", "content": "You are PAE"},
            {"role": "user", "content": "Vysvětli prosím kvásek."},
        ],
        registry=registry,
        context=FakeContext(),
    )
    assert result == "Nemám podklady pro odpověď."
    assert registry.calls == []


def test_unrelated_dos_final_dump_is_suppressed():
    provider = FakeProvider([
        'Repo: hssgj/PAE\nCesta: discipline_os/current_state.json',
    ])
    result = run_agent_turn(
        provider,
        [
            {"role": "system", "content": "You are PAE"},
            {"role": "user", "content": "Co je to mouka?"},
        ],
        registry=FakeRegistry(),
        context=FakeContext(),
    )
    assert "zablokována" in result


def test_genuine_pae_status_can_still_read_authoritative_state():
    from agent_loop import required_tool_call
    messages = [
        {"role": "user", "content": "Jaký je aktuální stav PAE?"}
    ]
    action = required_tool_call(messages)
    assert action is not None
    assert action.arguments["repo"] == "hssgj/PAE"
    assert action.arguments["path"] == "discipline_os/current_state.json"


def test_unrelated_cached_dos_source_and_history_are_not_injected():
    provider = FakeProvider(["Odpověď k mouce."])
    old_snapshot = (
        "PERSISTENT SOURCE MATERIAL\n"
        "Repository: hssgj/PAE\n"
        "Path: discipline_os/current_state.json\n"
        '{"current_focus": {}, "open_external_items": []}'
    )
    result = run_agent_turn(
        provider,
        [
            {"role": "system", "content": "You are PAE"},
            {"role": "system", "content": old_snapshot},
            {"role": "assistant", "content": old_snapshot},
            {"role": "user", "content": "Proč kynuté těsto roste?"},
        ],
        registry=FakeRegistry(),
        context=FakeContext(),
    )
    assert result == "Odpověď k mouce."
    assert old_snapshot not in [m.get("content") for m in provider.seen_messages[0]]
