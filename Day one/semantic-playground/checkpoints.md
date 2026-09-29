# Checkpoints

## 2026-09-06 — Fake LLM checkpoint

Current educational objective:

Show that the language-intelligence layer and PAE/orchestration layer are separate components.

Current experiment:

`03_fake_llm.py`

Observed behavior:

- "Může Nessie jíst ostružiny?" → successful semantic interpretation.
- "Může ten pes žrát ostružiny?" → deliberate reference-resolution limitation.
- Typo such as "jisg" → deliberate fake-LLM failure because the current implementation uses exact string matching.

Next experiment:

Concept / typo / similarity resolution.

Target:

"muze nessie jisg ostruziny?"

should eventually become approximately:

subject = Nessie
action = EAT
object = BLACKBERRY
intent = INFORMATION_REQUEST

without pretending that the toy system is a real LLM.

## 2026-09-07 — Tokenization + vocabulary foundation

Added:

- `02_tokenization/tokenizer.py`
- `02_tokenization/vocabulary_lookup.py`
- `data/vocabulary/cz-mini.tsv`

Observed behavior:

- Raw Czech text can be split into simple word / punctuation tokens.
- Known wordforms can be mapped to lemma, category and role.
- Multiple analyses are preserved instead of silently selecting one.
- Unknown tokens remain UNKNOWN.

Important boundary:

This is still exact lookup. It does **not** yet solve typo similarity, semantic similarity or concept resolution.

## 2026-09-29 — Re-entry truth sync

Repository state was reviewed against the documentation.

Confirmed complete:

- 0.1 manual semantic fields
- 0.2 rule-based extraction
- 0.3 fake LLM boundary
- 0.4 foundation: tokenization
- 0.4 foundation: exact vocabulary lookup

Confirmed not yet implemented:

- typo / fuzzy matching
- similarity scoring
- concept normalization beyond exact known forms
- relations
- embeddings
- real LLM integration

Current experiment:

**0.4 / Typo + concept similarity**

Current boundary:

RAW TEXT
→ SIMPLE TOKENS
→ EXACT VOCABULARY LOOKUP
→ KNOWN / UNKNOWN

Next concrete experiment:

Add one controlled similarity step that can resolve a typo such as `jisg` toward `jíst`, while keeping uncertainty and UNKNOWN explicit.

Target remains:

`muze nessie jisg ostruziny?`

→ approximately:

subject = Nessie
action = EAT
object = BLACKBERRY
intent = INFORMATION_REQUEST
