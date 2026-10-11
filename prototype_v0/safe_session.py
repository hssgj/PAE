"""Conservative Termux safety runner for one PAE session (separate from Memory Guard)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path.home() / "PAE"
URL = "http://127.0.0.1:8080/slots"
MAX_BATTERY_C = 42.0
MIN_AVAILABLE_MB = 350
MAX_BUSY_SECONDS = 180
POLL_SECONDS = 5


def valid_temp(raw: str) -> float | None:
    try:
        value = float(raw.strip())
    except (ValueError, AttributeError):
        return None
    for factor in (1.0, 0.1, 0.001):
        temp = value * factor
        if 15.0 <= temp <= 65.0:
            return round(temp, 1)
    return None


def battery_temp() -> float | None:
    for path in (
        "/sys/class/power_supply/battery/temp",
        "/sys/class/power_supply/battery/batt_temp",
    ):
        try:
            temp = valid_temp(Path(path).read_text())
            if temp is not None:
                return temp
        except (OSError, UnicodeError):
            pass

    if shutil.which("dumpsys"):
        try:
            result = subprocess.run(
                ["dumpsys", "battery"], capture_output=True,
                text=True, timeout=3, check=False,
            )
            match = re.search(
                r"^\s*temperature:\s*(\d+)\s*$", result.stdout, re.M,
            )
            if match:
                temp = valid_temp(match.group(1))
                if temp is not None:
                    return temp
        except (OSError, subprocess.TimeoutExpired):
            pass

    if shutil.which("termux-battery-status"):
        try:
            result = subprocess.run(
                ["termux-battery-status"], capture_output=True,
                text=True, timeout=4, check=False,
            )
            data = json.loads(result.stdout)
            temp = valid_temp(str(data.get("temperature", "")))
            if temp is not None:
                return temp
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass
    return None


def mem_available_mb() -> int | None:
    try:
        match = re.search(
            r"^MemAvailable:\s*(\d+)\s+kB",
            Path("/proc/meminfo").read_text(), re.M,
        )
        return int(match.group(1)) // 1024 if match else None
    except OSError:
        return None


def slot_active() -> bool | None:
    try:
        with urlopen(URL, timeout=3) as response:
            slots = json.load(response)
        if (
            not isinstance(slots, list)
            or not slots
            or not all(
                isinstance(slot, dict)
                and isinstance(slot.get("is_processing"), bool)
                for slot in slots
            )
        ):
            return None
        return any(slot["is_processing"] for slot in slots)
    except (OSError, ValueError, TimeoutError):
        return None


def stop_runtime(child: subprocess.Popen | None, reason: str) -> None:
    print(f"\n[PAE SAFETY STOP] {reason}", file=sys.stderr, flush=True)
    # Never kill arbitrary PIDs: verify the command line belongs to llama-server.
    try:
        pid = int((ROOT / "llama-server.pid").read_text().strip())
        if b"llama-server" in Path(f"/proc/{pid}/cmdline").read_bytes():
            import os
            os.kill(pid, signal.SIGTERM)
    except (OSError, ValueError):
        print("[guard] Could not verify/stop server PID; check manually.", file=sys.stderr)
    if child is not None and child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--session", default="safety-smoke")
    args = parser.parse_args()

    temp, mem = battery_temp(), mem_available_mb()
    print(
        f"[guard] battery={temp if temp is not None else 'UNAVAILABLE'} C; "
        f"MemAvailable={mem if mem is not None else 'UNKNOWN'} MB",
        flush=True,
    )
    if temp is None:
        print("[guard] BLOCK: no readable battery temperature; no protected test.")
        return 2
    if temp >= MAX_BATTERY_C:
        print("[guard] BLOCK: battery too hot.")
        return 2
    if mem is not None and mem < MIN_AVAILABLE_MB:
        print("[guard] BLOCK: available RAM too low.")
        return 2
    if args.check:
        print("[guard] Sensor check PASS (battery, not CPU thermal protection).")
        return 0

    print(
        f"[guard] Starting {args.session}: battery < {MAX_BATTERY_C} C, "
        f"RAM >= {MIN_AVAILABLE_MB} MB, active request < {MAX_BUSY_SECONDS}s",
        flush=True,
    )
    child = subprocess.Popen(
        ["bash", str(ROOT / "start-local.sh"), args.session]
    )
    busy_since = None
    unknown_since = None
    saw_slots = False
    launched_at = time.monotonic()

    try:
        while child.poll() is None:
            temp, mem = battery_temp(), mem_available_mb()
            if temp is None:
                stop_runtime(child, "temperature reading became unavailable")
                return 3
            if temp >= MAX_BATTERY_C:
                stop_runtime(child, f"battery {temp} C reached threshold")
                return 3
            if mem is not None and mem < MIN_AVAILABLE_MB:
                stop_runtime(child, f"available RAM {mem} MB below threshold")
                return 3

            active = slot_active()
            now = time.monotonic()
            if active is None:
                if not saw_slots and now - launched_at >= 150:
                    stop_runtime(child, "/slots never became available")
                    return 3
                if saw_slots:
                    unknown_since = unknown_since or now
                    if now - unknown_since >= 30:
                        stop_runtime(child, "cannot inspect server for 30 seconds")
                        return 3
            else:
                saw_slots = True
                unknown_since = None
                if active:
                    busy_since = busy_since or now
                    if now - busy_since >= MAX_BUSY_SECONDS:
                        stop_runtime(child, "request exceeded 180 seconds")
                        return 3
                else:
                    busy_since = None
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        stop_runtime(child, "interrupted by user")
        return 130

    print("[guard] PAE session exited normally.")
    return child.returncode or 0


if __name__ == "__main__":
    raise SystemExit(main())
