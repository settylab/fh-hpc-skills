---
description: "Lmod environment modules on Gizmo: loading, searching, and managing software"
---

# Using Lmod Environment Modules on Gizmo

TRIGGER when: user asks about loading software on Rhino/Gizmo, using `module` or `ml` commands, finding available software versions, or understanding environment modules at Fred Hutch.

## Context

Fred Hutch uses the Lmod environment module system to manage software on the Rhino login nodes and Gizmo compute cluster. Modules configure your shell environment (PATH, library paths, etc.) so you can access specific software versions without conflicts. Always load software through modules rather than calling binaries directly to ensure reproducibility.

## Instructions

### Essential Module Commands

```bash
# List currently loaded modules
ml

# Load a module (short form)
ml R/4.3.1-gfbf-2022b

# Load a module (long form)
module load R/4.3.1-gfbf-2022b

# Unload a module
ml -R
module unload R

# Purge all loaded modules
ml purge

# Search for all versions of a module (preferred)
module spider R

# Get detailed info and loading instructions for a specific version
module spider R/4.3.1-gfbf-2022b

# List modules currently visible (may be incomplete — see below)
module avail Python/3
module avail fhPython
```

### module spider vs. module avail

**Use `module spider` for discovery, not `module avail`.** Fred Hutch uses Lmod's hierarchical module system, where software compiled against a specific toolchain (compiler + MPI library) is only visible after that toolchain is loaded. `module avail` shows only what is currently visible given your loaded modules; `module spider` searches the entire module tree regardless of what is loaded.

```bash
# This may show nothing if the right toolchain is not loaded:
module avail SomePackage

# This always finds it if it is installed:
module spider SomePackage

# module spider also tells you what you need to load first:
module spider SomePackage/1.2.3
#   You will need to have the following modules loaded:
#     GCCcore/12.3.0
```

The pattern is: `module spider <name>` to find what exists, then `module spider <name/version>` to learn what prerequisites to load, then `module load` those prerequisites followed by your target module.

### Why Use Modules

Loading software via `ml` rather than calling bare commands (e.g., `ml R` instead of just `R`) ensures:
- **Reproducibility**: You get a specific, documented version
- **Correct dependencies**: Required libraries are loaded automatically
- **Latest software**: Access to the most recent versions maintained by SciComp

### Common Module Patterns

```bash
# Load the Fred Hutch curated Python (scientific packages via foss toolchain)
ml fhPython                            # default: fhPython/3.11.3-foss-2023a

# Load JupyterLab with scientific packages
ml purge
ml JupyterLab/4.0.3-GCCcore-12.2.0 Seaborn/0.12.2-foss-2022b

# Load the Fred Hutch curated R (200+ Bioconductor/CRAN extensions)
ml fhR                                 # default: fhR/4.4.1-foss-2023b
```

### Choosing Between Rhino and Gizmo

| Environment | Use Case | Key Trait |
|------------|----------|-----------|
| **Local** | Small tasks, development | Immediate access, limited resources |
| **Rhino** (shared login nodes) | Moderate work, testing | Shared with other users, no job scheduler |
| **Gizmo** (compute cluster) | Production runs, large jobs | Exclusive node access via Slurm, may queue |

On both Rhino and Gizmo, load software through modules.

### When Modules Are Enough vs When You Need More

**Modules are sufficient when:**
- The software you need is already available (`module spider <name>`)
- You are doing interactive exploration or quick analyses
- Your project uses only the packages bundled in fhPython or fhR
- You need tools built against specific compilers/MPI stacks (e.g., CUDA-linked libraries)

**Use uv (Python) or renv (R) when:**
- You need packages not available in modules
- Your project requires exact, lockfile-based reproducibility
- You are building a shared project that others must reproduce
- You are preparing an analysis for publication

**Use mamba (not conda — it is very slow) when:**
- Your project mixes Python + R + system-level C libraries in one environment
- You need bioconda tools not available via PyPI or Lmod
- Configure mamba with the Fred Hutch mirror via project-local `.condarc` (see `fh.python` skill); anaconda.org is blocked
- **PATH ordering matters:** if a mamba env is active when `module load` runs, the module takes precedence. Deactivate all envs, load modules, then `mamba activate` to give the env priority

### Requesting a New Module from FH HPC

