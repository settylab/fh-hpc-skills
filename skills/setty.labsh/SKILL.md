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

## Sandbox build deps (Ubuntu 18.04 / agent-sandbox)

`labsh start` hardcodes `--with notebook-intelligence`, which pulls
`tiktoken`. On the agent-sandbox (and any other Ubuntu 18.04 host with
**glibc 2.27**), `tiktoken==0.12.0` has no compatible binary wheel
(its only Linux wheels are `manylinux_2_28`, requiring glibc ≥2.28),
so `uv` falls back to source build — which fails twice over:

1. No Rust on the default sandbox `PATH`.
2. Even with Lmod's `Rust/1.83.0`, `tiktoken==0.12.0`'s `Cargo.toml`
   requires the `edition2024` cargo feature, which was only stabilized
   in Rust 1.85+.

The recipe that actually makes `labsh start` succeed:

```bash
# 1. Pin tiktoken to a version with a manylinux_2_17 wheel (no source build)
echo 'tiktoken<0.12' > /tmp/labsh-constraints.txt
export UV_CONSTRAINT=/tmp/labsh-constraints.txt

# 2. Provide Rust + a writable CARGO_HOME, so any *other* PyO3 dep that
#    needs to build from source still works. ~/.cargo is not visible
#    inside the sandbox; use ~/.claude/ which is writable.
ml Rust/1.83.0-GCCcore-13.3.0
export CARGO_HOME="$HOME/.claude/cargo-cache"
mkdir -p "$CARGO_HOME"

labsh start
```

`uvx` honours `UV_CONSTRAINT` transparently, so no patch to labsh
itself is required. The recipe is sandbox-specific — on a host with
glibc ≥2.28 (or once the cluster ships Rust ≥1.85), the constraint
becomes unnecessary.

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
