# INTENT RESOLVER v0.1

## Purpose
Resolve what the user is actually asking before Discipline OS classifies or executes the request.

Intent is determined from semantic meaning and operational effect, not keywords or user framing alone.

## Core Rule
A request must be decomposed into meaningful action clauses before classification.

For each clause, determine:
1. stated intent — what the user says they want,
2. operational effect — what fulfilling it would actually cause,
3. work relevance — whether it affects projects, priorities, commitments, scope, execution, blockers, planning, or tooling,
4. impact level — how strongly it can alter work state.

When stated intent and operational effect conflict, gate on the operational effect.

## Intent Taxonomy
Assign one or more semantic intents to each clause:

- INFORMATION_ONLY — asks for explanation or facts without requesting action or state change.
- EXPLORATION — investigates an option without activating it.
- EXECUTION — asks for an action to be performed.
- COMMITMENT — creates or changes a promise, deadline, recurring obligation, or tracked responsibility.
- SCOPE_CHANGE — adds, removes, or materially changes deliverables/features within active work.
- PRIORITY_CHANGE — displaces, pauses, or replaces the current focus.
- BLOCKER_CHECK — investigates or removes a concrete blocker to the current focus.
- TOOLING — selects, installs, configures, researches, or changes tools/workflows.
- REVIEW — audits, checks, summarizes, verifies, or evaluates current work/state.
- CREATIVE_PLAY — fictional, game, lore, image, or playful work with no operational effect on active projects.
- CASUAL_FACTUAL — ordinary non-work factual or conversational request.

## Semantic Decomposition
One user message may contain several intents.

Example:
"How does Supabase work, and connect it to PAE."

Clause A:
- INFORMATION_ONLY

Clause B:
- EXECUTION
- TOOLING
- SCOPE_CHANGE

Each work-relevant clause must be gated independently before execution.

Never allow an INFORMATION_ONLY clause to smuggle an EXECUTION clause past the gate.

## Impact Levels
Assign the highest applicable impact level to each clause:

- 0 — no work impact
  Casual conversation, trivia, unrelated creative play.

- 1 — informational
  Explanation, review, or exploration that does not alter work state.

- 2 — directional
  Research or tooling exploration that could redirect execution, consume material time, or create a likely detour.

- 3 — operational
  Executes work, changes scope, creates files/repos/configuration, invokes tools with side effects, or materially consumes the current work block.

- 4 — state-changing
  Creates/changes commitments, active projects, deadlines, current focus, priority order, or persistent project state.

Mandatory gate:
- impact >= 2
- OR any clause has EXECUTION, COMMITMENT, SCOPE_CHANGE, PRIORITY_CHANGE, BLOCKER_CHECK, or TOOLING intent that could affect active work.

## Operational-Effect Rule
Do not trust minimizing language as a substitute for classification.

Phrases such as:
- "just quickly"
- "only take a look"
- "don't change priorities"
- "just test it"
- "only create one thing"

do not reduce impact if fulfilling the request actually creates work, changes state, expands scope, or causes a detour.

Example:
"Don't change priorities, just create a new backend."
Operational effect:
- EXECUTION
- TOOLING
- SCOPE_CHANGE or NEW_PROJECT
Gate on the operational effect.

## Information vs Execution Boundary
Default to INFORMATION_ONLY when a request is genuinely ambiguous and contains no explicit request for:
- a tool call with side effects,
- file/repository/configuration changes,
- state mutation,
- a commitment,
- a scheduled action,
- implementation,
- creation/deletion/update of project assets.

Do not silently execute merely because execution would be helpful.

However, once the user explicitly requests action, classify the action normally even if the message begins with an informational question.

## Tool-Call Rule
Tool calls that only retrieve/read information inherit the intent of the retrieval.

Tool calls that create, update, delete, install, send, schedule, publish, deploy, configure, or otherwise mutate state count as EXECUTION and must pass the gate before the first side-effecting call.

A gate decision made after execution is invalid.

## Work-Relevance Rule
Discipline OS should intervene when fulfilling the request could materially affect:
- current focus,
- current milestone,
- next action,
- active project count,
- commitments,
- execution sequence,
- scope,
- blockers,
- tooling path,
- time/attention allocated to current work.

It should not intervene merely because a request contains work-like vocabulary.

## Mapping to Decision Engine
After semantic resolution, map the dominant operational effect to exactly one primary request class:

- CONTINUE_CURRENT
- NEW_PROJECT
- SCOPE_EXPANSION
- BLOCKER_RESOLUTION
- MAINTENANCE
- REVIEW
- EMERGENCY

Secondary intents remain attached as context for the gate.

Examples:
- "Explain Git branches." -> INFORMATION_ONLY, impact 1 -> no project gate required.
- "Compare three databases for PAE." -> EXPLORATION + TOOLING, impact 2 -> classify against current work and gate.
- "Add Supabase to PAE." -> EXECUTION + TOOLING + SCOPE_CHANGE, impact 3 -> SCOPE_EXPANSION unless it removes a confirmed blocker.
- "I have a client deadline tonight; pause PAE." -> PRIORITY_CHANGE + COMMITMENT, impact 4 -> EMERGENCY or explicit priority renegotiation depending on facts.
- "Check whether TEST-01 passes." -> REVIEW, impact 1 or 2 depending on required execution -> REVIEW / CONTINUE_CURRENT.

## Fail-Safe
If two plausible interpretations would lead to different side effects:
- do not choose the more expansive interpretation,
- preserve the current focus,
- answer the non-destructive portion if useful,
- require explicit execution intent before mutating state.

UNKNOWN intent is never permission to execute.
