# Skill Validation Report

Date: 2026-04-14
Environment: gizmok1 (login node), kernel 4.15.0-213-generic, Slurm accessible via sandbox stubs

## Summary

- 29 skills validated
- 18 deviations found (5 critical, 8 moderate, 5 minor)
- 8 items could not be verified (sandbox limitations)

## Deviations from Wiki/Skills

### CRITICAL

**1. fh.partitions: chorus partition time limit wrong**
- **Skill claim**: chorus max wall time shown as "--" (blank) in the table
- **Reality**: `scontrol show partition chorus` reports `MaxTime=7-00:00:00` (7 days)
- **Severity**: critical
- **Recommendation**: Fill in "7 days" in the partition overview table

**2. fh.partitions: interactive partition time limit wrong**
- **Skill claim**: interactive max wall time shown as "--" (blank) in the table
- **Reality**: `scontrol show partition interactive` reports `MaxTime=7-00:00:00` (7 days)
- **Severity**: critical
- **Recommendation**: Fill in "7 days" in the partition overview table

**3. fh.partitions: restart-new partition described as "unlimited" time**
- **Skill claim**: restart-new has "unlimited" time
- **Reality**: `scontrol show partition restart-new` reports `MaxTime=30-00:00:00` (30 days)
- **Severity**: critical
- **Recommendation**: Change "unlimited" to "30 days" in the partition overview table

**4. fh.alphafold: Container path is empty and database path inaccessible**
- **Skill claim**: Container at `/app/software/AlphaFold/containers/alpafold3.sif` and reference data at `/shared/biodata/alphafold3`
- **Reality**: `/app/software/AlphaFold/containers/` exists but is empty (0 files). `/shared/biodata/alphafold3` does not exist (from login node). Also note typo: "alpafold3.sif" should likely be "alphafold3.sif"
- **Severity**: critical (users following this guide will get file-not-found errors)
- **Recommendation**: Verify container and data paths on chorus/harmony nodes (they may only be mounted there). Fix typo "alpafold3" to "alphafold3". Add a note that these paths are only accessible from chorus partition nodes.

**5. fh.alphafold: chorus partition limits wrong**
- **Skill claim**: "Maximum 8 CPUs per job" and "maximum: 5 days"
- **Reality**: `scontrol show partition chorus` shows `MaxCPUsPerNode=UNLIMITED` and `MaxTime=7-00:00:00` (7 days). Harmony nodes have 32 CPUs each.
- **Severity**: critical
- **Recommendation**: Correct CPUs max to 32 (per node) and time limit to 7 days

### MODERATE

**6. fh.r: R module name wrong**
- **Skill claim**: `ml R/3.6.2-foss-2016b-fh1`
- **Reality**: The actual module is `R/3.6.2-foss-2019b-fh1` (foss-2019b, not foss-2016b)
- **Severity**: moderate (module load would fail)
- **Recommendation**: Fix to `R/3.6.2-foss-2019b-fh1`, or better yet use a more current version like `R/4.3.1-gfbf-2022b` or `fhR/4.4.1-foss-2023b`

**7. fh.r / fh.modules: R/4.3.1-foss-2023a does not exist**
- **Skill claim**: `ml R/4.3.1-foss-2023a` referenced in fh.modules and fh.r skills
- **Reality**: `module avail R/4.3.1-foss-2023a` returns "No module(s) found". The actual module is `R/4.3.1-gfbf-2022b`
- **Severity**: moderate (module load would fail)
- **Recommendation**: Replace all `R/4.3.1-foss-2023a` references with `R/4.3.1-gfbf-2022b`

**8. fh.onboarding: "4 nodes" for rhino is wrong**
- **Skill claim**: "4 nodes via round-robin SSH"
- **Reality**: DNS for `rhino.fhcrc.org` resolves to 3 addresses (rhino01, rhino02, rhino03). `rhino04.fhcrc.org` returns NXDOMAIN.
- **Severity**: moderate
- **Recommendation**: Change "4 nodes" to "3 nodes" (rhino01-03)

