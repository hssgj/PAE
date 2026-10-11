"""Safely install /paste and non-content provider timing into local PAE Mobile.

Touches ONLY prototype_v0/app.py; creates dated backup before writing.
Memory Guard, provider.py, start-local.sh, agent_loop.py remain untouched.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "prototype_v0" / "app.py"
MARKER = "from paste_input import read_user_message"


def replace_once(text: str, needle: str, replacement: str, why: str) -> str:
    count = text.count(needle)
    if count != 1:
        raise RuntimeError(f"{why}: expected once, found {count}; NO EDIT")
    return text.replace(needle, replacement, 1)


def main() -> int:
    if not all((APP.parent / filename).exists() for filename in ("paste_input.py", "perf_log.py")):
        print("STOP: helper modules missing; no edit.")
        return 2
    old = APP.read_text(encoding="utf-8")
    if MARKER in old:
        print("ALREADY INSTALLED: no edit.")
        return 0
    try:
        updated = replace_once(
            old, "from __future__ import annotations\n",
            "from __future__ import annotations\n\n"
            "from paste_input import read_user_message\n"
            "from perf_log import TimedProvider\n",
            "imports",
        )
        updated = replace_once(
            updated, 'user_text = input("\\nyou> ").strip()',
            "user_text = read_user_message().strip()",
            "CLI input",
        )
        if "provider = BusyProvider(build_provider())" in updated:
            old_provider = "provider = BusyProvider(build_provider())"
        elif "provider = build_provider()" in updated:
            old_provider = "provider = build_provider()"
        else:
            raise RuntimeError("unexpected provider initialization; NO EDIT")
        updated = replace_once(
            updated, old_provider,
            old_provider.replace("provider = ", "provider = TimedProvider(", 1) + ")",
            "provider timing",
        )
        # append help only when this exact help structure is present
        updated = replace_once(
            updated,
            '"  /quit        save and exit"',
            '"  /paste       zadání přes více řádků; konec /end\\n"\n'
            '        "  /quit        save and exit"',
            "CLI help",
        )
        compile(updated, str(APP), "exec")
    except (RuntimeError, SyntaxError) as exc:
        print(f"STOP: {exc}")
        return 2

    directory = ROOT / "pae_backups"
    directory.mkdir(exist_ok=True)
    backup = directory / (
        "app_before_paste_perf_"
        + datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    backup.write_text(old, encoding="utf-8")
    APP.write_text(updated, encoding="utf-8")
    print("OK: /paste + timing installed; no Memory Guard changes.")
    print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
