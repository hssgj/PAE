#!/data/data/com.termux/files/usr/bin/bash
set -eu
PAE_ROOT="${PAE_ROOT:-$HOME/PAE}"
export PAE_GROQ_MODEL="qwen/qwen3.8-27b"
exec bash "$PAE_ROOT/start-groq.sh" "groq-qwen38"
