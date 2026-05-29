---
description: "Setty Lab manuscript audit: read paper and implementation in parallel, surface places where formulas, algorithms, dimensions, parameter defaults, or complexity claims in the manuscript diverge from the code. Use during paper review to verify methods sections against the actual implementation. Runs a skeptic confirmation pass before reporting non-trivial findings. Produces a markdown report — does not edit the paper or code."
---

# Setty Lab Manuscript Audit

TRIGGER when: the user is reviewing a paper or manuscript and asks to audit the methods section against the implementation, check whether the code matches what the paper claims, cross-check formulas/algorithms/tensor dimensions/parameter defaults between manuscript and code, or verify that a writeup is consistent with the codebase. Use specifically for the **paper-vs-code consistency** part of a review — not for prose feedback, narrative critique, citation hygiene, copy-editing, or pure code review unmoored from a manuscript.

This skill is the cross-cutting check that nobody runs because each side feels like someone else's job — yet it is where the worst bugs hide, because each side looks internally consistent.

Ported from `matsen/bipartite/skills/bip-ms-audit` (the upstream skill the Setty Lab kompot audit consumed) by the Setty Lab on 2026-05-28. Adapted to drop bipartite-specific `.ms-config.json` / `tracked_repos[]` infrastructure, replace `@surprising-conclusion-skeptic` with a general-purpose skeptic subagent, and add the 4-tier severity taxonomy and `REFUTED` verdict that the kompot audit surfaced.

## Core principle

**Trust nothing. Read both sides.** A surprising mismatch ("paper says $f^u_b$, code uses $f^d_b$") is exactly the finding most often either a real bug or a misreading on one side. Either outcome is valuable, but never report it without an independent skeptic verifying.

Two symmetric failure modes, both cost user trust:

- **False positive** — report a "bug" that isn't, sending the user on a wild-goose chase. Avoid by running a skeptic subagent on every non-trivial finding before propagating.
- **False negative** — skim formulas, miss the bug. Avoid by reading the actual implementation file with `Read`, not just grepping for keywords.

**Default to MATCH.** Most claims are correct. A report with 30 mismatches in a 40-claim audit almost always means the auditor is misreading the code.

## Workflow

### Step 1: Establish scope

Ask the user (or detect from the workspace):

1. **Paper file** — `.tex` source preferred (line numbers stable); PDF acceptable as a fallback. If multiple `.tex` files, ask which is the entry point.
2. **Code repo(s)** — local path(s) to the implementation(s) the paper describes. If multiple repos implement the same method (e.g., a reference `palantir` repo plus a downstream `kompot` repo), audit against all of them — divergence *between* implementations is itself a high-yield finding.
3. **Audit scope** — full Methods/Algorithms section by default; or a single section, subsection, or labeled equation if the user specifies one.

If working inside a nexus workspace (`work/<project>/`), inspect the project tree for `.tex` sources and obvious implementation directories before asking — silent detection beats interrogation when it's safe.

### Step 2: Partition and fan out

Partition the audit scope into independent chunks, then dispatch one `general-purpose` subagent per chunk **in parallel** — single message, multiple `Agent` tool calls.

Partitioning rules:

- **Whole paper** (default): one subagent per top-level Methods / Algorithms section.
- **One section**: one subagent per subsection, or per claim cluster (formula + its surrounding text) if subsections are missing.
- **One formula or label**: one subagent.

Brief for each audit subagent (the **line-by-line investigation** framing is mandatory — this is what separates an audit from a skim):

> **Line-by-line investigation** of paper section `<section>` against code repo(s) `<path(s)>`. This is not a scan. For every checkable claim in scope, you must read the implementation file in full with the `Read` tool — not a grep excerpt — and cite the specific paper line and code line that back your verdict. A verdict without a `file:line` citation on both sides will be rejected and re-dispatched.
>
> Tasks:
>
> 1. Read the paper section with `Read`. List every checkable, falsifiable claim: tensor/array dimensions, formulas (`align`/`equation`/display math), algorithm steps, hyperparameter values, counts/complexity, variable bindings, loss/metric definitions, data pipeline steps, theorem statements, FDR/p-value/correction taxonomies. Skip subjective claims ("our results suggest…"). Record paper `file:line` for each.
> 2. For each claim, locate the code-side counterpart. Use `rg` to find files, but then `Read` the file. Common keyword maps: tensor dims → `np.zeros`/`torch.zeros`/`AnnData` shape; formulas → `forward`/`loss`/aggregation/distance metrics; hyperparameters → `config.yaml`/CLI defaults/function defaults; loss/mask → training loop; data filtering → preprocessing pipeline. If a claim has multiple implementations (vectorized batch path + reference path), check **both** — frequent source of divergence.
> 3. For each claim, classify with a verdict:
>     - `MATCH` — paper and code agree
>     - `MISMATCH` — disagree on a substantive, falsifiable point
>     - `AMBIGUOUS` — paper is unclear/underspecified; code makes a specific choice
>     - `MULTIPLE IMPLS DISAGREE` — two code paths disagree with each other (and at most one matches the paper)
>     - `STALE PAPER` — paper describes an earlier code version
>     - `STALE CODE` — paper describes a fix code hasn't picked up
>
> **MATCH is the default.** If your report is mostly `MISMATCH`, you are misreading the code — stop and re-check the worst offenders before returning.
>
> Return under 500 words, structured:
>
> - `findings`: one entry per non-`MATCH` claim with paper quote + `file:line`, code quote + `file:line` (use `Read`, not grep excerpts), verdict, one-sentence rationale.
> - `matches`: count of `MATCH` verdicts (no quotes needed).
> - `surprises`: claims you couldn't certify a `file:line` for, variable names that mean different things in different places, `RECOMMEND DEEPER LOOK` flags.

