---
description: "Setty Lab plot aesthetics: publication-quality matplotlib/seaborn/scanpy styling, Helvetica/Arial fonts (with Liberation Sans fallback and mathtext-pitfall guidance), Paired palette, DPI/figure-size conventions, Illustrator handoff; pointers to palantir.plot and kompot.plot"
---

# Setty Lab Plot Aesthetics

TRIGGER when: user is making figures for a Setty Lab paper/poster/presentation, asks about matplotlib/seaborn/scanpy styling, wants lab-consistent colors or fonts, prepares figures for Illustrator, asks how to configure Arial/Helvetica for publication, sees title characters split into per-letter frames in Illustrator, needs an editable PDF (`pdf.fonttype=42`) with embedded Arial / Liberation Sans, or needs to plot palantir pseudotime/gene trends or kompot volcano/heatmap results.

## Context

The Setty Lab maintains consistent plot aesthetics so figures across projects and manuscripts read as one visual voice. The stack is matplotlib (canonical), with seaborn and scanpy layered on top — both inherit matplotlib `rcParams`, so the drop-in below configures all three. Lab-built plotting utilities live in `palantir.plot` (trajectory/pseudotime) and `kompot.plot` (differential abundance/expression); prefer these over ad-hoc code for lab-standard analyses. Publisher font requirements (typically Arial) are handled by transferring the font to the HPC once and referencing it from `rcParams`.

