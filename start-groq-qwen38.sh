#!/data/data/com.termux/files/usr/bin/bash
set -eu
: "${PAE_GROQ_MODEL:?Set PAE_GROQ_MODEL to a verified available Groq model ID for this historical launcher}"
PAE_ROOT="${PAE_ROOT:-$HOME/PAE}"
export PAE_GROQ_MODEL
exec bash "$PAE_ROOT/start-groq.sh" "groq-qwen38"
