#!/bin/bash
# Submit a week's worth of storage benchmarks at varied times so the
# results cover different cluster load regimes.
#
# Usage:
#   ./schedule_week.sh            # submit all jobs
#   ./schedule_week.sh --dry-run  # print sbatch lines without submitting
#
# Times chosen to span cluster-load patterns:
#   03:15  — overnight light load
#   09:30  — morning ramp-up
#   14:30  — afternoon peak
#   21:00  — evening wind-down
# 4 runs/day * 7 days = 28 jobs total, each ~10 min of compute.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SBATCH_SCRIPT="$SCRIPT_DIR/bench.sbatch"

TIMES=(03:15 09:30 14:30 21:00)
DAYS=7

DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

submitted=0
skipped=0

# Start from tomorrow so the first slot is in the future.
for day in $(seq 1 $DAYS); do
    base="$(date -d "+${day} days" +%Y-%m-%d)"
    for t in "${TIMES[@]}"; do
        begin="${base}T${t}:00"
        begin_epoch="$(date -d "$begin" +%s)"
        now_epoch="$(date +%s)"
        if (( begin_epoch <= now_epoch )); then
            echo "skip (past): $begin"
            skipped=$((skipped + 1))
            continue
        fi
        if (( DRY )); then
            echo "sbatch --begin=$begin $SBATCH_SCRIPT"
        else
            sbatch --begin="$begin" "$SBATCH_SCRIPT" >&2
        fi
        submitted=$((submitted + 1))
    done
done

echo ""
echo "submitted: $submitted   skipped: $skipped"
if (( ! DRY )); then
    echo "see queue: squeue -u \$USER --sort=S"
fi
