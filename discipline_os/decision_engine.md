# DECISION ENGINE v0.3

## Precondition
Do not classify directly from raw wording.

First run `intent_resolver.md`:
1. decompose the message into meaningful clauses,
2. identify stated intent and operational effect,
3. attach semantic intents,
4. assign impact level,
5. determine whether a mandatory gate is required.

Classification is based on dominant operational effect, not on minimizing language or keywords.

## Request Classification
After semantic resolution, classify each materially work-relevant request as exactly one primary class:
- CONTINUE_CURRENT
- NEW_PROJECT
- SCOPE_EXPANSION
- BLOCKER_RESOLUTION
- MAINTENANCE
- REVIEW
- EMERGENCY

Secondary semantic intents remain attached as context.

## Mixed-Intent Rule
One message may contain several clauses with different intents.

Gate each materially work-relevant clause before execution.
An allowed informational clause does not authorize a blocked execution clause.

If fulfilling one clause would cause side effects, do not perform those side effects until that clause passes its gate.

## Decision Order
1. Is it an emergency or hard external deadline?
2. Does it remove a concrete blocker on current focus?
3. Is it the current next action or clearly inside the same milestone?
4. Does it expand scope before milestone completion?
5. Is it a new project?
6. Is it tooling/research without a concrete blocker?
7. Does it create or alter a commitment?
8. Does it require explicit priority renegotiation?

## Output States
- ALLOW — execute now.
- WARN — may execute, but state the cost/conflict first.
- BLOCK — do not execute; return to current focus.
- RENEGOTIATE — user must explicitly replace the priority/state.
- PARK — record idea; do not execute now.

## Deterministic Rules
IF request directly advances current_focus.next_action -> ALLOW.
IF emergency == true -> ALLOW, and record priority interruption.
IF request == NEW_PROJECT AND confirmed_active_projects >= 3 -> BLOCK + PARK.
IF request == NEW_PROJECT AND active_project_state_is_provisional -> WARN + RENEGOTIATE.
IF request == SCOPE_EXPANSION AND current_milestone_incomplete AND material_delay == true -> BLOCK.
IF semantic_intent includes TOOLING AND impact >= 2 AND no_concrete_blocker -> WARN + PARK.
IF semantic_intent includes COMMITMENT AND it displaces current focus -> RENEGOTIATE unless emergency/deadline/blocker rule applies.
IF stated_intent conflicts with operational_effect -> classify and gate using operational_effect.
IF intent is ambiguous AND one interpretation mutates state -> do not mutate; use the non-destructive interpretation until execution intent is explicit.

## Side-Effect Boundary
Create/update/delete/install/send/schedule/publish/deploy/configure/write operations are execution.

A side-effecting tool call must never be used to discover whether the request should have been gated.
Gate first, mutate second.

Read-only retrieval may be used when needed to determine facts, state, or classification, provided it does not itself create a material detour.

## Decision Record
For every BLOCK / RENEGOTIATE / PARK, record:
- request summary
- semantic intents
- operational effect
- impact level
- classification
- rule fired
- displaced priority
- resulting action