If a subagent returns a finding without both `file:line` citations, re-dispatch with a narrower brief covering just that finding.

### Step 3: Consolidate findings

Collect all subagent reports and assemble a single working list of non-`MATCH` findings. No prose pasted verbatim from subagents — quote only the paper and code line excerpts they cited.

If any subagent's report has many findings (say >5 in a 10-claim section), treat that as the "everything looks like a mismatch" failure mode and re-dispatch with explicit instruction to verify each claim by reading the full implementation file before classifying.

### Step 4: Skeptic confirmation for every non-MATCH finding

For each non-`MATCH` finding, spawn a fresh `general-purpose` subagent as a skeptic — separate context, no prior commitments — and brief it to **try to refute** the finding. This step is the difference between a useful audit and one that cries wolf; never skip it for a finding you intend to surface to the user.

Skeptic brief:

> You are a skeptic. Your job is to refute, not confirm, the finding below. Read the paper context, read the code in full with `Read`, and rule out simpler explanations before agreeing the finding is real.
>
> **Finding**: <verdict, paper claim + line, code location + line, suggested mismatch>
>
> Explicitly evaluate these alternatives:
>
> - Maybe the auditor misread the paper.
> - Maybe the auditor misread the code (a downstream rebinding, a default override, a kwarg shadowing).
> - Maybe the two code paths are actually equivalent due to a specific construction (algebraic identity, broadcasting, masking).
> - Maybe one of them is dead code or only runs under a branch that never fires in practice.
> - Maybe the variable names mean something different in this context than the auditor thinks.
> - **`REFUTED`** — Maybe the paper has a typo / off-by-one / wrong sign and the code is the source of truth (a Setty-lab-frequent outcome — surface this verdict explicitly).
>
> Return: `CONFIRMED` | `PARTIALLY CONFIRMED <qualification>` | `REFUTED <why>` plus the `file:line` citations you read.

`CONFIRMED` → keep the finding. `REFUTED` → drop it from the report (or escalate as a paper typo if the skeptic flagged that). `PARTIALLY CONFIRMED` → keep with the qualification in the report.

### Step 5: Apply the severity taxonomy

Sort the surviving findings into four severity tiers. The split drives both report ordering and what the user does with each finding:

| Tier | What it is | Action implied |
|---|---|---|
| **BLOCKER** | Wrong formula or algorithm; tensor dimension off; complexity claim wrong by a polynomial factor; statistical test misapplied. Affects results / claims. | Paper edit AND code review both warranted; treat as a publication-blocking issue. |
| **MAJOR** | Substantive ambiguity or notation drift that a careful reader would catch. Default parameter values out of step. | Paper edit; code change usually not needed. |
| **MINOR** | Wording precision, unstated assumption, omitted edge-case behavior. | Suggest paper edit; user may defer. |
| **NIT** | Typo, inconsistent notation across sections, missing reference to an obvious citation. | Cluster into a single "minor revisions" list. |
| **REFUTED** | Skeptic identified the paper as having the typo / wrong sign; code is correct. | Paper edit only. Surface separately so the user sees them. |

