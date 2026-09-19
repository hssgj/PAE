# MATTHAEL DISCIPLINE OS v0.3

Persistent enforcement layer for PAE.

## Automatic ChatGPT boot
On the first materially work-related prompt in a new chat, use `BOOTSTRAP.md` as the entrypoint and fetch authoritative state from this repository before executing the request.

Important limitation: no system can run before the user sends the first message. Auto-boot means "first relevant message -> fetch state -> then answer".

## Boot order
1. BOOTSTRAP.md
2. discipline_kernel.md
3. current_state.json
4. commitments.json
5. decision_engine.md
6. enforcement_tone.md
7. boot_protocol.md
8. parking_lot.json when relevant

## Important
`current_state.json` currently contains PROVISIONAL project state. Provisional entries are not confirmed canon.

## Repository role
This folder is the authoritative persistent state for Discipline OS. Chat memory is context, not runtime truth.
