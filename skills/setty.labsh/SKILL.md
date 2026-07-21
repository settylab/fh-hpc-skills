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

## Troubleshooting: "server already running" but nothing serves (phantom-adopt)

**Symptom.** `labsh start` refuses with *"server is already running (pid
NNNN…)"* and returns non-zero, yet no server actually answers — every
health probe / `curl …/api/status` fails, and a supervisor that blindly
retries `start` re-adopts the same dead record on each attempt (a
multi-minute outage that never self-heals).

**Cause.** labsh's *start-guard* decides a server is running by scanning
`$JUPYTER_DATA_DIR/runtime/jpserver-*.json` and trusting the recorded pid
after only a bare `kill -0`. That check is too weak: after an abrupt node
reboot the recorded pid is often **recycled by the OS to an unrelated
live process** (or lingers as a zombie), so `kill -0` succeeds while
nothing serves. The guard adopts the phantom. Note the asymmetry: `labsh
status` *does* verify the pid's argv is a jupyter process (shows "servers:
none"), so **`status` and the `start` guard can disagree** — trust
`status`.

**Fixed upstream** (labsh, pending release): the start-guard now reads
`/proc/<pid>/cmdline` and requires a jupyter process before treating a
record as live, matching what `labsh status` already did, and removes
stale records as it finds them so `start` self-heals. Once your installed
labsh carries that change, this section is obsolete. **Until then** (the
cluster ships an older labsh), apply the manual cleanup below.

**Manual cleanup (older labsh).**
1. Confirm no live server: `labsh status` (and `labsh kernel ps`).
2. For each stale record, verify its pid is dead or not a jupyter process
   (`ps -p <pid> -o comm=`), then remove that **exact** file — `rm
   $JUPYTER_DATA_DIR/runtime/jpserver-<deadpid>.json`. Never broad-glob
   the runtime dir; you could delete a live server's record.
3. `labsh start` again — a real server launches (verify the pid changes
   and `api/status` → 200).

If the `labsh` binary itself was wiped (`start` fails rc=127), reinstall
it (`make -C <labsh-checkout> install-lib`) before step 3.

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

1. **`module load Rust/1.86.0-GCCcore-13.3.0` (Lmod, Gizmo) — the
   canonical fix.** As of 2026-05-01 this is the newest Rust on the
   FH Lmod stack and meets tiktoken's 1.85+ floor. It's the right
   recommendation for Gizmo / harmony / chorus: reproducible across
   users, no project-local toolchain to manage, no sandbox quota
   burned on a `~150 MB` toolchain.

   ```bash
   module load Rust/1.86.0-GCCcore-13.3.0
   labsh start --with-ai
   ```

   The module landed via
   [FredHutch/easybuild-life-sciences#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577)
   (closed-as-build-request — see `fh.modules` "Requesting a new
   module" for why upstream-stock easyconfigs get closed without
   merge once the build lands). Confirm with `module spider Rust`
   before relying on it; the stack moves.

2. **`module load Rust/1.83.0-GCCcore-13.3.0` (or older).** Older
   modules remain on the stack. Use one only if 1.86.0 isn't visible
   for your toolchain hierarchy *and* the calling crate's
   `Cargo.toml` doesn't require Rust ≥ 1.85 (e.g.,
   `tiktoken==0.12` does — see the `UV_CONSTRAINT` shortcut below
   for the no-Rust escape hatch in that exact case).

3. **Skip rust entirely** — confirm the user actually wants the AI
   extension. Default-off is the safe path. `labsh start` (no
   `--with-ai`) gives full base JupyterLab + kernels and never
   pulls `tiktoken` at all. Only stay on the toolchain path if
   `--with-ai` is a hard requirement.

4. **`labsh install-rust` (project-local rustup, planned for v0.5).**
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

5. **Last resort: manual `rustup` install to `~/.cargo`.** Same
   `curl … rustup.rs | sh` invocation as step 4, but without the
   project-local `CARGO_HOME` / `RUSTUP_HOME` redirect. Pollutes
   `$HOME` and is non-reproducible across machines — only use when
   nothing above works and the cost of a global toolchain is
   acceptable for the task.

### agent-sandbox specifics — `UV_CONSTRAINT` shortcut

On the agent-sandbox (Ubuntu 18.04, glibc 2.27) and other glibc-old
hosts there is a fourth option that sidesteps the Rust toolchain
problem entirely: pin `tiktoken` to a version that still ships a
`manylinux_2_17` wheel, so `uv` never falls back to a source build
in the first place.

```bash
# 1. Pin tiktoken to a manylinux_2_17-compatible release.
echo 'tiktoken<0.12' > /tmp/labsh-constraints.txt
export UV_CONSTRAINT=/tmp/labsh-constraints.txt

# 2. Insurance for any *other* PyO3 dep that still needs to build
#    from source. ~/.cargo is not writable inside agent-sandbox;
#    ~/.claude is. The Lmod Rust is fine for everything except
#    tiktoken==0.12 itself, which is what UV_CONSTRAINT removed.
ml Rust/1.83.0-GCCcore-13.3.0
export CARGO_HOME="$HOME/.claude/cargo-cache"
mkdir -p "$CARGO_HOME"

labsh start --with-ai
```

`uvx` honours `UV_CONSTRAINT` transparently — no labsh patch needed.
The constraint pins to `tiktoken==0.11.x`, whose wheel matches glibc
2.17 and dodges the 1.85+ Rust requirement that `tiktoken==0.12.0`'s
`Cargo.toml` introduces (it uses the `edition2024` cargo feature,
stabilized only in Rust 1.85 — Lmod's `Rust/1.83.0` cannot build it).

This is a transient workaround for two overlapping problems, both
already resolved on Gizmo:

- **Default path no longer hits it.** Since
  [katosh/labsh#1](https://github.com/katosh/labsh/pull/1) made
  `notebook-intelligence` opt-in (default off in labsh ≥ 0.4.0), the
  bare `labsh start` path no longer pulls `tiktoken` at all. Only
  `--with-ai` / `LABSH_AI=1` does.
- **Module-load path now works on Gizmo.** As of 2026-05-01
  `Rust/1.86.0-GCCcore-13.3.0` is built on gizmo, harmony, and
  chorus
  ([FredHutch/easybuild-life-sciences#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577)),
  so source-building `tiktoken==0.12` works directly via
  `module load` and the constraint is unnecessary for the
  AI-opt-in case on Gizmo.

The `UV_CONSTRAINT` shortcut remains the no-Rust escape hatch on
glibc-old hosts that don't see the FH module stack — typically
the agent-sandbox itself.

Recipe credit:
[settylab/fh-hpc-skills#8](https://github.com/settylab/fh-hpc-skills/pull/8)
(`@ethieme`).

### When to pick which path

| Context | Recommended path |
|---------|------------------|
| Don't actually need AI extension | Default — no rust needed |
| CI / batch / reproducibility-sensitive | `module load Rust/1.86.0-GCCcore-13.3.0` |
| Gizmo / harmony / chorus interactive, AI extension required | `module load Rust/1.86.0-GCCcore-13.3.0` |
| agent-sandbox (`--with-ai` required) | `UV_CONSTRAINT=tiktoken<0.12` shortcut, OR project-local rustup |
| Non-Gizmo host without Lmod | Project-local rustup (`install-rust` once shipped, manual until then) |
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
