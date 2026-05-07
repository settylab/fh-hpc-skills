#!/usr/bin/env python3
"""Analyze the week-long storage benchmark fleet.

Reads ``docs/benchmarks/weekly_summary.tsv`` (long-form, produced by
``aggregate_results.py``), drops the test run, and computes:

  * Median + IQR per (filesystem, metric) across the 28 weekly runs.
  * Spearman correlation of NFS metrics vs cluster load
    (slurm_cpus_alloc / slurm_cpus_total).
  * Per-host distribution of localtmp metrics (NVMe-vs-spinning split).
  * Time-of-day Kruskal-Wallis + pairwise Mann-Whitney with BH FDR.
  * Per-fs ordering robustness across the 28 runs.

Writes:

  * ``docs/benchmarks/medians_iqr.tsv``   — wide per-(fs,metric) table.
  * ``docs/benchmarks/nfs_load_corr.tsv`` — Spearman rho/p per fs+metric.
  * ``docs/benchmarks/time_of_day_stats.tsv`` — KW + MWU + BH per fs+metric.
  * ``docs/benchmarks/host_localtmp.tsv`` — per-host localtmp medians.
  * ``docs/benchmarks/ordering_robustness.tsv`` — per-run fs ordering.
  * ``docs/benchmarks/figures/*.png`` — six figures listed in __main__.
"""

import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

FS_ORDER = ["fast", "temp", "working", "localtmp", "shm"]
NFS_FS = ["fast", "temp", "working"]
METRICS = ["seq_write_MiBs", "seq_read_MiBs", "metadata_s", "random_read_ops"]
METRIC_LABEL = {
    "seq_write_MiBs": "Sequential write (MiB/s)",
    "seq_read_MiBs": "Sequential read (MiB/s)",
    "metadata_s": "Metadata 1000 files (s, lower = faster)",
    "random_read_ops": "Random 4 KiB reads (ops/s)",
}
HIGHER_IS_BETTER = {
    "seq_write_MiBs": True,
    "seq_read_MiBs": True,
    "metadata_s": False,
    "random_read_ops": True,
}
TOD_BUCKETS = {"03": "03:15", "09": "09:30", "14": "14:30", "21": "21:00"}

# Setty Lab plot aesthetics: Helvetica/Arial, Paired palette
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})
PALETTE = sns.color_palette("Paired", n_colors=10)


def load(tsv_path):
    df = pd.read_csv(tsv_path, sep="\t")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["slurm_cpus_alloc"] = pd.to_numeric(df["slurm_cpus_alloc"], errors="coerce")
    df["slurm_cpus_total"] = pd.to_numeric(df["slurm_cpus_total"], errors="coerce")
    df["this_node_load15"] = pd.to_numeric(df["this_node_load15"], errors="coerce")
    df["load_frac"] = df["slurm_cpus_alloc"] / df["slurm_cpus_total"]
    df["dt"] = pd.to_datetime(df["timestamp"], format="%Y%m%d_%H%M%S")
    df["hour"] = df["dt"].dt.hour
    # Map start hour into the 4 scheduled buckets (handles --begin slack).
    def bucket(h):
        # 03:15 → 03; 09:30 → 09; 14:30 → 14; 21:00 → 21
        for tag, _ in TOD_BUCKETS.items():
            target = int(tag)
            # nearest bucket within +/- 3h covers --begin slack
            if abs(h - target) <= 3 or (target == 21 and h in (0, 1)):
                return tag
        return "other"
    df["tod"] = df["hour"].apply(bucket)
    df["is_test"] = df["timestamp"] == "20260417_161801"
    return df


def medians_iqr(df_weekly, out_dir):
    rows = []
    for fs in FS_ORDER:
        for m in METRICS:
            vals = df_weekly[(df_weekly.fs == fs) & (df_weekly.metric == m)]["value"].dropna()
            if vals.empty:
                continue
            q25, q50, q75 = np.percentile(vals, [25, 50, 75])
            rows.append({
                "fs": fs, "metric": m, "n": int(len(vals)),
                "median": q50, "q25": q25, "q75": q75, "iqr": q75 - q25,
                "min": float(vals.min()), "max": float(vals.max()),
            })
    out = pd.DataFrame(rows)
    out.to_csv(out_dir / "medians_iqr.tsv", sep="\t", index=False, float_format="%.3f")
    return out


