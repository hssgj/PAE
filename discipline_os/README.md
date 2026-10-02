# MATTHAEL DISCIPLINE OS v0.5

Persistent enforcement and orientation layer for PAE.

## Automatic ChatGPT boot
On the first materially work-related prompt in a new chat, use `BOOTSTRAP.md` as the entrypoint and fetch authoritative state from this repository before executing the request.

Important limitation: no system can run before the user sends the first message. Auto-boot means "first relevant message -> fetch state -> then answer".

## Authoritative boot order
1. BOOTSTRAP.md
2. discipline_kernel.md
3. current_state.json
4. commitments.json
5. intent_resolver.md
6. decision_engine.md
7. enforcement_tone.md
8. leisure_guard.md
9. boot_protocol.md
10. parking_lot.json when relevant

## State semantics
- `current_state.json` is the current operational source of truth.
- Respect its explicit `state_status`; PROVISIONAL is never treated as CONFIRMED.
- Conversation memory is context, not runtime truth.
- Factual maintenance may advance stale state when the underlying outcome is already user-confirmed or externally verified.
- A genuine priority override still requires the normal gate/renegotiation rules.

## Scope
Discipline OS should stay small. Maintenance repairs state accuracy, contradictions, stale instructions, and broken tests. New interfaces, dashboards, automation layers, or workflow features are scope expansion and require an explicit gate.
