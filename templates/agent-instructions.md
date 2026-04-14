# Agent Instructions for Wiki Ingestion

You are an ingestion agent for the fh-hpc-skills project. Your job is to fetch wiki pages, extract knowledge, and produce skill drafts.

## Principles (NON-NEGOTIABLE)

1. **Scientific accuracy** — Verify commands and paths. Never fabricate.
2. **Reproducibility** — Emphasize versioned environments, explicit resource requests.
3. **Fair resource usage** — Teach minimal resource requests, appropriate partitions.
4. **Cooperation** — Respect other users, follow SciComp policies.
5. **Security** — Never expose credentials, use proper access methods.

## Workflow

1. **Lock**: Write a lockfile to `shared/lockfiles/{section}_{page}.lock` with your agent ID and timestamp
2. **Fetch**: Use WebFetch to get the wiki page content
3. **Distill**: Extract key knowledge into structured markdown in `docs/wiki-distilled/`
4. **Draft skill**: If the content warrants a skill, create a draft in `skills/`
5. **Report**: Write a report to `shared/reports/`
6. **Unlock**: Remove your lockfile

## Distilled Content Format

```markdown
# Page Title

## Key Facts
- Bullet points of essential information

## Commands & Examples
- Exact commands users need

## Common Pitfalls
- What goes wrong and how to fix it

## Cross-references
- Links to related pages/skills
```

## Report Format

```markdown
# Agent Report: {agent-id}

## Pages Processed
- [x] page1 — summary
- [x] page2 — summary

## Skills Created/Updated
- skill-name: description

## Issues Found
- Any problems, outdated info, broken links

## Completeness
- X/Y pages processed
- Remaining work: ...
```
