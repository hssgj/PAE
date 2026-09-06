# PAE — Architecture v0.1
## 7-Day Working Plan

This is the current working roadmap for completing a Level 1 definition of every major PAE architectural layer.

**Status:** Working roadmap — not architecture canon.

## Working Rules

- Architecture v0.1 is WORKING, not final canon.
- CANON ≠ IDEA.
- UNKNOWN ≠ INVENTED.
- Do not silently change established decisions.
- Preserve useful concrete examples.
- Do not over-engineer Level 1.
- One major architectural question / Boss Fight at a time.
- When a layer is sufficiently defined for a first implementation, mark it Level 1 and move on.
- Do not spend weeks solving hypothetical edge cases before the basic architecture exists.
- No serious implementation until the Level 1 architecture has been integrated and checked.
- Reality-check aggressively. No honeymouth: if something is unrealistic, say so.

# 7-DAY PLAN

## DAY 1 — COGNITION

Define the Cognition Cycle.

Main question:

> What exactly does PAE do from the moment it receives an objective until it decides what happens next?

Define at minimum:

```text
INPUT
↓
INTERPRET
↓
DECOMPOSE
↓
EVALUATE
↓
DECIDE
↓
OUTPUT
```

Clarify:
- what Cognition receives,
- how it understands the objective,
- how it creates semantic units,
- how it creates/modifies the Task Tree,
- how it determines required capabilities/resources,
- how it selects resources/models,
- what Cognition outputs,
- what causes another Cognition Cycle,
- how Cognition handles results from execution.

**Target:** Cognition v0.1 — Level 1 definition.

## DAY 2 — TASK TREE + EXECUTION

Connect Cognition to actual work.

```text
OBJECTIVE
↓
TASK TREE
↓
SEMANTIC UNITS
↓
EXECUTABLE ACTIONS
↓
EXECUTION
↓
RESULT
```

Define Level 1 behavior for dependencies, parallel/sequential tasks, completion, insertion, modification, retry, repair, replacement, continuation, and stopping.

Established principle: **The Task Tree is mutable during execution.**

**Target:** Task / Execution Model v0.1.

## DAY 3 — RESOURCES / REGISTRY / WELLS

Treat these as connected pieces:

```text
COGNITION
↓
"What do I need?"
↓
REGISTRY
↓
"What can provide it?"
↓
WELL
↓
RESOURCE
```

### Registry
Define what PAE needs to know about a resource: identity, type, capabilities, location, access method, inputs, outputs, requirements, limitations, availability/status.

### Well
A Well is a resource environment/storage/access location where usable resources are exposed. A Well is **not** itself a capability.

### Resource
A concrete capability/tool/model/service PAE can use.

Established principle: different tasks may use different resources/models; PAE is not tied to one AI provider or one model.

**Target:** Resource / Registry / Well Model v0.1.

## DAY 4 — EXECUTION ENVIRONMENT / HOST

Define where PAE actually operates.

Clarify:
- runtime,
- filesystem,
- persistent state,
- network access,
- temporary state,
- credentials/secrets,
- processes/services,
- what survives restart,
- how execution receives inputs,
- how execution returns results.

Question:

> What environment must exist for PAE to actually operate independently of a phone/interface?

**Target:** PAE Runtime / Environment v0.1.

## DAY 5 — STATE / MEMORY

Separate the different kinds of persistent information:

```text
EXECUTION STATE
MEMORY
KNOWLEDGE
EXPERIENCE
PROCEDURE
IDENTITY
```

Define what each means, what gets written/updated/deleted, what must persist, how execution state differs from long-term memory, and how experience can eventually become learned procedure/strategy.

Established long-term principle: learning may improve future decisions, but must not silently rewrite fundamental identity, security, or governing architecture.

**Target:** Persistent State / Memory Model v0.1.

## DAY 6 — FAILURE / RECOVERY / AUTHORIZATION

Integrate failure handling with authorization.

```text
ACTION
↓
RESULT
↓
VERIFY
↓
SUCCESS → CONTINUE

FAILURE
↓
DIAGNOSE
↓
ANALYZE
↓
POSSIBLE SOLUTIONS
↓
TRY / REPAIR / RETRY
↓
VERIFY
↓
CONTINUE
```

If no autonomous solution remains:

```text
TRUE BOUNDARY
├── TECHNICAL LIMIT → ANNOUNCE
└── AUTHORIZATION LIMIT → ASK USER
```

Established principles:
- Error ≠ immediate failure.
- PAE should diagnose before giving up.
- PAE may create intermediate repair tasks.
- PAE may modify the Task Tree to recover.
- PAE may try alternative resources.
- Human intervention should be an ultimate gate, not a substitute for autonomous reasoning.
- Capability ≠ Authorization.

**Target:** Failure / Recovery / Authorization v0.1.

## DAY 7 — INTEGRATION TEST

Do **not** introduce another major architectural layer.

Use this objective:

> "Harvest every sense concerning our project here, summarize it and write it up on GitHub."

Trace it through:

```text
INTERFACE
↓
PAE CORE
↓
COGNITION
↓
TASK TREE
↓
REGISTRY
↓
WELL
↓
RESOURCE
↓
EXECUTION
↓
RESULT
↓
VERIFY
↓
COGNITION AGAIN
↓
REPAIR / RETRY if needed
↓
PERSISTENT STATE
↓
ANNOUNCE
```

Check:
1. Can every layer pass what the next layer needs?
2. Are responsibilities clearly separated?
3. Are there circular dependencies that should not exist?
4. Can Cognition modify the Task Tree?
5. Can PAE choose different resources for different tasks?
6. Can execution return meaningful results to Cognition?
7. Can errors trigger repair rather than immediate failure?
8. Are authorization gates clearly separated from cognition?
9. Can persistent state survive the current model/interface?
10. Is the architecture concrete enough to begin implementation?

Any discovered holes become **targeted fixes**, not an excuse to redesign everything.

# END-OF-WEEK TARGET

```text
PAE ARCHITECTURE v0.1

INTERFACE       ✓ Level 1
CORE            ✓ Level 1
COGNITION       ✓ Level 1
TASK TREE       ✓ Level 1
EXECUTION       ✓ Level 1
REGISTRY        ✓ Level 1
WELLS           ✓ Level 1
RESOURCES       ✓ Level 1
ENVIRONMENT     ✓ Level 1
STATE / MEMORY  ✓ Level 1
VERIFICATION    ✓ Level 1
RECOVERY        ✓ Level 1
AUTHORIZATION   ✓ Level 1
```

The result does not need to be perfect. It needs to be **coherent, understandable, internally connected, and concrete enough to implement.**

Once this condition is met, stop expanding the architecture and move toward the first prototype.

## Current Starting Point

**DAY 1 — COGNITION**

> What exactly happens during one PAE Cognition Cycle, and what causes PAE to think again?