def nfs_load_corr(df_weekly, out_dir):
    rows = []
    for fs in NFS_FS:
        for m in METRICS:
            sub = df_weekly[(df_weekly.fs == fs) & (df_weekly.metric == m)].dropna(
                subset=["value", "load_frac"]
            )
            if len(sub) < 4:
                continue
            rho, pval = stats.spearmanr(sub["load_frac"], sub["value"])
            rows.append({
                "fs": fs, "metric": m, "n": len(sub),
                "spearman_rho": rho, "p_value": pval,
                "load_min": float(sub["load_frac"].min()),
                "load_max": float(sub["load_frac"].max()),
            })
    out = pd.DataFrame(rows)
    out.to_csv(out_dir / "nfs_load_corr.tsv", sep="\t", index=False, float_format="%.4f")
    return out


def host_localtmp(df_weekly, out_dir):
    sub = df_weekly[df_weekly.fs == "localtmp"]
    pivot = sub.pivot_table(
        index="host", columns="metric", values="value", aggfunc="median"
    ).reset_index()
    pivot["n_runs"] = sub.groupby("host").apply(
        lambda g: g["jobid"].nunique(), include_groups=False
    ).reindex(pivot["host"]).values
    pivot.to_csv(out_dir / "host_localtmp.tsv", sep="\t", index=False, float_format="%.2f")
    return pivot


def time_of_day(df_weekly, out_dir):
    """Kruskal-Wallis (4 buckets) per (fs, metric); pairwise MWU + BH."""
    kw_rows = []
    mwu_rows = []
    buckets = ["03", "09", "14", "21"]
    pairs = [(a, b) for i, a in enumerate(buckets) for b in buckets[i + 1:]]
    for fs in FS_ORDER:
        for m in METRICS:
            groups = []
            tod_used = []
            for t in buckets:
                vals = df_weekly[
                    (df_weekly.fs == fs) & (df_weekly.metric == m) & (df_weekly.tod == t)
                ]["value"].dropna().values
                if len(vals) >= 2:
                    groups.append(vals)
                    tod_used.append(t)
            if len(groups) < 2:
                continue
            try:
                kw = stats.kruskal(*groups)
                kw_rows.append({
                    "fs": fs, "metric": m,
                    "kw_H": kw.statistic, "kw_p": kw.pvalue,
                    "groups": ",".join(tod_used),
                    "n_total": int(sum(len(g) for g in groups)),
                })
            except ValueError:
                continue
            for a, b in pairs:
                va = df_weekly[
                    (df_weekly.fs == fs) & (df_weekly.metric == m) & (df_weekly.tod == a)
                ]["value"].dropna().values
                vb = df_weekly[
                    (df_weekly.fs == fs) & (df_weekly.metric == m) & (df_weekly.tod == b)
                ]["value"].dropna().values
                if len(va) < 2 or len(vb) < 2:
                    continue
                mwu = stats.mannwhitneyu(va, vb, alternative="two-sided")
                mwu_rows.append({
                    "fs": fs, "metric": m, "tod_a": a, "tod_b": b,
                    "n_a": len(va), "n_b": len(vb),
                    "median_a": float(np.median(va)),
                    "median_b": float(np.median(vb)),
                    "u_stat": mwu.statistic, "p_raw": mwu.pvalue,
                })
    mwu_df = pd.DataFrame(mwu_rows)
    if not mwu_df.empty:
        # Benjamini-Hochberg across all pairwise tests
        p_raw = mwu_df["p_raw"].values
        order = np.argsort(p_raw)
        ranked = p_raw[order]
        n = len(ranked)
        bh = ranked * n / np.arange(1, n + 1)
        # enforce monotonicity
        bh = np.minimum.accumulate(bh[::-1])[::-1]
        bh = np.clip(bh, 0, 1)
        bh_unsorted = np.empty_like(bh)
        bh_unsorted[order] = bh
        mwu_df["p_bh"] = bh_unsorted
    kw_df = pd.DataFrame(kw_rows)
    kw_df.to_csv(out_dir / "time_of_day_kw.tsv", sep="\t", index=False, float_format="%.4f")
    mwu_df.to_csv(out_dir / "time_of_day_mwu.tsv", sep="\t", index=False, float_format="%.4f")
    return kw_df, mwu_df


