---
description: "Sandbox-specific HPC notes for the agent-sandbox: bare pip fork-storms to PID exhaustion (use uv pip, never any pip), scientific-stack install traps (squidpy/Palantir/harmonypy/scIB), tmux 2.6 garbles the Claude Code TUI, Slurm sacct/squeue auto-scope semantics, the sbatch chaperon (refused flags, --export, how the script is delivered, symlinked logs, scancel), sandbox mounts and host-wide /proc and ulimit counts, token-safe git pushes (env credential helper, never a token in the URL)"
---

# Setty Lab — agent-sandbox HPC notes

TRIGGER when working inside the **agent-sandbox** (bwrap-mounted, kernel-enforced) environment used for nexus / Setty Lab agent work, and any of the following surfaces:

- `pip install` hangs for minutes with no output (especially `/app/bin/pip`)
- `sacct` / `squeue` results look filtered or surprising and you're tempted to broaden the query
- `git push` with a token (one-shot cross-repo bot writes) or a push that suddenly authenticates as the wrong identity
- `sbatch` refuses a flag, a job's environment, paths or logs differ from your session, or an `EROFS` appears

If the user is on the regular Gizmo cluster (not the agent-sandbox), `fh.slurm`, `fh.python`, and `fh.github` are the right references; the pip rule still applies for consistency.

## Why this still exists post-v0.5.0

`katosh/agent_sandbox` v0.5.0 (2026-04-28) closed the four bugs that previously shipped with this skill: sbatch positional-args dropping, `~/.gitconfig` being read-only, the `squeue` format-column scope leak, and `sacct --user $USER` being categorically denied. What remains is a smaller set of operational notes — surfaces that are still worth knowing about, but not bugs.

## 1. `pip install` hangs — always use `uv pip`

**Workspace-wide rule: always use `uv pip install`, never plain `pip install`.**

**Symptom.** `pip install <anything>` produces no output, no progress bars, no errors. It just sits. After 5+ minutes you `pkill` it and try again. The same install via `uv pip install` finishes in seconds.

```bash
pip install flake8 mypy            # >5 min, no output, had to pkill
uv pip install flake8 mypy         # ~3 s, success
```

**Root cause.** `/app/bin/pip` is a wrapper bash script that runs `ml Python/3.8.2-...` (Lmod module load) before invoking the real pip. The Lmod step compounds the underlying Isilon NFS metadata latency (`/app` is on the same shared NFS as `/fh/fast/`, and the wrapper triggers hundreds of small `openat` calls during module resolution). `uv pip` is a single statically-linked binary — no module load, no wrapper, no hang. See `reports/nexus_2026-04-14_fs-perf-investigation.md` for the per-syscall numbers (≈19.8 ms × ~529 NFS calls per `pip` invocation).

**Workaround.** Always reach for `uv` first.

```bash
# In a project venv
uv venv .venv
. .venv/bin/activate
uv pip install -r requirements.txt

# Ad-hoc one-shot, no venv
uv tool run flake8 .

# When `pip install` is hard-coded in someone else's Makefile / CI script,
# alias it for the sandbox session:
alias pip='uv pip'
```

If you need a specific Python interpreter, point `uv` at it explicitly (`uv venv --python 3.11`) — don't fall back to `ml Python/...; pip install`.

**This is not just slow — bare `pip` fork-storms to PID exhaustion and can take the node down.** A single `pip download <pkg> --no-deps` once re-exec'd the wrapped `/app/bin/pip` to **10,000+ processes**; every subsequent `fork()` on the box failed with `resource temporarily unavailable`, killing background services and most of the node's concurrent processes. Because `ps` itself could no longer fork, recovery meant killing thousands of pids straight out of `/proc`. So the rule is absolute:

- **NEVER invoke `pip` in ANY form** — not `pip install`, `pip download`, `pip index`, `pip3`, nor `python -m pip`. The wrapper re-execs itself without bound.
- Install with `uv pip install <pkg>` (seconds), one package at a time, under a hard `timeout`.
- Check availability WITHOUT a resolver: `uv pip install --dry-run <pkg>` or `curl -s https://pypi.org/pypi/<pkg>/json`.
- **Bound any command whose process tree can grow without a nameable limit** — `timeout <n>`, and `ulimit -u <n>` in a subshell (use `4096`, not `512` — `512` is too low for `timeout` itself to fork here). `ulimit -u` counts the uid's processes host-wide, so a fixed cap can already be exceeded while a runaway is live; prefer a cap relative to your current count (§8).
- Clean up by recorded pid, never `pkill -f <pattern>` (it reaps sibling workers sharing the launcher argv, plus your own shell).
- **Package-name trap:** verify the *distribution* name before installing — e.g. the BCR/scVDJ tool is `sc-dandelion`, while `dandelion` on PyPI is an unrelated deep-learning framework.
- Install a scientific package into a **separate throwaway venv**, never a pinned analysis `.venv` — a transitive `numpy`/`pandas` upgrade silently invalidates every number already computed.

