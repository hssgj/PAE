"""One-time conservative routing hotfix for the PAE Mobile agent loop.

Only edits prototype_v0/agent_loop.py after verifying exact anchors and syntax.
Does not alter Memory Guard, app.py, provider.py, Gmail or GitHub write flows.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "prototype_v0" / "agent_loop.py"
BACKUPS = ROOT / "pae_backups"
TAG = "PAE_MOBILE_ROUTING_FIX_V1"


def replace_one(content: str, old: str, new: str, label: str) -> str:
    found = content.count(old)
    if found != 1:
        raise ValueError(f"{label}: expected exactly one anchor, found {found}")
    return content.replace(old, new, 1)


def update(original: str) -> str:
    if TAG in original:
        raise ValueError("routing fix already installed")
    if "_pending_send_call(messages, context)" not in original:
        raise ValueError("this is not the expected PAE Mobile agent loop; no changes")

    content = original
    content = replace_one(
        content,
        "from tool_core import ToolContext, ToolRegistry\n",
        "from tool_core import ToolContext, ToolRegistry\n"
        "from github_routing import extract_github_read_scope\n",
        "import",
    )
    content = replace_one(
        content,
        """ACTIVE PROJECT CONTEXT
- Primary repository: hssgj/PAE
- The authoritative current Discipline OS state is:
  discipline_os/current_state.json
- When the user asks for the current PAE focus, priority, milestone, next action,
  or asks you to check the current GitHub state, ALWAYS use github_read on that
  file before answering. Persisted copies may be stale.
- Do not claim you checked GitHub unless you actually request github_read.""",
        """GITHUB SCOPE