def ordering_robustness(df_weekly, out_dir):
    """Per run, rank fs by each metric. Count flips vs the global ordering."""
    rows = []
    for m in METRICS:
        ascending = not HIGHER_IS_BETTER[m]  # rank=1 means best
        # global ordering by median over all weekly runs
        med = (
            df_weekly[df_weekly.metric == m]
            .groupby("fs")["value"].median().sort_values(ascending=ascending)
        )
        global_order = list(med.index)
        # per-run ordering
        per_run = (
            df_weekly[df_weekly.metric == m]
            .pivot_table(index="jobid", columns="fs", values="value")
        )
        flip_counts = {fs: 0 for fs in global_order}
        for jobid, row in per_run.iterrows():
            run_sorted = row.sort_values(ascending=ascending)
            run_order = list(run_sorted.index)
            for fs in global_order:
                if global_order.index(fs) != run_order.index(fs):
                    flip_counts[fs] += 1
            rows.append({
                "metric": m, "jobid": str(jobid),
                "global_order": "|".join(global_order),
                "run_order": "|".join(run_order),
                "matches_global": run_order == global_order,
            })
    out = pd.DataFrame(rows)
    out.to_csv(out_dir / "ordering_robustness.tsv", sep="\t", index=False)
    # summary table per metric
    summary_rows = []
    for m in METRICS:
        sub = out[out.metric == m]
        summary_rows.append({
            "metric": m,
            "n_runs": int(len(sub)),
            "n_matches_global": int(sub["matches_global"].sum()),
            "frac_matches_global": float(sub["matches_global"].mean()),
            "global_order": sub["global_order"].iloc[0] if len(sub) else "",
        })
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out_dir / "ordering_robustness_summary.tsv", sep="\t", index=False, float_format="%.3f")
    return out, summary


def fig_box_per_fs(df_weekly, out_dir):
    """Six panels — one per metric, box+strip across filesystems.

    Two panels become 'log y' for tmpfs/local (random_read_ops, seq_*) since
    /dev/shm dwarfs everything; the metadata_s panel stays linear.
    """
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, m in zip(axes.flat, METRICS):
        sub = df_weekly[df_weekly.metric == m]
        sns.boxplot(
            data=sub, x="fs", y="value", order=FS_ORDER, ax=ax,
            color="#cccccc", showcaps=True, showfliers=False, width=0.55,
        )
        sns.stripplot(
            data=sub, x="fs", y="value", order=FS_ORDER, ax=ax,
            color="#1f77b4", size=3.5, alpha=0.7, jitter=0.18,
        )
        ax.set_title(METRIC_LABEL[m])
        ax.set_xlabel("")
        ax.set_ylabel("")
        if m != "metadata_s":
            ax.set_yscale("log")
    fig.suptitle("Storage benchmark — weekly fleet (n=28)\nbox = quartiles, dots = individual runs", y=1.0)
    fig.tight_layout()
    fig.savefig(out_dir / "fig1_box_per_fs.png")
    plt.close(fig)


