# PAE prototype_v0

Small, intentionally disposable runtime for the four-day prototype sprint.

## Current status — Day 1 GREEN (2026-10-05)

Verified on Android/Termux with a real OpenRouter-backed LLM:

- real provider request/response path works
- JSON session persistence survives multiple process restarts
- separate session ids stay isolated
- smoke testing exceeded 10 user/assistant turns

Known non-blocking issues found during smoke testing:

- Ctrl+C while waiting for the provider currently emits a traceback
- an interrupted inference can leave a persisted user-only pending turn
- the actual routed model id returned by OpenRouter is not yet surfaced
- `openrouter/free` may route to different free models, so response quality/style varies

Next target: add the smallest read-only GitHub source loader, fetch one known file from `hssgj/PAE`, persist it as session source context, and use it in one real-model answer. Do not widen this into general PAE architecture or other integrations yet.

## What it does

- CLI chat loop
- persistent JSON sessions
- load UTF-8 logs / canon / notes into a session
- structured source-state extraction into:
  - `canon`
  - `characters`
  - `current_scene`
  - `important_facts`
  - `unknowns`
- persistent derived state survives restart and is fed back into later chat
- provider boundary with:
  - `echo` for zero-dependency smoke tests
  - any OpenAI-compatible `/v1/chat/completions` endpoint

The extractor is explicitly source-grounded: unsupported scene values stay
`UNKNOWN` instead of being guessed.

It deliberately does **not** contain registries, agents, a database, UI,
semantic memory, autodiscovery, or the future PAE architecture.

## Smoke test

```bash
cd prototype_v0
python app.py --session smoke
```

Type `hello`, exit with `/quit`, then run the same command again. The session
file survives in `prototype_v0/data/sessions/`.

## Load source material

```bash
python app.py --session test --load ../path/to/log.txt
```

You can also load files while running:

```text
/load ../path/to/canon.txt
/sources
```

## Extract structured state

State extraction requires a real model provider; the echo provider intentionally
refuses to fake semantic understanding.

After connecting a real provider:

```text
/analyze
/state
```

Or load and analyze before the chat starts:

```bash
python app.py --session test --load ../path/to/log.txt --analyze
```

The extracted state is saved inside the same session JSON and is automatically
included in future model context.

## Connect a real model

The runtime expects an OpenAI-compatible chat-completions endpoint.

Linux/macOS:

```bash
export PAE_PROVIDER=openai-compatible
export PAE_API_URL=http://127.0.0.1:1234/v1/chat/completions
export PAE_MODEL=your-model-name
python app.py --session test
```

PowerShell:

```powershell
$env:PAE_PROVIDER="openai-compatible"
$env:PAE_API_URL="http://127.0.0.1:1234/v1/chat/completions"
$env:PAE_MODEL="your-model-name"
python app.py --session test
```

`PAE_API_KEY` is optional for local servers and can be set when the endpoint
requires a bearer token.

## Day 2 acceptance target

Load one real `.txt` or `.md` source, run `/analyze`, and get a persisted
source-grounded summary of canon, characters, current scene, and important facts.
Missing details remain `UNKNOWN`. Exit, reopen the session, run `/state`, and
confirm that the extracted state survived the restart.
