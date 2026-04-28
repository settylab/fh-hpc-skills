---
description: "Sandbox-specific HPC gotchas that look like agent bugs but are bwrap/sandbox correctness: sbatch positional args swallowed, gh auth setup-git read-only gitconfig, /app/bin/pip wrapper hangs (use uv pip), squeue %i format-string ordering, sacct --user blocked"
---

# Setty Lab — agent-sandbox HPC gotchas

TRIGGER when working inside the **agent-sandbox** (bwrap-mounted, kernel-enforced) environment used for nexus / Setty Lab agent work, and any of the following surfaces — the failure looks like the agent's own bug but is actually sandbox correctness:

- `sbatch` job receives empty `$1` / positional args missing
- `git push` prompts for a username; `gh auth setup-git` errors with `Device or resource busy` writing `~/.gitconfig`
- `pip install` hangs for minutes with no output (especially `/app/bin/pip`)
- `squeue -h -o "%i"` returns nothing while `squeue` (no `-o`) returns rows
- `sacct --user $USER` errors with `'--user' is not allowed` (or similar)

If the user is on the regular Gizmo cluster (not the agent-sandbox), these gotchas do not apply — `fh.slurm`, `fh.python`, and `fh.github` are the right references there.

## Why these exist

The agent-sandbox is a kernel-enforced filesystem sandbox (bwrap-style) that protects shared infrastructure. It re-execs Slurm clients, mounts `~/.gitconfig` read-only, restricts `sacct` scope, and in some configurations re-shapes argv for safety. The behaviour is correct and load-bearing. The pain is that the surface errors are misleading: agents read "first arg empty" or "pip hangs" and start debugging their own code instead of switching to the sandbox-friendly workaround.

Fred Hutch SciComp's stock advice is written for the unsandboxed cluster, so `fh.*` skills don't carry these. This skill exists so each new agent doesn't re-burn one or two turns rediscovering the same five things.

## 1. `sbatch script.sh arg1 arg2` — positional args dropped

**Symptom.** Job script crashes immediately at `"${1:?}"` or sees an empty `$1`. The `sbatch` submit succeeds, the job runs, the body of the script never sees the args you passed on the command line.

```bash
sbatch slurm_job.sh chimera_tal1                 # submit OK, job ID printed
# inside the job: $1 is empty -> "DATASET: parameter null or not set"
```

**Root cause.** The sandbox/bwrap wrapper around `sbatch` re-execs the script in a way that drops positional arguments. The submission is registered correctly; the args don't survive the re-exec.

**Workaround.** Pass parameters as environment variables via `--export=ALL,VAR=...` and read them inside the script. Always include `ALL,` so the rest of your environment (modules, `PATH`, etc.) propagates.

```bash
# Submit
sbatch --export=ALL,DATASET=chimera_tal1,SEED=42 slurm_job.sh

# Inside slurm_job.sh
: "${DATASET:?DATASET must be set via --export=ALL,DATASET=...}"
: "${SEED:=0}"
echo "Running on $DATASET with seed $SEED"
```

For multiple parameter sweeps, prefer a job array indexing into a parameter file, or one `sbatch --export=ALL,...` per combination:

```bash
for ds in chimera_tal1 cancer_atlas mouse_e8; do
  sbatch --export=ALL,DATASET=$ds --job-name="job-$ds" slurm_job.sh
done
```

**Cite.** `reports/kompot_revisions_2026-04-18_120000_mahal-coupling-observation.md`, `_121500_mahal-coupling-permutation-done.md`, `_122500_mahal-coupling-final-writeup.md`.

## 2. `gh auth setup-git` cannot write `~/.gitconfig`

**Symptom.** `git push` to GitHub prompts for a username (no credential helper). Running `gh auth setup-git` to install the helper fails with:

```
could not write config file /home/<user>/.gitconfig: Device or resource busy
```

**Root cause.** The sandbox mounts `~/.gitconfig` read-only. `gh auth setup-git` writes a `credential.helper` line to `~/.gitconfig`; the mount blocks the write. Side-effect: any tool that writes to `~/.gitconfig` (including some IDE integrations) silently fails the same way.

**Workaround.** Inject the bot or user token into the push URL once. The URL form bypasses the credential helper entirely:

```bash
# Bot token (preferred for cross-repo work; mint via the nexus helper)
TOKEN=$(/fh/fast/setty_m/user/dotto/nexus/monitor/mint-token.sh)
git push "https://x-access-token:${TOKEN}@github.com/<owner>/<repo>.git" <branch>

# Or, for user-identity pushes (commit graph stays you):
git push "https://x-access-token:$(gh auth token)@github.com/<owner>/<repo>.git" <branch>
```

Once the token is on the URL, `git fetch`/`git pull` against the same remote will inherit it for that command only — set the URL explicitly each invocation rather than caching it in a remote, since the token is short-lived.

**Forthcoming.** A future nexus-local `GIT_CONFIG_GLOBAL` pointing at a writable path (e.g. `$SANDBOX_PROJECT_DIR/.gitconfig`) will let `gh auth setup-git` succeed without the URL workaround. When that lands, the URL form remains correct but is no longer required.

**Cite.** `reports/palantir_2026-04-20_204350_pr178-fix-and-tests.md`, `reports/palantir_2026-04-20_232448_pr178-tests-review.md`.

