# PAE prototype_v0

Small, intentionally disposable runtime for the four-day prototype sprint.

## What it does

- CLI chat loop
- persistent JSON sessions
- load UTF-8 game logs / canon / notes into a session
- provider boundary with:
  - `echo` for zero-dependency smoke tests
  - any OpenAI-compatible `/v1/chat/completions` endpoint

It deliberately does **not** contain registries, agents, a database, UI, semantic
memory, autodiscovery, or the future PAE architecture.

## Smoke test

```bash
cd prototype_v0
python app.py --session smoke
```

Type `hello`, exit with `/quit`, then run the same command again. The session
file survives in `prototype_v0/data/sessions/`.

## Load a game log

```bash
python app.py --session hp5e --load ../path/to/log.txt
```

You can also load files while running:

```text
/load ../path/to/canon.txt
/sources
```

## Connect a real model

The runtime expects an OpenAI-compatible chat-completions endpoint.

Linux/macOS:

```bash
export PAE_PROVIDER=openai-compatible
export PAE_API_URL=http://127.0.0.1:1234/v1/chat/completions
export PAE_MODEL=your-model-name
python app.py --session hp5e
```

PowerShell:

```powershell
$env:PAE_PROVIDER="openai-compatible"
$env:PAE_API_URL="http://127.0.0.1:1234/v1/chat/completions"
$env:PAE_MODEL="your-model-name"
python app.py --session hp5e
```

`PAE_API_KEY` is optional for local servers and can be set when the endpoint
requires a bearer token.

## Acceptance target

Load a real HP5e log/canon, have the model understand the setting and current
state, continue as GM in chat, exit, reopen the same session, and continue
without losing the persisted history/source material.