def fig_nfs_vs_load(df_weekly, corr_df, out_dir):
    fig, axes = plt.subplots(len(NFS_FS), len(METRICS), figsize=(14, 9), sharex=True)
    for i, fs in enumerate(NFS_FS):
        for j, m in enumerate(METRICS):
            ax = axes[i, j]
            sub = df_weekly[(df_weekly.fs == fs) & (df_weekly.metric == m)].dropna(
                subset=["value", "load_frac"]
            )
            ax.scatter(sub["load_frac"], sub["value"], s=22, alpha=0.75,
                       color=PALETTE[2 * i + 1])
            row = corr_df[(corr_df.fs == fs) & (corr_df.metric == m)]
            if not row.empty:
                rho = row["spearman_rho"].iloc[0]
                p = row["p_value"].iloc[0]
                ax.set_title("{0} / {1}\nρ={2:+.2f}, p={3:.3f}".format(fs, m, rho, p),
                             fontsize=9)
            if i == len(NFS_FS) - 1:
                ax.set_xlabel("cluster load (cpus_alloc / cpus_total)")
            if j == 0:
                ax.set_ylabel(fs)
            ax.tick_params(labelsize=8)
    fig.suptitle("NFS metrics vs cluster load — Spearman per panel", y=1.0)
    fig.tight_layout()
    fig.savefig(out_dir / "fig2_nfs_vs_load.png")
    plt.close(fig)


def fig_localtmp_per_host(df_weekly, out_dir):
    sub = df_weekly[df_weekly.fs == "localtmp"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    host_order = (
        sub.groupby("host")["value"].median().sort_values().index.tolist()
    )
    # Sort hosts by overall median seq_read so the pattern aligns across panels
    host_order_seqr = (
        sub[sub.metric == "seq_read_MiBs"]
        .groupby("host")["value"].median().sort_values(ascending=False).index.tolist()
    )
    if host_order_seqr:
        host_order = host_order_seqr
    for ax, m in zip(axes.flat, METRICS):
        s = sub[sub.metric == m]
        sns.stripplot(
            data=s, x="host", y="value", order=host_order, ax=ax,
            color="#d62728", size=6, alpha=0.85, jitter=0.18,
        )
        ax.set_title("localtmp / " + METRIC_LABEL[m])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=60, labelsize=8)
    fig.suptitle("Per-host /tmp performance — weekly fleet", y=1.0)
    fig.tight_layout()
    fig.savefig(out_dir / "fig3_localtmp_per_host.png")
    plt.close(fig)


def fig_time_of_day(df_weekly, out_dir):
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for ax, m in zip(axes.flat, METRICS):
        sub = df_weekly[df_weekly.metric == m].copy()
        # show NFS tiers + localtmp; shm dwarfs the panel
        sub = sub[sub.fs.isin(["fast", "temp", "working", "localtmp"])]
        sub["tod"] = pd.Categorical(sub["tod"], categories=["03", "09", "14", "21"], ordered=True)
        sns.boxplot(
            data=sub, x="tod", y="value", hue="fs",
            hue_order=["fast", "temp", "working", "localtmp"],
            palette=[PALETTE[1], PALETTE[3], PALETTE[5], PALETTE[7]],
            ax=ax, fliersize=2, linewidth=0.8,
        )
        ax.set_title(METRIC_LABEL[m])
        ax.set_xlabel("scheduled bucket")
        ax.set_ylabel("")
        if m != "metadata_s":
            ax.set_yscale("log")
        if ax is not axes.flat[0]:
            leg = ax.get_legend()
            if leg:
                leg.remove()
    fig.suptitle("Time-of-day buckets — by scheduled --begin (actual start may slip)", y=1.0)
    fig.tight_layout()
    fig.savefig(out_dir / "fig4_time_of_day.png")
    plt.close(fig)


