---
description: "nexus bot identity for all GitHub writes: monitor/ng for nexus repo, GH_TOKEN=$(mint-token.sh) gh for cross-repo. Never plain gh."
---

# nexus.bot — GitHub identity for spawned agents

TRIGGER when: agent considers any GitHub write (open/edit/merge a PR, create/comment/close an issue, add a reaction, edit the dashboard, upload to the wiki); agent reaches for `gh pr create`, `gh issue create`, `gh issue comment`, or `gh pr review`; agent embeds a local file (image, PDF, report) in a comment or PR/issue body.

## The one rule

Every GitHub write originating from a nexus agent MUST run as the
**bot**, not the user. Two channels:

1. **`monitor/ng <verb>`** — preferred for the nexus repo. Mints the
   bot token internally, picks up the configured repo from
   `config/nexus.yml`, hides the verbose `gh api` JSON.
2. **`GH_TOKEN=$(./monitor/mint-token.sh) gh <verb>`** — for cross-repo
   writes, or one-offs `ng` doesn't cover yet. Setting `GH_TOKEN` makes
   `gh` use the bot token instead of the user's cached auth.

The only GitHub interactions that may still use the user's identity
are `git commit` and `git push` (commit authorship stays the user's
on the commit graph).

## Why

GitHub mutes mobile push notifications for actions taken by the
recipient's own account. Any PR opened, issue created, or comment
posted as `@<user>` silently fails to notify `@<user>` — defeating the
whole point of the GitHub-issues control surface. The bot has its own
account (`<bot>[bot]`), so its writes always wake the user.

The bot also gives the watcher's eligibility filter a clean signal:
only comments authored by `github.user_login` are surfaced to the
monitor agent, so bot-authored content can never be mistaken for a
directive.

## `ng` verb table

Run from the nexus root (`monitor/ng <verb> ...` or
`./monitor/ng ...`). All verbs auto-mint the bot token.

| Subcommand | Purpose | Stdout on success |
|------------|---------|-------------------|
| `ng pr create --head <branch> [--base main] --title "…" --body-file b.md` | Open a PR | PR URL |
| `ng pr edit <n> [--title "…"] [--body-file b.md]` | Edit a PR | PR URL |
| `ng pr merge <n> [--squash\|--merge\|--rebase] [--delete-branch]` | Merge a PR | merge SHA |
| `ng pr view <n>` | Brief PR summary | `#<n> state=… author=… title=…` |
| `ng issue create --title "…" --body-file b.md [--label foo]…` | Create an issue | issue URL |
| `ng issue comment <n> --body-file b.md` | Comment on an issue | comment URL |
| `ng issue close <n> [--comment "…"]` | Optional comment, then close | `CLOSED` |
| `ng issue <n>` | One-line issue summary | `#<n> state=<STATE> title=<title>` |
| `ng reply <n>` | Same as `issue comment`, body from stdin | comment URL |
| `ng react <comment-id> <eyes\|rocket>` | Single reaction POST | (silent — see "react silence" below) |
| `ng process <comment-id>` | Eligibility check + eyes + fetch body | `issue=<n>` / `author=<login>` / `body<<EOF` … |
| `ng dashboard get` | Fetch overview-issue dashboard middle | dashboard markdown |
| `ng dashboard put [--body-file <path>]` | Splice + PATCH dashboard | issue URL |
| `ng upload <local-path> [--repo-path <path>] [--message <msg>]` | Commit a file to the nexus wiki under `status-assets/...` and print a URL that renders in any logged-in browser | wiki asset URL |
| `ng watcher-status` | One-shot watcher liveness summary | key=value block |
| `ng log-action <agent> --event <name> [--note <t>] [--extra k=v]…` | Append one JSONL action-trace line | (silent) |

### `react` silence

`ng react` exits 0 on success but prints nothing on the happy path —
trust the exit code. There's a documented friction request to add a
`reacted <content> on comment <id>` confirmation; until then, scripts
must check `$?` rather than parsing stdout.

### Verbs landing soon (`dominik/ng-omnibus`, not yet merged)

- `ng preflight <repo>` — hits `/installation/repositories` and prints
  whether the bot is installed on the target repo. Lets cross-repo
  writes fail fast instead of returning a confusing GraphQL 403.
- `ng show <comment-id>` — read-only fetch that bypasses the eligibility
  filter, so an agent can quote a prior bot-authored comment.
