# Grafana Monitoring Agent Report

Agent: grafana-agent
Date: 2026-04-13

## Summary

Cataloged the full Grafana instance at `grafana.fredhutch.org`, deep-dived key HPC/storage dashboards, and verified Prometheus queries against the live API.

## Dashboard Catalog

Total dashboards discovered: ~120 (including 12 folders)
Full catalog written to `docs/wiki-distilled/grafana-dashboards.md`

### By Category

| Category | Count | Relevance to HPC Users |
|----------|-------|----------------------|
| HPC / SLURM | 9 | High |
| Storage (general) | 11 | High |
| BeeGFS / Thorium | 13 | Medium (ops-focused but useful for troubleshooting) |
| Isilon / Silver | 5 | Low (infrastructure) |
| AWS / Cloud | 12 | Medium |
| Applications (JupyterHub, cBioPortal, etc.) | 13 | Low-Medium |
| Infrastructure (AD, DNS, networking) | 16 | Low |
| CIT-SEA (app dev) | 9 | None |
| Personal / Test | 12 | None |

### Key Dashboards Deep-Dived

1. **SLURM Dashboard (wDBLiGoGk)** — 28 panels. CPU/GPU allocation, node states, job queues, scheduler performance, per-account/user pie charts, rhino load, alert thresholds.

2. **HPC Metrics (000000004)** — 20 panels. SLA adherence, per-partition job status, core ownership. Note: `hpc_gizmo_*` metrics return zeros, suggesting the custom exporter is deprecated. The `slurm_*` metrics are the working replacement.

3. **SLURM Users and Accounts (41ukeATGk)** — 10 panels. Per-user/per-account breakdowns with template variables for filtering.

4. **Rhino Servers (HvsO4InGk)** — 20+ panels. Comprehensive rhino01-03 monitoring: CPU, RAM, swap, load, heavy users, network, disk, uptime.

5. **Gizmo Facility Metrics (v6s05e9Nz)** — 5 panels. Thermal monitoring (840 sensors across cluster), power consumption.

6. **QBR Dash (l-402TrMz)** — 3 panels. Quarterly business review: days >80% allocation, utilization ratio.

7. **Performance Troubleshooting (4MtUNFEWz)** — BeeGFS IOPS, throughput per user/client, CPU iowait on storage nodes.

8. **Storage Bottleneck? (SDlmBYEZk)** — ZFS throughput/latency, network throughput for Thorium storage nodes.

9. **Fast File (iXVX2whZk)** — BeeGFS cluster status, client count, capacity, request rates.

## Prometheus Query Testing

### Working Queries (Verified)

| Query | Status | Example Value |
|-------|--------|---------------|
| `slurm_cpus_alloc` | Working | 4371 |
| `slurm_cpus_total` | Working | 7096 |
| `slurm_cpus_other` | Working | 554 |
| `slurm_gpus_alloc` | Working | 170 |
| `slurm_gpus_total` | Working | 233 |
| `slurm_gpus_utilization` | Working | 0.73 |
| `slurm_nodes_alloc` | Working | 59 |
| `slurm_nodes_idle` | Working | 7 |
| `slurm_nodes_mix` | Working | 118 |
| `slurm_nodes_down` | Working | 2 |
| `slurm_nodes_drain` | Working | 18 |
| `slurm_nodes_comp` | Working | 5 |
| `slurm_account_cpus_running` | Working | 96 accounts |
| `slurm_account_jobs_running` | Working | 97 accounts |
| `slurm_account_jobs_pending` | Working | varies |
| `slurm_user_cpus_running` | Working | 144 users |
| `slurm_scheduler_queue_size` | Working | 0 |
| `node_load1{job="rhino"}` | Working | rhino01-03 + slurm-mon |
| `node_load15{instance=~"rhino.*"}` | Working | rhino01-03 |
| `node_memory_MemTotal_bytes{job="rhino"}` | Working | ~810 GB each |
| `node_memory_MemAvailable_bytes{job="rhino"}` | Working | varies |
| `heavy_cpu_user{instance=~"rhino.*"}` | Working | ~12 entries |
| `node_thermal_zone_temp{job="gizmo"}` | Working | 840 readings |
| `storcrawl_space_used_bytes` | Working | 824 entries (historical) |

### Non-Working / Empty Queries

| Query | Status | Notes |
|-------|--------|-------|
| `slurm_nodes_total` | Empty | Use sum of individual states |
| `slurm_job_count` | Empty | Use per-account aggregation |
| `slurm_jobs_running` | Empty | Use `sum(slurm_account_jobs_running)` |
| `slurm_jobs_pending` | Empty | Use `sum(slurm_account_jobs_pending)` |
| `slurm_partition_cpus_alloc` | Empty | Different metric name |
| `beegfs_*` | All empty | Different Prometheus instance |
| `hpc_gizmo_cores_used` | Returns 0 | Deprecated exporter |
| `hpc_gizmo_cores_total` | Returns 0 | Deprecated exporter |

### Data Source Access

| Source | Access |
|--------|--------|
| Prometheus (ID 1) | Works, unauthenticated |
| Datasource list API | 403 Forbidden |
| Dashboard JSON API | Works, unauthenticated |
| Dashboard Search API | Works, unauthenticated |
| InfluxDB / CloudWatch / Azure | Cannot determine IDs without datasource API |

## Outputs Written

1. `docs/wiki-distilled/grafana-dashboards.md` — Full catalog of all ~120 dashboards organized by category
2. `docs/wiki-distilled/prometheus-queries.md` — Verified query reference with examples and caveats
3. `skills/fh.monitoring/skill.md` — Updated with new dashboards, more queries, and verified examples

## Findings and Recommendations

1. The `hpc_gizmo_*` and `hpc_beagle_*` metrics (used by HPC Metrics dashboard) appear deprecated. All return zeros. The `slurm_*` metrics are the active replacement.

2. BeeGFS metrics (`beegfs_*`) are not accessible via Prometheus proxy ID 1. They likely use a different Prometheus instance or require a different datasource. The Fast File dashboard references these but they may only render in the Grafana UI.

3. Storage chargeback (`storcrawl_*`) data is historical (crawl dates from 2021-2022). Fred Hutch has transitioned to Starfish for current storage tracking.

4. The two SLURM controller instances (gizmo-ctld01, gizmo-ctld02) always report identical data. Queries should filter to one instance to avoid confusion.

5. No separate `fh.storage-monitoring` skill was created because storage monitoring queries are limited (BeeGFS unavailable via proxy, storcrawl is stale). The existing `fh.monitoring` skill covers what's available. If BeeGFS access is resolved, a dedicated storage monitoring skill would be warranted.
