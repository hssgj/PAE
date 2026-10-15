#!/data/data/com.termux/files/usr/bin/bash
set -eu
PAE_ROOT="${PAE_ROOT:-$HOME/PAE}"
KEY_FILE="$HOME/.config/pae/groq.key"
if [ ! -s "$KEY_FILE" ]; then
  echo "Missing key file: $KEY_FILE (store only the API key there)."
  exit 1
fi
chmod 600 "$KEY_FILE"
export PAE_API_KEY="$(tr -d '\r\n' < "$KEY_FILE")"
if [ -z "$PAE_API_KEY" ]; then echo "Empty API key."; exit 1; fi
export PAE_PROVIDER=openai-compatible
export PAE_API_URL="https://api.groq.com/openai/v1/chat/completions"
export PAE_MODEL="${PAE_GROQ_MODEL:-openai/gpt-oss-120b}"
export PAE_DISABLE_THINKING=0
export PAE_CTX_TOKENS=8192
export PAE_CTX_MARGIN=384
export PAE_MAX_TOKENS=1024
cd "$PAE_ROOT/prototype_v0"
echo "[configured] provider=groq model=$PAE_MODEL; automatic fallback is not installed."
exec python -c 'import runpy, urllib.request; opener=urllib.request.build_opener(); opener.addheaders=[("User-Agent", "PAE/0.1"), ("x-goog-api-client", "pae/0.1")]; urllib.request.install_opener(opener); runpy.run_path("app.py", run_name="__main__")' --session "${1:-groq-first-test}"
