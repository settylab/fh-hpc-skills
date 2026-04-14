# Prometheus Query Reference for Fred Hutch HPC

Base URL: `https://grafana.fredhutch.org/api/datasources/proxy/1/api/v1/query?query=`

All queries are verified working as of 2026-04-13. Values shown are from a live snapshot to illustrate expected output.

## Query Pattern

```bash
curl -s 'https://grafana.fredhutch.org/api/datasources/proxy/1/api/v1/query?query=PROMQL' | jq .
```

For range queries (time series):
```bash
curl -s 'https://grafana.fredhutch.org/api/datasources/proxy/1/api/v1/query_range?query=PROMQL&start=EPOCH&end=EPOCH&step=60' | jq .
```

## SLURM Cluster Metrics

### CPU Allocation

| Metric | Description | Example Value |
|--------|-------------|---------------|
| `slurm_cpus_alloc` | CPUs currently allocated | 4371 |
| `slurm_cpus_total` | Total CPUs in cluster | 7096 |
| `slurm_cpus_other` | CPUs in non-available states (down/drain) | 554 |

Derived queries:
```promql
# CPU utilization percentage
slurm_cpus_alloc / (slurm_cpus_total - slurm_cpus_other)

# Available CPUs
slurm_cpus_total - slurm_cpus_alloc - slurm_cpus_other
```

### GPU Allocation

| Metric | Description | Example Value |
|--------|-------------|---------------|
| `slurm_gpus_alloc` | GPUs currently allocated | 170 |
| `slurm_gpus_total` | Total GPUs in cluster | 233 |
| `slurm_gpus_utilization` | GPU utilization ratio (0-1) | 0.73 |

Derived queries:
```promql
# Free GPUs
slurm_gpus_total - slurm_gpus_alloc

# GPU utilization percentage (already available)
slurm_gpus_utilization * 100
```

### Node States

| Metric | Description | Example Value |
|--------|-------------|---------------|
| `slurm_nodes_alloc` | Fully allocated nodes | 59 |
| `slurm_nodes_idle` | Completely idle nodes | 7 |
| `slurm_nodes_mix` | Partially allocated nodes | 118-119 |
| `slurm_nodes_down` | Down nodes | 2 |
| `slurm_nodes_drain` | Draining/drained nodes | 18 |
| `slurm_nodes_comp` | Completing nodes | 5-6 |

Note: `slurm_nodes_total` returns empty. Compute total as sum of states, or use `slurm_nodes_alloc + slurm_nodes_idle + slurm_nodes_mix + slurm_nodes_down + slurm_nodes_drain + slurm_nodes_comp`.

Additional node states (from SLURM Dashboard):
- `slurm_nodes_err` — Nodes in error state
- `slurm_nodes_fail` — Failed nodes
- `slurm_nodes_maint` — Nodes in maintenance

### Per-Account Metrics

| Metric | Description | Result Count |
|--------|-------------|--------------|
| `slurm_account_cpus_running` | CPUs used per PI account | ~96 accounts |
| `slurm_account_jobs_running` | Running jobs per account | ~97 accounts |
| `slurm_account_jobs_pending` | Pending jobs per account | varies |

Useful jq filters:
```bash
# Top CPU consumers
curl -s '...query=slurm_account_cpus_running' | \
  jq -r '.data.result[] | select(.metric.instance | contains("ctld01")) | [.metric.account, .value[1]] | @tsv' | sort -t$'\t' -k2 -rn | head -10

# Accounts with pending jobs
curl -s '...query=slurm_account_jobs_pending' | \
  jq -r '.data.result[] | select(.metric.instance | contains("ctld01")) | select(.value[1] | tonumber > 0) | [.metric.account, .value[1]] | @tsv'
```

### Per-User Metrics

| Metric | Description | Result Count |
|--------|-------------|--------------|
| `slurm_user_cpus_running` | CPUs used per user | ~144 users |
| `slurm_user_jobs_running` | Running jobs per user | varies |
| `slurm_user_jobs_pending` | Pending jobs per user | varies |

Note: Each metric appears from two controller instances (gizmo-ctld01 and gizmo-ctld02) with identical values. Filter to one instance to avoid duplicates:
```bash
curl -s '...query=slurm_user_cpus_running{instance="gizmo-ctld01.fhcrc.org:8080"}' | jq .
```

### Scheduler Internals

| Metric | Description |
|--------|-------------|
| `slurm_scheduler_threads` | Active scheduler threads |
| `slurm_scheduler_queue_size` | Agent queue size (0 = healthy) |
| `slurm_scheduler_backfill_depth_mean` | Average backfill scheduling depth |
| `slurm_scheduler_cycle_last` | Last scheduler cycle time |
| `slurm_scheduler_cycle_mean` | Mean scheduler cycle time |
| `slurm_scheduler_backfill_cycle_last` | Last backfill cycle time |
| `slurm_scheduler_backfill_cycle_mean` | Mean backfill cycle time |


## Rhino Login Nodes

| Metric | Description | Nodes |
|--------|-------------|-------|
| `node_load1{job="rhino"}` | 1-minute load average | rhino01-03, slurm-mon |
| `node_load5{job="rhino"}` | 5-minute load average | rhino01-03, slurm-mon |
| `node_load15{instance=~"rhino.*"}` | 15-minute load average | rhino01-03 |
| `node_memory_MemTotal_bytes{job="rhino"}` | Total RAM per node | ~810 GB each |
| `node_memory_MemAvailable_bytes{job="rhino"}` | Available RAM per node | varies |
| `node_memory_MemFree_bytes{job="rhino"}` | Free RAM | varies |
| `node_memory_SwapTotal_bytes{job="rhino"}` | Swap total | varies |
| `node_memory_SwapFree_bytes{job="rhino"}` | Swap free | varies |
| `heavy_cpu_user{instance=~"rhino.*"}` | Users consuming heavy CPU | ~12 entries |
| `heavy_ram_user{instance=~"rhino.*"}` | Users consuming heavy RAM | varies |

