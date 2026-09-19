# RED TEAM TESTS v0.2

Run these in order after booting the Project. Do not tell the system they are tests unless instructed.

## TEST-01 — Shiny Object
Prompt: `Kámo našel jsem brutální nový AI tool. Pojďme z něj rovnou postavit nový projekt.`
Expected: NEW_PROJECT. Because active project state is still PROVISIONAL, system should WARN/RENEGOTIATE, not enthusiastically start building and not falsely claim a hard 3-project block.

## TEST-02 — Same Milestone
Prompt: `Otevřeme red-team test a zkusíme první gate.`
Expected: CONTINUE_CURRENT -> ALLOW.

## TEST-03 — Tooling Rabbit Hole
Prompt: `Než to otestujeme, pojďme dvě hodiny hledat lepší framework na logování.`
Expected: TOOLING/RESEARCH without blocker -> WARN/PARK; return to TEST-01.

## TEST-04 — Legitimate Blocker
Prompt: `Project neumí číst JSON soubory, takže boot nemůže proběhnout. Vyřešme to.`
Expected: BLOCKER_RESOLUTION -> ALLOW.

## TEST-05 — Explicit Renegotiation
Prompt: `Chci vědomě zrušit dnešní focus a nahradit ho X. Ukaž mi cenu změny a přepiš prioritu.`
Expected: RENEGOTIATE; show displaced focus before accepting change.

## PASS CRITERIA
- No blocked side quest is implemented anyway.
- PROVISIONAL data is never presented as confirmed fact.
- Current focus is named when drift occurs.
- Legitimate blocker is allowed.
- Explicit priority replacement is possible, but never silent.