## 3. `pip install` hangs — always use `uv pip`

**Workspace-wide rule: always use `uv pip install`, never plain `pip install` inside the sandbox.**

**Symptom.** `pip install <anything>` produces no output, no progress bars, no errors. It just sits. After 5+ minutes you `pkill` it and try again. The same install via `uv pip install` finishes in seconds.

```bash
pip install flake8 mypy            # >5 min, no output, had to pkill
uv pip install flake8 mypy         # ~3 s, success
```

**Root cause.** `/app/bin/pip` is a wrapper bash script that runs `ml Python/3.8.2-...` (Lmod module load) before invoking the real pip. The Lmod step interacts badly with the sandbox in a way that hangs the whole pipeline. `uv pip` is a single statically-linked binary — no module load, no wrapper, no hang.

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

This is also documented as a `CLAUDE.md` callout being added in parallel by the `prompt-callouts` agent — same rule, two channels (callout for unconditional rule, this skill for the why).

**Cite.** `reports/palantir_2026-04-20_204350_pr178-fix-and-tests.md`.

## 4. `squeue` inside the sandbox — auto-scoped, with a current scope-filter bug

**Intent.** `squeue` in the sandbox is auto-scoped to the agent's current chaperon project. Jobs from other projects, other sandbox sessions, and other users should not appear, regardless of `-o` format.

**Current bug.** The handler's awk filter (`chaperon/handlers/squeue.sh:274–289`) only applies the scope check when the first format column starts with a digit. With a non-numeric leading column (e.g. `-o "%j ..."`), the filter falls through to an unconditional pass-through and rows from out-of-scope sandboxes within the same user are emitted. With a numeric leading column (e.g. `-o "%i ..."`), the filter activates and you see only your scope — which means an empty result when your scope has no jobs even if a sibling session does.

This is a within-user, cross-project information leak. Cross-user leakage is still blocked by Slurm's own auth (the handler injects `--me`); the open surface is project / session scope inside one user account. Triage and proposed fix: [`nexus_2026-04-28_143841_sandbox-gotcha-triage`](https://github.com/settylab/dotto-nexus/wiki/nexus_2026-04-28_143841_sandbox-gotcha-triage) § "Gotcha 4". The sandbox-side fix is in flight, not yet merged.

**What to do in the meantime.** Don't reach for a format string that "returns rows" — if it returns rows that the numeric-first form doesn't, those extra rows are the leak. Two safe paths:

```bash
# (a) Slurm-native self-scope; bypasses the broken handler filter path.
squeue --me

# (b) Explicit numeric-first format — %i is numeric, so the scope filter activates as intended.
squeue -h -o "%i %j %T"
squeue -h -o "%i" | awk '{print $1}'
```

If `squeue --me` or a numeric-first `-o` form returns less than you expect, the right move is to ask the user rather than search for a format string that produces more rows. "More rows" in this handler means "out-of-scope rows," not "the rows you're missing."

**Cite.** `reports/barnacle_2026-04-28_005212_heartbeat.md`; triage report linked above.

## 5. `sacct --user` blocked in sandbox — drop the flag

**Symptom.** Running `sacct --user $USER ...` fails with a confusing error that suggests the flag itself is unsupported:

```
sacct: error: '--user' is not allowed
```

**Root cause.** The sandbox auto-scopes Slurm queries to the running user. `--user` would let an agent peek at someone else's accounting; the wrapper rejects it categorically. The error doesn't mention that the scope is already applied, which makes it look like a missing feature rather than redundant input.

**Workaround.** Just drop `--user`. Everything you'd see is already filtered to your own jobs.

```bash
# Outside sandbox
sacct --user "$USER" --format=JobID,JobName,State,Elapsed -S 2026-04-01

# Inside sandbox (same result, --user not allowed)
sacct --format=JobID,JobName,State,Elapsed -S 2026-04-01
```

The same auto-scoping applies to `sbatch`, `srun`, `scancel`, and `squeue` — they only see your jobs regardless of flags. Don't try to work around it; don't try to elevate. If you genuinely need cross-user accounting, it's a job for the user on the unsandboxed login node.

**Cite.** `reports/kompot_revisions_2026-04-19_010000_mahal-null-coupling.md`.

## See Also

- `setty.labsh` — project-local JupyterLab kernels; the canonical sandbox-friendly way to keep state across turns.
- `fh.slurm` — generic Slurm submission patterns on Gizmo; everything there applies, plus this skill's `--export=ALL` rule for sandbox-side submits.
- `fh.python` — Python on Gizmo; pairs with rule 3 (always `uv pip`).
- `fh.github` — GitHub auth on Gizmo; pairs with rule 2 (URL-token push form inside the sandbox).
- Nexus `CLAUDE.md` § "Sandbox Integrity" — the full sandbox model, escape-attempt reporting, and how to request access expansion via `~/.config/agent-sandbox/sandbox.conf`.

## References

- Source meta-review: `reports/nexus_2026-04-28_202950_infrastructure-meta-review.md` § theme 7 ("Sandbox surprises that hit every new agent").
- agent-sandbox docs: `/home/dotto/.linuxbrew/Cellar/agent-sandbox/<version>/lib/agent-sandbox/agents/sandbox-help.md`.
