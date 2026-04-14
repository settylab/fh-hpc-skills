# Fred Hutch Grafana Dashboard Catalog

Grafana instance: `https://grafana.fredhutch.org`
API access: unauthenticated read-only
Datasource proxy: `https://grafana.fredhutch.org/api/datasources/proxy/1/api/v1/query?query=PROMQL`

Last updated: 2026-04-13

## Folders

| Folder | UID | Purpose |
|--------|-----|---------|
| scicomp | DPTEjRnmk | Scientific Computing team dashboards (HPC, storage, Slurm) |
| scicomp OLD | Bwth928Gk | Deprecated scicomp dashboards |
| bmcgough | lL9fw1fiz | Infrastructure engineer personal dashboards |
| syseng | 9vM3OZwZk | Systems engineering (Windows, AD, network) |
| HDC | A2u8eFKmz | Hutch Data Core |
| CCC | v4vbRO9Zz | Cloud Computing Center (AWS) |
| cit-sea | duagAPVGk | CIT Seattle app dev (Docker, Portainer, OWL) |
| citdba | TvQl3XnMk | Database administration |
| hdcp | hnUXCoEmz | Hutch Data Core Projects |
| cbianche | GXJaBoDVk | Personal |
| ssisco | EvXRWjzWk | Personal |
| Dustin-Test | P5ZdjhIMk | Test |


## HPC and Slurm (High Value for Researchers)

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| SLURM Dashboard | wDBLiGoGk | (root) | CPU/GPU allocation, node states (alloc/idle/down/drain/mix), job queues (running/pending/completing), scheduler performance (threads, backfill depth, cycle times), per-account and per-user CPU usage pie charts, rhino load averages |
| HPC Metrics | 000000004 | scicomp | SLA adherence, per-partition job status (campus/restart/largenode), per-account core ownership, CPU/RAM utilization for Gizmo and Beagle clusters, node status |
| SLURM Users and Accounts | 41ukeATGk | scicomp | Per-user and per-account breakdowns of running/pending jobs and CPU allocation. Filterable by account and user |
| Rhino Servers | HvsO4InGk | scicomp | CPU utilization, load averages, RAM/swap usage, disk space, network I/O, heavy CPU/RAM users, uptime for rhino01-03 login nodes |
| Gizmo Facility Metrics | v6s05e9Nz | scicomp | Node temperatures (thermal zones), power consumption (watt), pod-level aggregates for the Gizmo cluster |
| QBR Dash | l-402TrMz | scicomp | Quarterly business review metrics. Days with >80% allocation, CPU utilization ratio, GPU utilization |
| slurm-statedb detail | aB8Tm4dDz | (root) | Slurmdbd process health: thread count, resident memory usage |
| Gizmo Overview | YAJ5Vo9Mk | scicomp OLD | Deprecated Gizmo overview |
| OLD Rhino Servers | 000000003 | scicomp OLD | Deprecated rhino metrics |


## Storage (High Value for Researchers)

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| Fast File | iXVX2whZk | scicomp | BeeGFS/Thorium fast filesystem: status, client count, capacity %, server request rates, data transfer rates |
| Data Core Storage Usage | dy5I3SIMk | scicomp | Storage consumption by PI/lab/division using storcrawl metrics. Now transitioning to Starfish |
| Data Core Storage Usage Trends | weIvHl0Gk | scicomp | Historical storage growth (Fast and Economy tiers) per PI/lab |
| Data Core Storage Usage Aggregate Trends | p_nXlEBnk | scicomp | Aggregate storage trends across all users |
| Storage Bottleneck? | SDlmBYEZk | scicomp | I/O bottleneck diagnostics: ZFS throughput/latency, network throughput for Thorium storage nodes |
| Performance Troubleshooting | 4MtUNFEWz | scicomp | BeeGFS user/client IOPS, read/write throughput, CPU iowait on storage nodes |
| Storage Users | CGmlfFfZz | (root) | Per-user storage usage |
| Fast File DR | 000000008 | (root) | Fast File disaster recovery |
| Fast File Users and Clients | QJSbU7BZz | (root) | Fast File per-user and per-client breakdowns |
| Scratch I/O | ju6R6mk7z | scicomp | Scratch filesystem I/O |
| Scratch Space Tracker | Dx-ihnfVk | (root) | Scratch filesystem capacity tracking |


