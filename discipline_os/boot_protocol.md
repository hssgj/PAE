# SESSION BOOT PROTOCOL v0.4

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
4. `intent_resolver.md`
5. `decision_engine.md`
6. `enforcement_tone.md`
7. `parking_lot.json` when relevant

## Session Boot vs Per-Request Gate
Session boot and enforcement are separate mechanisms.

SESSION BOOT:
- runs once on the first materially work-related request,
- establishes authoritative state.

PER-REQUEST GATE:
- runs on every materially work-relevant request after boot,
- semantically resolves intent before classification,
- evaluates operational effect and impact,
- gates each execution-relevant clause before action.

BOOTED != BYPASS.

A loaded session must not treat earlier boot as permission to execute later scope changes, new projects, tooling detours, commitments, or priority changes.

## Per-Request Sequence
For every materially work-relevant request:
1. Decompose the message using `intent_resolver.md`.
2. Identify stated intent and operational effect.
3. Assign semantic intents and impact level per meaningful clause.
4. Determine which clauses require a mandatory gate.
5. Map dominant operational effect to a primary request class.
6. Compare against current focus, milestone, next action, commitments, and active-project state.
7. Apply `decision_engine.md`.
8. Only after ALLOW/WARN permits execution may side-effecting tools or state mutations occur.
9. If BLOCK/PARK fires, do not implement the side quest anyway.

## After load
1. Identify the one `current_focus` and its `next_action`.
2. Check CONFIRMED vs PROVISIONAL.
3. Resolve the current request semantically.
4. Classify the request.
5. Apply the relevant gate.
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
