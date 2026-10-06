from __future__ import annotations

import argparse
import json
from pathlib import Path

from github_source import fetch_github_text, source_name
from provider import build_provider
from sessions import SessionStore
from state_extractor import extract_state


DEFAULT_SYSTEM_PROMPT = """You are PAE prototype_v0, a small persistent chat runtime.

Treat loaded source material as authoritative context. If the source is a game
log, canon, campaign notes, project notes, or other continuity material,
preserve it faithfully.

This prototype has no hidden memory system. Everything you must remember comes
from the loaded source material, derived persistent state, and persisted chat
history. Never invent a missing fact when the persistent state says UNKNOWN.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PAE prototype_v0")
    parser.add_argument(
        "--session",
        default="default",
        help="Session id to create or resume (default: default)",
    )
    parser.add_argument(
        "--load",
        action="append",
        default=[],
        metavar="PATH",
        help="Load a UTF-8 text/log/canon file into persistent context. Repeatable.",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Extract structured state from all loaded sources before chat starts.",
    )
    parser.add_argument(
        "--system",
        default=DEFAULT_SYSTEM_PROMPT,
        help="Base system prompt for a newly created session.",
    )
    return parser.parse_args()


def build_messages(session) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": session.system_prompt}
    ]

    for source in session.sources:
        messages.append(
            {
                "role": "system",
                "content": (
                    "PERSISTENT SOURCE MATERIAL\n"
                    f"Name: {source['name']}\n"
                    f"SHA256: {source['sha256']}\n"
                    "--- BEGIN SOURCE ---\n"
                    f"{source['content']}\n"
                    "--- END SOURCE ---"
                ),
            }
        )

    if session.derived_state:
        messages.append(
            {
                "role": "system",
                "content": (
                    "PERSISTENT DERIVED STATE\n"
                    "This is a source-grounded extraction. UNKNOWN means unknown; "
                    "do not fill it by guessing.\n"
                    + json.dumps(
                        session.derived_state,
                        ensure_ascii=False,
                        indent=2,
                    )
                ),
            }
        )

    messages.extend(session.messages)
    return messages


def load_file(store: SessionStore, session, raw_path: str) -> None:
    path = Path(raw_path).expanduser().resolve()
    content = path.read_text(encoding="utf-8")
    added = store.add_source(session, name=str(path), content=content)
    print(f"[{'loaded' if added else 'already loaded'}] {path}")


def load_github_source(
    store: SessionStore,
    session,
    repo: str,
    path: str,
    ref: str = "main",
) -> None:
    content = fetch_github_text(repo, path, ref=ref)
    name = source_name(repo, path, ref=ref)
    added = store.add_source(session, name=name, content=content)
    print(f"[{'loaded' if added else 'already loaded'}] {name}")


def analyze_sources(provider, store: SessionStore, session) -> None:
    state = extract_state(provider, session.sources)
    store.set_derived_state(session, state)
    print("[state extracted and saved]")


def print_state(session) -> None:
    if not session.derived_state:
        print("[no derived state; run /analyze]")
        return

    print(json.dumps(session.derived_state, ensure_ascii=False, indent=2))


def print_help() -> None:
    print(
        "Commands:\n"
        "  /load PATH   add a text/log/canon file to persistent session context\n"
        "  /github REPO PATH [REF]   load one GitHub text file into persistent context\n"
        "  /analyze     extract canon/characters/current_scene/important_facts\n"
        "  /state       print the persisted structured state\n"
        "  /sources     list loaded persistent sources\n"
        "  /save        force-save the session\n"
        "  /help        show commands\n"
        "  /quit        save and exit"
    )


def main() -> None:
    args = parse_args()
    store = SessionStore()
    session = store.open_or_create(args.session, system_prompt=args.system)

    for path in args.load:
        load_file(store, session, path)

    provider = build_provider()

    if args.analyze:
        try:
            analyze_sources(provider, store, session)
        except Exception as exc:
            print(f"[analysis error] {exc}")

    print(
        f"PAE prototype_v0 | session={session.session_id} | "
        f"provider={provider.name}"
    )
    print_help()

    while True:
        try:
            user_text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            store.save(session)
            break

        if not user_text:
            continue

        if user_text == "/quit":
            store.save(session)
            break

        if user_text == "/help":
            print_help()
            continue

        if user_text == "/save":
            store.save(session)
            print("[saved]")
            continue

        if user_text == "/sources":
            if not session.sources:
                print("[no sources loaded]")
            else:
                for source in session.sources:
                    print(f"- {source['name']} ({source['sha256'][:12]})")
            continue

        if user_text == "/state":
            print_state(session)
            continue

        if user_text == "/analyze":
            try:
                analyze_sources(provider, store, session)
                print_state(session)
            except Exception as exc:
                print(f"[analysis error] {exc}")
            continue

        if user_text.startswith("/load "):
            raw_path = user_text[len("/load ") :].strip()
            try:
                load_file(store, session, raw_path)
            except Exception as exc:
                print(f"[load error] {exc}")
            continue

        if user_text.startswith("/github "):
            raw_args = user_text[len("/github ") :].strip().split()
            if len(raw_args) not in {2, 3}:
                print("[usage] /github REPO PATH [REF]")
                continue

            repo, path = raw_args[0], raw_args[1]
            ref = raw_args[2] if len(raw_args) == 3 else "main"

            try:
                load_github_source(store, session, repo, path, ref)
            except Exception as exc:
                print(f"[github load error] {exc}")
            continue

        session.messages.append({"role": "user", "content": user_text})
        store.save(session)

        try:
            reply = provider.chat(build_messages(session))
        except Exception as exc:
            print(f"[provider error] {exc}")
            continue

        print(f"\npae> {reply}")
        session.messages.append({"role": "assistant", "content": reply})
        store.save(session)


if __name__ == "__main__":
    main()
