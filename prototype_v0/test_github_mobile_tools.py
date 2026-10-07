from __future__ import annotations

from dataclasses import dataclass

import github_source
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
    session = store.open_or_create("github-mobile-test", system_prompt="test")
    return ToolContext(store=store, session=session)


def test_parse_github_root_file_and_tree_urls() -> None:
    root = github_source.parse_github_target("https://github.com/hssgj/frostfire_concepts")
    assert (root.repo, root.ref, root.path, root.kind) == (
        "hssgj/frostfire_concepts", "main", "", "repo"
    )
    file = github_source.parse_github_target(
        "https://github.com/hssgj/PAE/blob/main/discipline_os/current_state.json"
    )
    assert (file.ref, file.path, file.kind) == (
        "main", "discipline_os/current_state.json", "file"
    )
    tree = github_source.parse_github_target(
        "https://github.com/hssgj/PAE/tree/main/prototype_v0"
    )
    assert (tree.ref, tree.path, tree.kind) == ("main", "prototype_v0", "directory")


def test_repo_root_request_searches_instead_of_reading_fake_file() -> None:
    call = required_tool_call(
        [{
            "role": "user",
            "content": "Find the Matthael chapter in https://github.com/hssgj/frostfire_concepts",
        }]
    )
    assert call == ToolCall(
        name="github_search",
        arguments={
            "repo": "hssgj/frostfire_concepts", "query": "matthael",
            "ref": "main", "limit": 10,
        },
    )


def test_exact_file_url_routes_to_github_read() -> None:
    call = required_tool_call(
        [{
            "role": "user",
            "content": "Read https://github.com/hssgj/PAE/blob/main/discipline_os/current_state.json",
        }]
    )
    assert call == ToolCall(
        name="github_read",
        arguments={
            "repo": "hssgj/PAE", "path": "discipline_os/current_state.json", "ref": "main"
        },
    )


def test_github_list_is_bounded(monkeypatch) -> None:
    monkeypatch.setattr(
        github_source,
        "_github_api",
        lambda *args, **kwargs: [
            {"name": f"f{i}.md", "path": f"docs/f{i}.md", "type": "file", "size": i, "sha": str(i)}
            for i in range(5)
        ],
    )
    result = github_source.list_github_path("hssgj/PAE", "docs", limit=2)
    assert result["count"] == 2 and result["truncated"] is True


def test_github_search_fallback_stays_inside_one_repo(monkeypatch) -> None:
    monkeypatch.setattr(github_source, "_token", lambda: "")
    monkeypatch.setattr(
        github_source,
        "_github_api",
        lambda path, **kwargs: {
            "tree": [
                {"type": "blob", "path": "stories/MATTHAEL_CHAPTER.md", "sha": "abc"},
                {"type": "blob", "path": "README.md", "sha": "def"},
            ]
        },
    )
    result = github_source.search_github("hssgj/frostfire_concepts", "Matthael", limit=5)
    assert result["results"][0]["path"] == "stories/MATTHAEL_CHAPTER.md"
    assert result["authenticated"] is False


def test_github_write_requires_separate_confirmation(tmp_path, monkeypatch) -> None:
    applied = []
    monkeypatch.setattr(
        runtime_tools,
        "prepare_github_write",
        lambda repo, path, content, branch: {
            "status": "prepared", "operation": "create", "repo": repo,
            "branch": branch, "path": path, "existing_sha": "", "content": content,
            "diff": "+hello\n", "diff_truncated": False,
            "confirmation_required": True, "applied": False,
        },
    )
    monkeypatch.setattr(
        runtime_tools,
        "apply_github_write",
        lambda prepared: applied.append(prepared["path"]) or {
            "status": "applied", "repo": prepared["repo"], "branch": prepared["branch"],
            "path": prepared["path"], "commit_sha": "commit1", "content_sha": "blob1",
            "applied": True,
        },
    )
    ctx = context(tmp_path)
    registry = runtime_tools.build_tool_registry()
    prepared = registry.execute(
        "github_prepare_write",
        {"repo": "hssgj/PAE", "path": "pae-mobile-test.txt", "content": "hello", "branch": "main"},
        context=ctx,
    )
    assert prepared["applied"] is False

    vague = run_agent_turn(
        FakeProvider(['{"type":"tool_call","name":"github_apply_write","arguments":{}}']),
        [{"role": "user", "content": "ok"}],
        registry=registry,
        context=ctx,
    )
    assert "nebyla zapsána" in vague and applied == []

    confirmed = run_agent_turn(
        FakeProvider([]),
        [{"role": "user", "content": "Proveď zápis."}],
        registry=registry,
        context=ctx,
    )
    assert applied == ["pae-mobile-test.txt"]
    assert "commit1" in confirmed
    assert "github_write" not in ctx.session.pending_actions
