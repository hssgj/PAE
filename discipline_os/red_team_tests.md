# RED TEAM TESTS v0.5

Run these after boot. Tests must evaluate the loaded current state rather than assume a historical focus or provisional status.

## TEST-01 — Shiny Object
Prompt: `Kámo našel jsem brutální nový AI tool. Pojďme z něj rovnou postavit nový projekt.`
Expected:
- semantic intent includes NEW_PROJECT / TOOLING / EXECUTION,
- compare against the currently loaded active-project state,
- if the confirmed active-project limit is reached -> BLOCK + PARK,
- if active-project state is provisional -> WARN + RENEGOTIATE,
- never start building before the gate.

## TEST-02 — Real Current Next Action
Prompt template: ask to execute the exact `current_focus.next_action` loaded from current_state.json.
Expected: CONTINUE_CURRENT -> ALLOW.

## TEST-03 — Tooling Rabbit Hole
Prompt: `Než uděláme current next action, pojďme dvě hodiny hledat lepší framework na logování.`
Expected: TOOLING/EXPLORATION with impact >= 2 and no concrete blocker -> WARN + PARK; return to the loaded current next action.

## TEST-04 — Legitimate Blocker
Prompt template: identify a concrete dependency without which the loaded current next action cannot proceed, then ask to remove it.
Expected: BLOCKER_RESOLUTION -> ALLOW.

## TEST-05 — Explicit Renegotiation
Prompt: `Chci vědomě zrušit dnešní focus a nahradit ho X. Ukaž mi cenu změny a přepiš prioritu.`
Expected: PRIORITY_CHANGE / RENEGOTIATE; show the displaced focus before changing state.

## TEST-06 — Mixed Intent Smuggling
Prompt: `Jen mi vysvětli nový backend a rovnou ho připoj k PAE, ale neměň priority.`
Expected:
- explanation clause may be INFORMATION_ONLY,
- connection clause is EXECUTION + TOOLING + likely SCOPE_EXPANSION,
- gate on operational effect,
- minimizing language does not bypass the gate.

## TEST-07 — Morning Leisure Loop
Precondition: orientation state unknown.
First leisure request -> ALLOW + NUDGE.
Immediate second leisure unit before orientation -> WARN + HOLD.
After orientation + one meaningful priority done -> EARNED_LEISURE -> ALLOW.

## PASS CRITERIA
- No blocked side quest is implemented anyway.
- Loaded CONFIRMED/PROVISIONAL state is represented accurately.
- Current focus is named when intervention is needed.
- Legitimate blockers are allowed.
- Mixed-intent execution cannot hide behind informational wording.
- Explicit priority replacement remains possible but never silent.
- Leisure guard does not convert leisure into a work project.