- `--repo OWNER/NAME` flag on `ng pr ...` and `ng issue ...` —
  retargets the verb at a sibling settylab repo without falling back
  to raw `gh api`.

Until these merge, cross-repo writes use the `GH_TOKEN=…` escape
hatch below.

## Embedding local files (the wiki-upload rule)

GitHub readers cannot see anything outside `main`. Bare paths to local
files — `reports/<file>.md`, scratch images, PDFs — render as broken
links on github.com. Upload to the wiki first.

```bash
url=$(./monitor/ng upload reports/<your-report>.md)
# in the comment body:  [full report]($url)

url=$(./monitor/ng upload path/to/figure.png)
# in the comment body:  ![figure]($url)
```

`ng upload` commits the file to the nexus wiki under `status-assets/...`
and prints a `github.com/{owner}/{repo}/wiki/...` URL.

Two defaults worth knowing:

- **`reports/` auto-clusters.** Sources whose path contains a
  `reports/` segment land at `status-assets/reports/<basename>` rather
  than mixing with image assets at the wiki root.
- **`.md` extension drops from the URL.** Markdown uploads render via
  the wiki page router (`<slug>` → `<slug>.md` on disk), so the
  printed URL has no `.md`. Other extensions (`.png`, `.pdf`, `.csv`)
  keep theirs and are served as raw assets.

Override the default destination with `--repo-path foo/bar.png` for
fine control.

What **not** to use: `raw.githubusercontent.com/...` (wrong-domain
cookies on private repos), `data:` URIs in `<img>` (sanitiser strips
them), signed Contents-API `?token=` URLs (5-min TTL), release
assets (anonymous 404), and bare repo paths to gitignored content
(404 on github.com).

## Cross-repo writes (the `GH_TOKEN` escape hatch)

For repos `ng` doesn't yet target with `--repo`, mint the token
inline:

```bash
GH_TOKEN=$(./monitor/mint-token.sh) gh pr create \
  --repo settylab/<repo> \
  --head <branch> --base main \
  --title "…" \
  --body-file body.md
```

Same for `gh issue create`, `gh issue comment`, `gh api ...`.

### Bot install scope caveat

The bot is a GitHub App; it can only act on repos it's installed on.
At time of writing it covers a subset of `settylab/*` (the nexus repo
plus a handful of project repos that have been individually opted
in). Cross-repo writes to **uninstalled** repos return:

- HTTP 403 `Resource not accessible by integration`, or
- a misleading GraphQL error `Could not resolve to a Repository`.

If you hit either on a settylab repo, the bot is not yet installed
there. Surface it as a blocker:

1. Push your branch under the user's identity (`git push`) so the
   work isn't lost.
2. Record it in your final report's `## Infrastructure Issues`
   section with the repo name and command that failed.
3. The user / org admin expands the App's repo scope (one click in
   the App settings page); a follow-up agent can then open the PR.

## The fail-loud rule (security boundary)

`mint-token.sh` returning empty MUST exit non-zero — never let
`GH_TOKEN=""` fall through to the user's cached `gh` auth. An empty
`GH_TOKEN` is treated by `gh` as "no override", so the API call
silently runs as the user. If the user happens to have the right
scope, the action succeeds — posted as `@<user>`, not `@<bot>` —
and the user-side notification is muted. The bot/user identity
boundary is silently breached.

Two defenses in scripts that mint tokens:

```bash
GH_TOKEN=$(./monitor/mint-token.sh) || { echo "mint-token failed" >&2; exit 1; }
[ -n "$GH_TOKEN" ] || { echo "empty GH_TOKEN — refusing to run" >&2; exit 1; }
gh <whatever>
```

Don't pipe `mint-token.sh` straight into `GH_TOKEN=$(...)` without
checking — the script is also CWD-sensitive, and a silent empty
return from a non-nexus-root cwd is the most-cited security-relevant
foot-gun in the workspace report corpus.

## See Also

- `nexus.tmux-spawn` — how to delegate work into a tmux window so the
  spawned agent inherits this skill cleanly.
- `nexus.report` — the report convention; the `## Infrastructure
  Issues` section is the right place to flag bot-install gaps,
  missing `ng` verbs, and any other tooling friction.
- `monitor/README.md` (in the nexus root) — full architecture, GitHub
  interaction model, the eligibility filter, env-var override table.
- `monitor/agent-prompt.md` — the launch prompt for the monitor
  agent itself; references the same `ng` verbs.
