# Slurm through the sandbox chaperon

Inside the agent-sandbox, `sbatch` goes through a whitelisting wrapper (the "chaperon") that re-wraps every job. Its refusals are terminal: do not retry or route around one. Everything here was measured inside the sandbox; plain Gizmo Slurm behaves as documented in `fh.slurm`.

## Refused or rewritten at submit

- **`%x` in `--output`/`--error`** ("agent-controlled and could change the directory slurmstepd writes to"). Use a literal prefix plus `%j` or `%A_%a` (`--output=/abs/proj/logs/align_%j.out`). Plain Slurm accepts `%x`; the generic examples in `fh.slurm` and `fh.reproducibility` use it and fail only here.
- `--kill-on-invalid-dep`, `--chdir` (WorkDir is always the submit cwd), `--input`, `sacct -B`, short flags such as `-c1` (use the long form), and an `#SBATCH` line carrying an inline comment.
- **A submit whose cwd is outside the project** (`cd / && sbatch …`: "working directory / is outside the project directory … Do not retry"). Write submit lines as `cd /abs/project/dir && sbatch job.sbatch`, keep `--output`/`--error` absolute, and never rely on `SLURM_SUBMIT_DIR` or a relative path before the script's own `cd`. One re-submit from a project cwd is compliant; a second refusal means stop and ask.
- `--export` containing `PATH`, and any `--export=NONE,VAR` form ("Slurm does not allow explicit variables with NONE").
- `scontrol update … ArrayTaskThrottle=` is refused: an array's `%N` cannot be changed after submit, so size it at submit (pilot `MaxDiskRead / Elapsed` in `sacct`; stagger heavy `/fh/fast` readers).
- `--dependency=afterok|afterany:<id>` IS accepted; confirm with `squeue -o '%i %E'` right after submit.
- **`--test-only` sees none of these** (nor a missing `--export=NONE`, nor QOS/partition refusals). Run it once per distinct flag shape (with `--dependency` and `--array` included) and still read the real submit's outcome and `squeue %r` reason.
- Never pass sbatch flags through an unquoted zsh variable: `S="--job-name=x --dependency=singleton"; sbatch $S` sends ONE argument, which becomes the job name, and the dependency is silently dropped. Build flags in a bash array.

## Job environment (`--export`)

- Bare `--export=NONE` works, and the job then has bash's built-in default PATH (`/usr/local/sbin:…:/usr/bin:/bin`): `git` is the system 2.17.1 (no `worktree add -q`, rc 129) and `/usr/bin/setsid` lacks `-f`. Call tools by absolute path, set `LANG`/`LC_ALL` in the script, and smoke EVERY verb the payload uses under the job env (`env -i PATH=/usr/bin:/bin …`) before submitting. Session tests on your interactive PATH test the wrong tools.
- Put `#SBATCH --export=NONE` IN the script as well as on the command line: the default export copies the session's API-key names into the job. When a job's environment looks wrong, diff the good and bad jobs' `#SBATCH` headers before theorising about the platform.
- Never export credential-shaped variables (`*_TOKEN`, `*_API_KEY`, `GH_*`): Slurm stores the exported environment in the job record at submit, readable cluster-side, so an in-job `env -i` is too late.
- The sandbox injects a site-configured credential-path variable into every batch env even under NONE. A names-only env assert must allow exactly that name; never `unset` it in-job to make an assert pass.
- `VAR=x sbatch --export=ALL` did not deliver VAR. `--export=ALL,K=V` works, but Slurm splits on commas: pass comma-valued parameters as arguments or in a file.
- An `sbatch` issued inside a job does not inherit `SBATCH_*` variables (e.g. `SBATCH_CONSTRAINT`); the child ran unconstrained at rc 0. Put routing flags explicitly on the child's line.
- The batch environment differs from your session in `TMPDIR`, cwd, filesystems and injected variables, so a session green is not evidence for the job. A session replay of a job's computation must copy the job's WHOLE `export` block: a replay missing one variable silently used a code default and moved every downstream number, while its control compared a quantity that variable did not touch.

## How the script reaches the node

