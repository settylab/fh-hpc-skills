---
description: "Getting an interactive shell on the Setty lab shared node (gizmok1) via barnacle"
---

# fh.settylab-interactive

TRIGGER when: a Setty lab member wants interactive compute, asks about `barnacle`, `gizmok1`, "how do I get a shell in the lab", or is looking for the lab's preferred interactive workflow. Non-settylab Fred Hutch users: see `fh.interactive-sessions` instead.

## Context

The Setty lab pools its interactive work onto a single shared Gizmo compute node (`gizmok1`) managed by [`barnacle`](https://github.com/settylab/barnacle). Rather than each member burning a full `grabnode` allocation, members take over one or more "slots" on `gizmok1` and share the node's CPUs, memory, and GPUs as needed. dotto runs a `barnacle watch` process on the node that welcomes new joiners and repairs broken slot chains in the background.

The `barnacle` executable is available to the whole lab at a shared path:

```
/fh/fast/setty_m/user/dotto/shared_node/barnacle
```

## Canonical Join Flow

```bash
ssh rhino                                                                     # 1
/fh/fast/setty_m/user/dotto/shared_node/barnacle -n gizmok1 status            # 2
/fh/fast/setty_m/user/dotto/shared_node/barnacle -n gizmok1 join              # 3
logout                                                                        # 4
ssh gizmok1.fhcrc.org                                                         # 5
```

1. Log in to a rhino node (the only place Slurm commands work off-cluster).
2. Confirm `gizmok1` has free slots and the watcher is alive before you touch anything.
3. Submit your slot jobs. `join` claims free placeholder slots under your own Slurm account; the watcher hands them over automatically once your jobs start running.
4. Exit rhino — the slot jobs keep running on the cluster.
5. SSH directly to `gizmok1`. As long as one of your slot jobs is running on the node, the process reaper will not kick your session. Start `tmux` and work normally.

## Pre-Join Status Check

`barnacle -n gizmok1 status` is the canonical pre-flight. Read it before every join:

- **System overview panel**: node name, Slurm state, 1/5/15-min load, memory usage. State should be `IDLE` or `MIXED`, never `DRAIN`/`DOWN`.
- **Slot table**: one row per slot, showing owner, extension number, time remaining, and whether it is running or queued. Slots owned by `free` are the placeholder slots that `join` will claim.
- **Free slots**: the count of `free` placeholder slots currently running. This is your budget — if it is `0`, do not `join` (see "When NOT to use barnacle" below).
- **Watcher**: a running `barnacle watch` process shows up in the "other jobs" list on the node (owner `dotto`, command `barnacle watch`). If it is missing, ping dotto before joining — without the watcher, handover of running placeholder slots does not happen automatically.

Other useful subcommands once you are set up:

- `barnacle -n gizmok1 users` — who currently holds slots.
- `barnacle -n gizmok1 free` — just the free-slot count.
- `barnacle -n gizmok1 health` — load + memory summary.
- `barnacle -n gizmok1 chain <slot>` — inspect a slot's dependency chain.

TODO: a multi-node "which gizmok hosts are barnacled right now?" listing is planned upstream but not yet in `main` on <https://github.com/settylab/barnacle>. Until it lands, `gizmok1` is the only shared node to check.

## Leaving Cleanly

When you're done with the shared node for an extended period (vacation, switching projects, graduation), release your slots so others can claim them:

```bash
ssh rhino
/fh/fast/setty_m/user/dotto/shared_node/barnacle -n gizmok1 leave
```

`leave` cancels your running slot jobs and the entire follow-up chain in a single `scancel`. Stale allocations block the rest of the lab from joining, so do not leave silent slots behind. If you only need a short break, just SSH out — the slot chain keeps your seat warm for you.

## When NOT to Use Barnacle

Skip `barnacle` and use the standard Fred Hutch interactive path in `fh.interactive-sessions` when:

- **`status` shows 0 free slots.** The node is saturated. Taking someone else's slot is rude; `grabnode` gives you a dedicated session on a different gizmo.
- **You need guaranteed resources.** `barnacle` is a shared tenancy — other members can consume CPU/memory at any time. For a job that must have N cores to itself (benchmarks, timing-sensitive work), use `grabnode` or a dedicated `sbatch` allocation.
- **You need a GPU that `gizmok1` doesn't have.** `gizmok1` is a k-generation CPU node. GPU work belongs on `chorus` — see `fh.gpu` and `fh.partitions`.
- **You only need a one-off short session.** `grabnode` with a 1-day time limit is lower friction than claiming and then releasing a slot.

## Agent Checklist

Before spawning interactive work on behalf of a Setty lab user:

1. Run `barnacle -n gizmok1 status` and confirm ≥1 free slot.
2. Verify the watcher is running (an `other` job owned by `dotto` named `barnacle watch`).
3. Join with `barnacle -n gizmok1 join` (default 1 slot is plenty for most work).
4. SSH to `gizmok1.fhcrc.org` in `tmux` and start your session.
5. On finishing a long-lived session, run `barnacle -n gizmok1 leave`.
6. Follow the shared-node etiquette in `fh.shared-nodes` (memory caps, CPU caps, no fork-bombs) while you are on the node.

## See Also

- `fh.shared-nodes` — etiquette for behaving on any multi-tenant node, including `gizmok1`.
- `fh.interactive-sessions` — the standard Fred Hutch interactive path (`grabnode`, direct `srun`). Use this when `barnacle` is not the right fit.
- `fh.slurm` — submitting batch jobs once you have a shell on `gizmok1`.
- `fh.onboarding` — new-user orientation; this skill is the lab-specific step after the generic ones.

## References

- Barnacle source + docs: <https://github.com/settylab/barnacle>
- Shared executable: `/fh/fast/setty_m/user/dotto/shared_node/barnacle`
- Questions: dotto@fredhutch.org
