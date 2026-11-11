# Statistical and scope traps that read as findings

Each entry: the trap, then the check. All were measured on lab analyses and caught by a skeptic pass after a first verdict had been published.

## Scope: is the claim about what was measured?

- **Measure the quantity the figure PLOTS.** Trace the code from raw data to the plotted value (`file:line`) before any statistic: an "outlier explained by a per-sample offset" was true of the row mean and false of the plotted quantities, computed after the offset was removed. A null whose MEAN sits at the observed value shows the statistic could not fail.
- **QC metrics before gene restriction.** Compute `pct_counts_mt`, `n_genes` per deposit on its OWN full feature space, then intersect. An intersection that dropped MT genes zeroed the mt fraction and the filter went inert (retention 91.5% → 95.7%). A retention rate that IMPROVES after a fix is the tell; assert the MT-gene count after any build.
- **Curated exemplars are not the population.** A 17/17 hit rate on canonical rename pairs was generalised to 1,496 genes; decomposed, 16% were renames and the remedy removed 235. Decompose by mechanism, state which stratum each rate came from, and measure what the remedy actually removes.
- **Same sample is not same cells.** Put n per arm per sample in any side-by-side: a curated 7k-cell subset against an uncurated 29k-cell rule is two populations under one sample name. When n differs by more than ~20%, restrict the new data to the old population before naming a cause.
- **Re-derive the WORDS, not only the numbers.** A qualitative clause ("mostly cell type A") written from a one-sample pilot survived three reviews into a cohort summary while every number was re-derived; it was false in 5 of 9 samples. Tie each factual clause to a command over the full-cohort tables.
- **"Independent of X" covers the input selection.** Code that reads no annotation label can still run on a cell set filtered by one; read the producer's kept/excluded rules and scope the claim.

## Size, power and calibration

- **Measure the statistic's type-I rate at the data's OWN reliability.** A correlation-based separation statistic rejected its null in 55/55 groups with zero true effect once one sample's reliability was degraded to the observed level (attenuation by sqrt(rel_i·rel_j)). Inject noise to the observed reliability with no effect and count rejections; report power too.
- **A disqualification does not transfer across axes.** Write down the CONDITION that ruled a statistic out, re-measure it on the new data, and measure both error rates by injection before choosing a replacement.
- **p = 0/N is a floor (1/(N+1)), not a measurement**, and "survives 200/200 posterior draws" is a statement about precision, never about the claim.
- **A selection-free rebuild still needs a null.** Permute the FEATURE (not the labels) and quote how often the rebuilt statistic fires (a "6 of 6 nested comparisons" claim fired 12% of the time on a permuted feature).
- **Replicate-range acceptance false-fails 2/(k+1)** ("final inside min-max of k exchangeable runs"). State a criterion's null false-fail rate before approving it; if a flawed rule fires, record "FAIL as specified", never swap in a post-hoc rule.
- **KS on rank-transformed p-values against themselves is a tautology** (uniform by construction). Test the method's own real-vs-null p-value, compare raw magnitudes across versions, and include a control that must fail.

## Confounds and controls

- **Do not adjudicate a confound with a statistic that is a function of it.** Before calling N measures "independent corroboration", compute their correlation with each other. Read a control on the CONCLUSION variable, not a proxy.
- **A batch is a property of the ASSAY the statistic was computed on.** Read it from the same instrument runs, not from another modality of the same samples. Tabulate run/slide per arm and name the aliased contrasts; when a covariate is fixed by the label itself, "not estimable on this design" can be the honest answer.
- **Diff what the CONTROL holds fixed against what the COMPARISON holds fixed:** a size ladder that varies one arm also varies total N.
- **Symmetric controls.** "Partition X is tied to condition S" needs the same procedure run on every condition and every partition scored on every condition; a rule-based label set is not a comparable reference.
- **Plant the effect at the hypothesis LEVEL.** A within-cell-state hypothesis needs a within-state plant; permuting across states also erases between-state structure and made an instrument look ~40x more sensitive than it was.
- **One reference per estimand.** A reference built from one arm mis-scores every arm with a different transform; a large FLAT offset across levels is a wiring defect before it is a result. Assert in code which reference each arm uses.
- **Debiasing toward the plug-in is not debiasing toward the truth.** Under shrinkage it manufactured a false clade with support 1.00. Ask "biased relative to WHAT?", report both estimators, and run a known-truth simulation covering both regimes. When posterior trace dominates, raw-draw distances are ~d̂² + tr_i + tr_j and Ward merges the two largest-trace outliers.

## Shares, ranks and cuts

- **Share of level is not share of variance.** A component that is 36% of the level can be 87% of the variance, and rankings, clusterings and outlier calls follow variance. When a decomposition is exact by construction, state the identity, not a variance-explained figure.
- **A rank percentile is not a test.** Ask how many items clear the same bar (44, not 1), what they are (mostly stress/mito/ribosomal), and what an independence null predicts; answer with an instrument that has a p-value and a potency control.
- **Measure false-positive burden at the cut the code takes.** Under a top-N cut every labelling calls N, so counts are vacuous: report the value at rank N and the OVERLAP of the sets.
- **A pAUC cap-ladder sign flip is not the ROC crossing:** the cumulative lead must erode first, so the turnover is late by construction. Read crossings pointwise.
- **The patient-level summary is an undeclared degree of freedom.** Mean-of-log1p CP10K vs counts pseudobulk moved panel p-values across 0.05: compute both, report both, and carry any cell-type restriction into every cohort.
- **ORA background = the population the foreground was selected from.** A genome-wide universe inflated term counts 1.35x-13.4x (worst for the most careful designs). State the background; run a size-matched random-draw control.
- **Never shrink the null set without explicit instruction.** In a benchmark the null is every non-target item; subsetting or expression-matching it changes the metric. State its size and composition, and make any code path that can shrink it fail unless explicitly opted in.

## Data-structure traps

- **Self-match:** a prefix filter over label columns admitted the ground-truth column, so every type scored Jaccard 1.0. Select columns by explicit list; treat a metric identical for every item as a defect; give synthetic tests a case whose right answer is not the extreme value.
- **Atlas-projection columns (`*.mapped`) are not the design.** Filtering on a per-cell projected stage substitutes a maturity percentile for a timepoint; cross-tab against the sample/design column first.
- **Ambient RNA biases marginal detection in chimeras.** Y-gene detection in a host compartment beside an abundant single-sex donor understates sex mixing; condition Y load on each cell's own Xist status, and never call sex from a gene the panel displays.
