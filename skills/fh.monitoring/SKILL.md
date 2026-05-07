---
description: "Monitor Fred Hutch HPC cluster utilization, job queues, node health, and storage via Grafana/Prometheus and Slurm commands"
---

# HPC Monitoring

TRIGGER when: user asks about cluster utilization, node status, GPU availability, queue depth, job failures, storage usage, how busy the cluster is, monitoring dashboards, rhino load, or temperature

## Grafana Dashboards

Fred Hutch runs Grafana at `grafana.fredhutch.org` backed by Prometheus (`prometheus.fredhutch.org`), InfluxDB, and CloudWatch. The API is queryable without authentication for read-only access.

### Key Dashboards for HPC Users

| Dashboard | UID | What it shows |
|-----------|-----|---------------|
| SLURM Dashboard | `wDBLiGoGk` | CPU/GPU allocation, node states, job queues, scheduler performance, per-account/user pie charts |
| HPC Metrics | `000000004` | SLA adherence, per-partition job status, per-account cores, Gizmo + Beagle |
| SLURM Users and Accounts | `41ukeATGk` | Per-user and per-account resource breakdown (filterable) |
| Rhino Servers | `HvsO4InGk` | Rhino01-03 CPU, RAM, swap, load, heavy users, network, disk |
| Gizmo Facility Metrics | `v6s05e9Nz` | Node temperatures, power consumption, pod-level aggregates |
| QBR Dash | `l-402TrMz` | Days >80% allocation, CPU utilization ratio, GPU utilization |

### Storage Dashboards

| Dashboard | UID | What it shows |
|-----------|-----|---------------|
| Fast File | `iXVX2whZk` | BeeGFS/Thorium: status, capacity %, request rates, transfer rates |
| Data Core Storage Usage | `dy5I3SIMk` | Per-PI storage consumption (transitioning to Starfish) |
| Storage Usage Trends | `weIvHl0Gk` | Historical storage growth per PI (Fast/Economy tiers) |
| Storage Bottleneck? | `SDlmBYEZk` | ZFS throughput/latency, network I/O on storage nodes |
| Performance Troubleshooting | `4MtUNFEWz` | BeeGFS user/client IOPS, throughput, CPU iowait |

### Direct Dashboard Links

```
https://grafana.fredhutch.org/d/wDBLiGoGk/slurm-dashboard
https://grafana.fredhutch.org/d/000000004/hpc-metrics
https://grafana.fredhutch.org/d/41ukeATGk/slurm-users-and-accounts
https://grafana.fredhutch.org/d/HvsO4InGk/rhino-servers
https://grafana.fredhutch.org/d/v6s05e9Nz/gizmo-facility-metrics
https://grafana.fredhutch.org/d/dy5I3SIMk/data-core-storage-usage
https://grafana.fredhutch.org/d/iXVX2whZk/fast-file
```

## Live Prometheus Queries via Grafana API

Query live cluster metrics through the Grafana datasource proxy. Prometheus datasource ID is 1.

### Beyond live lookup: cluster-state JSONs as a correlation tool

The same proxy endpoint is also useful for *recording* cluster state alongside experiments — giving you a load axis to correlate against later. The storage benchmark in this repo (`docs/benchmarks/`) demonstrates the pattern end-to-end:

- `docs/benchmarks/capture_cluster_state.sh` — single curl call, captures `slurm_cpus_alloc`, `slurm_cpus_total`, `node_load15`, etc. into a per-run JSON.
- `docs/benchmarks/aggregate_results.py` — joins per-run summary TSVs with the captured cluster JSONs.
- `docs/benchmarks/analyze_weekly.py` — Spearman correlation of measured throughput vs `slurm_cpus_alloc / slurm_cpus_total`. Surfaced the `/fh/working/` ρ = −0.60 load-sensitivity finding (n=28, Apr 2026).

Use this pattern any time you suspect cluster load is confounding an experiment (alignment runtime, job startup latency, NFS-bound throughput). The Grafana proxy is unauthenticated and read-only, so capturing state per-run is a one-line shell call with no credential rotation.

### Query Pattern

```bash
curl -s 'https://grafana.fredhutch.org/api/datasources/proxy/1/api/v1/query?query=PROMQL' | jq .
```

**Important**: Two SLURM controller instances report identical data. Filter to one to avoid double-counting:
```bash
curl -s '...query=slurm_cpus_alloc{instance="gizmo-ctld01.fhcrc.org:8080"}' | jq .
```

### Cluster CPU Status

```bash
# Total, allocated, and unavailable CPUs
curl -s '...query=slurm_cpus_alloc' | jq '.data.result[0].value[1]'   # e.g. 4371
curl -s '...query=slurm_cpus_total' | jq '.data.result[0].value[1]'   # e.g. 7096
curl -s '...query=slurm_cpus_other' | jq '.data.result[0].value[1]'   # e.g. 554 (down/drain)

# CPU utilization ratio
curl -s '...query=slurm_cpus_alloc/(slurm_cpus_total-slurm_cpus_other)' | jq '.data.result[0].value[1]'

# CPUs running per account (top 10)
curl -s '...query=slurm_account_cpus_running{instance="gizmo-ctld01.fhcrc.org:8080"}' | \
  jq -r '.data.result[] | [.metric.account, .value[1]] | @tsv' | sort -t$'\t' -k2 -rn | head -10
```

### GPU Status

```bash
# GPU allocation
curl -s '...query=slurm_gpus_alloc' | jq '.data.result[0].value[1]'   # e.g. 170
curl -s '...query=slurm_gpus_total' | jq '.data.result[0].value[1]'   # e.g. 233

# GPU utilization percentage
curl -s '...query=slurm_gpus_utilization' | jq '.data.result[0].value[1]'   # e.g. 0.73
```

