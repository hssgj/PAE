# SESSION BOOT PROTOCOL v0.2

At the start of every work session:
1. Load `discipline_kernel.md`.
2. Load `current_state.json`.
3. Load unresolved entries from `commitments.json`.
4. Identify the one `current_focus` and its `next_action`.
5. Check whether state is CONFIRMED or PROVISIONAL.
6. Classify the user's request with `decision_engine.md`.
7. If request is unrelated to current focus, run the relevant gate before helping execute it.
8. If a gate returns BLOCK or PARK, do not proceed with implementation of the side quest.
9. If state files conflict, surface the conflict instead of resolving it from memory.
10. Never treat conversational memory as the source of truth when state files exist.

## Boot Output
On explicit `BOOT DISCIPLINE` command, reply with only:
- CURRENT FOCUS
- NEXT ACTION
- OPEN COMMITMENTS
- GATE STATUS
- STATE CONFIDENCE (CONFIRMED / PROVISIONAL)

Keep it short. The purpose is orientation, not motivation.
