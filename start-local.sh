#!/data/data/com.termux/files/usr/bin/bash

set -u

PAE_ROOT="$HOME/PAE"
APP_DIR="$PAE_ROOT/prototype_v0"
MODEL="$PAE_ROOT/models/Qwen3-1.7B-Q4_K_M.gguf"
LOG="$PAE_ROOT/llama-server.log"
PIDFILE="$PAE_ROOT/llama-server.pid"
HOST="127.0.0.1"
PORT="8080"
SESSION="${1:-local-brain-smoke}"

echo "=== PAE LOCAL BOOT ==="

if ! command -v llama-server >/dev/null 2>&1; then
    echo "ERROR: llama-server not found"
    exit 1
fi

if [ ! -f "$MODEL" ]; then
    echo "ERROR: model not found:"
    echo "$MODEL"
    exit 1
fi

if curl -sf --max-time 2 "http://$HOST:$PORT/health" >/dev/null 2>&1; then
    echo "Local brain already ready."
else
    echo "Starting local brain..."

    if [ -f "$PIDFILE" ]; then
        OLD_PID="$(cat "$PIDFILE" 2>/dev/null || true)"
        if [ -n "${OLD_PID:-}" ]; then
            kill "$OLD_PID" 2>/dev/null || true
        fi
    fi

    llama-server \
        -m "$MODEL" \
        -c 2048 \
        --host "$HOST" \
        --port "$PORT" \
        > "$LOG" 2>&1 &

    echo $! > "$PIDFILE"

    echo "Waiting for local brain..."

    READY=0
    for _ in $(seq 1 60); do
        if curl -sf --max-time 2 "http://$HOST:$PORT/health" >/dev/null 2>&1; then
            READY=1
            break
        fi
        sleep 2
    done

    if [ "$READY" -ne 1 ]; then
        echo "ERROR: local brain did not become ready."
        echo "=== LAST SERVER LOG ==="
        tail -n 30 "$LOG" 2>/dev/null || true
        exit 1
    fi

    echo "Local brain ready."
fi

export PAE_PROVIDER=openai-compatible
export PAE_API_URL="http://$HOST:$PORT/v1/chat/completions"
export PAE_MODEL=local
export PAE_DISABLE_THINKING=1
export PAE_MAX_TOKENS=512

echo "Starting PAE session: $SESSION"
echo

cd "$APP_DIR" || exit 1
exec python app.py --session "$SESSION"
