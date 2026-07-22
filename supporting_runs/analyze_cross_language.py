#!/usr/bin/env python3
"""Cross-language analysis: Python vs R.
Reads results_v2.json (Python) + results_v2_R.json (R) and the two reference files,
then reports (a) within-language reproducibility and validity per cell, and
(b) cross-language output equivalence (do Python and R agree within tolerance?).
Writes a combined table, a cross-language summary, and figures."""
import json, statistics as st
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
PY = json.loads((HERE / "results_v2.json").read_text())
RR = json.loads((HERE / "results_v2_R.json").read_text())
REF = {"python": json.loads((HERE / "data" / "references.json").read_text()),
       "r":      json.loads((HERE / "data" / "references_R.json").read_text())}
DATA = {"python": PY, "r": RR}

CONDS = ["C0", "C1", "C2", "C3", "C4"]
TASKS = ["T1", "T2", "T3", "T4"]
TNAME = {"T1": "iris correlation", "T2": "penguin sex classifier",
         "T3": "penguin mass ANOVA", "T4": "LTEM reef-fish biomass"}
TOL = {"T1": 1e-3, "T2": 1e-3, "T3": 1e-3, "T4": 1e-2}

def cells(runs):
    d = defaultdict(list)
    for r in runs:
        if r.get("value") is not None:
            d[(r["task"], r["condition"])].append(float(r["value"]))
    return d

def tolerance_clusters(vals, tol):
    clusters = []
    for value in sorted(vals):
        if not clusters or value - clusters[-1][0] > tol:
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return clusters


def modal(vals, tol):
    cluster = max(tolerance_clusters(vals, tol), key=len)
    return st.mean(cluster)

def summarize(vals, ref, tol):
    sd = st.pstdev(vals) if len(vals) > 1 else 0.0
    clusters = tolerance_clusters(vals, tol)
    mk = max(map(len, clusters))
    valid = sum(1 for v in vals if abs(v - ref) <= tol) / len(vals)
    return dict(n=len(vals), sd=sd, n_distinct=len(clusters), agreement=mk / len(vals),
                valid=valid, mean=st.mean(vals), modal=modal(vals, tol))

PYc, RRc = cells(PY), cells(RR)

print("=" * 92)
print("WITHIN-LANGUAGE REPRODUCIBILITY AND VALIDITY")
print("=" * 92)
summary = {}
for lang, C in [("python", PYc), ("r", RRc)]:
    print(f"\n--- {lang.upper()} ---")
    for t in TASKS:
        row = []
        for c in CONDS:
            vs = C.get((t, c), [])
            if not vs:
                row.append(f"{c}:--"); continue
            s = summarize(vs, REF[lang][t]["value"], TOL[t])
            summary[f"{lang}_{t}_{c}"] = s
            row.append(f"{c}:SD={s['sd']:.3f},agree={s['agreement']*100:.0f}%,valid={s['valid']*100:.0f}%")
        print(f"  {t} {TNAME[t]:<26} " + " | ".join(row))

print("\n" + "=" * 92)
print("CROSS-IMPLEMENTATION COMPARISON (Python modal vs R modal, within tolerance)")
print("=" * 92)
xlang = {}
for t in TASKS:
    print(f"\n{t} {TNAME[t]} (tol {TOL[t]}):")
    for c in CONDS:
        pv = PYc.get((t, c)); rv = RRc.get((t, c))
        if not pv or not rv:
            print(f"  {c}: missing"); continue
        pm = modal(pv, TOL[t]); rm = modal(rv, TOL[t])
        agree = abs(pm - rm) <= TOL[t]
        xlang[f"{t}_{c}"] = dict(py=pm, r=rm, diff=abs(pm - rm), agree=bool(agree))
        print(f"  {c}: Python={pm:.4f}  R={rm:.4f}  |diff|={abs(pm-rm):.4f}  same output={'YES' if agree else 'no'}")

(HERE / "results" / "cross_language_summary.json").write_text(
    json.dumps({"within": summary, "cross": xlang,
                "refs": REF}, indent=2, default=float))
print("\nWrote results/cross_language_summary.json")

