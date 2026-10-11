"""Opt-in PAE provider timing, with no prompt contents stored.

Run: python perf_log.py  (from prototype_v0 or elsewhere).
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_LOG = Path(__file__).resolve().parent / "data" / "performance.jsonl"


class TimedProvider:
    def __init__(self, provider, log_path: Path | None = None):
        self.provider = provider
        self.name = provider.name
        self.log_path = log_path or DEFAULT_LOG

    def chat(self, messages):
        started = time.monotonic()
        timestamp = datetime.now(timezone.utc).isoformat()
        outcome = "ok"
        output_chars = 0
        try:
            answer = self.provider.chat(messages)
            output_chars = len(answer) if isinstance(answer, str) else 0
            return answer
        except Exception as exc:
            outcome = type(exc).__name__
            raise
        finally:
            record = {
                "utc": timestamp,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "message_count": len(messages),
                "input_characters": sum(
                    len(str(msg.get("content", ""))) for msg in messages
                ),
                "output_characters": output_chars,
                "outcome": outcome,
            }
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as file:
                    file.write(json.dumps(record, ensure_ascii=False) + "\n")
            except OSError:
                # Telemetry must never break PAE.
                pass


def summarize(path: Path = DEFAULT_LOG) -> str:
    if not path.is_file():
        return "Žádná měření. Nejprve proveď jednu PAE odpověď."
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
            if "elapsed_seconds" in entry:
                records.append(entry)
        except (ValueError, TypeError):
            continue
    if not records:
        return "Žádná platná měření."
    latest = records[-10:]
    times = [float(row["elapsed_seconds"]) for row in latest]
    sizes = [int(row.get("input_characters", 0)) for row in latest]
    return (
        f"Posledních {len(latest)} volání modelu: "
        f"medián {sorted(times)[len(times)//2]:.1f} s, "
        f"min {min(times):.1f} s, max {max(times):.1f} s, "
        f"průměr {sum(times)/len(times):.1f} s; "
        f"průměrný vstup {sum(sizes)//len(sizes)} znaků. "
        "Znakový počet NENÍ počet tokenů."
    )


if __name__ == "__main__":
    print(summarize())