## 2. Slurm queries are auto-scoped to your user

`squeue`, `sacct`, `scontrol`, and friends inside the sandbox auto-scope to your chaperon project and user. Output is identical to host equivalents minus the cross-project / cross-user rows. Practical consequences:

- `sacct --user $USER`, `--user $(id -un)`, `--user <self-uid>`, and `--me` are accepted silently — pass them or omit them, the result is the same. Cross-user `--user $OTHER` is denied with an actionable message.
- `squeue` with any `-o` format string returns only your in-scope rows. If a query returns less than you expect, ask the user rather than reaching for a different format string — there's no "more rows" to be unlocked from inside the sandbox.

If you genuinely need cross-user accounting, that's a job for the user on the unsandboxed login node.

Inside that scope, some queries still answer wrongly at rc 0 (details in `reference/slurm-chaperon.md` → Queries):

- `sacct -s <STATE>` can return a silent zero; query without `-s` and filter with `awk`. The job that prompted the question must appear in the result.
- `squeue %o` and `sacct SubmitLine` show only the chaperon wrapper, never your script: identify jobs by `-J` name and WorkDir.
- `sstat -j <id>_<task>.batch` fails on array tasks; `sstat -j <id>_<task> -a` works.

## 3. Token-bearing git pushes — keep the token in the environment, reset the helper list

**Never put a token in a git URL or in argv** (`https://x-access-token:…@github.com/…`, `-c http.extraheader=…`; base64 is not protection). Measured in the sandbox:

- the URL is in git's argv, readable via `/proc/<pid>/cmdline` by every same-uid process (sibling agents included) for the whole call;
- with a global `credential.helper cache`, git **approves** the URL credential into the shared cache, so for the cache lifetime every session's "user" push to that host silently ran as the bot (403s);
- a clone or fetch URL is written verbatim into `.git/logs/**` (reflog) and survives `remote set-url`.

Use a helper that reads the token from the environment, and clear inherited helpers first:

```bash
# Bot identity, one-shot cross-repo write (T = a short-lived installation token, however your setup mints it)
GH_TOKEN="$T" git -c credential.helper= \
  -c credential.helper='!f() { echo username=x-access-token; echo "password=$GH_TOKEN"; }; f' \
  push https://github.com/<owner>/<repo>.git <branch>

# User identity (commit graph stays you)
git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin <branch>
```

The leading empty `credential.helper=` clears the inherited list (the cache); on its own it fails rc 128 by design. If a user push fails "denied to …[bot]", a cached bot token is the first suspect: `git credential-cache exit` clears it, but the cache is shared, so ask first. Never print `git reflog`, `remote -v` or `config -l` of a repo that may once have been cloned with a tokenized URL. For sustained bot-write workflows, prefer tooling that mints per call (the `nexus.bot` skill in a nexus workspace).

## 4. Scientific-stack install traps in the sandbox

The single-cell / spatial Python stack needs specific pins and shims to run in the sandbox (Ubuntu 18.04, **glibc 2.27**, g++ 7.5, py3.12 venvs). All of the failures below fail *soft* — a caught exception becomes a `NaN` or a mis-shaped array rather than a hard error — so they corrupt results silently. Build compiled deps as wheels first (`uv pip install --only-binary=:all: numpy scipy h5py torch pandas`), then let pure-python deps (docrep, …) build from sdist; a global `--only-binary=:all:` fails on docrep.

**squidpy** (py3.12 venv):
```bash
uv pip install --only-binary=:all: pyproj==3.7.1      # FIRST: 3.7.2 has no py3.12 wheel; sdist fails ("proj executable not found")
uv pip install "squidpy==1.8.2" "pyproj==3.7.1" "setuptools<81"   # setuptools<81: xarray_schema imports removed pkg_resources
uv pip install joblib==1.4.2
```
Do **NOT** set `JOBLIB_MULTIPROCESSING=0` — it forces joblib's threading backend, but squidpy's `parallelize` passes `inner_max_num_threads` (loky-only), which threading rejects → `nhood_enrichment` crashes (`AssertionError: ThreadingBackend does not accept … inner_max_num_threads`). Leave the default loky backend. (squidpy 1.6.5 is incompatible with scanpy 1.12 — use 1.8.2.)

