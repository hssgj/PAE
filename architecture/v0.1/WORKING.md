# PAE Architecture v0.1 — Working

> Strong architectural directions that are useful for design, but are not yet fully closed.

## 1. Cognition Cycle

Working model:

```text
OBJECTIVE / NEW STATE
        ↓
     COGNITION
        ↓
INTERPRET → EVALUATE → DECIDE
        ↓
TASK / RESOURCE / STATE CHANGE
        ↓
     EXECUTION
        ↓
      RESULT
        ↓
     COGNITION
```

A cognition cycle should be able to operate on both the original objective and newly produced state.

The next cognition cycle may be triggered by an execution result, failure, changed dependency, newly available resource, user input or another relevant state/event change.

## 2. Cognition as a Decision Layer

Cognition should not simply mean "ask an LLM what to do."

The architecture should contain a decision/cognition mechanism that uses models and other resources as computational components.

Potential inputs:

```text
RULES
REGISTERS
CURRENT STATE
OBJECTIVE
CONTEXT
AVAILABLE RESOURCES
RESULTS
```

Potential decisions:

```text
NEXT ACTION
TASK MODIFICATION
RESOURCE SELECTION
RETRY / REPAIR
WAIT
ASK
CONTINUE
FINISH
```

The exact internal mechanism is intentionally open.

## 3. Models as Replaceable Cognitive Resources

PAE may eventually use multiple external and local models according to task requirements.

A small local model may handle simple semantic parsing or classification while a stronger external model handles a harder reasoning task. Different tasks in the same Task Tree may use different models.

A future PAE-owned/local cognition model is possible, but the architecture must not depend on one specific model.

## 4. Resource Access / Common Doorway

Working direction: resources should be accessible through a common architectural contract even if their internal implementations differ.

Conceptual form:

```text
REQUEST
   ↓
RESOURCE ACCESS
   ↓
INPUT
   ↓
EXECUTE
   ↓
RESULT / STATUS
```

The exact contract, adapters and lifecycle are still open.

## 5. Learning

Long-term learning follows a direction such as:

```text
EXPERIENCE
   ↓
LEARNING
   ↓
PERSISTENT STATE
   ↓
BETTER FUTURE DECISION
```

Useful distinctions remain:

- Memory = X happened / X is true.
- Knowledge = understand X.
- Procedure = know how to do X.
- Experience = done X before.
- Learned strategy = discovered a better way.

Learning should not silently rewrite fundamental identity, security or governing architecture.

## 6. Resource Discovery and Acquisition

PAE should eventually be able to discover resources beyond its current Registry when cognition identifies a missing capability.

Working direction:

```text
MISSING CAPABILITY
      ↓
DISCOVER CANDIDATES
      ↓
EVALUATE
      ↓
REQUEST AUTHORIZATION IF NEEDED
      ↓
ACQUIRE / PROCESS
      ↓
LEARN HOW TO USE
      ↓
TEST / VERIFY
      ↓
REGISTER
```

This is intentionally broader than simply "give PAE internet access." Internet/search is one possible discovery environment among many.

## 7. Verification

Execution results should not automatically be treated as successful simply because a tool returned something.

PAE should be able to compare results against the intended task, dependencies and expected conditions, then decide whether to accept, retry, repair, substitute, continue or escalate.

The exact verification architecture remains open.

## 8. Architecture Boundary

The system should preserve the distinction between:

- Cognition — determines what should happen.
- Registry — describes what resources exist.
- Resource access — obtains access to a resource.
- Execution — performs concrete actions.
- Authorization — determines what is permitted.
- Persistent state — preserves information beyond the current execution/model.

Some of these may eventually be implemented together internally, but the conceptual responsibilities should remain distinguishable.
