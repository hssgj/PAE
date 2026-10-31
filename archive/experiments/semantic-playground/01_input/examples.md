# 01 — Input Examples

This folder contains the raw sentences we use as experiments in the Semantic Playground.

The goal is **not** to answer the questions yet.

We first observe what information is present in the sentence and what a semantic system would need to identify before an answer can be produced.

---

## Example 01 — Dog and blackberries

**Raw input:**

> Zjisti mi, jestli pes může jíst ostružiny.

### First observations

- `Zjisti mi` → request / instruction
- `jestli` → yes/no question structure
- `pes` → entity / animal
- `může` → possibility / permission / safety modality
- `jíst` → action
- `ostružiny` → entity / food

### Initial semantic sketch

```text
request = determine whether
subject = pes
action = jíst
object = ostružiny
question_type = possibility
```

**Important:** This is an observation, not a final semantic representation. We will refine it as the experiment develops.

---

## Example 02 — Simple factual question

**Raw input:**

> Kolik má pes nohou?

### First observations

- `Kolik` → quantity question
- `pes` → entity / animal
- `má` → possession / attribute relation
- `nohou` → body-part entity / countable attribute

### Initial semantic sketch

```text
question_type = quantity
subject = pes
relation = má
object = nohy
```

---

## Example 03 — Context-dependent sentence

**Raw input:**

> A může je jíst taky?

### First observations

This sentence is intentionally ambiguous when isolated.

- `A` → continuation marker
- `může` → possibility / permission / modality
- `je` → pronoun; meaning depends on context
- `jíst` → action
- `taky` → addition / also

### Initial semantic sketch

```text
question_type = possibility
subject = UNKNOWN
relation = jíst
object = UNKNOWN
modifier = také
context_required = true
```

This example exists to demonstrate that **meaning is not always contained entirely inside one sentence**.

---

## Experiment rule

For now, preserve the raw input exactly as written.

Do not silently fix grammar, translate, answer, or invent missing context.

**Raw input → observation → semantic hypothesis.**

Later experiments will test what happens between these stages.
