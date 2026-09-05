# PAE Architecture v0.1 — Closed

> Working architecture summary. This file contains decisions that are sufficiently established for v0.1.
>
> This is architecture, not yet final project canon.

## 1. Core Vision

PAE is a persistent personal AI system whose identity and operational continuity do not depend on a phone, interface, provider or individual AI model.

The phone is an interface/window into PAE, not the intelligence itself.

PAE should receive an objective, determine what is needed, obtain appropriate capabilities, execute work, evaluate results and continue the objective without requiring the user to direct every intermediate step.

## 2. Interface

Interfaces may include phone chat, web, PC, voice or terminal.

Conceptually:

```text
INPUT → TRANSPORT → PAE → RESPONSE → DISPLAY
```

The interface is not the intelligence or execution environment.

## 3. PAE Core

PAE Core is the central coordinating layer. It is not a single AI model.

It coordinates objectives, interpretation/cognition, task structure, execution state, resources, results, verification and continuation.

Authorization is separate from cognition. PAE should be able to think through intermediate steps without asking for permission at every step, while still stopping at defined authorization boundaries.

## 4. Cognition

Cognition is the process by which PAE interprets the current objective and state, understands meaning, creates and modifies meaningful work structure, determines what is needed, selects appropriate resources and decides what should happen next.

Initial cognition can transform an objective into semantic units and a Task Tree.

Continuing cognition processes execution results and state changes, evaluates progress, and determines whether to continue, modify, repair, retry, wait, ask or finish.

A model may be used as a computational resource inside cognition. The cognition mechanism itself is architecturally independent from any particular model or provider.

### Typical cognition inputs

- objective
- current state
- context
- rules
- registers/resource information
- Task Tree / execution structure
- execution results
- available resources

### Typical cognition outputs

- new or modified Task Tree structure
- semantic work units
- required capabilities/resources
- resource/model selection
- next action or execution package
- task modification
- retry/repair/alternative strategy
- wait / ask
- continue / finish

## 5. Semantic Units vs Executable Actions

A **Semantic Unit** describes what should be accomplished: e.g. Analyze context, Write email, Search information, Review email.

An **Executable Action** describes what the system can concretely perform to accomplish that semantic unit.

These concepts must remain distinct.

## 6. Task Tree

The primary human-readable execution structure is the Task Tree.

The underlying implementation may use a graph where dependencies become complex, but the Task Tree remains the main conceptual structure because it is readable, manageable, debuggable and versatile.

The Task Tree is created by cognition from the objective. It does not have to exist before initial cognition.

### Example

```text
OBJECTIVE
│
├── 1. READ
│   └── 1.1 ANALYZE
│
├── 2. CREATE GITHUB RECORD
│   ├── 2.1 MARKUP / PREPARE
│   ├── 2.2 WRITE
│   └── 2.3 SAVE
│
└── 3. ANNOUNCE
```

Dependencies determine what can proceed in parallel and what must wait.

For example, 1 and 2 may progress concurrently, but 2.3 cannot complete until its required dependencies, including 1.1 and 2.2, are complete.

## 7. Mutable Execution

The Task Tree is a living execution structure, not a fixed prophecy.

Cognition may add, remove, split, retry, repair, replace, return, wait or otherwise modify tasks when execution reveals new information, errors, missing dependencies or better solutions.

Intermediate repair tasks are a normal part of execution.

### Example: repair after failure

```text
2.2 WRITE
   ↓
 ERROR
   ↓
 COGNITION
   ├─ identify problem
   ├─ analyze possible solutions
   ├─ create repair/intermediate task
   ├─ execute repair
   ├─ verify
   └─ return to 2.2
   ↓
2.3 SAVE
```

## 8. Failure Is Not Immediate Final Failure

When an execution step fails, PAE should not immediately announce an error.

Cognition should first be able to:

1. identify the problem,
2. analyze possible solutions,
3. try an appropriate alternative,
4. repair or modify the task when possible,
5. learn from available resources when useful,
6. verify the result.

Only when reasonable autonomous options are exhausted, or a genuine boundary is reached, should PAE announce that it cannot continue autonomously.

## 9. Resource Selection

Cognition may select different resources/models for different semantic units within the same objective.

One objective does not require one model or one tool.

For example:

```text
Task 1 → Claude
Task 2 → GPT
Task 3 → Claude
Task 4 → GitHub tool
```

Selection is based on what the task requires and what the Registry says about available resources.

The Registry describes resources; Cognition decides how they should be used.

## 10. Wells

A **Well** is a resource environment, storage or access location where usable resources are available or exposed.

A Well is not itself a capability.

Examples may include repositories, prepared modules, service environments or environments containing tools/resources.

Reaching into a Well means obtaining access to a resource or capability; it does not necessarily mean copying the resource into PAE.

## 11. External Resources

Some resources exist outside PAE-controlled environments.

Examples include external AI models/providers, APIs, search services and remote services.

PAE architecture therefore distinguishes:

- resource storage/environment
- resource access
- resource registry
- cognition that determines what is needed

## 12. Registry

The Registry is the description/knowledge layer for resources.

It should be able to describe things such as:

- identity
- type
- location
- access method
- capabilities
- inputs/outputs
- requirements
- limitations

The Registry does not itself perform the resource's work. It tells PAE what exists and how it may be accessed.

## 13. Capability vs Authorization

These remain separate concepts.

**Capability:** what the system can technically do.

**Authorization:** what the system is currently allowed to do.

A capability may exist while authorization to use it for a particular operation does not.

Authorization gates execution; it should not unnecessarily micromanage cognition.

## 14. Ultimate Human Confirmation

When PAE reaches a boundary of what it is authorized to do, it should ask the user for confirmation rather than silently crossing that boundary.

Human confirmation is an ultimate authorization gate, not the default mechanism for every intermediate decision.

Before asking, PAE should normally have identified the problem, considered available alternatives and established why the requested action requires human authorization.

## 15. Capability Acquisition — Established Direction

PAE should eventually be able to recognize when a required capability is missing, discover possible resources that could provide it, evaluate them, request authorization when acquisition/use requires it, obtain and process the resource, learn how to use it, verify it and register it for future use.

Conceptually:

```text
NEED CAPABILITY
      ↓
   DISCOVERY
      ↓
   EVALUATE
      ↓
AUTHORIZATION GATE
      ↓
    ACQUIRE
      ↓
 PROCESS / LEARN
      ↓
    VERIFY
      ↓
 REGISTER RESOURCE
      ↓
      USE
```

This is an architectural direction, not a claim that v0.1 will implement autonomous resource acquisition.
