#!/bin/bash
# Snapshot Slurm/Grafana cluster state at benchmark time.
# Writes a JSON file with CPU alloc, node states, and the load of
# the node we're running on. Used to correlate benchmark variance
# with cluster utilization.
set -euo pipefail

out=${1:?usage: capture_cluster_state.sh <output.json>}

# Grafana Prometheus datasource proxy (no auth needed for read queries).
G="https://grafana.fredhutch.org/api/datasources/proxy/1/api/v1/query"

q() {
  # Args: promql query. Returns value[1] or "null".
  curl -sS --max-time 10 --get --data-urlencode "query=$1" "$G" \
    | jq -r '.data.result[0].value[1] // "null"'
}

host=$(hostname -s)

cat > "$out" <<EOF
{
  "timestamp_iso":       "$(date -Iseconds)",
  "timestamp_epoch":     $(date +%s),
  "hostname":            "$host",
  "slurm_job_id":        "${SLURM_JOB_ID:-manual}",
  "slurm_partition":     "${SLURM_JOB_PARTITION:-unknown}",
  "slurm_cpus_alloc":    "$(q 'slurm_cpus_alloc')",
  "slurm_cpus_total":    "$(q 'slurm_cpus_total')",
  "slurm_cpus_other":    "$(q 'slurm_cpus_other')",
  "slurm_gpus_alloc":    "$(q 'slurm_gpus_alloc')",
  "slurm_gpus_total":    "$(q 'slurm_gpus_total')",
  "slurm_nodes_alloc":   "$(q 'slurm_nodes_alloc')",
  "slurm_nodes_idle":    "$(q 'slurm_nodes_idle')",
  "slurm_nodes_mix":     "$(q 'slurm_nodes_mix')",
  "slurm_nodes_down":    "$(q 'slurm_nodes_down')",
  "slurm_nodes_drain":   "$(q 'slurm_nodes_drain')",
  "this_node_load15":    "$(q "node_load15{instance=~\"$host.*\"}")",
  "this_node_mem_pct":   "$(q "100-((node_memory_MemAvailable_bytes{instance=~\"$host.*\"}*100)/node_memory_MemTotal_bytes{instance=~\"$host.*\"})")"
}
EOF
