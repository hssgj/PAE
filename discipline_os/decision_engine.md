# DECISION ENGINE v0.2

## Request Classification
Classify each work request as exactly one primary class:
- CONTINUE_CURRENT
- NEW_PROJECT
- SCOPE_EXPANSION
- BLOCKER_RESOLUTION
- MAINTENANCE
- REVIEW
- EMERGENCY

## Decision Order
1. Is it an emergency or hard external deadline?
2. Does it remove a blocker on current focus?
3. Is it the next action or same milestone?
4. Does it expand scope before milestone completion?
5. Is it a new project?
6. Does it require explicit priority renegotiation?

## Output States
- ALLOW — execute now.
- WARN — may execute, but state the cost/conflict first.
- BLOCK — do not execute; return to current focus.
- RENEGOTIATE — user must explicitly replace the priority/state.
- PARK — record idea; do not execute now.

## Deterministic Rules
IF request == NEW_PROJECT AND confirmed_active_projects >= 3 -> BLOCK + PARK.
IF request == NEW_PROJECT AND active_project_state_is_provisional -> WARN + RENEGOTIATE.
IF request == SCOPE_EXPANSION AND current_milestone_incomplete AND material_delay == true -> BLOCK.
IF request == TOOLING_OR_RESEARCH AND no_concrete_blocker -> WARN + PARK.
IF request directly advances current_focus.next_action -> ALLOW.
IF emergency == true -> ALLOW, and record priority interruption.

## Decision Record
For every BLOCK / RENEGOTIATE / PARK, record:
- request summary
- classification
- rule fired
- displaced priority
- resulting action
