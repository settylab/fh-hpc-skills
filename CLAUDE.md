# fh-hpc-skills — Fred Hutch HPC Claude Code Plugin

A Claude Code skill bundle providing comprehensive guidance for the Fred Hutch HPC (Gizmo cluster).

## Principles

Every skill in this plugin must uphold:

1. **Scientific accuracy** — Commands, paths, and configurations must be verified against the live cluster and official SciComp documentation.
2. **Reproducibility** — Encourage versioned environments (modules, containers, conda envs), explicit resource requests, and documented workflows.
3. **Fair resource usage** — Teach users to request only what they need, use appropriate partitions, and respect shared infrastructure.
4. **Cooperation** — Respect other users' jobs, avoid monopolizing nodes, follow SciComp policies.
5. **Security** — Never expose credentials, use proper access methods, follow Fred Hutch data security policies.
6. **Critical review** — Act as an additional pair of eyes. Verify correctness of paths, resource requests, array ranges, and logic before submission. Catch mistakes that waste cluster time or produce misleading results.

## Project Structure

```
skills/              # Claude Code skills (the deliverable)
docs/wiki-raw/       # Raw fetched wiki content (markdown)
docs/wiki-distilled/ # Distilled, structured knowledge
shared/lockfiles/    # Agent coordination lockfiles
shared/reports/      # Agent work reports
templates/           # Skill templates
sources.yml          # Wiki URL manifest
```

## Agent Coordination Protocol

### Lockfiles (`shared/lockfiles/`)

Format: `{section}_{page}.lock`, YAML content:

```yaml
agent_name: ingest-compute       # Name used in Agent(name=...) for SendMessage
parent_name: orchestrator        # Parent agent name, for sibling escalation via SendMessage
session_id: 4c46ec97-630e-...    # Claude Code session UUID (for log inspection)
started_at: 2026-04-14T08:03:18Z # ISO 8601
work_description: "Ingesting compute_jobs and compute_parallel wiki pages"
```

**Rules:**
- An agent MUST create a lockfile before working on a page and remove it when done.
- Never remove a lockfile from a running agent.

**Checking if a lock holder is still alive:**
Claude Code writes to `~/.claude/projects/{project-slug}/{session_id}.jsonl` on every tool call. Check this file's mtime to determine if the locking agent is still active. If the log has not been modified for an unreasonable duration (given the work described in the lockfile), the agent is likely dead and the lock is stale.

**Communication between agents:**
- **Subagents with a shared parent**: Use `SendMessage(to: parent_name, ...)` to escalate. The parent can check on the lock holder or relay messages between siblings.
- **Separate Claude Code sessions**: Use Agent Teams messaging (enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) for direct cross-session communication, including lock status queries.

### Reports (`shared/reports/`)
- Format: `{agent-id}_{section}.md`
- Must include: pages processed, skills created, issues found, completeness assessment
- Supervising agent reviews reports and re-dispatches incomplete work

## Skill Format

Each skill lives in `skills/{name}/` with:
- `SKILL.md` — The skill prompt with frontmatter (description for lookup)
- Supporting files as needed

## Building & Testing

```bash
# Validate all skills have proper frontmatter
for f in skills/*/SKILL.md; do head -5 "$f"; echo "---"; done

# Check for broken references
grep -r '/scicomputing/' skills/ | grep -v 'sciwiki.fredhutch.org'
```
