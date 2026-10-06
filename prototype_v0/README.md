# PAE prototype_v0

Small, intentionally disposable runtime for the four-day prototype sprint.

## Current status — Local brain GREEN (2026-10-06)

Verified on Android/Termux:

- `prototype_v0` runs against a local Qwen3-1.7B Q4_K_M GGUF through `llama-server`
- local inference works through the OpenAI-compatible `/v1/chat/completions` endpoint
- Qwen thinking can be disabled through `PAE_DISABLE_THINKING=1`
- persisted session history survives runtime and model-server restarts
- a full cold boot succeeded with airplane mode enabled: server off -> network off -> server boot -> PAE boot -> local response
- `~/PAE/start-local.sh <session>` reproduces the working local stack with one command

Current known limitations:

- local 1.7B inference can be slow on long prompts/tool context
- the CLI has no busy/thinking indicator yet, so long generations look frozen
- the model does not inherently know host/device facts unless runtime context or a tool provides them
- network-backed tools such as GitHub still require connectivity when invoked

Next target: add a small truthful busy spinner/status indicator, then continue the bounded read-only tool integration one tool at a time.

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
