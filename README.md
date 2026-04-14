# fh-hpc-skills

A Claude Code skill plugin for the Fred Hutchinson Cancer Center HPC cluster (Gizmo). It provides contextual, accurate guidance on job submission, storage, software modules, GPU computing, monitoring, and more, loaded on demand as you work.

## What this is

Claude Code loads skills based on what you're doing. Ask about submitting a Slurm job, and it loads `fh.slurm`. Ask about GPU availability, and it loads `fh.gpu` and `fh.monitoring`. Each skill is a focused document covering one topic with commands, examples, pitfalls, and references.

29 skills cover the full surface area of the Fred Hutch HPC:

| Skill | Description |
|-------|-------------|
| `fh.access` | SSH, NoMachine, VPN, Open OnDemand, session persistence |
| `fh.alphafold` | AlphaFold 3 on the chorus GPU partition |
| `fh.aws-access` | AWS account access, SSO login, S3, Batch, cost management |
| `fh.cloud` | AWS cloud computing (Batch, WDL/PROOF, Nextflow, CloudShell) |
| `fh.cluster-overview` | Quick reference: partitions, node hardware, GPU inventory, key paths |
| `fh.containers` | Apptainer/Docker containers on Gizmo |
| `fh.credentials` | HutchNet ID, Slurm access, GitHub org membership, MFA |
| `fh.cromwell` | Cromwell/WDL workflow execution |
| `fh.databases` | MyDB (Postgres, MariaDB, MongoDB, Neo4j), REDCap, MS SQL |
| `fh.data-transfer` | Motuz, Globus, AWS CLI, Aspera, migration to Economy Cloud |
| `fh.github` | Fred Hutch GitHub org, security policies, version control |
| `fh.gpu` | GPU types (1080 Ti, 2080 Ti, L40S), CUDA, chorus partition |
| `fh.grants` | HPC descriptions and citations for grant applications |
| `fh.interactive-sessions` | grabnode, srun, resource flags, session management |
| `fh.linux-basics` | Essential shell commands for HPC users |
| `fh.modules` | Lmod environment modules: loading, searching, managing |
| `fh.monitoring` | Grafana/Prometheus queries, Slurm CLI monitoring, dashboards |
| `fh.nextflow` | Nextflow workflows on Gizmo and AWS Batch |
| `fh.onboarding` | New user checklist for Fred Hutch computational resources |
| `fh.parallel` | Job arrays, threading, MPI, workflow managers |
| `fh.partitions` | Partition specs, node hardware, decision guide |
| `fh.python` | Python modules, virtual envs, conda, Jupyter |
| `fh.r` | R/RStudio modules, packages, Bioconductor, Jupyter R kernel |
| `fh.slurm` | sbatch, srun, scancel, squeue, sacct, job arrays |
| `fh.storage` | Overview of all storage tiers (home, fast, scratch, economy) |
| `fh.storage-fast` | /fh/fast/ POSIX storage: paths, quotas, collaboration |
| `fh.storage-s3` | Economy/S3 storage: CLI, boto3, R, sharing, versioning |
| `fh.storage-scratch` | /hpc/temp/, job-local scratch, tmpfs, performance comparison |
| `fh.vscode-remote` | VS Code remote development with Lmod integration |

## Sources

Skill content is distilled from:

