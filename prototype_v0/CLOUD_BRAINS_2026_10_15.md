# Cloud brains — 2026-10-15

## Verified scope
User ran PAE in Android/Termux and supplied a successful response after configuring:
- Endpoint: https://api.groq.com/openai/v1/chat/completions
- Requested model: openai/gpt-oss-120b
- Key file: ~/.config/pae/groq.key (secret stays outside repository).
- PAE_PROVIDER=openai-compatible; PAE_DISABLE_THINKING=0.
- PAE_CTX_TOKENS=8192; PAE_CTX_MARGIN=384; PAE_MAX_TOKENS=1024.
- User-observed guard input approximately 5011/6784 tokens.
- Original failure: 4096 context with 2048 output and 384 margin left only 1664 input tokens.
- Subsequent HTTP 403 error 1010 resolved in the user workflow after adding User-Agent: PAE/0.1 to local provider.py.
- This verifies a successful user-observed remote response with that configuration, not model identity derived from model self-report or session name, benchmarks, or all tools.

## Launchers
Run from Termux:
    bash "$HOME/PAE/start-groq.sh"
    bash "$HOME/PAE/start-gemini.sh"

Optional first argument selects a session ID. Session name does not select a model. Default Groq session is groq-first-test.
Launchers configure a process-local urllib opener with PAE client identification; no need to overwrite locally modified provider.py.
Both scripts passed bash syntax checks in the assistant environment; these new launcher files still require phone validation.
PAE_ROOT may select a different checkout.
PAE_GROQ_MODEL / PAE_GEMINI_MODEL may explicitly override the requested model.

## Gemini — PREPARED, NOT LIVE VERIFIED
- Key file: ~/.config/pae/gemini.key
- Endpoint: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
- Default requested model: gemini-3.8-flash, documented by Google at preparation time.
- Documentation: https://ai.google.dev/gemini-api/docs/openai and https://ai.google.dev/gemini-api/docs/pricing
- Confirm Free tier in Google AI Studio; local launcher does not enforce provider billing settings.
- Account access, quota, response length including reasoning, and PAE tool-loop behavior require live validation.

## Remaining
- No automatic provider rotation/fallback implemented.
- No native inference of current runtime identity: PAE previously hallucinated Qwen expansion and fake PAE_ENGINE / pae_runtime APIs.
- Do not use model answers as authoritative runtime configuration.
- Original local Qwen launcher remains separate; do not use cloud context settings for local Qwen.
- Do not commit keys, session archives, or replace phone-local modified code with a blind git pull.
