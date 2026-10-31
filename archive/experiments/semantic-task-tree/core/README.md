# PAE Core prototype — semantic units → Task Tree v0.1

**Status: experiment / implementation proposal; not architecture canon.** This folder is separate from `Day one/semantic-playground` and preserves the existing architecture documents.

## What actually works
- A supplied structured interpretation becomes provenance-tagged Semantic Units.
- Each task links to a unit, has explicit dependencies and a verifiable acceptance criterion.
- Task Tree can grow and dependencies can be revised; missing dependencies and cycles are rejected.
- `ready()` respects dependencies, unresolved unknowns and explicit approval flags.
- `start / finish / retry` maintain state and append an inspectable revision log.
- `snapshot()` exports JSON; **saving that JSON durably is not implemented**.

## What is not implemented
Free-text understanding, Qwen inference, contextual retrieval, real tool execution, independent result verification, durable database, authorization policy, crash recovery or autonomous scheduling. The caller supplies interpretation, evidence, approvals and verification. Do not equate `verified=True` supplied by a caller with independent verification.

## Run tests
```sh
python -m unittest discover -s core/tests -v
```

## Integration boundary
A future model adapter should return a validated structured interpretation and label its provenance as `model`, not `user` or `tool`. A separate evidence/authorization/verification layer will evaluate it before side effects. The registry maps required capabilities to available resources; this prototype only records requirements.
