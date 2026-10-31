# PAE runtime — CLI + Mobile

The canonical source is hssgj/PAE main. CLI and the recovered mobile branch share one runtime, tool registry and JSON session store.

## Present capabilities

- CLI chat with a busy indicator around provider calls.
- Persistent history, sources and derived structured state.
- OpenAI-compatible model boundary, plus echo for offline smoke tests.
- GitHub read/list/search and prepared writes with separate confirmation.
- Gmail search/read/draft/send with separate confirmation.
- Local mobile HTTP bridge and Android shell source.
- Newer main exact-file routing and unrelated-DOS suppression retained.

The root [start guide](../docs/START_HERE.md) and [launcher map](../docs/LAUNCHERS.md) define current entry points. Model rotation/fallback and the phone-local context guard are not implemented or recovered by this consolidation.

## Offline smoke

From prototype_v0, run `python app.py --session smoke`, enter hello, then /quit. The default echo provider needs no model or API key. Sessions are local and ignored by Git.

Real providers use the existing launchers. Model credentials belong outside the repository.

## Verification boundary

Historical Android/Qwen and Groq milestones are retained as historical evidence. Code merge and local regression checks do not prove current phone installation, API account access, model identity from self-report or APK behavior.

The optional paste/profiling/source-focus helpers are retained, not automatically installed. See the historical PERFORMANCE_PLAN_V0_2.md before invoking an installer. No removed Safety Guard was restored.

## Tests

`python -m pytest -q prototype_v0` from repository root, with pytest installed. Additional stdlib checks: `python -m unittest discover -s tools -v`. Archived experiment tests run from archive/experiments/semantic-task-tree with `python -m unittest discover -s core/tests -v`.