# ---- figure: Python vs R value strips per task ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
YLIM = {"T1": (-0.14, -0.09), "T2": (0.84, 0.96), "T3": (0.60, 0.74), "T4": (3.15, 3.55)}
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, t in zip(axes.ravel(), TASKS):
    for j, c in enumerate(CONDS):
        for lang, C, off, col in [("Python", PYc, -0.13, "#2166ac"), ("R", RRc, 0.13, "#b2182b")]:
            vs = C.get((t, c), [])
            xs = np.random.default_rng(j).normal(j + off, 0.03, len(vs)) if vs else []
            ax.scatter(xs, vs, s=42, alpha=0.6, color=col, edgecolor="white", lw=0.4,
                       label=lang if (j == 0) else None, zorder=3)
    ax.axhline(REF["python"][t]["value"], ls="--", lw=1, color="#2166ac", alpha=0.8)
    if abs(REF["r"][t]["value"] - REF["python"][t]["value"]) > TOL[t]:
        ax.axhline(REF["r"][t]["value"], ls="--", lw=1, color="#b2182b", alpha=0.8)
    ax.set_ylim(*YLIM[t])
    ax.set_xticks(range(5)); ax.set_xticklabels(CONDS)
    ax.set_title(f"{t}  {TNAME[t]}", fontsize=10)
    ax.grid(axis="y", ls=":", alpha=0.4); ax.legend(fontsize=8, loc="best")
fig.tight_layout(); fig.savefig(HERE / "results" / "fig4_python_vs_r.png", dpi=150)
print("Wrote results/fig4_python_vs_r.png")

# Main-text Figure 2: descriptive replication of the task-specific binding
# transitions. Pooling is weighted by the number of runs in each cell.
def pooled_rate(lang, task, conditions, key):
    total = sum(summary[f"{lang}_{task}_{c}"]["n"] for c in conditions)
    successes = sum(round(summary[f"{lang}_{task}_{c}"][key]
                          * summary[f"{lang}_{task}_{c}"]["n"])
                    for c in conditions)
    return 100 * successes / total


from matplotlib.lines import Line2D
fig2, axes2 = plt.subplots(1, 2, figsize=(10.8, 4.7), sharex=True, sharey=True)
transition_specs = [
    ("T2", ["C0", "C1", "C2"], ["C3", "C4"],
     "A  Classifier: controls bind the choice", "C0-C2", "C3-C4"),
    ("T4", ["C0", "C1"], ["C2", "C3", "C4"],
     "B  Biomass: contract binds the choice", "C0-C1", "C2-C4"),
]
rows = [("agreement", "Agreement · Python", "python"),
        ("agreement", "Agreement · R", "r"),
        ("valid", "Validity · Python", "python"),
        ("valid", "Validity · R", "r")]
ypos = np.arange(len(rows))[::-1]
for ax, (task, preconds, postconds, title, prelab, postlab) in zip(axes2, transition_specs):
    for y, (key, label, lang) in zip(ypos, rows):
        pre = pooled_rate(lang, task, preconds, key)
        post = pooled_rate(lang, task, postconds, key)
        ax.plot([pre, post], [y, y], color="#9ca3af", lw=2, zorder=1)
        ax.scatter(pre, y, s=72, facecolor="white", edgecolor="#6b7280",
                   linewidth=1.8, zorder=3)
        ax.scatter(post, y, s=52, marker="D", color="#0072B2", zorder=4)
        label_dy = -0.30 if y == ypos[0] else 0.23
        if abs(pre - post) < 0.5:
            ax.text(pre - 2.5, y + label_dy, f"{pre:.0f}→{post:.0f}",
                    ha="right", va="center", fontsize=8.5)
        else:
            ax.text(pre, y + label_dy, f"{pre:.0f}", ha="center", va="center", fontsize=8.5)
            ax.text(post, y + label_dy, f"{post:.0f}", ha="center", va="center", fontsize=8.5)
    ax.axhline(1.5, color="#d1d5db", lw=1)
    ax.set_title(title, fontsize=10.5, loc="left", fontweight="bold")
    ax.set_xlim(-8, 109); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Pooled run-level rate (%)")
    ax.grid(axis="x", color="#e5e7eb", lw=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
axes2[0].set_yticks(ypos); axes2[0].set_yticklabels([r[1] for r in rows], fontsize=9)
axes2[1].tick_params(labelleft=False)
legend_handles = [
    Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
           markeredgecolor="#6b7280", markeredgewidth=1.8, markersize=7, label="Before binding constraint"),
    Line2D([0], [0], marker="D", color="none", markerfacecolor="#0072B2",
           markeredgecolor="#0072B2", markersize=6, label="After binding constraint"),
]
fig2.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, 0.99),
            ncol=2, frameon=False, fontsize=9)
fig2.tight_layout(rect=[0, 0.02, 1, 0.92])
fig2.savefig(HERE / "results" / "fig2_binding_replication.png", dpi=200,
             bbox_inches="tight")
print("Wrote results/fig2_binding_replication.png")
