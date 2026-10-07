from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_ROOT = Path(__file__).resolve().parent / "data" / "sessions"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_session_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    if not cleaned:
        raise ValueError("session id cannot be empty")
    return cleaned[:120]


@dataclass
class Session:
    session_id: str
    system_prompt: str
    schema_version: int = SCHEMA_VERSION
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    sources: list[dict[str, Any]] = field(default_factory=list)
    messages: list[dict[str, str]] = field(default_factory=list)
    derived_state: dict[str, Any] = field(default_factory=dict)
    pending_actions: dict[str, dict[str, Any]] = field(default_factory=dict)


class SessionStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or DEFAULT_ROOT
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, session_id: str) -> Path:
        return self.root / f"{safe_session_id(session_id)}.json"

    def open_or_create(self, session_id: str, *, system_prompt: str) -> Session:
        session_id = safe_session_id(session_id)
        path = self.path_for(session_id)

        if path.exists():
            return self.load(session_id)

        session = Session(
            session_id=session_id,
            system_prompt=system_prompt,
        )
        self.save(session)
        return session

    def load(self, session_id: str) -> Session:
        path = self.path_for(session_id)
        data = json.loads(path.read_text(encoding="utf-8"))

        if data.get("schema_version") != SCHEMA_VERSION:
            raise RuntimeError(
                "unsupported session schema "
                f"{data.get('schema_version')!r}; expected {SCHEMA_VERSION}"
            )

        return Session(**data)

    def save(self, session: Session) -> None:
        session.updated_at = utc_now()
        path = self.path_for(session.session_id)
        temp_path = path.with_suffix(".json.tmp")

        temp_path.write_text(
            json.dumps(asdict(session), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(path)

    def add_source(self, session: Session, *, name: str, content: str) -> bool:
        """Add an immutable/local source, deduplicating by content hash."""
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()

        if any(source.get("sha256") == digest for source in session.sources):
            return False

        session.sources.append(
            {
                "name": name,
                "sha256": digest,
                "content": content,
            }
        )
        self.save(session)
        return True

    def upsert_source(
        self,
        session: Session,
        *,
        source_id: str,
        name: str,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Insert or refresh a mutable source identified independently of content."""
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        metadata = dict(metadata or {})

        replacement: dict[str, Any] = {
            "source_id": source_id,
            "name": name,
            "sha256": digest,
            "content": content,
            **metadata,
        }

        matches = [
            index
            for index, source in enumerate(session.sources)
            if source.get("source_id") == source_id
            or (
                source.get("source_id") is None
                and source.get("name") == name
            )
        ]

        if not matches:
            session.sources.append(replacement)
            self.save(session)
            return "loaded"

        first = matches[0]
        existing = session.sources[first]
        unchanged = (
            existing.get("sha256") == digest
            and all(existing.get(key) == value for key, value in metadata.items())
        )

        # Replace the canonical entry and collapse legacy duplicates with the same identity.
        session.sources[first] = replacement
        for index in reversed(matches[1:]):
            del session.sources[index]

        if unchanged and len(matches) == 1:
            return "already loaded"

        self.save(session)
        return "refreshed"

    def set_derived_state(
        self,
        session: Session,
        state: dict[str, Any],
    ) -> None:
        session.derived_state = state
        self.save(session)
