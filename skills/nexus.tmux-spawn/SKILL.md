---
description: "Spawn delegated nexus work in tmux windows via prompt-file + launcher; never use the in-process Agent tool for nexus delegations."
---

# nexus.tmux-spawn — delegating work into tmux windows

TRIGGER when: agent considers delegating non-trivial work to another
agent for a nexus project; agent reaches for the in-process `Agent`
tool to drive a `work/<project>` task; agent needs to send a follow-up
message to a running tmux agent; agent is briefing a fresh worker on a
project that already has prior reports.

## The one rule

For any nexus delegation, **spawn a tmux window** using the
prompt-file + launcher pattern below. Do **not** use the in-process
`Agent` tool (sub-agent) for nexus delegations.

Use the `Agent` tool only for tight, bounded research or file searches
that stay inside your own thinking loop (codebase questions, "find all
the places that …"). Never for delegations the nexus needs to track.

## Why

In-process `Agent` sub-agents are:

- **Blocking** — they consume the orchestrator's turn until they
  return.
- **Distracting** — they pull the nexus away from its main
  monitor-agent responsibilities.
- **Context-hungry** — their final result funnels back into the
  orchestrator's context even when launched async, eating tokens for
  output the orchestrator doesn't need to see in detail.

Tmux agents, in contrast:

- Run **truly parallel** on their own compute.
- Land their output **in the real world** — commits, reports in
  `reports/`, GitHub comments — without ever traversing the
  orchestrator's context.
- Are **visible** (`tmux list-windows`), **inspectable**
  (`tmux capture-pane`), and **redirectable** (paste-buffer
  follow-ups).

The orchestrator learns about their progress through the watcher loop
(reports under `reports/`, the dashboard, `tmux list-windows` snapshots),
not through the Agent tool's transcript.

When Agent Teams pane splitting fails (common in nested tmux / sandbox
environments), the prompt-file + launcher pattern is the reliable way
to spawn. **Never pass prompts inline via shell expansion** — it
breaks in nested tmux.

## The pattern

```bash
# 1. Write prompt to a temp file
cat > /tmp/prompt-TASKNAME.txt <<'EOF'
Your full agent prompt here. Multi-line, free-form, can include
backticks and $variables — the heredoc keeps everything literal.
EOF

# 2. Create a launcher that reads the prompt safely
cat > /tmp/launch-TASKNAME.sh <<'LAUNCHER'
#!/bin/bash
prompt=$(</tmp/prompt-TASKNAME.txt)
rm -f /tmp/prompt-TASKNAME.txt /tmp/launch-TASKNAME.sh
claude --dangerously-skip-permissions "$prompt"  # positional arg, NOT -p (print mode is non-interactive)
LAUNCHER
chmod +x /tmp/launch-TASKNAME.sh

# 3. Create window and send the launcher
tmux new-window -d -n 'TASKNAME' -c '/path/to/workdir'
tmux send-keys -t 'TASKNAME' '/tmp/launch-TASKNAME.sh' Enter
```

### Why this shape

- **Prompt file, not shell expansion.** Inline `"$(cat ...)"` or
  single-quoted multi-line prompts break with special characters,
  nested quotes, and zsh escaping in tmux. The `<<'EOF'` heredoc
  preserves the prompt verbatim.
- **Separate `new-window` and `send-keys`.** Combining them as
  `tmux new-window -n name "command"` can fail silently in nested
  tmux sessions.
- **`-d` flag.** Creates the window without switching the attached
  client's focus; the orchestrator keeps its current view.
- **`-c '/path/to/workdir'`.** Sets the working directory for the
  spawned agent. Use the absolute path to the project repo (e.g.
  `/fh/fast/setty_m/user/dotto/nexus/work/<project>`).
- **Self-cleaning.** The launcher removes its own temp files after
  reading them, so /tmp doesn't accumulate prompt scraps.
- **`claude --dangerously-skip-permissions "$prompt"`.** Positional
  arg starts an **interactive** session with the prompt as the first
  user turn. Do not use `-p`/`--print` — that's non-interactive print
  mode and exits after one turn.

## Sending follow-up messages

`claude "prompt"` starts an interactive session, so follow-ups go
through tmux. The message is queued and delivered when the agent's
current turn finishes.

```bash
# Write the follow-up to a temp file (avoids quoting issues)
cat > /tmp/followup-TASKNAME.txt <<'EOF'
Your follow-up instructions here.
EOF

# Use tmux paste-buffer (reliable for any length), then Enter to submit
tmux set-buffer -b msg "$(cat /tmp/followup-TASKNAME.txt)"
tmux paste-buffer -b msg -t 'TASKNAME'
sleep 0.1
tmux send-keys -t 'TASKNAME' Enter
rm -f /tmp/followup-TASKNAME.txt
```

**Why `set-buffer` + `paste-buffer`.** `tmux send-keys` with long
strings can drop characters or mishandle timing. The paste-buffer
approach loads the full text atomically into a named buffer (`-b msg`),
pastes it as a single chunk, then submits with `Enter`. The
`sleep 0.1` lets the terminal process the paste before the submit key
arrives.

## VI-mode hazard (read this if you've ever lost a follow-up)

Claude Code uses VI keybindings. If the agent is in **normal mode**
(no `-- INSERT --` in the status bar), keystrokes are interpreted as
VI commands and your message is silently lost (or worse, executes
random VI motions on the prompt line).

If you're not sure of the mode, send `i` first to ensure insert mode
before the paste:

```bash
tmux send-keys -t 'TASKNAME' i
sleep 0.1
tmux set-buffer -b msg "$(cat /tmp/followup-TASKNAME.txt)"
tmux paste-buffer -b msg -t 'TASKNAME'
sleep 0.1
tmux send-keys -t 'TASKNAME' Enter
```

The lone `i` is a no-op if already in insert mode and a mode switch
otherwise — safe either way.

## Naming convention

Short, descriptive, kebab-case window names tied to the task or
project: `repro-skills`, `data-mgmt`, `slurm-update`, `kompot-fig3`,
`barnacle-list`. The watcher's `tmux list-windows` snapshot surfaces
the name on the dashboard, so use something a human can identify at a
glance.

Before spawning, check `tmux list-windows` for collisions. The
dashboard's running-agents table also lists current windows.

## Briefing agents with prior-report context

Spawned agents working on a `work/<project>` task should discover
their own context by scanning `reports/`. Include this in every
delegation prompt:

```
Before starting, scan for prior work:
  ls reports/{project}_* 2>/dev/null
Read the title and status lines (head -7) of any matches to decide
which are relevant. Read full reports only if they directly inform
your task.
```

This lets the agent triage itself instead of bloating the
orchestrator's prompt with pre-digested summaries that may be wrong
or stale. Replace `{project}` with the actual subdirectory name
(e.g. `kompot`, `fh-hpc-skills`, `labsh`, or `nexus` for
workspace-level work).

## See Also

- `nexus.bot` — the spawned agent's GitHub identity. Every delegation
  posting to GitHub must use the bot, not user `gh`.
- `nexus.report` — what the spawned agent should write before
  finishing or going idle. Reports are the primary channel by which
  the orchestrator learns the outcome.
- nexus root `CLAUDE.md` — workspace-level architecture, watcher
  protocol, and the "Spawning Agents in Tmux Windows" canonical
  reference.
