# Checkpoints

## 2026-09-06 — Fake LLM checkpoint

Current educational objective:

Show that the language-intelligence layer and PAE/orchestration layer are separate components.

Current experiment:

`experiments/03_fake_llm.py`

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
