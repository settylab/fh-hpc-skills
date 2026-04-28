---
description: "Write reports/{project}_{ts}_{slug}.md before finishing, going idle, or on context pressure. Required sections + the Infrastructure Issues feedback loop."
---

# nexus.report — agent report convention

TRIGGER when: agent is completing a delegated task; agent is going
idle with partial work and waiting for input; agent's context window
is filling up and state should be captured before it's lost; agent is
spawning a follow-up worker that needs a brief; agent is about to hand
off work to a sibling agent.

## The one rule

Every nexus agent MUST write a report file before finishing, going
idle, or when context is running low. Reports let work resume from
the file alone if the session crashes, the orchestrator restarts, or
a sibling needs to pick up where you left off.

Reports are **append-only during a session**. Write a new file for
each significant state change rather than overwriting the previous
one.

## Filename convention

```
reports/{project}_{YYYY-MM-DD}_{HHMMSS}_{slug}.md
```

- **`{project}`** — name of the `work/` subdirectory being worked on
  (e.g. `kompot`, `fh-hpc-skills`, `labsh`). Use `nexus` for
  workspace-level tasks that span projects.
- **`{YYYY-MM-DD}`** — ISO date.
- **`{HHMMSS}`** — 24h time. UTC or local — be consistent across the
  session.
- **`{slug}`** — short kebab-case description, e.g. `fig2-revision`,
  `scout-setup`, `benchmark-run`, `nexus-skills`.

Example: `reports/kompot_2026-04-14_153200_fig2-revision.md`.

The watcher snapshots `reports/*.md` filenames + mtimes on every poll
cycle, so a new report is automatically picked up by the monitor and
surfaced to the orchestrator.

## Required sections

```markdown
# {Title}

**Agent:** {agent name or session id}
**Project:** {work/ subdir, or `nexus` for workspace-level}
**Started:** {ISO timestamp}
**Status:** {completed | blocked | idle | crashed}

## What Was Done
- Concise list of actions taken and files changed.

## Current State
- What is the state of the work right now?
- What files were created or modified?
- Any running jobs (Slurm job IDs, PIDs)?

## What Remains
- Specific next steps, in order.
- Known blockers or decisions needed.

## How to Resume
- Exact commands or instructions to pick up where this left off.
- Branch name if applicable.
- Any context that would be lost without this report.

## Infrastructure Issues
- Anything that made the work harder than it needed to be, even if
  you worked around it. Be specific: what you tried, what happened,
  what you expected.
- Omit the section entirely if nothing came up. No placeholders.
```

The four content sections (`What Was Done`, `Current State`,
`What Remains`, `How to Resume`) are mandatory. `Infrastructure
Issues` is conditional — present and substantive when something hurt,
omitted when nothing did.

## Why `Infrastructure Issues` matters (read this even if nothing came up)

This section is the **source material for periodic tooling
meta-reviews**. The 2026-04-28 review
(`reports/nexus_2026-04-28_202950_infrastructure-meta-review.md`)
triaged 173 reports — 93 of them carrying `## Infrastructure Issues`
content — and clustered the cross-cutting themes into a 15-item
ranked backlog of fixes the workspace shipped or queued. Themes
surfaced (each cited 6+ times) included:

- `monitor/ng react` exits silently on success — 11 reports.
- The bot's GitHub App was installed on a subset of `settylab/*`,
  blocking cross-repo writes — 16 reports.
- `ng pr create` and `ng issue create` were repo-locked to the nexus
  with no `--repo` flag — 8 reports.
- `mint-token.sh` returned empty silently from a non-nexus-root cwd —
  1 report, but the highest-severity finding (security boundary
  bypassed by falling through to user `gh` auth).

None of those would have been spotted without agents writing them
down. If your run hit any of:

- A command that was hard to discover or had surprising behaviour.
- Confusing or missing documentation.
- Broken / flaky tooling, or sandbox / Slurm / environment
  surprises.
- A GitHub-interface rough edge (auth confusion, missing `ng` verbs,
  misleading errors).
- Agent-to-agent communication friction (paste-buffer weirdness,
  lost follow-ups, unclear routing).

— record it. One paragraph per issue, with concrete reproduction
detail. Don't write placeholders ("nothing to report") — just omit
the section.

## When to write a report

1. **Task completion.** Final report summarises what was done and
   sets `Status: completed`.
2. **Before going idle.** Partial work, waiting on input or a
   decision: write a report capturing the partial state, set
   `Status: idle` or `blocked`. The orchestrator and any successor
   agent can resume from it.
3. **Context pressure.** If your context window is filling up,
   write a report **before** it's lost. A crashed session with no
   report is wasted compute.
4. **Handoff.** When spawning a follow-up worker that needs to pick
   up your in-progress work, write a report the new agent can
   consume — that's the brief.

## Append-only convention

Reports are not edited or overwritten. If state changes
significantly during the session, write a *new* report file with a
fresh timestamp. The trail of progressive reports preserves history;
a single overwritten file loses it.

This means it's normal for a single project to accumulate multiple
reports per session — `reports/kompot_2026-04-14_103000_fig2-start.md`
followed by `reports/kompot_2026-04-14_153200_fig2-done.md` is the
intended shape.

## How to share a report on GitHub

`reports/` is gitignored at the workspace level — readers on
github.com cannot see bare `reports/<file>.md` paths. To reference a
report in a comment, PR body, or issue body, upload it to the wiki
first:

```bash
url=$(./monitor/ng upload reports/<your-report>.md)
# in the comment body:  [full report]($url)
```

`ng upload` clusters `reports/*.md` under
`status-assets/reports/<basename>` and strips the `.md` from the
URL so the wiki page router serves the report rendered. See the
`nexus.bot` skill for the full upload-rule cheatsheet.

## See Also

- `nexus.bot` — the GitHub-write rules; needed when uploading the
  report to the wiki or referencing it from a PR/issue.
- `nexus.tmux-spawn` — when spawning a follow-up worker, briefing it
  with prior-report context (`ls reports/{project}_*`) is part of
  the spawn pattern.
- nexus root `CLAUDE.md` — the canonical "Agent Reports (CRITICAL)"
  section the workspace relies on.
