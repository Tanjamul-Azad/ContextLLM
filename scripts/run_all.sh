#!/usr/bin/env bash
# Runs every pilot experiment in order on one GPU and logs each step.
# Usage: bash scripts/run_all.sh
set -u
cd "$(dirname "$0")/.."
mkdir -p results/logs
LOG=results/logs/run_all.log
step() {
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') START $*" | tee -a "$LOG"
  python -I "$@" 2>&1 | grep -v -iE "symlink|developer mode|warnings.warn|Loading weights|Fetching" >> "$LOG"
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') END   $* (exit ${PIPESTATUS[0]})" | tee -a "$LOG"
}

step src/run_behaviour.py qwen2.5-3b
step src/logit_lens.py qwen2.5-3b
step src/contamination.py qwen2.5-3b 60

# the 7B weights may still be downloading
until python -I -c "from huggingface_hub import snapshot_download as s; s('unsloth/Qwen2.5-7B-Instruct-bnb-4bit', local_files_only=True, allow_patterns=['*.safetensors'])" >/dev/null 2>&1 \
      && ls /d/huggingface_cache/hub/models--unsloth--Qwen2.5-7B-Instruct-bnb-4bit/snapshots/*/model*.safetensors >/dev/null 2>&1 \
      && [ -z "$(ls /d/huggingface_cache/hub/models--unsloth--Qwen2.5-7B-Instruct-bnb-4bit/blobs/*.incomplete 2>/dev/null)" ]; do sleep 30; done
step src/run_behaviour.py qwen2.5-7b-4bit
step src/run_behaviour.py llama3.1-8b-4bit
step src/wildchat_mine.py 150 qwen2.5-3b
step src/analyze.py
echo "=== ALL DONE $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
