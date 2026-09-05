# PAE Architecture v0.1 — Open

> Remaining architectural questions. Nothing in this file should be treated as closed until explicitly resolved.

## 1. Environment / Host

Where does PAE actually live and operate?

Need to define the conceptual execution environment, including:

- runtime
- filesystem / persistent storage
- network access
- secrets and credentials
- processes and services
- what remains alive continuously
- what may be temporary

## 2. Resource Access Contract

How does PAE reach and invoke a resource once Cognition has selected it?

Questions:

- What is the common doorway between PAE and different resources?
- What information is required for a request?
- How are inputs and outputs represented?
- How are errors/status returned?
- How are resource-specific adapters represented?

## 3. Registry Lifecycle & Discovery

The Registry's basic purpose is established, but its lifecycle is not.

Still to define:

- registration
- discovery
- querying
- dynamic appearance/disappearance
- resource evaluation
- stale descriptions
- unavailable/broken resources
- version changes
- trust/quality information

## 4. Failure & Recovery Model

The principle is established: failure should trigger diagnosis and reasonable recovery attempts before final escalation.

Still to define:

- failure categories
- detection
- retry rules
- alternative selection
- repair-task creation
- rollback / preservation of progress
- partial completion
- repeated failure handling
- when a failure becomes a genuine boundary

## 5. Authorization & Safety Gates

The separation between capability and authorization is established.

Still to define the architecture of:

- authorization policies
- human confirmation
- irreversible actions
- sensitive operations
- credential boundaries
- approval scope
- expiration/reuse of approval
- actions that must never be autonomous

The intended principle remains: authorization should be an ultimate execution gate, not continuous micromanagement of cognition.

## 6. Persistent State / Memory Final Pass

Need a final architectural distinction among:

- execution state
- task history
- persistent memory
- knowledge
- learned procedures
- experience
- identity
- canonical/governing state

Also determine which state can be rewritten automatically and which requires stronger protection.

## 7. Cognition Cycle Formalization

The working cognition loop is clear enough to continue design, but its formal contract remains open.

Need to define:

- exact cycle inputs
- exact cycle outputs
- state transition
- what constitutes a new cycle
- how concurrent work is represented
- how cognition observes and reconciles parallel results
- termination conditions

## 8. Capability Acquisition Boundary

The long-term direction is established: PAE may discover missing capabilities and eventually acquire, learn and register them.

Still open:

- which resource types may be acquired autonomously
- which require human authorization
- how candidate resources are evaluated
- how untrusted resources are isolated
- how newly acquired capabilities are tested
- when a capability becomes trusted/registered
- how acquisition can be reversed

## 9. Final Architecture Gate

Before architecture v0.1 becomes final canon, verify that the above boundaries form a coherent system without hidden responsibility overlap or missing transition between layers.

No implementation should be forced merely to make the architecture look complete.
