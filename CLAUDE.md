# fh-hpc-skills — Fred Hutch HPC Claude Code Plugin

A Claude Code skill bundle providing comprehensive guidance for the Fred Hutch HPC (Gizmo cluster).

## Principles

Every skill in this plugin must uphold:

1. **Scientific accuracy** — Commands, paths, and configurations must be verified against the live cluster and official SciComp documentation.
2. **Reproducibility** — Encourage versioned environments (modules, containers, conda envs), explicit resource requests, and documented workflows.
3. **Fair resource usage** — Teach users to request only what they need, use appropriate partitions, and respect shared infrastructure.
4. **Cooperation** — Respect other users' jobs, avoid monopolizing nodes, follow SciComp policies.
5. **Security** — Never expose credentials, use proper access methods, follow Fred Hutch data security policies.

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
- Format: `{section}_{page}.lock` containing agent ID and timestamp
- An agent MUST create a lockfile before working on a page
- An agent MUST remove its lockfile when done
- A supervising agent must clean up lockfiles of finished subagents

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