## BeeGFS / Thorium (Detailed Storage)

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| Thorium | Vz1SDlHZk | scicomp | Thorium cluster overview |
| Thorium Buddies | VDZ0aJhWk | scicomp | Thorium buddy allocator metrics |
| Thorium Client Experience | I_Z3Eh2Wz | scicomp | Client-side performance |
| Thorium Clients | YurnkbbZk | scicomp | Connected client list and stats |
| Thorium Detailed Client Stats | c11zFFBZz | scicomp | Deep-dive per-client metrics |
| Thorium Detailed User Stats | oZI9KX-Zk | scicomp | Per-user Thorium usage |
| Thorium Gateway | jdna7CBWk | scicomp | Gateway node metrics |
| Thorium Metadata Resync | MFu__wUWz | scicomp | Metadata resync operations |
| Thorium Storage | 7I6k2kJZz | scicomp | Storage tier metrics |
| Thorium Writers | 0yQXRZwZk | scicomp | Write operation details |
| Three Levels | KGC6WQ2Zz | scicomp | Multi-level storage view |
| BeeGFS metadata reqs | iZQxfu2Zk | scicomp | Metadata request rates |
| BeeGFS Metrics | kRguzjjVk | bmcgough | BeeGFS monitoring (personal copy) |

## Isilon / Silver (Storage Infrastructure)

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| Isilon Cluster Metrics | -KRvNqkGz | scicomp | Isilon storage cluster metrics |
| Silver | aYwrz6QWk | syseng | Silver storage system |
| Silver Node Metrics | pv8HD3zGk | scicomp | Per-node Silver metrics |
| Silver Performance | q9xknvpGk | scicomp | Silver performance indicators |
| Silver Errors | hKlomVbGk | bmcgough | Silver error tracking |


## AWS and Cloud

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| AWS Cost Reporting | 000000007 | (root) | AWS cost breakdowns |
| AWS Dashboard | E4C9sHZVk | (root) | AWS overview |
| AWS EC2 Instances | 000000012 | (root) | EC2 instance inventory and metrics |
| AWS S3 Buckets | Pfe5to4ik | scicomp | S3 bucket usage |
| AWS Sandbox Dashboard | 1lmI0LuZk | scicomp | AWS sandbox environment |
| AWS Cost Explorer | Q1gazGKMz | bmcgough | Cost exploration tool |
| AWS EC2 EBS HSE | MLhlyMPMz | bmcgough | EBS volume metrics |
| EC2 (CCC) | ULs3-vrWz | CCC | EC2 instance details |
| EFS (CCC) | N7aQEmqZz | CCC | EFS filesystem metrics |
| Cloud VPNs | 000000015 | (root) | VPN connection status |
| FH AWS VPN | ZRmeZjOZk | (root) | Fred Hutch AWS VPN |
| fh-aws-network | xIByZA2Mz | (root) | AWS network topology |


## Applications and Services

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| Jupyterhub | 000000009 | (root) | JupyterHub service metrics |
| cBioPortal | I5CnzT_Sz | scicomp | cBioPortal application |
| HICOR-IQ | RnhJJ2Aik | scicomp | HICOR-IQ system |
| Rancher Apps | mciFezQik | scicomp | Rancher-managed applications |
| Motuz Alerts | eepG26DMz | scicomp | Motuz data transfer alerts |
| Motuz Host(s) | FYqbt6vMz | scicomp | Motuz host system metrics |
| RStudio | 000000011 | (root) | RStudio Server |
| MatLab Licensing | 6Z60UlOmk | scicomp | MATLAB license server status |
| MyDB | 1-v9RiMik | (root) | MariaDB as a Service |
| HutchBASE | UUvpa3gZz | cit-sea | HutchBASE application |
| HutchScreen | QvcF59gMz | (root) | HutchScreen |
| SMRTlink | WBl89qlMk | scicomp OLD | PacBio SMRTlink |
| SMRTlink Overview | 4sVy6lXGk | scicomp OLD | SMRTlink overview |
| Swarm App Status | 9t65pB_Sz | (root) | Docker Swarm apps |
| Archer Analysis | SXW_m4DSz | (root) | Genomics - Archer pipeline |


