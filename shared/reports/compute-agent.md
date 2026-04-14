# Compute Agent Report

Agent: compute-agent
Section: LARGE SCALE COMPUTING
Date: 2026-04-13

## Pages Processed (9/9)

| Page | Source URL | Distilled Doc | Status |
|------|-----------|---------------|--------|
| compute_overview | /scicomputing/compute_overview/ | compute_overview.md | Complete (navigation hub, minimal content) |
| compute_quickstart | /scicomputing/compute_quickstart/ | compute_quickstart.md | Complete (deprecated, redirects to /pathways/path-batch-computing/) |
| compute_platforms | /scicomputing/compute_platforms/ | compute_platforms.md | Complete (node specs, generations, local storage) |
| compute_environments | /scicomputing/compute_environments/ | compute_environments.md | Complete (Lmod, Apptainer, custom installs) |
| compute_scientificSoftware | /scicomputing/compute_scientificSoftware/ | compute_scientificSoftware.md | Complete (module categories, fh. prefix, requests) |
| compute_jobs | /scicomputing/compute_jobs/ | compute_jobs.md | Complete (sbatch flags, partitions, env vars, failure reasons) |
| compute_parallel | /scicomputing/compute_parallel/ | compute_parallel.md | Complete (arrays, threading, MPI, workflow managers) |
| compute_cloud | /scicomputing/compute_cloud/ | compute_cloud.md | Complete (AWS Batch, PROOF/WDL, Nextflow, CloudShell) |
| compute_gpu | /scicomputing/compute_gpu/ | compute_gpu.md | Complete (GPU types, chorus partition, CUDA) |

Also fetched: /pathways/path-batch-computing/ (quickstart redirect target) for supplementary content.

## Skills Created (7)

| Skill | File | Description |
|-------|------|-------------|
| fh.slurm | skills/fh.slurm/skill.md | Submitting and managing Slurm jobs (sbatch, srun, scancel, squeue, sacct) |
| fh.partitions | skills/fh.partitions/skill.md | Gizmo partitions guide with limits, node specs, decision guide |
| fh.grabnode | skills/fh.grabnode/skill.md | Interactive compute sessions via grabnode |
| fh.gpu | skills/fh.gpu/skill.md | GPU computing (requesting GPUs, CUDA, L40S, chorus partition) |
| fh.containers | skills/fh.containers/skill.md | Apptainer/Docker containers on the cluster |
| fh.parallel | skills/fh.parallel/skill.md | Parallel computing patterns (arrays, threading, MPI, workflows) |
| fh.cloud | skills/fh.cloud/skill.md | AWS cloud computing (AWS Batch, PROOF/WDL, Nextflow) |

## Issues and Observations

1. **Quickstart page is deprecated.** It redirects to /pathways/path-batch-computing/ which has only basic content. The real substance lives in compute_jobs and compute_platforms.

2. **Memory is advisory-only.** Slurm at Fred Hutch does NOT enforce memory limits. The documented workaround is requesting 1 CPU per 4 GB needed. This is a significant deviation from standard Slurm behavior and is documented prominently in the skills.

3. **Chorus partition isolation.** Harmony nodes run a different OS and CPU architecture (AMD EPYC vs Intel). Users must `module purge` before loading modules. This is a common source of errors and is emphasized in fh.gpu, fh.partitions, and distilled docs.

4. **GPU distribution.** Standard j/k nodes have only 1 GPU each. Multi-GPU work requires chorus partition (harmony nodes with 4x L40S). This constraint is documented in fh.gpu.

5. **Restart partition naming.** The wiki uses both "restart" and "restart-new" naming. The skill uses "restart-new" with `--qos=restart` as shown in the wiki examples.

6. **Limited parallel computing content.** The wiki page on parallel computing is relatively thin. The fh.parallel skill supplements wiki content with practical job array examples and environment variable usage patterns.

7. **Cloud computing maturity.** Nextflow on AWS is explicitly noted as "not currently fully supported." The skill warns users to consult SciComp before relying on it.

## Completeness Assessment

All 9 pages fetched and distilled. All 7 skills created with proper frontmatter. Content coverage is comprehensive for what the wiki provides. The skills add practical guidance (example scripts, decision guides, common pitfalls) beyond what the wiki pages contain.