- **[SciComp Wiki](https://sciwiki.fredhutch.org/scicomputing/comp_index/)** — the official Fred Hutch Scientific Computing documentation, covering access, storage, software, and large-scale computing
- **[SciComp Resource Library](https://sciwiki.fredhutch.org/compdemos/)** — 45+ tutorials and how-to guides
- **[SciComp Pathways](https://sciwiki.fredhutch.org/pathways/)** — step-by-step workflows for common tasks
- **Live cluster probing** — partition specs, module versions, mount points, and environment variables verified directly on Gizmo
- **[Grafana](https://grafana.fredhutch.org/)** — dashboard catalog and Prometheus query patterns for cluster monitoring

Where the wiki and the live cluster disagree, we trust the cluster. Deviations are documented in `shared/reports/validation-agent.md`.

## Principles

Every skill upholds these values:

1. **Scientific accuracy** — commands, paths, and configurations are verified against the live cluster. No fabrication.
2. **Reproducibility** — skills encourage versioned environments (modules, containers, conda envs), explicit resource requests, and documented workflows.
3. **Fair resource usage** — skills teach users to request only what they need, use appropriate partitions, and release resources when done. An idle grabnode session wastes what someone else could use.
4. **Cooperation** — the cluster is shared infrastructure. Skills promote `--nice` for non-urgent work, checking cluster load before large submissions, and respecting SciComp policies.
5. **Security** — skills never expose credentials, enforce proper access methods, and flag PHI/PII handling requirements.

## Installation

### Quick install (clone into ~/.claude)

Cloning into `~/.claude/` ensures skills are accessible inside the [agent_sandbox](https://github.com/katosh/agent_sandbox), which mounts `~/.claude` as writable by default. No extra sandbox configuration needed.

```bash
git clone git@github.com:settylab/fh-hpc-skills.git ~/.claude/fh-hpc-skills

# Symlink into the Claude Code config directory (respects custom CLAUDE_CONFIG_DIR)
SKILLS_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
mkdir -p "$SKILLS_DIR"
for skill in ~/.claude/fh-hpc-skills/skills/fh.*/; do
  ln -sf "$skill" "$SKILLS_DIR/$(basename "$skill")"
done
```

If you don't have SSH keys configured for GitHub, use HTTPS instead:

```bash
git clone https://github.com/settylab/fh-hpc-skills.git ~/.claude/fh-hpc-skills
```

### Manual install (single skill)

```bash
SKILLS_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
mkdir -p "$SKILLS_DIR"
cp -r ~/.claude/fh-hpc-skills/skills/fh.slurm "$SKILLS_DIR/"
```

### Verify installation

```bash
SKILLS_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
ls "$SKILLS_DIR"/fh.*/SKILL.md
```

Skills become available immediately in your next Claude Code session. No restart required.

## Usage

Skills load automatically based on context. Just ask naturally:

```
> How do I submit a GPU job?
  → loads fh.slurm, fh.gpu, fh.partitions

> What storage should I use for intermediate files?
  → loads fh.storage, fh.storage-scratch

> How busy is the cluster right now?
  → loads fh.monitoring

> I'm new here, where do I start?
  → loads fh.onboarding
```

You can also invoke skills directly with slash commands if configured:

```
> /fh.slurm
> /fh.monitoring
```

## Project structure

```
skills/              # The deliverable: 29 Claude Code skills
docs/wiki-raw/       # Raw fetched wiki content
docs/wiki-distilled/ # Structured knowledge extracted from wiki + live cluster
shared/reports/      # Agent work reports and validation results
shared/lockfiles/    # Agent coordination (empty when complete)
templates/           # Skill and agent instruction templates
sources.yml          # Wiki URL manifest
```

## Contributing

To update a skill:

1. Check the [SciComp Wiki](https://sciwiki.fredhutch.org/scicomputing/comp_index/) for the latest documentation
2. Verify against the live cluster (paths, modules, partitions may change)
3. Edit `skills/<name>/SKILL.md` directly
4. Ensure the `description:` frontmatter is specific enough for accurate skill loading
5. Run the validation agent to check for inconsistencies

To add a new skill:

1. Create `skills/fh.<name>/SKILL.md` with frontmatter and a TRIGGER line
2. Keep it focused on one topic — if it exceeds ~150 lines, consider splitting
3. Cross-reference related skills rather than duplicating content

## Known limitations

A few items could not be verified from the CLI and remain based on wiki documentation: the Open OnDemand URL and available apps, current SciComp Slack channel names, SMB/NFS desktop mount paths, and the AWS SSO browser flow.

## License

Internal use at Fred Hutchinson Cancer Center.
