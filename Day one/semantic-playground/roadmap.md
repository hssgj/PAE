# Roadmap

## Foundation

- [x] 0.1 Manual semantic fields
- [x] 0.2 Rule-based extraction
- [x] 0.3 Fake LLM boundary
- [ ] 0.4 Typo + concept similarity
  - [x] 0.4a Simple tokenization
  - [x] 0.4b Exact vocabulary lookup
  - [ ] 0.4c Controlled typo / near-match resolution
  - [ ] 0.4d Explicit confidence / ambiguity handling
- [ ] 0.5 Concepts + relations
- [ ] 0.6 Embeddings
- [ ] 0.7 Real LLM
- [ ] 0.8 Structured LLM output
- [ ] 0.9 Persistent memory
- [ ] 1.0 Tools + orchestration
- [ ] 1.x Agent loop

## Current next step

Implement only the missing 0.4 similarity layer.

First target:

`muze nessie jisg ostruziny?`

The experiment should demonstrate how an unknown token can become a candidate known concept without silently pretending certainty.

Do not jump to embeddings, a real LLM, memory or orchestration before this boundary is understood.

## Boundary to preserve

FAKE/REAL LLM
    =
language intelligence

PAE
    =
orchestration + memory + context + state + tools + task management + continuity

Do not collapse these layers.