**Palantir 1.4.4 / harmonypy 2.0 / cellrank ≥2.1**:
- Palantir hangs unless `LOKY_MAX_CPU_COUNT` is set (`joblib._count_physical_cores` raises "found 0 physical cores"). Export `LOKY_MAX_CPU_COUNT=8 OMP_NUM_THREADS=4` before `run_palantir`.
- Palantir `core.py:762` — `bp.values[...] = 1` fails `assignment destination is read-only` on pandas ≥2 (`.values` is a read-only view). Patch the installed file to build the DataFrame directly: `bp = pd.DataFrame(np.eye(len(terminal_states)), index=terminal_states, columns=terminal_states)`.
- `read_h5ad` returns non-writable `obsm`/`X` → in-place writes fail. After load: `for k in a.obsm: a.obsm[k] = np.array(a.obsm[k], order="C")` and copy `X`.
- harmonypy 2.0's `run_harmony(data_mat, meta, vars_use)` takes cells×PCs and returns `Z_corr` as cells×PCs (no transpose). scanpy's `sce.pp.harmony_integrate` wrapper assumes the old PCs×cells layout and silently mis-shapes output — call `harmonypy.run_harmony` directly, use `.Z_corr` untransposed.
- cellrank ≥2.1 dropped top-level `cellrank.logging`. Shim: `try: from cellrank import logging as logg` / `except ImportError: from scanpy import logging as logg` (API-compatible).

**scIB 1.1.7** (LISI + graph metrics silently NaN on glibc 2.27):
```bash
# 1. LISI kernel ships a prebuilt knn_graph.o needing GLIBC≥2.34 — recompile locally:
cd <venv>/lib/python3.*/site-packages/scib/knn_graph && \
  cp knn_graph.o knn_graph.o.prebuilt.bak && \
  g++ -std=c++11 -O3 knn_graph.cpp -o knn_graph.o
```
```python
# 2. graph_connectivity calls pd.value_counts (removed in pandas ≥2) — shim BEFORE importing scib:
if not hasattr(pd, "value_counts"):
    pd.value_counts = lambda x, **k: pd.Series(x).value_counts(**k)
```

**Heavy loads on a contended node:** the foreground Bash 2-min timeout kills large (5 GB+) `h5ad` reads, and `nohup` children of a timed-out shell get killed with it. Run heavy steps as background jobs and wait on the completion notification.

R-side equivalents (Monocle 3, `qs`/`anndataR`) live in `fh.r`.

## 5. tmux 2.6 garbles the Claude Code TUI

The sandbox ships **tmux 2.6** (`tmux -V`). Claude Code's TUI uses synchronized output (DCS `?2026h/l`), RGB negotiation, and DCS passthrough — none proxied correctly before tmux 3.2–3.3 — so the display garbles intermittently ("malformed tmux"). This is a **version limitation of the host's tmux, not a bug the sandbox can patch away in config**: no 2.6 config fully fixes the escape proxying.

The durable fix is to **run a newer tmux**, and the sandbox already helps you there — the `bin/tmux` wrapper it ships auto-prefers a newer tmux binary if one is reachable, and its `sandbox-tmux.conf` already sets the Claude Code compatibility options (`terminal-features ",*:RGB"`, `allow-passthrough on`, extended-keys, truecolor override) behind version-safe `set -q` guards. So the one action left to you is to install a newer tmux **outside** the sandbox (`brew install tmux` for 3.5+); the wrapper picks it up automatically on the next session. No further config is required, and no sandbox change fixes the underlying 2.6 rendering — it is a host-version constraint.

Inside the cluster a newer tmux is also available through Lmod: `module load tmux/3.4-GCCcore-13.2.0` (the full name; a bare `tmux/3.4` does not resolve). That matches GitHub's `ubuntu-latest`, so a "fails only on tmux 3.x in CI" claim can be tested locally. Run it on a private socket (`env -u TMUX tmux -L <name>`), never against the session's live server (§8).

## 6. Slurm through the sandbox chaperon

`sbatch` goes through a whitelisting wrapper that re-wraps every job. Its refusals are terminal: never retry or route around one. Full list and measurements: [reference/slurm-chaperon.md](reference/slurm-chaperon.md).

- **Refused:** `%x` in `--output`/`--error` (plain Slurm accepts it; use a literal prefix + `%j`/`%A_%a` here), `--kill-on-invalid-dep`, `--chdir`, `--input`, short flags like `-c1`, `#SBATCH` lines with inline comments, `--export` naming `PATH`, `--export=NONE,VAR`, `scontrol update ArrayTaskThrottle=`, and any submit whose cwd is outside the project (`cd /abs/project && sbatch …`). `--test-only` sees none of these.
- **`--export=NONE` gives bash's default PATH**, so `git` is the system 2.17.1 and other tools are old: smoke every verb under `env -i PATH=/usr/bin:/bin` first. Put `--export=NONE` in the script too, and never export `*_TOKEN`-shaped variables (the job record stores them).
- **Delivery differs from plain Slurm:** a bash body is piped to `bash -s` (`$0` = `/bin/bash`); a Python script is staged with its `#SBATCH` lines stripped and exec'd, so its shebang may carry only ONE argument (`-IB`, not `-I -B`) and a self-hash of `argv[0]` never matches. Fixtures must reproduce the real delivery.
- **`$HOME` is a tmpfs** (lost at job end, rc 0); `$TMPDIR`'s bare job dir is shared with the chaperon: use your own subdir. **Logs are symlinks:** freeze with `cp -L` + `chmod 0444` before hashing or pinning.
- **No `scancel` form has been shown to run an in-job trap; release resources from outside the job** once sacct shows it terminal. `scancel` may return rc 127 while the signal was delivered.

