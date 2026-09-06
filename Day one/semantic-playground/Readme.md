# Semantic Playground

A small laboratory for learning how language can be transformed into structured meaning.

This is **not** an attempt to manually build a full LLM.

Instead, we build simplified experiments that let us observe the path from natural language toward something a machine could reason over.

## Current experiment

We are starting with a simple Czech sentence:

> Zjisti mi, jestli pes může jíst ostružiny.

The first experiment separates:

```text
RAW INPUT
   ↓
TOKENS
   ↓
LINGUISTIC ROLES
   ↓
RELATIONS
   ↓
SEMANTIC REPRESENTATION
   ↓
KNOWLEDGE / REASONING
   ↓
ANSWER
```

The important boundary is this:

**Understanding a question is not the same thing as knowing its answer.**

## Structure

### `01_input/`
Raw sentences and initial human observations.

### `02_tokenization/`
Experiments with breaking language into smaller units.

### `03_semantics/`
Experiments with entities, actions, relations, modality, intent, and meaning.

### `04_context/`
Experiments showing how surrounding conversation changes meaning.

### `05_fake_llm/`
A deliberately simplified model that lets us run the pipeline ourselves and see what each stage contributes.

## Rules of the playground

- **Observe before formalizing.**
- **Raw input stays raw.**
- **Do not confuse tokens with meaning.**
- **Do not invent missing context.**
- **Do not claim that the simplified experiment is the exact internal process of an LLM.**
- **Unknown stays UNKNOWN until evidence resolves it.**

The playground is allowed to evolve. Its structure should follow what we actually discover, rather than pretending the final architecture is already known.
