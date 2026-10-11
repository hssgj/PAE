"""Opt-in PAE Mobile source excerpt installation.

Requires the preceding PAE_MOBILE_ROUTING_FIX_V1 hotfix. Only modifies
prototype_v0/agent_loop.py after validating a unique anchor; backs it up.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "prototype_v0" / "agent_loop.py"
MARKER = "# PAE_FOCUSED_RECIPE_SOURCE_V1"


def main() -> int:
    if not (TARGET.parent / "source_focus.py").is_file():
        print("STOP: source_focus.py missing")
        return 2
    original = TARGET.read_text(encoding="utf-8")
    if MARKER in original:
        print("ALREADY INSTALLED")
        return 0
    if "# PAE_MOBILE_ROUTING_FIX_V1" not in original:
        print("STOP: mobile routing hotfix not installed; no changes")
        return 2

    anchor = "from github_routing import extract_github_read_scope\n"
    replacement = anchor + "from source_focus import focus_source\n"
    if original.count(anchor) != 1:
        print("STOP: unexpected imports; no changes")
        return 2

    old = '''            else:
                successful_tools.append("github_read")
                last_tool_action, last_tool_result = call, result
        if failures:'''
    new = r'''            else:
                successful_tools.append("github_read")
                last_tool_action, last_tool_result = call, result
                # PAE_FOCUSED_RECIPE_SOURCE_V1
                excerpt = focus_source(
                    str(result.get("content", "")),
                    _last_user_text(messages),
                )
                if excerpt is not None:
                    working[-1] = {
                        "role": "system",
                        "content": (
                            "GITHUB FILE VERIFIED (full text archived, relevant lines "
                            "shown below)\n"
                            f"Repo: {explicit_scope.repo}\n"
                            f"Path: {path}\n"
                            f"Ref: {explicit_scope.ref}\n\n"
                            + excerpt
                        ),
                    }
        if failures:'''
    if original.count(old) != 1:
        print("STOP: expected exact GitHub-read success block missing; no changes")
        return 2

    updated = original.replace(anchor, replacement, 1).replace(old, new, 1)
    try:
        compile(updated, str(TARGET), "exec")
    except SyntaxError as exc:
        print(f"STOP: patch would be invalid: {exc}; no changes")
        return 2

    backups = ROOT / "pae_backups"
    backups.mkdir(exist_ok=True)
    backup = backups / (
        "agent_loop_before_focused_sources_"
        + datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(updated, encoding="utf-8")
    print("OK: recipe excerpts in working prompt; archive unchanged.")
    print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
