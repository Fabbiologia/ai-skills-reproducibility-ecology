#!/usr/bin/env python3
"""Score output reproducibility for the 4-task x 5-rung ablation experiment.

The analysis is intentionally descriptive at the task level.  The experiment was
not preregistered and contains only four tasks, so the two Fisher tests reported
in the manuscript are labelled exploratory contrasts rather than population-wide
inference about ecological analyses.
"""
import json, statistics as st
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).parent
runs = json.loads((HERE / "results_v2.json").read_text())
REF = json.loads((HERE / "data" / "references.json").read_text())  # {task: {value, ...}}

CONDS = ["C0", "C1", "C2", "C3", "C4"]
CLABEL = {"C0":"C0 none","C1":"C1 basic","C2":"C2 contract","C3":"C3 +controls","C4":"C4 full"}
TASKS = ["T1", "T2", "T3", "T4"]
TNAME = {"T1":"iris correlation","T2":"penguins sex classifier",
         "T3":"penguins mass ANOVA (eta^2)","T4":"LTEM reef-fish biomass"}
# task categorical key + numeric tolerance for "same answer within tolerance"
TOL = {"T1":1e-3, "T2":1e-3, "T3":1e-3, "T4":1e-2}   # T4 biomass abs tol (units ~g/m2)

cells = defaultdict(list)
for r in runs:
    if r.get("value") is None:      # failed run
        continue
    cells[(r["task"], r["condition"])].append(r)

def tolerance_clusters(vals, tol):
    """Return deterministic complete-linkage clusters whose span is <= tol."""
    clusters = []
    for value in sorted(vals):
        if not clusters or value - clusters[-1][0] > tol:
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return clusters


def cell_stats(task, rs):
    vals = [float(r["value"]) for r in rs]
    ref = REF[task]["value"]
    tol = TOL[task]
    clusters = tolerance_clusters(vals, tol)
    modal_cluster = max(map(len, clusters))
    sd = st.pstdev(vals) if len(vals) > 1 else 0.0
    mean = st.mean(vals)
    cv = (sd/abs(mean)) if mean else 0.0
    valid = sum(1 for v in vals if abs(v-ref) <= tol) / len(vals)
    return {
        "n":len(vals), "mean":mean, "sd":sd, "cv":cv,
        "range":max(vals)-min(vals), "n_distinct":len(clusters),
        "modal_agreement_rate":modal_cluster/len(vals),
        "abs_err_ref":abs(mean-ref), "validity_rate":valid,
        "vals":vals,
    }

summary = {}
print("="*100)
print("OUTPUT REPRODUCIBILITY — 4 tasks x 5-rung ablation")
print("="*100)
for task in TASKS:
    print(f"\n### {task}  {TNAME[task]}   (reference value = {REF[task]['value']})")
    print(f"  {'cond':<12}{'n':>3} {'SD':>9} {'CV':>8} {'range':>9} {'#distinct':>10} "
          f"{'agree%':>8} {'valid%':>8} {'|Δref|':>9}")
    for cond in CONDS:
        rs = cells.get((task,cond), [])
        if not rs:
            print(f"  {CLABEL[cond]:<12}  (no successful runs)"); continue
        s = cell_stats(task, rs)
        summary[f"{task}_{cond}"] = {k:v for k,v in s.items() if k!="vals"}
        print(f"  {CLABEL[cond]:<12}{s['n']:>3} {s['sd']:>9.4f} {s['cv']:>8.3f} "
              f"{s['range']:>9.4f} {s['n_distinct']:>10} {s['modal_agreement_rate']*100:>7.0f}% "
              f"{s['validity_rate']*100:>7.0f}% {s['abs_err_ref']:>9.4f}")

def fisher_contrast(success_a, total_a, success_b, total_b):
    table = [[success_a, total_a - success_a], [success_b, total_b - success_b]]
    odds_ratio, p = stats.fisher_exact(table, alternative="two-sided")
    return {"group_a": [success_a, total_a], "group_b": [success_b, total_b],
            "odds_ratio": float(odds_ratio), "p_two_sided": float(p)}


# Exploratory contrasts selected to describe the two visible transition points.
exploratory = {
    "T2_modal_agreement_python_low_C0_C2_vs_high_C3_C4": fisher_contrast(16, 30, 20, 20),
    "T2_validity_python_low_C0_C2_vs_high_C3_C4": fisher_contrast(12, 30, 20, 20),
    "T4_validity_python_precontract_C0_C1_vs_contract_C2_C4": fisher_contrast(0, 20, 30, 30),
}

(HERE/"results"/"summary_v2.json").write_text(json.dumps(
    {"cells":summary, "exploratory_contrasts":exploratory, "references":REF},
    indent=2, default=float))
print("\nWrote results/summary_v2.json")

