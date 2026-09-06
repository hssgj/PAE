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

**0.3 / Fake LLM**

Goal:

LANGUAGE INTERPRETATION ≠ PAE ORCHESTRATION

The fake LLM intentionally uses simple rules. It simulates the interface a real language model could provide:

natural language → structured interpretation

The surrounding code handles grounding, situation/context, task creation and orchestration.

## Device

Current: Android + Pydroid 3

Later: Termux for actual PAE development.
