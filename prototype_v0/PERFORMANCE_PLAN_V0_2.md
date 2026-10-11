# PAE Response Speed Optimization v0.2 — Recovered plan
Date: 2026-10-11; scope: Android/Termux, PAE Mobile, local Qwen3-1.7B Q4_K_M.

## Protect
- Do not overwrite local app.py, provider.py, start-local.sh, context_guard.py, branch changes, sessions or archives.
- Preserve Memory Guard, context 4096, one server slot, spinner. Safety Guard remains rolled back.
- Local runtime tests must be completed by user; remote commits alone are not validation.

## A–F workstreams
| Key | Workstream | Status |
|---|---|---|
| A | Timings, prompt vs inference vs tool latency | Initial baseline done, optional profiler prepared |
| B | Source/context selection | Memory Guard local; focused excerpt helper prepared, untested locally |
| C | Selective GitHub routing | 11 simulated tests passed; live multiline test failed |
| D | Prompt caching | llama.cpp documented default enabled; real cache reuse not verified |
| E | CPU threads, backend, slots | 1 slot verified; 8 CPU threads logged; backend tuning untested |
| F | Streaming | Spinner works; true token streaming not installed |

## Primary newly discovered issue
- app.py reads user messages with a single call to Python input(), so pasted multiline prompts are split into independent turns.
- The routing unit tests assumed one multiline message. Thus passing them did not validate the mobile CLI input path.
- In the failed live test Qwen read README.md then searched GitHub; it never read either explicit recipe file.
- Both exact recipe paths were verified present in hssgj/frostfire_concepts on main.
- Together the recipes have over 16,000 characters, which compete with a working budget of 3200 tokens.

## Prepared (optional, not yet installed/tested on the phone)
- paste_input.py: /paste to start collecting lines, /end to submit one message.
- perf_log.py: records duration, character counts and message count, never prompt contents.
- source_focus.py: source excerpts for dough technique in model's working context, while full GitHub sources remain archived.
- installers create backups, anchor-check local files, syntax-check before modifying app.py and agent_loop.py.

## Measured baseline
- Four slots: 7–11 prompt tokens/s and 0.6–1.9 generation tokens/s with KV warnings.
- One slot: 664 prompt tokens in 57.6 s (11.53 tok/s), 58 output tokens in 27.1 s (2.11 tok/s), 0 KV warnings.
- Only one measurement at one slot; more controlled benchmarks required.

## Next validation
1. Fetch only added helper files; run helper tests.
2. Install opt-in /paste, profiling and focused-source patches, verify Python compilation.
3. Rerun existing routing regression suite; use /paste in an actual new session.
4. Compare runtime timings and tool calls, keeping Memory Guard and local archives untouched.
5. Tune CPU threads only with measured comparisons; safe streaming requires withholding tool JSON.

Do not re-enable the removed Safety Guard or blindly upgrade to a larger phone model.