Source: [Setty Lab Wiki — Plot Aesthetics](https://github.com/settylab/Lab-wiki/wiki/Plot-Aesthetics).

## The rules

These are the lab conventions. Every figure should satisfy them unless there is a specific reason to deviate.

1. **Resolution:** 150 DPI.
2. **Consistent colors across plots** — same category gets the same color everywhere in the paper.
3. **Separate legend** from the plot where possible (detached in Illustrator) so the axes panel is not compressed.
4. **All text must be legible.** If you are fighting matplotlib, finish it in Illustrator.
5. **No axes on UMAPs.** If axes are unavoidable, hide the ticks.
6. **No bounding box** — use `sns.despine()` or drop all four spines.
7. **At most 2 ticks per axis** when ticks are shown.
8. **Panel alignment** — use Illustrator's Transform X/Y to align multi-panel figures.
9. **No gridlines.**
10. **Square aspect ratio** when both axes share units (PCA, UMAP, diffusion maps).
11. **Font:** Helvetica for publications (Arial if the publisher requires it).

## Drop-in matplotlib setup

Put this at the top of any script or notebook that produces lab figures. seaborn and scanpy inherit these settings automatically:

```python
import matplotlib.pyplot as plt
import matplotlib

# Resolution and canvas
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300               # for final PDF/SVG export
plt.rcParams["figure.figsize"] = (6, 6)         # square default; override per-plot for bars/lines
plt.rcParams["image.cmap"] = "Spectral_r"       # lab default continuous palette

# No bounding box, no gridlines
for side in ("top", "right", "bottom", "left"):
    plt.rcParams[f"axes.spines.{side}"] = False
plt.rcParams["axes.grid"] = False

# Fonts: Helvetica preferred; Arial when a publisher mandates it.
# Liberation Sans is metric-compatible with Arial (identical glyph
# widths) so a font swap in Illustrator does not reflow the layout.
# DejaVu Sans last — keep as the matplotlib-bundled last resort
# only; its metrics differ from Arial. See "Arial on Gizmo" below.
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"]

# Keep text as real text (not outlined paths) in PDF/SVG so Illustrator
# can edit labels directly.
plt.rcParams["pdf.fonttype"] = 42               # TrueType, editable in Illustrator
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"           # emit <text> elements, not paths
```

Per-plot tick limiting (rule 7):

```python
plt.locator_params(axis="x", nbins=3)
plt.locator_params(axis="y", nbins=3)
# or, with an Axes handle:
ax.xaxis.set_major_locator(plt.MaxNLocator(2))
ax.yaxis.set_major_locator(plt.MaxNLocator(2))
```

UMAP / PCA panels (rules 5, 10):

```python
ax.set_aspect("equal")
ax.set_xticks([]); ax.set_yticks([])
ax.set_xlabel("UMAP1"); ax.set_ylabel("UMAP2")
for s in ax.spines.values():
    s.set_visible(False)
```

## Seaborn and scanpy

Both inherit the matplotlib `rcParams` set above. A few caveats:

- `sns.set_theme()` **overrides** your `rcParams`. If you call it, call it *before* the drop-in, or pass `rc={...}` to merge. Simplest: do not call `sns.set_theme()`.
- Use `sns.despine()` per-figure to drop the top/right spines when you want to keep bottom/left (the drop-in removes all four globally; override per-plot if you need axes).
- scanpy plotting (`sc.pl.*`) respects `rcParams["figure.figsize"]` and font settings but its palette is set per call via `palette=`. Pass a lab palette explicitly — do not rely on scanpy defaults.

```python
sc.pl.umap(adata, color="celltype", palette=CELLTYPE_COLORS, frameon=False, size=8)
```

`frameon=False` drops the scanpy-specific frame; it is not controlled by the spines rcParams.

## Lab plotting libraries

Prefer these over rolling your own plot code when the analysis matches:

### palantir.plot (trajectory / pseudotime)

```python
import palantir
```

| Function | Use |
|---|---|
| `plot_palantir_results(ad)` | Pseudotime, differentiation potential, branch probabilities on UMAP (one-call summary figure) |
| `plot_diffusion_components(ad)` | Diffusion map components panel grid |
| `plot_terminal_state_probs(ad, cells)` | Terminal-state probability bars per cell |
| `plot_branch_selection(ad)` | Inspect which cells are assigned to each branch |
| `plot_gene_trends(ad, genes=[...])` | Smoothed gene expression vs pseudotime, per branch |
| `plot_gene_trend_heatmaps(ad, genes=[...])` | Gene-by-pseudotime heatmap, one panel per branch |
| `plot_gene_trend_clusters(ad, clusters)` | Cluster-mean trend curves |
| `plot_trajectory(ad, branch)` / `plot_trajectories(ad)` | Trajectory overlay on embedding |
| `highlight_cells_on_umap(ad, cells)` | Subset highlight on UMAP |
| `gene_score_histogram(ad, score)` | Score distribution with thresholds |

Docs and tutorials: [settylab/Palantir](https://github.com/settylab/Palantir), [readthedocs](https://palantir.readthedocs.io/).

### kompot.plot (differential abundance / expression)

```python
from kompot.plot import (
    volcano_de, volcano_da, multi_volcano_da,
    heatmap, direction_barplot,
    plot_gene_expression, embedding, plot_smoothing,
    StringDBReport,
)
```

| Function | Use |
|---|---|
| `volcano_de(ad, ...)` | Differential **expression** volcano (log-fold-change vs significance) |
| `volcano_da(ad, ...)` | Differential **abundance** volcano (per-cell log-density change) |
| `multi_volcano_da(ad, ...)` | Grid of DA volcanoes across comparisons |
| `heatmap(ad, genes=[...])` | Gene × group heatmap with direction annotations |
| `direction_barplot(ad)` | Up/down gene counts per group |
| `plot_gene_expression(ad, genes=[...])` | Side-by-side expression across conditions |
| `embedding(ad, color=...)` | Kompot-styled UMAP/embedding plot |
| `plot_smoothing(ad, gene)` | Kompot density smoothing diagnostic |
| `StringDBReport(genes).render()` | Auto-generate a STRING-db gene-set report |

Docs: [settylab/kompot](https://github.com/settylab/kompot), `kompot/docs/source/plotting.rst` in the repo. These functions accept standard matplotlib `ax=` / `figsize=` kwargs, so the rcParams drop-in applies. They handle rule-compliant styling internally (despining, tick limits) — if you see a kompot plot that violates the rules, that is a kompot bug, not yours to paper over.

## Colors

The lab commonly reaches for the matplotlib `Paired` qualitative palette for categorical data:

```python
import matplotlib
matplotlib.colormaps["Paired"]                                              # preview
[matplotlib.colors.rgb2hex(c) for c in matplotlib.colormaps["Paired"].colors]
# -> ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
#     '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928']
```

For continuous maps, the lab default is `Spectral_r` (set above in `rcParams`).

## Arial on Gizmo (publisher-required)

Arial is **not redistributable**; supply your own licensed copy. The metric-compatible fallback is **Liberation Sans** (ships with `fonts-liberation`) — its glyph widths match Arial exactly, so swapping to real Arial in Illustrator does not reflow. Do **not** fall back to DejaVu Sans; its metrics differ.

### Place and discover

Put licensed TTFs (Regular **plus** Bold/Italic/BoldItalic — variants register separately, see pitfalls) in one of `~/.fonts/`, `~/.local/share/fonts/` (XDG), `~/.claude/fonts/` (sandbox-writable), or `<repo>/.fonts/` (gitignore — Arial is not redistributable). Then `fc-cache -f <dir>` and restart Python; `fc-list | grep -iE 'arial|liberation'` confirms.

### Register before rcParams

```python
import matplotlib as mpl
from pathlib import Path

def _register_arial_if_available():
    for d in [Path.home() / ".fonts",
              Path.home() / ".local" / "share" / "fonts",
              Path.home() / ".claude" / "fonts",
              Path(__file__).parent / ".fonts"]:
        if not d.is_dir():
            continue
        for ttf in d.iterdir():
            if ttf.suffix.lower() == ".ttf" and "arial" in ttf.name.lower():
                mpl.font_manager.fontManager.addfont(str(ttf))

_register_arial_if_available()  # call before the rcParams drop-in above
```

The drop-in's font chain (`Arial → Liberation Sans → Helvetica → DejaVu Sans`) resolves to Arial if registered, Liberation Sans otherwise — layout is preserved either way.

### Verify embedded fonts

```bash
pdffonts figures/Fig4.pdf
# Expected: BGZIHO+Arial or BGZIHO+LiberationSans, type "CID TrueType", emb yes.
# Failure: any "Type 3" line — vector paths, not editable text.
```

If poppler is missing on the sandbox, regex `/BaseFont` + `/Subtype` directly out of the PDF bytes (`re.findall(rb"/BaseFont\s*/([\w+\-]+).*?/Subtype\s*/([\w]+)", open(pdf,"rb").read(), re.DOTALL)`); subtype must be `Type0` / `CIDFontType2`, never `Type3`. For per-title structural checks, `pdfminer.six` extracts each title as a single `LTTextContainer` — a multi-line title like `'Tal1 chimera: Phlda2 LFC\n(WT → Tal1-/-)'` should come out as one container, not multiple (multiple = per-glyph emission, Illustrator will split the title on import). Install with `uv pip install pdfminer.six` (see `settylab.sandbox-gotchas` for the `uv pip` rule).

### Known pitfalls

- **Mathtext kills connected text.** Any `$\it{…}$`, `$\rightarrow$`, `$X^{Y}$` span in a title forces per-glyph `Tj` emission, and Illustrator splits the title into per-character text frames on import. Use plain Unicode (`→`, `α`, `±`) for arrows, Greek, math symbols. Italics for gene/species names belong in the editorial pass on the PDF, not in the matplotlib title string. **This is the most common Arial-pipeline regression.**
- **`pdf.use14corefonts=True` is a foot-gun.** Forces the 14 PDF base fonts (Helvetica is Arial-metric-equivalent) and **ignores** `font.sans-serif`, so Arial registered via `addfont` is discarded. Do not combine.
- **Italic / Bold variants must be registered separately.** `addfont('Arial.ttf')` adds only Regular. Without `Arial-Bold.ttf` / `Arial-Italic.ttf`, `fontstyle='italic'` silently falls back to DejaVu Sans Oblique and the figure mixes fonts.
- **Configure rcParams once, in the entry module.** Child modules and per-panel functions that re-set rcParams override the global config and silently desync panels.
- **Fontconfig cache staleness.** After dropping a TTF into `~/.fonts/`, run `fc-cache -f ~/.fonts` and restart Python. In long-running Jupyter sessions, force matplotlib to re-scan with `mpl.font_manager._load_fontmanager(try_read_cache=False)`.

## Export for Illustrator

Finalize figures as vectors, not PNG, so they edit cleanly:

```python
fig.savefig("fig2a.pdf", bbox_inches="tight", dpi=300)
# or SVG for pure vector editing:
fig.savefig("fig2a.svg", bbox_inches="tight")
```

With `pdf.fonttype = 42` and `svg.fonttype = "none"` set in the drop-in above, text remains selectable/editable in Illustrator. Avoid `bbox_inches="tight"` on multi-panel figures where you care about exact panel sizing — `tight` trims whitespace and breaks panel-to-panel alignment.

## Good vs bad

| | Bad | Good |
|---|---|---|
| Resolution | 72 DPI preview-quality | `figure.dpi = 150`, `savefig.dpi = 300` |
| Font | matplotlib default (DejaVu Sans), rasterized | Helvetica/Arial, `pdf.fonttype=42` so editable |
| Spines | Default box | `sns.despine()` or spines off |
| UMAP axes | Tick marks with numeric coords | No ticks, `set_aspect("equal")` |
| Axis ticks (when shown) | 6–10 auto-chosen ticks | 2–3 ticks via `MaxNLocator(2)` |
| Colors | Fresh palette each notebook | Central `palettes.py` with fixed celltype → hex map |
| Gridlines | `plt.grid(True)` | `axes.grid = False` |
| Export | PNG at screen DPI | PDF/SVG, text kept as text |

## Principles

- Consistency across a manuscript beats perfection in any single panel.
- Fix aesthetics once in `rcParams`; do not re-style plot-by-plot.
- Keep text as text in vector exports so Illustrator edits do not require re-running notebooks.
- Do not commit Arial or other non-redistributable fonts to git.
- If a lab-wide palette or convention changes, update this skill and the wiki together.

## References

- [Setty Lab Wiki — Plot Aesthetics](https://github.com/settylab/Lab-wiki/wiki/Plot-Aesthetics) (canonical source)
- [Setty Lab Wiki — Tips & Tricks: Jupyter plot presets](https://github.com/settylab/Lab-wiki/wiki/Tips-and-Tricks#jupyter-notebook)
- [matplotlib rcParams reference](https://matplotlib.org/stable/users/explain/customizing.html); lab plotting libraries linked inline above ([Palantir](https://github.com/settylab/Palantir), [Kompot](https://github.com/settylab/kompot)).
- Related skills: `fh.python` (matplotlib/seaborn/scanpy environments), `fh.vscode-remote` (plots over SSH), `setty.labsh` (stateful Jupyter), `settylab.sandbox-gotchas` (`uv pip` rule for `pdfminer.six`).
