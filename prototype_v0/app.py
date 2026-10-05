from __future__ import annotations

import argparse
from pathlib import Path

from provider import build_provider
from sessions import SessionStore


DEFAULT_SYSTEM_PROMPT = """You are PAE prototype_v0, a small persistent chat runtime.

Treat loaded source material as authoritative context. If the source is a game
log, canon, campaign notes, or character sheet, preserve continuity and act as
a consistent interactive GM when the user asks to play.

This prototype has no hidden memory system. Everything you must remember comes
from the loaded source material and persisted chat history.
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

    messages.extend(session.messages)
    return messages


def load_file(store: SessionStore, session, raw_path: str) -> None:
    path = Path(raw_path).expanduser().resolve()
    content = path.read_text(encoding="utf-8")
    added = store.add_source(session, name=str(path), content=content)
    print(f"[{'loaded' if added else 'already loaded'}] {path}")


def print_help() -> None:
    print(
        "Commands:\n"
        "  /load PATH   add a text/log/canon file to persistent session context\n"
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

        if user_text.startswith("/load "):
            raw_path = user_text[len("/load ") :].strip()
            try:
                load_file(store, session, raw_path)
            except Exception as exc:
                print(f"[load error] {exc}")
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
