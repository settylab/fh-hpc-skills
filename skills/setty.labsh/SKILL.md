---
description: "labsh: project-local JupyterLab with CLI-driven stateful kernels for iterative analysis; Setty Lab go-to when data is slow to load"
---

# Setty Lab — labsh for stateful experimentation

TRIGGER when: user asks about stateful experimentation, iterative analysis on slow-to-load data, keeping a kernel alive across agent turns, executing Python against a running notebook from the CLI, inspecting live kernel variables, or specifically mentions `labsh`, `JupyterLab in the project`, or "don't reload the data each time".

## Context

`labsh` ([github.com/katosh/labsh](https://github.com/katosh/labsh)) is a
project-local JupyterLab wrapper with CLI access to live kernels. It
solves the recurring Setty Lab problem where a dataset (large `AnnData`
object, trained model, trajectory graph) takes minutes to load but each
subsequent operation is fast — reloading once per agent turn is
unacceptable friction, and clicking through the web UI is non-scriptable.

With `labsh`, the agent runs the server headlessly, attaches a kernel to
a notebook, and executes code against the kernel's live namespace from
the shell. Variables persist; re-runs are cheap. The same server also
serves the normal browser UI, so a human can open the notebook and drive
it interactively while the agent continues to script against the same
kernel.

`labsh` runs entirely from the current directory (config, kernels, auth
token under `./.jupyter`, venv under `./.venv`) — no writes to `~/.local`,
no cross-project leakage, and a fresh clone gets a clean state.

## When to prefer labsh

- **Slow-to-load data.** 30 s+ to read/process the dataset. Reloading
  every turn burns wall-time and spins up the same large memory
  footprint repeatedly.
- **Iterative exploration.** Chained analysis steps where each depends
  on the previous result (`df = ...` → `fit = model(df)` →
  `plot(fit)`). Keeping state in a kernel is exactly what notebooks
  are for.
- **Agent-driven notebook construction.** Appending cells with
  `labsh notebook append --execute` writes both the source and the
  captured outputs, so the resulting `.ipynb` is reviewable.
- **Mixed human + agent work.** Researcher opens the notebook in the
  browser; the agent runs `labsh kernel exec` against the same kernel
  from a different tmux pane.

Skip `labsh` for one-shot scripts (no state to preserve), batch Slurm
jobs (`sbatch` a `.py`), or when JupyterLab via an Lmod module fits
your workflow (see `fh.python`).

## Install

```bash
# Homebrew (Linux) — recommended on Gizmo
brew tap katosh/tools
brew install labsh

# Or from source (requires uv on PATH)
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/katosh/labsh.git
cd labsh && make install    # installs to ~/.local/bin/labsh
```

## Usage

### One-time per project

```bash
cd /path/to/project
labsh kernel add                        # create .venv, register kernel
labsh kernel install scanpy kompot      # add packages as needed
```

### Agent-driven (background mode)

```bash
labsh start                             # daemonize; log at .jupyter/labsh.bg.log
labsh notebook attach analysis.ipynb    # spawn a kernel for the notebook
labsh kernel exec -n analysis.ipynb "import scanpy as sc; adata = sc.read_h5ad('data.h5ad')"
labsh kernel exec -n analysis.ipynb "adata.shape"           # still loaded next turn
labsh kernel inspect -n analysis.ipynb                      # whos-style variable listing
labsh notebook append -n analysis.ipynb --execute "sc.pl.umap(adata, color='leiden')"
labsh stop                              # shutdown when done
```

### Human-driven (foreground mode)

```bash
labsh                                   # runs in tmux pane, prints URL + token
# Open the printed URL in a browser and work interactively.
# An agent in another pane can still attach:
labsh kernel exec -n analysis.ipynb "adata.obs['leiden'].value_counts()"
```

### Inspecting state

```bash
labsh status                            # server + kernel summary
labsh kernel ps                         # live kernels: PID, notebook, kernelspec
labsh kernel inspect -n analysis.ipynb  # variables in the kernel's namespace
```

## Shared-node etiquette

`labsh` daemonized with `labsh start` holds a kernel process in memory
on the compute node. On the Setty Lab shared `gizmok1` (see
`fh.settylab-interactive`), that memory counts against the pool shared
with everyone else on the node. Run `labsh stop` when you step away,
and don't leave abandoned kernels holding an `AnnData` object for days.
`labsh kernel ps` shows what's alive; `labsh status` shows the server
as a whole.

Outside the shared node, the same applies to any `grabnode` or `srun
--pty` session (`fh.interactive-sessions`): kill the server before
releasing the allocation, or you're leaking memory in the remaining
walltime.

## Network and auth

`labsh` binds to `0.0.0.0` by default (reachable on the local network)
and writes a stable token to `./.jupyter/token` (mode `0600`). On a
shared login or compute node, prefer `labsh start --ip 127.0.0.1` and
SSH-tunnel from your laptop:

```bash
ssh -L 8888:localhost:8888 user@gizmok1.fhcrc.org
```

For network-visible binds, use `labsh start --https` — `labsh`
auto-generates a self-signed cert under `.jupyter/ssl/`.

## Rust toolchain fallback (only relevant for `--with-ai` / `LABSH_AI=1`)

The `notebook-intelligence` extension (opt-in via `--with-ai` or
`LABSH_AI=1`, off by default since labsh v0.4.0) pulls `tiktoken`,
which only ships `manylinux_2_28` wheels. On hosts with glibc < 2.28
(Ubuntu 18.04, RHEL 7, the agent-sandbox) `uv` falls back to a
**source build that needs Rust ≥ 1.85**. None of this matters in the
default opt-out config — `labsh start` works fine without rust on a
glibc-old host, the AI extension just isn't loaded.

When the user *does* want the AI extension on a glibc-old host, work
through the fallback chain in this order:

1. **Skip rust entirely** — confirm the user actually wants the AI
   extension. Default-off is the safe path. `labsh start` (no
   `--with-ai`) gives full base JupyterLab + kernels. Only continue
   below if `--with-ai` is a hard requirement.

2. **`module load Rust/<version>` (Lmod, Gizmo).** Check what's
   available before recommending a version:

   ```bash
   module avail Rust
   ```

   As of 2026-04, the FH Lmod stack tops out at
   `Rust/1.83.0-GCCcore-13.3.0` (default `(D)`) — **too old** for
   tiktoken's 1.85+ requirement. [FredHutch/easybuild-life-sciences
   #577](https://github.com/FredHutch/easybuild-life-sciences/pull/577)
   adds `Rust/1.86.0-GCCcore-13.3.0`; once it lands,
   `module load Rust/1.86.0-GCCcore-13.3.0` is the cleanest fix and
   the right recommendation for Gizmo (no project-local toolchain to
   manage, reproducible, lives outside the sandbox quota).

   Re-run `module avail Rust` instead of trusting this snapshot — the
   stack moves.

3. **`labsh install-rust` (project-local rustup, planned for v0.5).**
   When no compatible module exists (e.g., on the agent-sandbox host,
   or any non-Gizmo target) the labsh-shipped helper bootstraps
   rustup-init into `./.jupyter/.cargo/` and `./.jupyter/.rustup/` —
   same per-project pattern as `.jupyter/.labshvenv`. No
   `~/.local` writes, no Lmod, `uv` picks up `cargo` from
   `$CARGO_HOME/bin` once the helper exports the paths.

   ```bash
   labsh install-rust          # idempotent; bootstraps under ./.jupyter/.cargo
   labsh start --with-ai       # toolchain sourced before uv sees the build
   ```

   **Status (as of labsh v0.4.0): `install-rust` is proposed but not
   yet shipped.** It's the consensus follow-up from
   [katosh/labsh#1](https://github.com/katosh/labsh/pull/1) (see the
   comment thread for the design). Until it lands, the manual
   equivalent is:

   ```bash
   export CARGO_HOME="$PWD/.jupyter/.cargo"
   export RUSTUP_HOME="$PWD/.jupyter/.rustup"
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- \
       --default-toolchain stable --no-modify-path -y
   export PATH="$CARGO_HOME/bin:$PATH"
   labsh start --with-ai
   ```

### When to pick which path

| Context | Recommended path |
|---------|------------------|
| Don't actually need AI extension | Default — no rust needed |
| CI / batch / reproducibility-sensitive | Module load (when ≥ 1.85 ships) |
| Gizmo interactive, AI extension required | Module load if available, else project-local rustup |
| agent-sandbox / non-Gizmo host | Project-local rustup (`install-rust` once shipped) |
| One-off experiment, host-rust available | Whatever's already on `$PATH`, fastest |

The module-load path is preferred when available because it's
reproducible across users on the same node and doesn't burn
sandbox / project-quota disk on a `~150 MB` toolchain. Project-local
rustup is the universal fallback that always works.

## See Also

- `fh.python` — Python on Gizmo (uv, modules, venvs); the
  complementary skill for how the `.venv` behind the kernel gets its
  packages and Python version.
- `fh.settylab-interactive` — Setty Lab shared `gizmok1` via
  barnacle; where most lab `labsh` sessions will actually run.
- `fh.interactive-sessions` — `grabnode` / `srun --pty` for
  non-settylab or dedicated-resource work.
- `setty.plots` — the lab's figure conventions; pair with
  `labsh notebook append --execute` for publication-grade notebooks.

## References

- Repo: <https://github.com/katosh/labsh>
- Agent-oriented reference: <https://github.com/katosh/labsh/blob/main/doc/labsh.md>
