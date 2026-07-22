#!/usr/bin/env python3
"""Combine the within-provider (three model sizes, agentic harness) and the
cross-provider (two further providers, code-generation harness) runs into one
picture of how the full skill affects agreement and validity across models and
companies. Provider names are withheld for the anonymised submission; the exact
model identifiers are in the archived record files.

Reads results/rerun_records.csv (Anthropic sizes) and
results/crossprovider_records.csv (OpenAI, Google). Writes results/fig_providers.png
and results/providers_summary.json.
"""
import csv, json, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
REF = json.loads((HERE / "data" / "references.json").read_text())
TOL = {"T1": 1e-3, "T2": 1e-3, "T3": 1e-3, "T4": 1e-2}
TASKS = ["T1", "T2", "T3", "T4"]

# Ordered model set with anonymised labels. Each tuple: (key, label, source).
MODELS = [
    ("opus",   "Provider 1 (large)",  "rerun"),
    ("sonnet", "Provider 1 (medium)", "rerun"),
    ("haiku",  "Provider 1 (small)",  "rerun"),
    ("openai", "Provider 2",          "cross"),
    ("google", "Provider 3",          "cross"),
]

def load():
    cells = defaultdict(list)   # (mkey, task, cond) -> [values]
    fails = defaultdict(int)
    # within-provider (Anthropic sizes)
    for r in csv.DictReader(open(HERE / "results" / "rerun_records.csv")):
        if r["condition"] in ("C0", "C4") and r["model"] in ("opus", "sonnet", "haiku"):
            if r["value"] not in ("", "None"):
                cells[(r["model"], r["task"], r["condition"])].append(float(r["value"]))
            else:
                fails[(r["model"], r["task"], r["condition"])] += 1
    # cross-provider (OpenAI, Google)
    for r in csv.DictReader(open(HERE / "results" / "crossprovider_records.csv")):
        if r["condition"] in ("C0", "C4"):
            if r["value"] not in ("", "None"):
                cells[(r["provider"], r["task"], r["condition"])].append(float(r["value"]))
            else:
                fails[(r["provider"], r["task"], r["condition"])] += 1
    return cells, fails

def rate(vals, task):
    ref, tol = REF[task]["value"], TOL[task]
    if not vals:
        return dict(n=0, agree=None, valid=None, median=None)
    clusters = []
    for v in sorted(vals):
        if not clusters or v - clusters[-1][-1] > tol:
            clusters.append([v])
        else:
            clusters[-1].append(v)
    modal = max(len(c) for c in clusters) / len(vals)
    valid = sum(1 for v in vals if abs(v - ref) <= tol) / len(vals)
    return dict(n=len(vals), agree=modal, valid=valid, median=st.median(vals))

def main():
    cells, fails = load()
    summ = {}
    print(f"{'model':22}{'task':5}{'cond':5}{'n':>3}{'fail':>5}{'agree':>7}{'valid':>7}  median")
    for mkey, label, _ in MODELS:
        for task in TASKS:
            for cond in ("C0", "C4"):
                s = rate(cells.get((mkey, task, cond), []), task)
                f = fails.get((mkey, task, cond), 0)
                summ[f"{mkey}_{task}_{cond}"] = {**s, "fail": f, "label": label}
                a = "-" if s["agree"] is None else f"{s['agree']*100:.0f}%"
                v = "-" if s["valid"] is None else f"{s['valid']*100:.0f}%"
                md = "-" if s["median"] is None else f"{s['median']:.4f}"
                print(f"{label:22}{task:5}{cond:5}{s['n']:>3}{f:>5}{a:>7}{v:>7}  {md}")
    (HERE / "results" / "providers_summary.json").write_text(json.dumps(summ, indent=2, default=float))

    # ---- figure: validity at C0 vs C4 for the two non-ceiling tasks, all models ----
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    import numpy as np
    OK_GREY, OK_BLUE = "#BBBBBB", "#0072B2"
    mtasks = [("T2", "T2  Stochastic classifier"), ("T4", "T4  Reef-fish biomass")]
    labels = [m[1] for m in MODELS]
    x = np.arange(len(MODELS)); w = 0.38
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    for ax, (task, title) in zip(axes, mtasks):
        c0 = [(summ[f"{m[0]}_{task}_C0"]["valid"] or 0) * 100 for m in MODELS]
        c4 = [(summ[f"{m[0]}_{task}_C4"]["valid"] or 0) * 100 for m in MODELS]
        b0 = ax.bar(x - w / 2, c0, w, label="No skill (C0)", color=OK_GREY)
        b4 = ax.bar(x + w / 2, c4, w, label="Full skill (C4)", color=OK_BLUE)
        for bars in (b0, b4):
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{b.get_height():.0f}",
                        ha="center", va="bottom", fontsize=7.5)
        ax.axhline(100, ls=":", color="#9ca3af", lw=1)
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8.5)
        ax.set_ylim(0, 114); ax.set_ylabel("runs matching the reference (%)")
        ax.set_title(title, fontsize=11, loc="left", fontweight="bold")
        ax.grid(axis="y", ls=":", alpha=0.4); ax.spines[["top", "right"]].set_visible(False)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 0.99), ncol=2, frameon=False, fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(HERE / "results" / "fig_providers.png", dpi=200)
    print("\nWrote results/fig_providers.png and results/providers_summary.json")

if __name__ == "__main__":
    main()