## Infrastructure (Ops-focused, less relevant for researchers)

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| Alerts - Server Status | pbHjqZzmk | (root) | Linux/Windows server alerts |
| Active Directory | fsJk96Aiz | (root) | AD metrics |
| Azure SQLaaS | L8wzYL2mk | (root) | Azure SQL databases |
| Domain Controllers | u-wdIqAmz | syseng | Windows domain controllers |
| DNS Shield | UWip2pJik | (root) | DNS ad/malware blocking |
| LDAP | TEWvysOmz | scicomp | LDAP directory |
| Network Access Control | CyIhFZJiz | (root) | NAC metrics |
| Node Exporter Full | z8VIpHTWk | bmcgough | Generic node_exporter dashboard |
| Prometheus Server | 5YNcPZJWk | (root) | Prometheus self-monitoring |
| SAS Desktops | 000000001 | (root) | SAS desktop metrics |
| SAS Servers | 000000014 | (root) | SAS server metrics |
| SysEng Linux | qEszS7IMz | syseng | Linux servers (Aspera) |
| SysEng Windows | -YaLUH6Wk | syseng | Windows servers |
| DBA Dashboard | 18oU3XnGk | citdba | Database admin |
| Cortex Kubernetes | mciFezQik | HDC | Kubernetes metrics |
| Container in Docker and System Monitoring | txRDkmcGk | (root) | Docker containers |
| Graphite Carbon Metrics | -Zs4lnDIz | (root) | Graphite backend health |
| Halo | a7txVQsVk | (root) | Halo security |
| MiM Dashboard | 6XS41eGGz | syseng | MiM identity management |
| Telegraf: system dashboard | 000000127 | (root) | InfluxDB/Telegraf system |
| FredHutch Websites | d5VLSLWik | (root) | Website uptime |
| CVProfiles Website | DhFlyKLiz | (root) | CV Profiles site |
| Graph-development | 000000016 | (root) | Development |


## CIT-SEA Application Development

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| DocFinity Dev | docfinity-windows-monitoring | cit-sea | DocFinity on Windows |
| OWL DB Dev | owl-db-dev | cit-sea | OWL MSSQL monitoring |
| OWL Web Dev | IV0hu1m7z | cit-sea | OWL web app |
| RCP-API-DEV Container Health | rcp-api-container-dev | cit-sea | RCP API containers |
| RCP-API-DEV Status | rcp-api-status-test | cit-sea | RCP API up/down |
| Sea App Dev - Portainer Host | 2ZexdV5vk | cit-sea | Portainer host |
| Sea App01 Dev - Containers | 58oDSD5vk | cit-sea | Docker container metrics |
| Sea App01 Dev - Container Status | portainer-containers-status | cit-sea | Container status |
| Sea App01 Dev - Container Alerts | portainer-containers-status-alerts | cit-sea | Container alerts |
| Portainer Containers - Dev | portainer-containers-dev | (root) | Portainer dev |


## ZFS (Storage Infrastructure)

| Dashboard | UID | Folder | What it monitors |
|-----------|-----|--------|------------------|
| ZFS L2ARC | GxVoYNPWz | bmcgough | ZFS L2 ARC cache |
| ZFS pool read/write latency | ab1iSJhmk | bmcgough | Pool latency |
| ZFS pool all queues | GIhK4-hik | bmcgough | All queue latencies |


## Miscellaneous / Personal

| Dashboard | UID | Folder |
|-----------|-----|--------|
| Bruce Test | vh0k4fxmz | (root) |
| Scott's Dashboard | 7P-NWjzWz | ssisco |
| Scott's Rhino Server Dashboard | 000000768 | (root) |
| Dashboards | 000000006 | (root) |
| cbianche - Hosts IPMI | qsry05emz | (root) |
| Scratch (bmcgough) | dKk_naRnk | bmcgough |
| Scratch Usage | Ndd0JfsVz | bmcgough |
| junk yard | SOs7H8MGz | syseng |
| testplugins | b0pQM52Zk | bmcgough |
| rancher test | TIiTyZ4Mz | bmcgough |
| Swift Metdata Mapping | 1UaN_JBmk | bmcgough |
| Isilon Times | fivnCnmGk | bmcgough |
| Prometheus MSSQL Exporter | TocpL9Lizd | (root) |
| res_status_per_pod | NnFpQOKGk | (root) |