### Node States

```bash
# Nodes in each state
curl -s '...query=slurm_nodes_alloc' | jq '.data.result[0].value[1]'  # fully allocated
curl -s '...query=slurm_nodes_idle'  | jq '.data.result[0].value[1]'  # idle
curl -s '...query=slurm_nodes_mix'   | jq '.data.result[0].value[1]'  # partially allocated
curl -s '...query=slurm_nodes_down'  | jq '.data.result[0].value[1]'  # down
curl -s '...query=slurm_nodes_drain' | jq '.data.result[0].value[1]'  # draining
curl -s '...query=slurm_nodes_comp'  | jq '.data.result[0].value[1]'  # completing
```

### Rhino Login Node Load

```bash
# Load averages
curl -s '...query=node_load15{instance=~"rhino.*"}' | \
  jq -r '.data.result[] | [.metric.instance, .value[1]] | @tsv'

# RAM usage percentage
curl -s '...query=100-((node_memory_MemAvailable_bytes{job="rhino"}*100)/node_memory_MemTotal_bytes{job="rhino"})' | \
  jq -r '.data.result[] | [.metric.instance, .value[1]] | @tsv'

# Heavy CPU users on rhinos
curl -s '...query=heavy_cpu_user{instance=~"rhino.*"}' | \
  jq -r '.data.result[] | [.metric.instance, .metric.user, .value[1]] | @tsv'
```

### Job Queue

```bash
# Running/pending jobs per account
curl -s '...query=slurm_account_jobs_running{instance="gizmo-ctld01.fhcrc.org:8080"}' | \
  jq -r '.data.result[] | [.metric.account, .value[1]] | @tsv' | sort -t$'\t' -k2 -rn | head -10

curl -s '...query=slurm_account_jobs_pending{instance="gizmo-ctld01.fhcrc.org:8080"}' | \
  jq -r '.data.result[] | select(.value[1] | tonumber > 0) | [.metric.account, .value[1]] | @tsv'

# Scheduler health
curl -s '...query=slurm_scheduler_queue_size' | jq '.data.result[0].value[1]'  # 0 = healthy
```

### Gizmo Node Temperatures

```bash
# Average cluster temperature
curl -s '...query=avg(node_thermal_zone_temp{job="gizmo"})' | jq '.data.result[0].value[1]'

# Total cluster power (watts)
curl -s '...query=sum(node_hwmon_power_average_watt{job="gizmo"}<2000)' | jq '.data.result[0].value[1]'
```

### Storage (Limited via Proxy)

```bash
# Storage usage per PI (historical data, may be stale - use Starfish for current)
curl -s '...query=storcrawl_space_used_bytes{owner="PI_NAME",type="Fast"}' | jq .
```

Note: BeeGFS metrics (`beegfs_*`) are defined in dashboards but return empty via proxy ID 1. They likely use a different Prometheus instance.

## Slurm CLI Monitoring (No Grafana Needed)

```bash
# Partition utilization summary
sinfo -o "%P %a %D %C"
# Output: PARTITION AVAIL NODES CPUS(Allocated/Idle/Other/Total)

# Your running jobs
squeue -u $USER

# Your historical resource usage
sacct -u $USER --format=JobID,JobName,Partition,State,Elapsed,MaxRSS,AllocCPUS -S 2026-01-01

# Job efficiency (how well did you use allocated resources)
# Note: seff may not be installed on all systems.
# Alternative: sacct -j <jobid> --format=JobID,Elapsed,AllocCPUS,MaxRSS,ReqMem
seff <jobid>

# Cluster-wide job queue
squeue -o "%i %j %u %P %T %M %C %m" | head -30

# Node-level detail (CPUs, memory, GPUs, state)
sinfo -N -o "%N %P %c %m %G %T" | head -30

# GPU nodes specifically
sinfo -p chorus -o "%N %G %T"

# Why is my job pending?
squeue -u $USER -t PD -o "%i %j %r"
```

## What to Monitor and Why

| Scenario | Check | Why |
|----------|-------|-----|
| Job stuck pending | `squeue -u $USER -t PD -o "%r"` | Shows REASON (Resources, Priority, QOSLimit) |
| Before big submission | `sinfo -o "%P %C"` or Prometheus CPU query | See available CPUs per partition |
| GPU availability | `sinfo -p chorus -o "%N %G %T"` or GPU Prometheus query | Check before requesting L40S |
| Job used too much/little | `sacct -j JOBID --format=MaxRSS,ReqMem,AllocCPUS,Elapsed` | Right-size future requests |
| Cluster busy? | SLURM Dashboard or `slurm_cpus_alloc / (slurm_cpus_total - slurm_cpus_other)` | Quick utilization check |
| Rhino slow? | Rhino Servers dashboard or `node_load15{instance=~"rhino.*"}` | Find the least-loaded login node |
| Storage filling up | Grafana Data Core dashboard or Starfish | Track growth trends |
| Node issues | `slurm_nodes_down` / `slurm_nodes_drain` queries | Report persistent issues to scicomp@ |

## Principles

- Check cluster load before large job array submissions. Be a good neighbor.
- Right-size resource requests based on past job metrics (use `sacct`/`seff`).
- Monitor GPU availability on chorus before requesting multiple L40S.
- Use `sinfo -o "%P %C"` to pick the least-loaded partition.
- Report persistent node issues (down/drain) to SciComp: cit-sc@fredhutch.org.
