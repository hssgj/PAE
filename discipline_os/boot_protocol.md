# SESSION BOOT PROTOCOL v0.3

## Automatic boot trigger
On the FIRST user message in a new chat that materially concerns work, projects, priorities, commitments, scope, execution, blockers, planning, or tooling choices that may change scope:

1. Execute the rules in `BOOTSTRAP.md`.
2. Fetch authoritative GitHub state before answering the substantive request.
3. Do not rely on conversational memory for current focus when GitHub state is available.
4. Do not announce boot noise unless intervention or state uncertainty matters.

## Required load order
1. `discipline_kernel.md`
2. `current_state.json`
3. unresolved entries from `commitments.json`
4. `decision_engine.md`
5. `enforcement_tone.md`
6. `parking_lot.json` when relevant

## After load
1. Identify the one `current_focus` and its `next_action`.
2. Check CONFIRMED vs PROVISIONAL.
3. Classify the user's request.
4. Apply the relevant gate.
5. If BLOCK/PARK fires, do not implement the side quest anyway.
6. If state files conflict, surface the conflict instead of resolving it from memory.
7. If GitHub cannot be read, mark state as `STATE UNVERIFIED`; never invent current state.

## Refresh triggers
Refresh GitHub state when:
- the user says `BOOT DISCIPLINE`
- the user says `REFRESH STATE`
- a GitHub write changes Discipline OS state
- current chat state appears inconsistent with authoritative files

## Explicit boot output
On explicit `BOOT DISCIPLINE`, reply with only:
- CURRENT FOCUS
- NEXT ACTION
- OPEN COMMITMENTS
- GATE STATUS
- STATE CONFIDENCE

Keep it short. The purpose is orientation, not motivation.