If the module you need is not available, the inventory is what
`module spider` shows on the cluster — not the file tree of any
GitHub repo. SciComp builds and maintains modules using the
[EasyBuild](https://easybuild.io/) framework, with FH-local
easyconfigs collected at
[FredHutch/easybuild-life-sciences](https://github.com/FredHutch/easybuild-life-sciences).
The maintainer (`@fizwit`) treats incoming PRs *as build requests*:
the build is what matters; the repo is just one input. An
upstream-stock easyconfig PR will typically be closed without merge
once the build lands on the cluster — that's expected, not a
rejection. Verify with `module spider <Name>/<version>` after a few
days.

For escalations or non-PR-shaped questions: email
`scicomp@fredhutch.org`.

#### Decision tree — which path fits your request

Pick the path that matches the easyconfig you need *and* your time
pressure.

| Path | Easyconfig source | Urgency | Where to file |
|------|-------------------|---------|---------------|
| **A** | Generally useful, no FH-local changes | Need it now | PR on `easybuilders/easybuild-easyconfigs` (upstream EB), then issue on `FredHutch/easybuild-life-sciences` asking for `eb --from-pr <upstream-PR-#>` build |
| **B** | Generally useful, no FH-local changes | Not urgent | PR on upstream `easybuilders/easybuild-easyconfigs` only; FH picks it up after upstream merge |
| **C** | FH-specific (custom config, pinned dep, modified version) | — | PR on `FredHutch/easybuild-life-sciences` with the unique/modified easyconfig — *this kind gets merged* |
| **D** | Already merged upstream, just needs building locally on FH | — | Issue on `FredHutch/easybuild-life-sciences` ("please build `<Name>/<version>`"). PR works too but will be closed-not-merged after the build lands |

**Path A — generally useful + you need it now.** Two-step: open
the PR upstream so the recipe lives in the canonical
`easybuilders/easybuild-easyconfigs` collection, then ask FH HPC
to build it via the EasyBuild `--from-pr` flag without waiting for
upstream review. The flag tells the EB framework to fetch the
recipe from the open PR and build against it locally.

```bash
# example body to send to scicomp / on a FH-side issue:
# please build via:  eb --from-pr <upstream-PR-#>
```

This is the right path when the recipe is generic but the upstream
review queue is slow (often weeks). FH builds immediately; later,
when the upstream PR merges, FH picks it up natively from the
released collection. You skip the upstream-merge wait without
forking the recipe FH-side.

**Path B — generally useful + not urgent.** Open the PR upstream
on `easybuilders/easybuild-easyconfigs` and let FH pick it up after
upstream merge. Slow but zero coordination on the FH side and the
recipe ends up in the canonical place.

**Path C — recipe is FH-specific.** Modified version, custom
toolchain pin, lab-specific dependency injection, an entirely
new recipe that doesn't make sense upstream. Open the PR on
`FredHutch/easybuild-life-sciences` with the unique easyconfig.
fizwit *merges* this kind per the policy of accepting "unique
easyconfigs, or ones that have been modified" (PR
[FredHutch/easybuild-life-sciences#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577)).
This is the only path that produces a long-lived FH-repo
artifact.

**Path D — already merged upstream, just needs building on FH.**
File an *issue* on `FredHutch/easybuild-life-sciences` with a
one-line ask: "please build `<Name>/<version>` for gizmo / harmony
/ chorus". A PR with the stock upstream easyconfig also works —
it's how PR
[#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577)
landed `Rust/1.86.0-GCCcore-13.3.0` on 2026-05-01 — but expect the
PR to be **closed without merge** after the build lands. fizwit's
own words on the same PR: *"I am trying to limit the number of EB
in our github. Just accepting unique easyconfigs, or ones that
have been modified. Treating this PR as a request. The software
inventory is the ultimate list of what is installed, using `module
spider` to create the list. I do not reference the repo as an
inventory."* The build is the deliverable; the PR is just the
trigger. Don't be alarmed by the close.

#### Worked example — the Rust/1.86.0 request (Path D)

PR
[FredHutch/easybuild-life-sciences#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577)
("Add Rust 1.86.0-GCCcore-13.3.0 easyconfig"):

- **Opened:** 2026-04-30 with the stock upstream easyconfig.
- **Outcome:** Closed 2026-05-01, *not merged*. fizwit commented
  *"Rust-1.86.0-GCCcore-13.3.0.eb install for gizmo, harmony, and
  chorus"* and closed the PR.
- **Verification:** `module spider Rust/1.86.0-GCCcore-13.3.0`
  immediately showed the module as loadable.

The lesson: the PR is the request channel; the cluster is the
deliverable surface; `module spider` is the source of truth.

#### Building a request PR or issue

For both Path C (PR) and Path D (issue or PR):

- **Title:** `Add <Name>/<version> easyconfig` (PR) or
  `Please build <Name>/<version>` (issue).
- **Body:** state the requesting use case + lab, the dependency
  chain you need, the target compute environments
  (gizmo / harmony / chorus). Cite the upstream EasyBuild PR if
  you're requesting a Path-A `--from-pr` build, or the upstream
  merged commit for Path D.
- **PR file:** stock easyconfig copied from
  `easybuilders/easybuild-easyconfigs` (Path D), or the modified
  one (Path C).

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use explicit version numbers in module loads for reproducible analyses
- Use `ml purge` before loading a new set of modules to avoid conflicts
- Respect shared infrastructure and other users
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_overview/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_running/
- EasyBuild inventory: https://fredhutch.github.io/easybuild-life-sciences/
- FH easyconfig collection (request channel): https://github.com/FredHutch/easybuild-life-sciences
- Upstream EasyBuild easyconfigs: https://github.com/easybuilders/easybuild-easyconfigs
- EasyBuild docs (`--from-pr`): https://docs.easybuild.io/version-specific/easyconfigs/
