---
description: "Sandbox-specific HPC notes for the agent-sandbox: /app/bin/pip wrapper hangs (use uv pip), Slurm sacct/squeue auto-scope semantics, x-access-token URL push form for one-shot cross-repo bot writes"
---

# Setty Lab — agent-sandbox HPC notes

TRIGGER when working inside the **agent-sandbox** (bwrap-mounted, kernel-enforced) environment used for nexus / Setty Lab agent work, and any of the following surfaces:

- `pip install` hangs for minutes with no output (especially `/app/bin/pip`)
- `sacct` / `squeue` results look filtered or surprising and you're tempted to broaden the query
- `git push` to a repo where you don't want to install a credential helper (one-shot bot-token writes)

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

## 2. Slurm queries are auto-scoped to your user

`squeue`, `sacct`, `scontrol`, and friends inside the sandbox auto-scope to your chaperon project and user. Output is identical to host equivalents minus the cross-project / cross-user rows. Practical consequences:

- `sacct --user $USER`, `--user $(id -un)`, `--user <self-uid>`, and `--me` are accepted silently — pass them or omit them, the result is the same. Cross-user `--user $OTHER` is denied with an actionable message.
- `squeue` with any `-o` format string returns only your in-scope rows. If a query returns less than you expect, ask the user rather than reaching for a different format string — there's no "more rows" to be unlocked from inside the sandbox.

If you genuinely need cross-user accounting, that's a job for the user on the unsandboxed login node.

## 3. Cross-repo bot-token pushes — URL form

For one-shot pushes to a repo where you don't want to install a credential helper (or where the helper is already configured for a different identity), inject the token into the push URL once. The URL form bypasses the credential helper entirely:

```bash
# Bot token (preferred for cross-repo writes; mint via the nexus helper)
TOKEN=$(/fh/fast/setty_m/user/dotto/nexus/monitor/mint-token.sh)
git push "https://x-access-token:${TOKEN}@github.com/<owner>/<repo>.git" <branch>

# Or, for user-identity pushes (commit graph stays you):
git push "https://x-access-token:$(gh auth token)@github.com/<owner>/<repo>.git" <branch>
```

Set the URL explicitly each invocation rather than caching it in a remote — bot tokens are short-lived and you don't want them in `.git/config`. For sustained bot-write workflows, prefer the `nexus.bot` skill's `ng` verbs (which mint per-call).

## See Also

- `setty.labsh` — project-local JupyterLab kernels; the canonical sandbox-friendly way to keep state across turns.
- `fh.slurm` — generic Slurm submission patterns on Gizmo.
- `fh.python` — Python on Gizmo; pairs with rule 1 (always `uv pip`).
- `fh.github` — GitHub auth on Gizmo; pairs with rule 3 (URL-token push form).
- `nexus.bot` — `ng` verbs for routine bot-identity GitHub writes; reach here before the URL-token form for anything that isn't a one-shot push.
- Nexus `CLAUDE.md` § "Sandbox Integrity" — the full sandbox model, escape-attempt reporting, and how to request access expansion via `~/.config/agent-sandbox/sandbox.conf`.

## References

- `katosh/agent_sandbox` v0.5.0 release notes — fixed sbatch arg-passing, `~/.gitconfig` writability (`HOME_SEEDED_FILES`), `squeue` scope filter on every row, and `sacct --user $USER` partial-acceptance.
- `reports/nexus_2026-04-28_143841_sandbox-gotcha-triage.md` — the triage that mapped each gotcha to its upstream fix.
- `reports/nexus_2026-04-14_fs-perf-investigation.md` — the NFS metadata-latency numbers behind the `pip` slowness.
- agent-sandbox docs: `/home/dotto/.linuxbrew/Cellar/agent-sandbox/<version>/lib/agent-sandbox/agents/sandbox-help.md`.
