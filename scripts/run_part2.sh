#!/usr/bin/env bash
# Second batch: 4-bit models need the conda Python (it has bitsandbytes), plus OASST2 mining.
set -u
cd "$(dirname "$0")/.."
LOG=results/logs/run_all.log
PY=/f/cONDA/python
step() {
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') START $*" | tee -a "$LOG"
  "$PY" -s "$@" 2>&1 | grep -v -iE "symlink|developer mode|warnings.warn|Loading weights|Fetching" >> "$LOG"
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') END   $* (exit ${PIPESTATUS[0]})" | tee -a "$LOG"
}
step src/run_behaviour.py qwen2.5-7b-4bit
step src/run_behaviour.py llama3.1-8b-4bit
step src/wildchat_mine.py 150 qwen2.5-3b oasst
step src/analyze.py
step src/make_results.py
echo "=== PART2 DONE $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
