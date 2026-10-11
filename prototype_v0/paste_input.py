"""Reliable opt-in multiline input for the Termux PAE CLI.

At you> enter /paste, paste lines, then enter /end on its own line.
Nothing is submitted to the agent before /end.
"""

from __future__ import annotations


def read_user_message() -> str:
    first = input("\nyou> ")
    if first.strip() != "/paste":
        return first

    print("[paste] Vlož víceřádkové zadání. Ukonči samostatným řádkem /end.")
    lines: list[str] = []
    total = 0
    overflow = False
    while True:
        try:
            line = input("... ")
        except EOFError:
            print("[paste] Nedokončené zadání zrušeno; nic nebylo odesláno.")
            return ""
        if line.strip() == "/end":
            break
        total += len(line) + 1
        if len(lines) >= 120 or total > 20000:
            overflow = True
        if not overflow:
            lines.append(line)

    if overflow:
        print("[paste] Zadání překročilo 120 řádků / 20 000 znaků; neodesláno.")
        return ""
    message = "\n".join(lines).strip()
    print(f"[paste] Přijato {len(lines)} řádků jako jedna zpráva.")
    return message
