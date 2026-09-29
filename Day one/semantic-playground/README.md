# Semantic Playground

A small learning laboratory for understanding how language can become structured interpretation and how that interpretation can feed an orchestration system.

## Purpose

Semantic Playground is **not PAE implementation**.

It is a sequence of tiny executable experiments designed to make the following pipeline visible:

RAW INPUT
→ INTERPRETATION
→ SEMANTIC REPRESENTATION
→ GROUNDING
→ CONTEXT
→ STATE
→ INTENT
→ TASK
→ ORCHESTRATION
→ ACTION
→ RESULT
→ STATE UPDATE

Experiments are designed to run on Android with Pydroid 3.

## Core rules

- Continuity > Convenience
- Canon ≠ Idea
- Unknown ≠ Invented
- Model abstraction ≠ literal internal LLM mechanism
- Retrieval ≠ Generation
- Memory ≠ State
- Task ≠ Action
- Words ≠ Meaning

## Current path

0.1 — manual semantic fields
0.2 — rule-based extraction
0.3 — fake LLM boundary
0.4 — concept / typo / similarity experiment
0.5 — concepts and relations
0.6 — embeddings
0.7 — real LLM
0.8 — structured LLM output
0.9 — memory
1.0 — tools + orchestration
1.x — agent loop

## Current experiment

**0.4 / Typo + concept similarity — foundation in place, similarity not implemented yet**

The previous 0.3 experiment established the boundary:

LANGUAGE INTERPRETATION ≠ PAE ORCHESTRATION

The repository now also contains the first two foundation pieces for 0.4:

1. `02_tokenization/tokenizer.py`
   - transforms raw text into simple word / punctuation tokens,
   - deliberately does not imitate a production LLM tokenizer.

2. `02_tokenization/vocabulary_lookup.py` + `data/vocabulary/cz-mini.tsv`
   - performs exact lookup of known Czech wordforms,
   - returns every matching analysis,
   - deliberately keeps unknown words UNKNOWN.

### What exists now

RAW TEXT
→ SIMPLE TOKENS
→ EXACT VOCABULARY LOOKUP
→ KNOWN / UNKNOWN ANALYSES

### What does not exist yet

- typo correction or fuzzy matching,
- similarity scoring,
- concept normalization beyond exact known forms,
- relation extraction,
- embeddings,
- a real LLM boundary.

The next experiment is therefore still the missing part of 0.4:

> Resolve a controlled typo / near-match such as `jisg` toward the intended concept `jíst` without pretending that exact lookup already understands language.

Target example:

`muze nessie jisg ostruziny?`

should eventually become approximately:

- subject = Nessie
- action = EAT
- object = BLACKBERRY
- intent = INFORMATION_REQUEST

while keeping confidence, ambiguity and UNKNOWN behavior visible.

## Current files

- `01_semantic_units.py` — 0.1 manual semantic representation
- `02_rule_parser.py` — 0.2 rule-based extraction
- `03_fake_llm.py` — 0.3 fake LLM boundary
- `02_tokenization/tokenizer.py` — 0.4 foundation: tokenization
- `02_tokenization/vocabulary_lookup.py` — 0.4 foundation: exact vocabulary lookup
- `data/vocabulary/cz-mini.tsv` — deliberately small Czech teaching vocabulary
- `checkpoints.md` — chronological learning checkpoints
- `roadmap.md` — experiment progression

## Device

Current: Android + Pydroid 3

Later: Termux for actual PAE development.