# ---- FIGURES ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
# Colour-blind-safe palettes. Condition colours are sampled from cividis, a
# sequential map designed to be legible under the common forms of colour vision
# deficiency; the two outcome series use Okabe-Ito qualitative colours.
_civ = plt.get_cmap("cividis")
CCOL = {c: to_hex(_civ(x)) for c, x in zip(CONDS, [0.05, 0.30, 0.52, 0.74, 0.96])}
OK_BLUE, OK_ORANGE, OK_GREEN = "#0072B2", "#D55E00", "#009E73"

# Fig 1: per-task value strips
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, task in zip(axes.ravel(), TASKS):
    for j,cond in enumerate(CONDS):
        ys = [float(r["value"]) for r in cells.get((task,cond),[])]
        xs = np.random.default_rng(j).normal(j, 0.05, len(ys)) if ys else []
        ax.scatter(xs, ys, s=55, alpha=0.6, color=CCOL[cond], edgecolor="white", lw=0.5, zorder=3)
    ax.axhline(REF[task]["value"], ls="--", lw=1, color="crimson", zorder=1,
               label=f"reference {REF[task]['value']:.4g}")
    ax.set_xticks(range(5)); ax.set_xticklabels([CLABEL[c] for c in CONDS], rotation=20, fontsize=8)
    ax.set_title(f"{task} — {TNAME[task]}", fontsize=10)
    ax.grid(axis="y", ls=":", alpha=0.4); ax.legend(fontsize=7, loc="best")
fig.tight_layout(); fig.savefig(HERE/"results"/"fig1_value_strips.png", dpi=150)

# Fig 2: reproducibility gradient — CV (or SD) by condition, one line per task
fig2, (axL, axR) = plt.subplots(1, 2, figsize=(12, 4.6))
for task in TASKS:
    sds = [summary.get(f"{task}_{c}",{}).get("sd", np.nan) for c in CONDS]
    cvs = [summary.get(f"{task}_{c}",{}).get("cv", np.nan) for c in CONDS]
    axL.plot(range(5), sds, "o-", label=task)
    axR.plot(range(5), cvs, "o-", label=task)
for ax, ttl, yl in [(axL,"Run-to-run SD by condition","SD of output"),
                    (axR,"Coefficient of variation by condition","CV")]:
    ax.set_xticks(range(5)); ax.set_xticklabels([CLABEL[c] for c in CONDS], rotation=20, fontsize=8)
    ax.set_title(ttl, fontsize=11); ax.set_ylabel(yl); ax.grid(ls=":", alpha=0.4); ax.legend(fontsize=8)
fig2.tight_layout(); fig2.savefig(HERE/"results"/"fig2_reproducibility_gradient.png", dpi=150)