- **Shell shebang:** the body is piped to `bash -s -- <args>`. `$0` is `/bin/bash`; `BASH_SOURCE` and `dirname "$0"` name nothing; `exec timeout … "$0" "$@"` runs `/bin/bash <arg1>` and dies rc 127. Re-exec the committed script by ABSOLUTE path, with `</dev/null`.
- **Non-shell shebang (Python):** the `#SBATCH` lines are stripped, the rest is written to `/tmp/.chaperon-script-*`, made executable and exec'd. `__file__` is that copy (no siblings or configs beside it), and a self-check hashing `sys.argv[0]` against the committed sha can never pass.
- **The kernel parses that shebang**, passing everything after the interpreter as ONE argument: `#!/venv/bin/python -I -B` hands Python the option `"-I -B"` and dies rc 2 before any code runs. Combine flags (`#!/venv/bin/python -IB`); sweep with `git grep -nE '^#!\S+( +\S+){2,}'`.
- **Self-sha that works:** hash the absolute committed path against a sha passed in argv or a literal. Stronger: a thin launcher reads the payload bytes once, verifies them, and executes THOSE bytes (`exec(compile(b, path, "exec"))`; for bash, a 0400 temp copy re-hashed before running).
- **Fixtures must use the real delivery:** `grep -v '^#SBATCH' job.sh | /bin/bash -s -- args`, exec a byte copy for Python (`chmod +x copy && ./copy args`), or a one-task real sbatch canary. A copy your fixture stages byte-identical, or `[python, "-I", "-B", job.py]`, cannot catch the stripping or the shebang split.

## Job filesystem

- `$HOME` in a job is a tmpfs ("home: tmpwrite (writes to tmpfs — not persisted)"): results under `~/` vanish at job end while the job reports rc 0. Write outputs under the project.
- `$TMPDIR` is `/loc/scratch/$SLURM_JOB_ID`, and that bare directory also holds the chaperon's own directory and read-only mounts. `rm -rf "$TMPDIR"` hit "Device or resource busy" and 32 read-only entries, and the job still ended rc 0. Create and remove only your own subdir (`mkdir "$TMPDIR/<name>"` without `-p`, refuse if it exists) and put `HOME`, `TMPDIR`, `MPLCONFIGDIR` inside it. Caveat: in one measurement (2026-10) `$TMPDIR` was a RAM tmpfs, not the node NVMe that `fh.storage-scratch` lists; check `df -T "$TMPDIR"` in a job before sizing on it.
- **Logs are SYMLINKS.** An in-project `--output` is written under `.sandbox-state/slurm-logs/__abs__/<abs path>` and the requested path is a symlink to it, created at a time not established (seen mid-run and at job end). `[ -f f ] && [ ! -L f ]` refuses it while `sha256sum` reads through; `stat` shows the link's 777 and `chmod` fails EROFS. Never pin or hash a log path as a later job's input: freeze it (`cp -L f kept/f && chmod 0444 kept/f`, assert `[ ! -L kept/f ]`). An in-job count of the job's own log must FAIL on a missing or unreadable file, never print `count=0`.
- `/sys` is hidden, so `lscpu` fails; read `/proc/cpuinfo`.

## Queries

- `squeue %o` and `sacct SubmitLine` show only the wrapper (`/tmp/chaperon-wrapper-XXXX.sh`), so a grep there for your script name answers 0 at rc 0. Identify jobs by `-J` name, WorkDir (`%Z`) and `scontrol show job` StdOut; give every job a `-J`.
- `sacct -s <STATE>` can return a silent zero (`-s CA` omitted the very CANCELLED job under investigation). Query without `-s` and filter: `awk -F'|' '$2 ~ /CANCEL/'`. The job that prompted the question must appear in the result.
- `sstat` on an array task: `-j 1234567_3.batch` and `-j <raw id>.batch` both fail; `sstat -j 1234567_3 -a -o JobID,MaxRSS -n -P` works.
- Jobs cancelled by uid 0 after ~2:01 (observed 2026-11, cause unknown): `.batch` CANCELLED, `.extern` COMPLETED, no log written. Inspect with `sacct -j <id>` WITHOUT `-X` (step rows carry the evidence). A wait loop keyed on each task's log never ends for a task killed before it logs; wait on `sacct` State too. If it recurs, collect job id, node, partition, times and step states for SciComp.

## PID namespace and cancel

- The job shell runs under bwrap in its own PID namespace (`$$` = 2, pid 1 = bwrap). Its session and group leaders are outside, so `getsid`/`getpgid` read 0, `ps --sid 0` lists nothing, and "child sid == my sid" passes vacuously (0 == 0). A child started with `setsid` IS its own leader inside (`kill -- -<pid>` works). The agent session is also a bwrap namespace, so "we are in a child namespace" distinguishes nothing.
- Leftover-process checks: test `/proc/<pid>` + state letter after reaping, refuse sid 0 as uninformative, and include a live SIGTERM-ignoring plant that MUST be reported. A watchdog kills its own descendant tree found by PPid chains in `/proc/*/status`, never by cmdline.
- **No `scancel` form has been shown to run an in-job EXIT/TERM trap here; release locks and reservations from outside the job once it is terminal.** Plain `scancel` and `--signal=TERM --full` both ended jobs without the trap's line in measured cases, and `scancel --signal=TERM` without `--full` signals only the batch step's init, which swallows it: the job runs on and ends `COMPLETED 0:0`.
- `scancel` through the chaperon can return rc 127 ("failed to read chaperon response") while the signal WAS delivered; read sacct State/ExitCode, not the wrapper rc.