The kompot audit (worked example, settylab/dotto-nexus#142) caught 3 BLOCKERs (Mahalanobis denominator, DA PTP factor, FDR taxonomy), 3 MAJORs, and 5 MINOR/NIT findings via this exact methodology — illustrative of the expected severity distribution from a thorough audit of a method paper.

### Step 6: Write the report

Produce a markdown report at the manuscript repo (or a path the user specifies) named `MS-AUDIT-<ISO-date>.md`:

```markdown
# Manuscript audit — <paper title> — <ISO date>

Paper: `<paper-file>` @ <git-sha-short>
Code:  `<repo>/<commit-sha-short>` (one line per repo if multiple)

## Summary

| Tier | Count |
|---|---|
| BLOCKER  | N |
| MAJOR    | N |
| MINOR    | N |
| NIT      | N |
| REFUTED  | N |
| MATCH    | N (count only, no listing) |

## Findings

### BLOCKER 1. Tensor dimension `(n-3) × N × 4` — MISMATCH

**Paper** (`main.tex:296`): "creating a tensor of dimension $(n-3) \times N \times 4$"

**Code** (`pkg/wrapper.py:228-234`):

\`\`\`python
mutations = np.full(
    (len(trees), max_n_nodes, max_n_sites, 4), -1, ...)
\`\`\`

Allocates `max_n_nodes` ≈ 2n-2 entries — paper's `(n-3)` is too small.

**Skeptic verdict**: CONFIRMED (cited `file:line`, ruled out the "pendant edges always zero" alternative).

**Suggested action**: change paper to `(2n-3) × N × 4` and clarify "indexed by non-root nodes."

### MAJOR 1. Default learning rate drift

[same format — paper quote, code quote, skeptic verdict, suggested action]

...

### REFUTED 1. Mahalanobis denominator sign

**Paper** (`methods.tex:482`): denominator written as `2σ²`.

**Code** (`pkg/distance.py:91`): uses `σ²` (no factor of 2).

**Skeptic verdict**: REFUTED — code matches the standard textbook form (Mahalanobis distance is `(x-μ)ᵀ Σ⁻¹ (x-μ)`, no 2 in the denominator). The `2σ²` in the paper is a typo carried over from a Gaussian PDF derivation in the previous paragraph.

**Suggested action**: paper edit to drop the `2`.
```

For each finding include: paper quote + line, code quote + line, skeptic verdict, suggested action. Group by severity tier in the order above.

### Step 7: Hand off

Show the report path. Offer:

1. Open the report (`less <path>` or whatever the user's editor invocation is).
2. For each BLOCKER and MAJOR, ask whether to draft a paper edit, file a code issue, or both.
3. Do not auto-edit the paper or auto-file issues. The user decides.

## Guidelines

- **Read the actual files.** Every reported finding must have a `Read` (not just a `grep`) backing it on both sides.
- **Default to MATCH.** Most claims are correct.
- **Always run the skeptic on non-`MATCH` findings.** Surprising bug reports cost user trust when wrong; the skeptic round trip is cheap insurance.
- **Cite both sides with line numbers.** `main.tex:296` and `pkg/wrapper.py:228` — never "around line 200ish."
- **Don't fix anything.** This skill produces a report. Edits to the paper and code changes happen in separate, explicit steps.
- **Two implementations of the same thing are a high-yield search target.** A vectorized batch path and a tree-iteration reference path of the same algorithm are an excellent place to find bugs even when neither side disagrees with the paper individually.
- **Hyperparameter drift is real.** Paper says lr = 5 × 10⁻⁵; config says lr = 1 × 10⁻⁴ because someone tuned and forgot to update the paper. Cheap to check, often wrong.
- **Notation traps.** A formula using `v` for a node and `v` for a function is a warning sign; verify the paper's `v` in storage matches the code's `v` in storage, not just both being plausible.
- **REFUTED is a first-class outcome.** When the skeptic identifies the paper as the side with the typo, surface it as such — the user gets a paper edit out of it just as much as a `MISMATCH`.

## When to use this vs. siblings

| Need | Skill |
|---|---|
| Test scientific code (pytest, testthat, nf-test) | `fh.testing` |
| Reproducibility hygiene (pin versions, container digests) | `fh.reproducibility` |
| Setty Lab plot conventions for figures | `setty.plots` |
| Stateful iterative analysis with project-local JupyterLab | `setty.labsh` |
| **Cross-check paper claims against the code** | **this skill** |

## Why this shape

- **Reads paper as source of truth for *intent*, code as source of truth for *behavior*.** Either can be wrong; the audit's job is to surface the gap.
- **Skeptic step is non-optional.** Without it the skill is a false-positive machine; with it it earns its place. Surprising bug reports cost user trust when wrong; the skeptic round-trip is cheap insurance.
- **Severity taxonomy on top of verdict taxonomy.** The verdict (`MISMATCH`, `AMBIGUOUS`, …) tells you *what* the gap is; the tier (`BLOCKER`, `MAJOR`, …) tells you *what to do about it*. Both are needed for a useful report.
- **Output is a markdown report, not auto-applied edits.** A bad finding propagated as a paper edit is much more expensive than the same finding in a markdown report.
- **No state directory.** Papers and code change together; "regression since last audit" framing isn't useful. Re-run as needed; the report is the artifact.