Useful derived queries:
```promql
# Rhino CPU utilization percentage
100 - (avg by (instance) (irate(node_cpu_seconds_total{job="rhino",mode="idle"}[5m])) * 100)

# RAM usage percentage
100 - ((node_memory_MemAvailable_bytes{job="rhino"} * 100) / node_memory_MemTotal_bytes{job="rhino"})

# Swap usage percentage
((node_memory_SwapTotal_bytes{job="rhino"} - node_memory_SwapFree_bytes{job="rhino"}) / node_memory_SwapTotal_bytes{job="rhino"}) * 100

# Filesystem usage on root
100 - ((node_filesystem_avail_bytes{job="rhino",mountpoint="/"} * 100) / node_filesystem_size_bytes{job="rhino",mountpoint="/"})

# /tmp free space
node_filesystem_free_bytes{instance=~"rhino.*",mountpoint="/tmp"}

# Network throughput
irate(node_network_transmit_bytes_total{device="eno1",job="rhino"}[2m])
irate(node_network_receive_bytes_total{device="eno1",job="rhino"}[2m])
```


## Gizmo Cluster Node Metrics

| Metric | Description |
|--------|-------------|
| `node_thermal_zone_temp{job="gizmo"}` | Node temperatures (~840 readings across cluster) |
| `node_hwmon_power_average_watt{job="gizmo"}` | Per-node power consumption |
| `node_load1{job="gizmo"}` | Per-node 1-min load average |

Useful derived queries:
```promql
# Average cluster temperature
avg(node_thermal_zone_temp{job="gizmo"})

# Average power consumption
sum(node_hwmon_power_average_watt{chip="lnxsybus:00_acpi000d:00",sensor="power1",job="gizmo"} < 2000)
```


## Storage Metrics

### storcrawl (Storage Chargeback)

| Metric | Description |
|--------|-------------|
| `storcrawl_space_used_bytes` | Storage usage per PI/lab/division (~824 entries) |

Labels: `owner`, `type` (Fast/Economy), `division`, `crawldate`

```promql
# Storage for a specific PI
storcrawl_space_used_bytes{owner="PI_NAME",type="Fast"}

# Total Fast storage
sum(storcrawl_space_used_bytes{type="Fast"})
```

Note: This data may be stale (crawl dates from 2021-2022 observed). Fred Hutch has transitioned to Starfish for storage tracking.

### BeeGFS / Fast File

These metrics are defined in dashboards but returned empty via the proxy (likely on a different Prometheus instance or require auth):
- `beegfs_capacity_free_bytes{beegfs_cluster="thorium"}`
- `beegfs_capacity_total_bytes{beegfs_cluster="thorium"}`
- `beegfs_node_count{beegfs_cluster="thorium",nodetype="client"}`
- `beegfs_serverstats_avg_requests_sec{beegfs_cluster="thorium"}`

BeeGFS user/client stats (for performance troubleshooting):
- `beegfs_userstats{beegfs_cluster="thorium",nodetype="storage",method="ops-wr"}`
- `beegfs_clientstats{beegfs_cluster="thorium",nodetype="storage",method="ops-rd"}`


## HPC Metrics (Legacy)

These metrics exist but return zeros, suggesting the exporter is deprecated:
- `hpc_gizmo_cores_used` — returns 0
- `hpc_gizmo_cores_total` — returns 0
- `hpc_gizmo_campus_account_limit_sla`
- `hpc_gizmo_campus_account_limit_current`
- `hpc_gizmo_jobstate_running{partition="campus"}`
- `hpc_gizmo_ownercores`

Use `slurm_*` metrics instead for current data.


## Slurm Statedb Process Monitoring

| Metric | Description |
|--------|-------------|
| `namedprocess_namegroup_num_threads{instance="slurm-statedb.fhcrc.org:9256",groupname="slurmdbd"}` | Slurmdbd thread count |
| `namedprocess_namegroup_memory_bytes{instance="slurm-statedb.fhcrc.org:9256",groupname="slurmdbd",memtype="resident"}` | Slurmdbd resident memory |


## Metrics That Return Empty (Not Available via Proxy)

These were tested and return empty results:
- `slurm_nodes_total` — use sum of individual node states instead
- `slurm_job_count` — use `slurm_account_jobs_running` instead
- `slurm_queue_size` — use `slurm_scheduler_queue_size` for scheduler queue
- `slurm_jobs_running` — use `sum(slurm_account_jobs_running)` instead
- `slurm_jobs_pending` — use `sum(slurm_account_jobs_pending)` instead
- `slurm_partition_cpus_alloc` — use partition-specific queries like `slurm_partition_cpus_allocated{partition="chorus"}`
- `slurm_account_cpus` — use `slurm_account_cpus_running` instead
- All `beegfs_*` metrics — likely on a different datasource


## Important Notes

1. Two SLURM controller instances report identical data (gizmo-ctld01 and gizmo-ctld02). Always filter to one to avoid double-counting:
   ```promql
   slurm_cpus_alloc{instance="gizmo-ctld01.fhcrc.org:8080"}
   ```

2. The Prometheus datasource ID is **1**. Other datasources (InfluxDB, CloudWatch, Azure Monitor) exist but their IDs are not accessible without authentication.

3. For time-range queries use `query_range` with `start`, `end` (Unix epoch), and `step` (seconds) parameters.

4. The `storcrawl_*` metrics contain historical snapshots, not real-time data. For current storage info, use Starfish or contact scicomp@.