- Read only the repository and path relevant to the current user request.
- Only access PAE Discipline OS state for an explicit PAE status/focus question.
- Never read unrelated DOS state after a failed read or as fallback.
- A missing file is a limitation, not permission to switch repositories.
- Do not claim a GitHub read happened unless a tool executed.""",
        "protocol prompt",
    )
    content = replace_one(
        content,
        '{{"type":"tool_call","name":"github_read","arguments":{{"repo":"hssgj/PAE","path":"discipline_os/current_state.json","ref":"main"}}}}',
        '{{"type":"tool_call","name":"github_read","arguments":{{"repo":"owner/repository","path":"README.md","ref":"main"}}}}',
        "protocol example",
    )

    content = replace_one(
        content,
        "def required_tool_call(messages: list[dict[str, str]]) -> ToolCall | None:\n",
        '''def is_pae_state_request(messages: list[dict[str, str]]) -> bool:
    user_text = _last_user_text(messages)
    tokens = _tokens(user_text)
    if "discipline_os/current_state.json" in user_text and (
        "hssgj/PAE" in user_text or "hssgj/" not in user_text
    ):
        return True
    has_pae = bool(set(tokens) & {"pae", "dos", "discipline"})
    has_state = _approx_any(tokens, {
        "focus", "stav", "state", "priority", "priorita", "milestone",
        "next", "action", "dalsi", "aktualni", "current",
    })
    return has_pae and has_state


def is_dos_dump(content: str) -> bool:
    return (
        "Cesta: discipline_os/current_state.json" in content
        or ('"current_focus"' in content and '"open_external_items"' in content)
    )


def required_tool_call(messages: list[dict[str, str]]) -> ToolCall | None:
''',
        "PAE status discriminator",
    )
    content = replace_one(
        content,
        "    if explicit_path:\n",
        "    if explicit_path and is_pae_state_request(messages):\n",
        "explicit state path",
    )
    content = replace_one(
        content,
        "    if mentions_freshness and mentions_state:\n",
        "    if mentions_freshness and mentions_state and is_pae_state_request(messages):\n",
        "freshness state routing",
    )

    content = replace_one(
        content,
        "    working = list(messages)\n    working.insert(\n",
        '''    # PAE_MOBILE_ROUTING_FIX_V1
    explicit_scope = extract_github_read_scope(_last_user_text(messages))
    if explicit_scope is not None and user_forbids_tools(messages):
        return "Rozpor: požaduješ GitHub čtení a současně zakazuješ nástroje."
    if explicit_scope is not None:
        current_user = next(
            message for message in reversed(messages) if message.get("role") == "user"
        )
        working = [messages[0], current_user]
    else:
        working = list(messages)
        if not is_pae_state_request(messages):
            working = [
                msg for msg in working
                if not (
                    msg.get("role") == "system"
                    and msg.get("content", "").startswith("PERSISTENT SOURCE MATERIAL")
                    and "Path: discipline_os/current_state.json" in msg.get("content", "")
                )
                and not (
                    msg.get("role") == "assistant"
                    and is_dos_dump(msg.get("content", ""))
                )
            ]
    working.insert(
''',
        "working messages",
    )
    content = replace_one(
        content,
        "    required = confirmation_call or required_tool_call(messages)\n",
        "    required = confirmation_call or (\n"
        "        None if explicit_scope is not None else required_tool_call(messages)\n"
        "    )\n",
        "required tool routing",
    )
    content = replace_one(
        content,
        "    last_tool_result: dict[str, Any] | None = None\n",
        '''    last_tool_result: dict[str, Any] | None = None

    # Exact requested reads precede model inference; never let the model
    # rewrite a path, add "1. ", or switch to an unrelated repository.
    if explicit_scope is not None:
        failures = []
        for path in explicit_scope.paths:
            call = ToolCall(
                name="github_read",
                arguments={
                    "repo": explicit_scope.repo,
                    "path": path,
                    "ref": explicit_scope.ref,
                },
            )
            tool_calls += 1
            result = _append_tool_attempt(
                working, call, registry=registry, context=context
            )
            if result is None:
                failures.append(path)
            else:
                successful_tools.append("github_read")
                last_tool_action, last_tool_result = call, result
        if failures:
            return (
                "Nepodařilo se načíst požadované soubory: "
                + "; ".join(failures)
                + ". Jiné soubory nehledám."
            )
        working.append({
            "role": "system",
            "content": (
                "All exact requested GitHub files are already loaded above. "
                "Do not call tools again. Compare ONLY those files and respond "
                "briefly in the user's language. Do not dump raw tool results, "
                "or output unrelated Discipline OS state."
            ),
        })
''',
        "exact reads",
    )
    content = replace_one(
        content,
        "    forbidden_attempts = 0\n",
        "    forbidden_attempts = 0\n"
        "    scoped_reprompts = 0\n"
        "    dos_reprompts = 0\n",
        "repair counters",
    )
    content = replace_one(
        content,
        "        if isinstance(action, FinalAnswer):\n",
        '''        if isinstance(action, FinalAnswer):
            if not is_pae_state_request(messages) and is_dos_dump(action.content):
                return (
                    "Odpověď zablokována: obsahovala nesouvisející stav DOS "
                    "místo odpovědi na aktuální otázku."
                )
''',
        "final reply gate",
    )
    content = replace_one(
        content,
        "        if forbid_optional_tools:\n            forbidden_attempts += 1\n",
        '''        if explicit_scope is not None:
            print("[tool guard] extra tool blocked during exact-file request")
            if scoped_reprompts >= 1:
                return "Model žádal další nástroj, ale čtení zůstalo omezené na zadané soubory."
            scoped_reprompts += 1
            working.append({
                "role": "system",
                "content": "No more tools. Summarize the two fetched files now.",
            })
            continue

        if (
            action.name == "github_read"
            and str(action.arguments.get("path", "")).lstrip("/")
            == "discipline_os/current_state.json"
            and not is_pae_state_request(messages)
        ):
            print("[tool guard] unrelated DOS read blocked")
            if dos_reprompts >= 1:
                return "Model žádal nesouvisející DOS stav; další čtení zablokováno."
            dos_reprompts += 1
            working.append({
                "role": "system",
                "content": (
                    "Do not access PAE/DOS state unless the user requested it. "
                    "Answer from the requested subject, or say what is missing."
                ),
            })
            continue

        if forbid_optional_tools:
            forbidden_attempts += 1
''',
        "model tool gate",
    )
    compile(content, str(TARGET), "exec")
    return content


def main() -> int:
    if not (ROOT / "prototype_v0" / "github_routing.py").exists():
        print("STOP: github_routing.py missing; no changes", file=sys.stderr)
        return 2
    original = TARGET.read_text(encoding="utf-8")
    try:
        updated = update(original)
    except ValueError as exc:
        print(f"STOP: {exc}; no changes", file=sys.stderr)
        return 2
    BACKUPS.mkdir(exist_ok=True)
    backup = BACKUPS / (
        "agent_loop_before_mobile_routing_"
        + datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(updated, encoding="utf-8")
    print("OK: PAE Mobile routing hotfix installed")
    print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