**9. fh.onboarding: chorus max time stated as "5 days"**
- **Skill claim**: Partition table shows chorus max time as "5 days"
- **Reality**: `MaxTime=7-00:00:00` (7 days)
- **Severity**: moderate
- **Recommendation**: Change to "7 days"

**10. fh.onboarding: restart partition described as "7 days"**
- **Skill claim**: restart partition max time is "7 days"
- **Reality**: `MaxTime=30-00:00:00` (30 days)
- **Severity**: moderate
- **Recommendation**: Change to "30 days"

**11. fh.onboarding: /fh/economy/ path referenced**
- **Skill claim**: Storage includes `/fh/economy/` (economy)
- **Reality**: `/fh/economy/` does not exist. Economy storage is S3-based, accessed via AWS CLI (not POSIX mount)
- **Severity**: moderate
- **Recommendation**: Replace with "Economy Cloud (S3 buckets via aws s3)" or similar

**12. fh.data-transfer: /fh/temp/ path referenced**
- **Skill claim**: Storage tiers table lists Temp as `/fh/temp/`
- **Reality**: The actual temp path is `/hpc/temp/`, not `/fh/temp/`. The `/fh/temp/` path does not exist.
- **Severity**: moderate
- **Recommendation**: Change `/fh/temp/` to `/hpc/temp/` in the storage tiers table

**13. fh.gpu: L40S VRAM stated as 44 GB**
- **Skill claim**: L40S has "44 GB" GPU memory
- **Reality**: NVIDIA L40S has 48 GB VRAM (per NVIDIA specs). The cluster-overview skill correctly says 48 GB.
- **Severity**: moderate
- **Recommendation**: Change "44 GB" to "48 GB" in the GPU table

### MINOR

**14. fh.partitions: j-node count says 42, reality is 37**
- **Skill claim**: 42 j-class nodes
- **Reality**: `sinfo` shows 37 j-class nodes (gizmoj series)
- **Severity**: minor (the cluster-overview skill correctly says 37)
- **Recommendation**: Change 42 to 37

**15. fh.partitions: k-node count says 170, reality is 161**
- **Skill claim**: 170 k-class nodes
- **Reality**: `sinfo` shows 161 k-class nodes (gizmok series). Total campus-new = 198 nodes = 37 + 161.
- **Severity**: minor (cluster-overview correctly says 161)
- **Recommendation**: Change 170 to 161

**16. fh.partitions: Missing canto partition**
- **Skill claim**: Partition overview table lists only 5 partitions (campus-new, short, restart-new, chorus, interactive)
- **Reality**: There is also a `canto` partition (3 nodes, 36 CPUs, ~1.5 TB RAM, 1x RTX 2080 Ti, 7-day max)
- **Severity**: minor (covered in cluster-overview but missing from partitions skill)
- **Recommendation**: Add canto to the partition overview table

**17. fh.monitoring: seff command referenced but not available**
- **Skill claim**: `seff <jobid>` for job efficiency
- **Reality**: `which seff` returns "not found"
- **Severity**: minor (seff is a common Slurm tool but apparently not installed here)
- **Recommendation**: Note that seff may not be available; suggest `sacct` with `--format=MaxRSS,ReqMem,AllocCPUS,Elapsed` as alternative

**18. fh.gpu: interactive partition lists "rhino" as node gen with 1080ti**
- **Skill claim**: interactive partition has "rhino" nodes with "NVIDIA RTX 1080ti"
- **Reality**: The interactive partition shares the same gizmoj/gizmok nodes as campus-new. Rhino is a login node, not a compute node. Also "RTX 1080ti" is wrong; it's "GTX 1080 Ti".
- **Severity**: minor
- **Recommendation**: Remove the "interactive/rhino" row or clarify that interactive uses the same j/k nodes. Fix "RTX" to "GTX".

## Verified Correct

