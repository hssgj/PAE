#!/data/data/com.termux/files/usr/bin/bash

set -u

PAE_ROOT="$HOME/PAE"
APP_DIR="$PAE_ROOT/prototype_v0"
MODEL="$PAE_ROOT/models/Qwen3-1.7B-Q4_K_M.gguf"
LLAMA_LOG="$PAE_ROOT/llama-server.log"
LLAMA_PID="$PAE_ROOT/llama-server.pid"
MOBILE_LOG="$PAE_ROOT/mobile-server.log"
MOBILE_PID="$PAE_ROOT/mobile-server.pid"
MOBILE_HASH="$PAE_ROOT/mobile-server.codehash"
GMAIL_ENV="$HOME/.config/pae/gmail.env"

if [ -f "$GMAIL_ENV" ]; then
    set -a
    . "$GMAIL_ENV"
    set +a
fi

if ! curl -sf --max-time 2 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    llama-server -m "$MODEL" -c 2048 --host 127.0.0.1 --port 8080 > "$LLAMA_LOG" 2>&1 &
    echo $! > "$LLAMA_PID"
fi

for _ in $(seq 1 60); do
    curl -sf --max-time 2 "http://127.0.0.1:8080/health" >/dev/null 2>&1 && break
    sleep 2
done

if ! curl -sf --max-time 2 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    echo "ERROR: local brain did not become ready"
    exit 1
fi

export PAE_PROVIDER=openai-compatible
export PAE_API_URL="http://127.0.0.1:8080/v1/chat/completions"
export PAE_MODEL=local
export PAE_DISABLE_THINKING=1
export PAE_MAX_TOKENS=512

CODE_HASH="$(sha256sum \
    "$APP_DIR/mobile_server.py" \
    "$APP_DIR/agent_loop.py" \
    "$APP_DIR/runtime_tools.py" \
    "$APP_DIR/gmail_source.py" \
    "$APP_DIR/sessions.py" \
    | sha256sum | cut -d' ' -f1)"

RUNNING_HASH="$(cat "$MOBILE_HASH" 2>/dev/null || true)"
if curl -sf --max-time 2 "http://127.0.0.1:8765/api/health" >/dev/null 2>&1; then
    if [ "$RUNNING_HASH" = "$CODE_HASH" ]; then
        echo "PAE mobile already ready"
        exit 0
    fi
    OLD_MOBILE_PID="$(cat "$MOBILE_PID" 2>/dev/null || true)"
    if [ -n "${OLD_MOBILE_PID:-}" ]; then
        kill "$OLD_MOBILE_PID" 2>/dev/null || true
        sleep 1
    fi
fi

cd "$APP_DIR" || exit 1
nohup python mobile_server.py > "$MOBILE_LOG" 2>&1 &
echo $! > "$MOBILE_PID"
echo "$CODE_HASH" > "$MOBILE_HASH"

for _ in $(seq 1 30); do
    curl -sf --max-time 2 "http://127.0.0.1:8765/api/health" >/dev/null 2>&1 && exit 0
    sleep 1
done

echo "ERROR: PAE mobile server did not become ready"
tail -n 30 "$MOBILE_LOG" 2>/dev/null || true
exit 1