# Main-text Figure 1: three panels. A and B show the two non-ceiling tasks as
# agreement versus validity by skill level. Panel C plots the T4 output values
# themselves, so that "perfectly reproducible and still wrong" is visible as a
# tight cluster sitting on the wrong number until the contract moves it onto the
# reference (added in response to reviewer comment; colour-blind-safe palette).
MAIN_LABEL = {
    "C0": "C0\nnone", "C1": "C1\nbasic", "C2": "C2\ncontract",
    "C3": "C3\ncontrols", "C4": "C4\nfull",
}
from matplotlib.lines import Line2D
fig_main1, axes_main1 = plt.subplots(1, 3, figsize=(15.2, 4.7))
x = np.arange(len(CONDS), dtype=float)
line_specs = [
    (axes_main1[0], "T2", 3, "A  Stochastic classifier (T2)", "C3 fixes split, seed\nand preprocessing"),
    (axes_main1[1], "T4", 2, "B  Reef-fish biomass (T4)", "C2 defines the\nsurvey unit"),
]
for ax, task, binding, title, annotation in line_specs:
    agreement = np.array([summary[f"{task}_{c}"]["modal_agreement_rate"] * 100 for c in CONDS])
    validity = np.array([summary[f"{task}_{c}"]["validity_rate"] * 100 for c in CONDS])
    ax.axvspan(binding - 0.5, 4.5, color="#dbe9f6", alpha=0.55, zorder=0)
    ax.axvline(binding - 0.5, color="#6b7280", lw=1, ls="--", zorder=1)
    ax.plot(x - 0.035, agreement, color=OK_BLUE, marker="o", ms=7,
            markerfacecolor="white", markeredgewidth=1.8, lw=2.2,
            label="Modal agreement", zorder=3)
    ax.plot(x + 0.035, validity, color=OK_ORANGE, marker="s", ms=6.5,
            lw=2.2, label="Reference validity", zorder=4)
    ax.annotate(annotation, xy=(binding, 103), xytext=(binding, 116),
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color="#4b5563", lw=1))
    ax.set_xticks(x); ax.set_xticklabels([MAIN_LABEL[c] for c in CONDS], fontsize=8)
    ax.set_xlim(-0.45, 4.45); ax.set_ylim(-5, 126)
    ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(["0", "25", "50", "75", "100"])
    ax.set_title(title, fontsize=11, loc="left", fontweight="bold")
    ax.grid(axis="y", color="#d1d5db", lw=0.8, alpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
axes_main1[0].set_ylabel("Runs in modal cluster / matching reference (%)")

# Panel C: the actual T4 values, coloured by validity.
axC = axes_main1[2]
ref_T4 = REF["T4"]["value"]
c0_vals = [float(r["value"]) for r in cells.get(("T4", "C0"), [])]
wrong_val = float(np.mean(c0_vals)) if c0_vals else 3.2952
for j, cond in enumerate(CONDS):
    vals = [float(r["value"]) for r in cells.get(("T4", cond), [])]
    ok = [abs(v - ref_T4) <= TOL["T4"] for v in vals]
    xs = np.random.default_rng(7 + j).normal(j, 0.06, len(vals))
    axC.scatter([xj for xj, k in zip(xs, ok) if not k], [v for v, k in zip(vals, ok) if not k],
                s=48, color=OK_ORANGE, edgecolor="white", lw=0.6, zorder=3)
    axC.scatter([xj for xj, k in zip(xs, ok) if k], [v for v, k in zip(vals, ok) if k],
                s=48, color=OK_GREEN, edgecolor="white", lw=0.6, zorder=3)
axC.axhline(ref_T4, ls="--", lw=1.4, color=OK_GREEN, zorder=1)
axC.axhline(wrong_val, ls=":", lw=1.5, color=OK_ORANGE, zorder=1)
axC.text(4.45, ref_T4, f"reference {ref_T4:.3f} ", va="bottom", ha="right", fontsize=8, color=OK_GREEN)
axC.text(-0.4, wrong_val, f" reproducible but wrong {wrong_val:.3f}", va="top", ha="left", fontsize=8, color=OK_ORANGE)
axC.axvspan(1.5, 4.5, color="#dbe9f6", alpha=0.55, zorder=0)
axC.axvline(1.5, color="#6b7280", lw=1, ls="--", zorder=1)
axC.set_xticks(x); axC.set_xticklabels([MAIN_LABEL[c] for c in CONDS], fontsize=8)
axC.set_xlim(-0.45, 4.45)
axC.set_title("C  Same task, the actual values (T4)", fontsize=11, loc="left", fontweight="bold")
axC.set_ylabel("Mean per-transect biomass")
axC.grid(axis="y", color="#d1d5db", lw=0.8, alpha=0.8)
axC.spines[["top", "right"]].set_visible(False)

handles, labels = axes_main1[0].get_legend_handles_labels()
handles += [Line2D([0], [0], marker="o", color="w", markerfacecolor=OK_GREEN, markersize=8),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=OK_ORANGE, markersize=8)]
labels += ["Valid run (matches reference)", "Invalid run (reproducible but wrong)"]
fig_main1.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.99),
                 ncol=4, frameon=False, fontsize=8.5)
fig_main1.tight_layout(rect=[0, 0, 1, 0.92])
fig_main1.savefig(HERE/"results"/"fig1_binding_transitions.png", dpi=200)

# Fig 3: heatmaps of modal agreement within tolerance and validity rate
fig3, (h1, h2) = plt.subplots(1, 2, figsize=(12, 4.2))
for ax, key, ttl in [(h1,"modal_agreement_rate","Modal agreement within tolerance"),
                     (h2,"validity_rate","Validity rate (agreement with reference)")]:
    M = np.array([[summary.get(f"{t}_{c}",{}).get(key, np.nan) for c in CONDS] for t in TASKS])
    im = ax.imshow(M, cmap="cividis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(5)); ax.set_xticklabels([CLABEL[c] for c in CONDS], rotation=20, fontsize=8)
    ax.set_yticks(range(4)); ax.set_yticklabels(TASKS)
    for i in range(4):
        for j in range(5):
            v=M[i,j]
            if not np.isnan(v):
                ax.text(j,i,f"{v*100:.0f}",ha="center",va="center",fontsize=9,
                        color=("white" if v < 0.55 else "black"))
    ax.set_title(ttl, fontsize=10); fig3.colorbar(im, ax=ax, fraction=0.046)
fig3.tight_layout(); fig3.savefig(HERE/"results"/"fig3_heatmaps.png", dpi=150)

# summary CSV
import csv
with open(HERE/"results"/"summary_v2.csv","w",newline="") as f:
    w=csv.writer(f, lineterminator="\n"); w.writerow(["task","condition","n","mean","sd","cv","range","n_distinct",
        "modal_agreement_rate","validity_rate","abs_err_ref"])
    for task in TASKS:
        for cond in CONDS:
            s=summary.get(f"{task}_{cond}")
            if s: w.writerow([task,cond,s["n"],f"{s['mean']:.5f}",f"{s['sd']:.5f}",f"{s['cv']:.4f}",
                f"{s['range']:.5f}",s["n_distinct"],f"{s['modal_agreement_rate']:.3f}",
                f"{s['validity_rate']:.3f}",f"{s['abs_err_ref']:.5f}"])
print("Wrote results/fig1_binding_transitions.png and diagnostic Figures S2/S4")
print("Wrote results/fig1_value_strips.png, fig2_reproducibility_gradient.png, fig3_heatmaps.png, summary_v2.csv")