## 7. Filesystem and environment inside the sandbox

Detail: [reference/filesystem-and-processes.md](reference/filesystem-and-processes.md).

- The parent of your project bind (`/fh/fast/<lab>`) is always read-only; after an `EROFS` read your project bind's own row in `/proc/mounts`. An RO incident is sandbox-local: Slurm jobs keep writing.
- `/` is a writable private tmpfs, so a relative path after `cd /` really writes there. Probe with `test -w`, never `touch`.
- After a mount repair, a long-lived shell's cwd can silently fail every relative write: `cd -- "$PWD"` per loop iteration and write by absolute path.
- The scratchpad is on `/tmp`, another filesystem: `mv` into the project is copy + delete and can fail half-way. `/tmp` may be shared between sandboxes: never write into a pre-existing `/tmp` dir you did not create.
- The batch environment (TMPDIR, cwd, injected variables) is not your session's; a session green is not evidence for a job. A session replay must copy the job's whole `export` block.

## 8. Processes, `/proc` and the tmux server

- `/proc/loadavg`, `/proc/stat` and `top`'s CPU line describe the whole node, not your sandbox; count your own tasks with `ps -u "$USER"`. Load is still the right number to record beside a timing-sensitive result.
- `ulimit -u` is host-wide while `ps` shows only the namespace: use a cap relative to your current thread count, and treat `fork: Resource temporarily unavailable` as void, not a test failure.
- **The tmux server is the sandbox.** `kill-server`, killing the last session, or `kill-window` on the last window ends every agent, service and the user's session. Test tmux only on `env -u TMUX tmux -L <private>`, with a short `TMUX_TMPDIR` (`sun_path` is 107 bytes).
- Exit words: `Aborted` = it killed itself, `Killed` = SIGKILL (OOM or `kill -9`), `Terminated` = SIGTERM.

## 9. Network, mail and git transport

- **Check, do not assume, network isolation in batch jobs.** The filter has been observed to fall back to unfiltered on compute nodes, with a `network filter fell back from 'filtered' to 'open'` line in the job log. Without evidence of no traffic, write "network use not measured".
- Outbound mail is disabled (exit 77): email is not an escalation channel from inside the sandbox.
- `git@github.com:` failing "correct access rights" after `No user exists for uid N` is a passwd/NSS problem, not auth: `getent passwd "$(id -u)"`. Use HTTPS plus the §3 helper meanwhile.
- `git clone` on NFS under a short `timeout` dies in checkout (rc 124); give clones a long bound.

## See Also

- `setty.labsh` — project-local JupyterLab kernels; the canonical sandbox-friendly way to keep state across turns.
- `fh.slurm` — generic Slurm submission patterns on Gizmo.
- `fh.python` — Python on Gizmo; pairs with rule 1 (always `uv pip`).
- `fh.github` — GitHub auth on Gizmo; pairs with rule 3 (env credential-helper push form).
- `fh.storage-fast` → `reference/nfs-pitfalls.md` — NFS caching, mount entries, `st_dev` per node, setgid modes, hard-linked trees.
- `nexus.bot` — `ng` verbs for routine bot-identity GitHub writes; reach here before the §3 helper form for anything that isn't a one-shot push.
- Nexus `CLAUDE.md` § "Sandbox Integrity" — the full sandbox model, escape-attempt reporting, and how to request access expansion via `~/.config/agent-sandbox/sandbox.conf`.

## References

- `katosh/agent_sandbox` v0.5.0 release notes — fixed sbatch arg-passing, `~/.gitconfig` writability (`HOME_SEEDED_FILES`), `squeue` scope filter on every row, and `sacct --user $USER` partial-acceptance.
- `reports/nexus_2026-04-28_143841_sandbox-gotcha-triage.md` — the triage that mapped each gotcha to its upstream fix.
- `reports/nexus_2026-04-14_fs-perf-investigation.md` — the NFS metadata-latency numbers behind the `pip` slowness.
- agent-sandbox docs: `/home/dotto/.linuxbrew/Cellar/agent-sandbox/<version>/lib/agent-sandbox/agents/sandbox-help.md`.
