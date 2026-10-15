#!/data/data/com.termux/files/usr/bin/bash
set -eu
PAE_ROOT="${PAE_ROOT:-$HOME/PAE}"
export PAE_GROQ_MODEL="openai/gpt-oss-20b"
exec bash "$PAE_ROOT/start-groq.sh" "groq-gpt-oss-20b"
