#!/bin/bash
#SBATCH --job-name=storage_bench
#SBATCH --partition=short
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --output=%x_%j.out

# Weekly storage benchmark. Captures cluster state + bench results
# so we can correlate variance with cluster utilization.
set -euo pipefail

# Resolve the benchmark directory.
# Slurm copies the batch script into /var/tmp/slurmd/... and runs it from
# there, so $BASH_SOURCE points at the staged copy. Use $SLURM_SUBMIT_DIR
# (the directory sbatch was called from) to find the originals. Fall back
# to BASH_SOURCE for manual invocations outside Slurm.
if [[ -n "${SLURM_SUBMIT_DIR:-}" && -f "$SLURM_SUBMIT_DIR/storage_bench.py" ]]; then
    SCRIPT_DIR="$SLURM_SUBMIT_DIR"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
RESULTS_DIR="$SCRIPT_DIR/results"
mkdir -p "$RESULTS_DIR"

TS="$(date +%Y%m%d_%H%M%S)"
HOST="$(hostname -s)"
TAG="${TS}_${HOST}_${SLURM_JOB_ID:-manual}"

STATE_JSON="$RESULTS_DIR/${TAG}_cluster.json"
BENCH_LOG="$RESULTS_DIR/${TAG}_bench.log"

echo "[$TS] starting bench on $HOST (job ${SLURM_JOB_ID:-manual})" >&2

"$SCRIPT_DIR/capture_cluster_state.sh" "$STATE_JSON"

# Run the benchmark, tee full output to the log.
python3 "$SCRIPT_DIR/storage_bench.py" 2>&1 | tee "$BENCH_LOG"

# Extract TSV summary into its own file for easy aggregation.
awk '/^--- tsv summary ---$/{flag=1; next} flag' "$BENCH_LOG" \
    > "$RESULTS_DIR/${TAG}_summary.tsv"

# Capture cluster state again on the way out, in case load shifted.
"$SCRIPT_DIR/capture_cluster_state.sh" "$RESULTS_DIR/${TAG}_cluster_end.json"

echo "[$(date +%Y%m%d_%H%M%S)] done; artifacts under $RESULTS_DIR/${TAG}_*" >&2

# Slurm stdout file: move it into results/ to keep cwd clean.
# (Slurm writes %x_%j.out to the submit directory, not per-job.)
if [[ -n "${SLURM_JOB_ID:-}" ]] && [[ -f "${SLURM_SUBMIT_DIR:-.}/storage_bench_${SLURM_JOB_ID}.out" ]]; then
    mv "${SLURM_SUBMIT_DIR}/storage_bench_${SLURM_JOB_ID}.out" \
       "$RESULTS_DIR/${TAG}_slurm.out" || true
fi
