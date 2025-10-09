#!/bin/bash
set -euo pipefail

# 
ROOT=/Users/shirinnataneli/Documents/Research/ancestry_switches/TraceAdmix/final_code/TraceAdmix/simulations
N=100 # UPDATE
START_GEN=1899
GEN_FIRST=$((START_GEN + 2))   # first processed generation (1901)
GEN_COUNT=11                   # gens processed (1901..1911)
REPS=10                        # reps 0..9
ADMIX_POP=2
TREE_PATH=tree_outputs/constant_recomb/ # UPDATE: if running variable recomb case change path to "tree_outputs/recomb_map/"
OUT_DIR=obs_switches/constant_recomb/  # UPDATE: if running variable recomb case change path to "obs_switches/recomb_map/"
HEARTBEAT=200000
PY=./sim_switch_analysis_reps.py

cd "$ROOT"

# Loop over reps and gens
for REP in $(seq 0 $((REPS-1))); do
  for ((OFF=0; OFF<GEN_COUNT; OFF++)); do
    GEN=$((GEN_FIRST + OFF))
    OUT_FILE="$OUT_DIR/observed_switches_rep_${REP}_gen_${GEN}.csv"

    if [[ -f "$OUT_FILE" ]]; then
      echo "Skipping rep=$REP gen=$GEN (already exists: $OUT_FILE)"
      continue
    fi

    echo "=== $(date)  n=$N  rep=$REP  gen=$GEN ==="
    python "$PY" \
      --n "$N" \
      --rep "$REP" \
      --gen "$GEN" \
      --start-gen "$START_GEN" \
      --admix-pop-id "$ADMIX_POP" \
      --tree-path "$TREE_PATH" \
      --out-dir "$OUT_DIR" \
      --heartbeat "$HEARTBEAT"
  done
done