def fig_ordering_heatmap(order_df, out_dir):
    """Heatmap: per-run, per-metric, fs rank position."""
    fig, axes = plt.subplots(1, len(METRICS), figsize=(16, 5), sharey=True)
    for ax, m in zip(axes, METRICS):
        sub = order_df[order_df.metric == m].copy()
        global_order = sub["global_order"].iloc[0].split("|")
        rows = []
        for _, r in sub.iterrows():
            run_order = r["run_order"].split("|")
            for fs in global_order:
                rows.append({"jobid": r["jobid"], "fs": fs, "rank": run_order.index(fs) + 1})
        rdf = pd.DataFrame(rows)
        mat = rdf.pivot(index="jobid", columns="fs", values="rank")
        mat = mat[global_order]
        sns.heatmap(
            mat, annot=True, fmt=".0f", cmap="RdYlGn_r", vmin=1, vmax=len(global_order),
            cbar=False, ax=ax, linewidths=0.3, linecolor="white",
        )
        ax.set_title(m + "\n(global: " + " > ".join(global_order) + ")", fontsize=9)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=45, labelsize=9)
        ax.tick_params(axis="y", labelsize=7)
    fig.suptitle("Per-run filesystem rank (1 = best). Green = ordering matches global; red = flipped.", y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / "fig5_ordering_heatmap.png")
    plt.close(fig)


def fig_load_distribution(df_weekly, out_dir):
    """Quick sanity check: how loaded was the cluster across the 28 runs?"""
    runs = (
        df_weekly[["jobid", "load_frac", "this_node_load15", "tod", "host"]]
        .drop_duplicates(subset="jobid")
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    sns.histplot(runs["load_frac"], bins=14, ax=axes[0], color=PALETTE[1])
    axes[0].set_xlabel("cluster load (cpus_alloc / cpus_total)")
    axes[0].set_ylabel("# runs")
    axes[0].set_title("Cluster CPU load at run start")
    sns.boxplot(data=runs, x="tod", y="load_frac",
                order=["03", "09", "14", "21"],
                color="#cccccc", ax=axes[1])
    sns.stripplot(data=runs, x="tod", y="load_frac",
                  order=["03", "09", "14", "21"],
                  color=PALETTE[1], ax=axes[1], size=5)
    axes[1].set_title("Cluster load by scheduled bucket")
    axes[1].set_xlabel("scheduled --begin bucket")
    axes[1].set_ylabel("cluster load")
    fig.tight_layout()
    fig.savefig(out_dir / "fig6_load_distribution.png")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="docs/benchmarks/weekly_summary.tsv")
    ap.add_argument("--out-dir", default="docs/benchmarks")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = load(args.input)
    df_weekly = df[~df.is_test].copy()

    print("rows total: {0}".format(len(df)))
    print("rows weekly (excluding test): {0}".format(len(df_weekly)))
    print("unique jobs: {0}".format(df_weekly["jobid"].nunique()))
    print("unique hosts: {0}".format(df_weekly["host"].nunique()))
    print("hosts: {0}".format(sorted(df_weekly["host"].unique())))
    print("tod counts:")
    print(df_weekly.groupby("tod")["jobid"].nunique())

    miqr = medians_iqr(df_weekly, out_dir)
    print("\n=== medians + IQR per (fs, metric) ===")
    print(miqr.to_string(index=False))

    corr = nfs_load_corr(df_weekly, out_dir)
    print("\n=== NFS metric vs cluster load (Spearman) ===")
    print(corr.to_string(index=False))

    host = host_localtmp(df_weekly, out_dir)
    print("\n=== per-host localtmp medians ===")
    print(host.to_string(index=False))

    kw, mwu = time_of_day(df_weekly, out_dir)
    print("\n=== Kruskal-Wallis time-of-day ===")
    print(kw.to_string(index=False))
    print("\n=== Significant pairwise (BH q<0.10) ===")
    if not mwu.empty:
        print(mwu[mwu["p_bh"] < 0.10].to_string(index=False))

    order, order_summary = ordering_robustness(df_weekly, out_dir)
    print("\n=== ordering robustness summary ===")
    print(order_summary.to_string(index=False))

    fig_box_per_fs(df_weekly, fig_dir)
    fig_nfs_vs_load(df_weekly, corr, fig_dir)
    fig_localtmp_per_host(df_weekly, fig_dir)
    fig_time_of_day(df_weekly, fig_dir)
    fig_ordering_heatmap(order, fig_dir)
    fig_load_distribution(df_weekly, fig_dir)
    print("\nfigures written to {0}".format(fig_dir))


if __name__ == "__main__":
    main()
