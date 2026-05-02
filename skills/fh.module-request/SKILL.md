---
description: "Requesting new software modules at Fred Hutch HPC: 4-path decision tree (PR upstream urgent / PR upstream non-urgent / FH-specific recipe / version bump build) and Rust 1.86 worked example. Triggered when an agent has determined a needed module is missing and wants to request a build or version bump."
---

# Requesting a New Module from FH HPC

TRIGGER when: `module spider <Name>` returns nothing for a needed package, the user explicitly asks how to get new software added to the cluster, an existing module needs a version bump, or an agent needs to file a build request to SciComp / `FredHutch/easybuild-life-sciences`.

If you only need to *use* an already-available module, see `fh.modules` instead.

## Context

The FH module inventory is what `module spider` shows on the cluster — not the file tree of any GitHub repo. SciComp builds and maintains modules using the [EasyBuild](https://easybuild.io/) framework, with FH-local easyconfigs collected at [FredHutch/easybuild-life-sciences](https://github.com/FredHutch/easybuild-life-sciences). The maintainer (`@fizwit`) treats incoming PRs *as build requests*: the build is what matters; the repo is just one input. An upstream-stock easyconfig PR will typically be closed without merge once the build lands on the cluster — that's expected, not a rejection. Verify with `module spider <Name>/<version>` after a few days.

For escalations or non-PR-shaped questions: email `scicomp@fredhutch.org`.

## Instructions

### Decision tree — which path fits your request

Pick the path that matches the easyconfig you need *and* your time pressure.

| Path | Easyconfig source | Urgency | Where to file |
|------|-------------------|---------|---------------|
| **A** | Generally useful, no FH-local changes | Need it now | PR on `easybuilders/easybuild-easyconfigs` (upstream EB), then issue on `FredHutch/easybuild-life-sciences` asking for `eb --from-pr <upstream-PR-#>` build |
| **B** | Generally useful, no FH-local changes | Not urgent | PR on upstream `easybuilders/easybuild-easyconfigs` only; FH picks it up after upstream merge |
| **C** | FH-specific (custom config, pinned dep, modified version) | — | PR on `FredHutch/easybuild-life-sciences` with the unique/modified easyconfig — *this kind gets merged* |
| **D** | Already merged upstream, just needs building locally on FH | — | Issue on `FredHutch/easybuild-life-sciences` ("please build `<Name>/<version>`"). PR works too but will be closed-not-merged after the build lands |

**Path A — generally useful + you need it now.** Two-step: open the PR upstream so the recipe lives in the canonical `easybuilders/easybuild-easyconfigs` collection, then ask FH HPC to build it via the EasyBuild `--from-pr` flag without waiting for upstream review. The flag tells the EB framework to fetch the recipe from the open PR and build against it locally.

```bash
# example body to send to scicomp / on a FH-side issue:
# please build via:  eb --from-pr <upstream-PR-#>
```

This is the right path when the recipe is generic but the upstream review queue is slow (often weeks). FH builds immediately; later, when the upstream PR merges, FH picks it up natively from the released collection. You skip the upstream-merge wait without forking the recipe FH-side.

**Path B — generally useful + not urgent.** Open the PR upstream on `easybuilders/easybuild-easyconfigs` and let FH pick it up after upstream merge. Slow but zero coordination on the FH side and the recipe ends up in the canonical place.

**Path C — recipe is FH-specific.** Modified version, custom toolchain pin, lab-specific dependency injection, an entirely new recipe that doesn't make sense upstream. Open the PR on `FredHutch/easybuild-life-sciences` with the unique easyconfig. fizwit *merges* this kind per the policy of accepting "unique easyconfigs, or ones that have been modified" (PR [FredHutch/easybuild-life-sciences#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577)). This is the only path that produces a long-lived FH-repo artifact.

**Path D — already merged upstream, just needs building on FH.** File an *issue* on `FredHutch/easybuild-life-sciences` with a one-line ask: "please build `<Name>/<version>` for gizmo / harmony / chorus". A PR with the stock upstream easyconfig also works — it's how PR [#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577) landed `Rust/1.86.0-GCCcore-13.3.0` on 2026-05-01 — but expect the PR to be **closed without merge** after the build lands. fizwit's own words on the same PR: *"I am trying to limit the number of EB in our github. Just accepting unique easyconfigs, or ones that have been modified. Treating this PR as a request. The software inventory is the ultimate list of what is installed, using `module spider` to create the list. I do not reference the repo as an inventory."* The build is the deliverable; the PR is just the trigger. Don't be alarmed by the close.

### Worked example — the Rust/1.86.0 request (Path D)

PR [FredHutch/easybuild-life-sciences#577](https://github.com/FredHutch/easybuild-life-sciences/pull/577) ("Add Rust 1.86.0-GCCcore-13.3.0 easyconfig"):

- **Opened:** 2026-04-30 with the stock upstream easyconfig.
- **Outcome:** Closed 2026-05-01, *not merged*. fizwit commented *"Rust-1.86.0-GCCcore-13.3.0.eb install for gizmo, harmony, and chorus"* and closed the PR.
- **Verification:** `module spider Rust/1.86.0-GCCcore-13.3.0` immediately showed the module as loadable.

The lesson: the PR is the request channel; the cluster is the deliverable surface; `module spider` is the source of truth.

### Building a request PR or issue

For both Path C (PR) and Path D (issue or PR):

- **Title:** `Add <Name>/<version> easyconfig` (PR) or `Please build <Name>/<version>` (issue).
- **Body:** state the requesting use case + lab, the dependency chain you need, the target compute environments (gizmo / harmony / chorus). Cite the upstream EasyBuild PR if you're requesting a Path-A `--from-pr` build, or the upstream merged commit for Path D.
- **PR file:** stock easyconfig copied from `easybuilders/easybuild-easyconfigs` (Path D), or the modified one (Path C).

## Principles

- Verify with `module spider <Name>/<version>` rather than checking the GitHub repo — the cluster is the source of truth.
- Don't be surprised by closed-not-merged PRs on Path D; the build *is* the deliverable.
- Pick the lightest path that fits: Path B (just PR upstream) is cheapest; Path A only when you genuinely cannot wait.
- Cite the use case, lab, and target environments in the request body — fizwit triages by signal, not volume.

## References

- FH easyconfig collection (request channel): https://github.com/FredHutch/easybuild-life-sciences
- Upstream EasyBuild easyconfigs: https://github.com/easybuilders/easybuild-easyconfigs
- EasyBuild docs (`--from-pr`): https://docs.easybuild.io/version-specific/easyconfigs/
- EasyBuild inventory (FH): https://fredhutch.github.io/easybuild-life-sciences/
- Worked example PR: https://github.com/FredHutch/easybuild-life-sciences/pull/577