### Partitions and Nodes
- campus-new: 198 nodes, 30-day max, default 3-day, correct
- short: 198 nodes, 12-hour max, correct
- chorus: 8 harmony nodes, 32 CPUs, ~1.5 TB RAM, 4x L40S GPUs, correct
- canto: 3 nodes, 36 CPUs, ~1.5 TB RAM, 1x RTX 2080 Ti, correct
- interactive: 198 nodes, 7-day max, highest priority (PriorityTier=30000), correct
- restart-new: preemptible, PreemptMode=REQUEUE, correct
- J-class: 24 cores, 350 GB RAM (350000 MB), 1x GTX 1080 Ti, confirmed
- K-class: 36 cores, 700 GB RAM (700000 MB), 1x RTX 2080 Ti, confirmed
- Harmony: 32 cores, ~1.5 TB RAM (1545980 MB), 4x L40S, confirmed
- MaxCPUsPerNode on campus-new: 36, confirmed

### Storage
- /fh/fast/ exists and is NFS-mounted from `silver` (Isilon), confirmed
- /fh/scratch/ deprecated and not mounted, confirmed
- /hpc/temp/ exists and is NFS4-mounted from `scratch.chromium.fhcrc.org`, confirmed
- $SCRATCH, $DELETE10, $DELETE30, $DELETE90 env vars exist but point to non-existent paths, confirmed
- NFS details: silver server, NFSv3, 128KB read / 512KB write, hard mount, confirmed
- /hpc/temp NFS4.1, 1MB read/write, hard mount, confirmed
- /fh/working/ not mounted from login node (sandbox limitation, see below)

### Modules
- Python/3.11.3-GCCcore-12.3.0 exists, confirmed
- Python/3.10.8-GCCcore-12.2.0 exists, confirmed
- fhPython/3.11.3-foss-2023a exists (default), confirmed
- fhPython/3.8.6-foss-2020b-Python-3.8.6 exists, confirmed
- CUDA versions from 9.2 through 12.6.0 available, confirmed
- Apptainer/1.1.6 (default), confirmed
- JupyterLab/4.0.3-GCCcore-12.2.0 exists, confirmed
- awscli/2.17.54-GCCcore-12.3.0 (default), confirmed
- GlobusConnectPersonal/3.2.0-GCCcore-11.2.0 exists, confirmed
- Nextflow module available (multiple versions), confirmed
- tmux module available, confirmed
- OpenMPI modules available, confirmed

### Commands and Tools
- grabnode: exists at /app/bin/grabnode, limits confirmed (36 cores, 1 GPU, 3 concurrent jobs)
- hitparade: exists at /app/bin/hitparade, confirmed
- fhfreeport: exists at /app/bin/fhfreeport, confirmed
- Slurm commands (sbatch, srun, scancel, squeue, sacct, sinfo, scontrol): all accessible
- /app/lmod/lmod/init/profile exists for script initialization, confirmed

### Services
- grafana.fredhutch.org resolves (alias for prometheus.fredhutch.org), confirmed
- motuz.fredhutch.org resolves, confirmed
- mydb.fredhutch.org resolves, confirmed
- rhino round-robin DNS: 3 addresses (rhino01-03), confirmed

### Other Skills Verified
- fh.slurm: sbatch flags, squeue, sacct, scancel, scontrol usage all correct
- fh.slurm: lmod init path `/app/lmod/lmod/init/profile` confirmed
- fh.storage: tier descriptions generally accurate
- fh.storage-fast: NFS server "silver", path structure, access patterns correct
- fh.storage-scratch: /hpc/temp description correct, deprecation of /fh/scratch/ correct
- fh.storage-s3: bucket naming conventions, AWS CLI usage correct
- fh.containers: Apptainer module available, usage patterns correct
- fh.python: module names and venv workflow correct
- fh.access: SSH to rhino, tmux, X11 forwarding guidance correct
- fh.credentials: HutchNet, Slurm account setup guidance correct
- fh.databases: mydb.fredhutch.org confirmed reachable
- fh.data-transfer: Motuz, Globus, AWS CLI guidance generally correct
- fh.github: GitHub org guidance correct
- fh.grants: NIH S10 citation and process correct
- fh.linux-basics: commands and paths correct
- fh.nextflow: module available, configuration patterns correct
- fh.parallel: job array syntax, threading patterns correct
- fh.vscode-remote: module references and workflow correct
- fh.cloud: AWS Batch, PROOF descriptions correct
- fh.aws-access: SSO landing page URL, CLI setup, S3 pricing correct
- fh.cromwell: WDL patterns and Apptainer usage correct
- fh.interactive-sessions: grabnode usage, limits, partition behavior correct
- fh.monitoring: Grafana URL, Prometheus query patterns, Slurm CLI monitoring correct

## Cannot Verify (Sandbox Limitations)

1. **AlphaFold paths on chorus nodes**: `/shared/biodata/alphafold3` and container SIF may only be accessible from harmony nodes. Cannot verify from login node sandbox.
2. **/fh/working/** path: Not mounted in sandbox environment. Cannot verify existence or properties.
3. **/fh/secure/** path: Not mounted in sandbox. Cannot verify existence.
4. **/loc/scratch/** (job-local storage): Only available during Slurm jobs. Cannot verify from login node.
5. **$TMPDIR in jobs**: Set per-job by Slurm. Not set on login node (as expected).
6. **Grafana API queries**: Network access to grafana.fredhutch.org may be restricted from sandbox. DNS resolves but HTTP queries were not tested.
7. **Open OnDemand**: Web-based service, cannot verify from CLI sandbox.
8. **Arbiter enforcement on rhino**: Login node throttling policies cannot be tested from sandbox.

## Raw Evidence

### Partition Summary (sinfo)
```
PARTITION      TIMELIMIT  NODES  CPUS   MEMORY   GRES                AVAIL
campus-new*    30-00:00:00  37   24     350000   gpu:gtx1080ti:1      up
campus-new*    30-00:00:00  161  36     700000   gpu:rtx2080ti:1      up
short          12:00:00     37   24     350000   gpu:gtx1080ti:1      up
short          12:00:00     161  36     700000   gpu:rtx2080ti:1      up
restart-new    30-00:00:00  37   24     350000   gpu:gtx1080ti:1      up
restart-new    30-00:00:00  161  36     700000   gpu:rtx2080ti:1      up
interactive    7-00:00:00   37   24     350000   gpu:gtx1080ti:1      up
interactive    7-00:00:00   161  36     700000   gpu:rtx2080ti:1      up
chorus         7-00:00:00   8    32     1545980  gpu:l40s:4            up
canto          7-00:00:00   3    36     1540000  gpu:rtx2080ti:1       up
```

### Node Counts
- campus-new: 198 total (37 j + 161 k)
- chorus: 8 harmony nodes
- canto: 3 nodes
- Total unique nodes: ~209

### Key Mount Points
```
silver:/ifs/data/fast/... on /fh/fast/... type nfs (vers=3, rsize=131072, wsize=524288, hard)
scratch.chromium.fhcrc.org:/temp/... on /hpc/temp/... type nfs4 (vers=4.1, rsize=1048576, wsize=1048576, hard)
```

### Module Availability (key modules)
- Python/3.11.3-GCCcore-12.3.0: YES
- fhPython/3.11.3-foss-2023a: YES (default)
- R/4.3.1-gfbf-2022b: YES (note: NOT foss-2023a)
- fhR/4.4.1-foss-2023b: YES (default)
- CUDA/12.6.0: YES (default)
- Apptainer/1.1.6: YES (default)
- JupyterLab/4.2.5-GCCcore-13.3.0: YES (default)

### Commands
- grabnode: /app/bin/grabnode (limits: 36 cores, 1 GPU, 3 jobs)
- hitparade: /app/bin/hitparade
- fhfreeport: /app/bin/fhfreeport
- seff: NOT FOUND

### DNS
- grafana.fredhutch.org -> 140.107.43.220
- motuz.fredhutch.org -> 140.107.222.25
- mydb.fredhutch.org -> 140.107.117.18
- rhino.fhcrc.org -> 3 IPs (rhino01-03)
