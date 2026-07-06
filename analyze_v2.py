#!/usr/bin/env python3
"""Score output reproducibility for the 4-task x 5-rung-ablation experiment.
Reads results_v2.json + data/references.json; writes summary table, stats, figures."""
import json, math, statistics as st
from collections import Counter, defaultdict
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
CATKEY = {"T1":"direction", "T2":"method", "T3":"method", "T4":"method"}

cells = defaultdict(list)
for r in runs:
    if r.get("value") is None:      # failed run
        continue
    cells[(r["task"], r["condition"])].append(r)

def cell_stats(task, rs):
    vals = [float(r["value"]) for r in rs]
    ref = REF[task]["value"]
    tol = TOL[task]
    # cluster values within tolerance -> count distinct answers
    uniq = []
    for v in sorted(vals):
        if not uniq or abs(v - uniq[-1]) > tol:
            uniq.append(v)
    modal_cluster = Counter(round(v/tol) for v in vals).most_common(1)[0][1]
    cat = [str(r.get(CATKEY[task])) for r in rs]
    cat_mode_n = Counter(cat).most_common(1)[0][1]
    sd = st.pstdev(vals) if len(vals) > 1 else 0.0
    mean = st.mean(vals)
    cv = (sd/abs(mean)) if mean else 0.0
    valid = sum(1 for v in vals if abs(v-ref) <= tol) / len(vals)
    return {
        "n":len(vals), "mean":mean, "sd":sd, "cv":cv,
        "range":max(vals)-min(vals), "n_distinct":len(uniq),
        "exact_match_rate":modal_cluster/len(vals),
        "cat_agreement":cat_mode_n/len(vals),
        "cat_dist":dict(Counter(cat)),
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
          f"{'exact%':>8} {'catAgree%':>10} {'valid%':>8} {'|Δref|':>9}")
    for cond in CONDS:
        rs = cells.get((task,cond), [])
        if not rs:
            print(f"  {CLABEL[cond]:<12}  (no successful runs)"); continue
        s = cell_stats(task, rs)
        summary[f"{task}_{cond}"] = {k:v for k,v in s.items() if k!="vals"}
        print(f"  {CLABEL[cond]:<12}{s['n']:>3} {s['sd']:>9.4f} {s['cv']:>8.3f} "
              f"{s['range']:>9.4f} {s['n_distinct']:>10} {s['exact_match_rate']*100:>7.0f}% "
              f"{s['cat_agreement']*100:>9.0f}% {s['validity_rate']*100:>7.0f}% {s['abs_err_ref']:>9.4f}")

# ---- inferential: Levene (Brown-Forsythe, median-centered) across conditions per task ----
print("\n" + "="*100)
print("VARIANCE HOMOGENEITY ACROSS CONDITIONS (Brown-Forsythe Levene, per task)")
print("="*100)
stat_rows = {}
for task in TASKS:
    groups = [ [float(r["value"]) for r in cells.get((task,c),[])] for c in CONDS ]
    groups = [g for g in groups if len(g) >= 2 and (max(g)-min(g))>0]
    if len(groups) >= 2:
        try:
            W, p = stats.levene(*groups, center="median")
            print(f"  {task} {TNAME[task]:<34} Levene W={W:.3f}, p={p:.2e}  "
                  f"(conditions differ in variance: {'YES' if p<0.05 else 'no'})")
            stat_rows[task] = {"levene_W":W, "levene_p":p}
        except Exception as e:
            print(f"  {task}: Levene failed ({e})")
            stat_rows[task] = {"levene_W":None,"levene_p":None}
    else:
        print(f"  {task} {TNAME[task]:<34} all values identical in >=4 conditions — "
              f"variance ~0 (skill removes essentially all run-to-run variation)")
        stat_rows[task] = {"levene_W":None,"levene_p":None,"note":"near-zero variance"}

(HERE/"results"/"summary_v2.json").write_text(json.dumps(
    {"cells":summary,"levene":stat_rows,"references":REF}, indent=2, default=float))
print("\nWrote results/summary_v2.json")

# ---- FIGURES ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
CCOL = {"C0":"#999999","C1":"#e08214","C2":"#7fbf7b","C3":"#4393c3","C4":"#2166ac"}

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
fig.suptitle("Output values by skill-richness (ablation) — 10 independent runs per cell",
             fontsize=12, fontweight="bold")
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
fig2.suptitle("Do richer skills reduce run-to-run variability? (lower = more reproducible)",
              fontsize=12, fontweight="bold")
fig2.tight_layout(); fig2.savefig(HERE/"results"/"fig2_reproducibility_gradient.png", dpi=150)

# Fig 3: heatmaps of exact-match rate and validity rate
fig3, (h1, h2) = plt.subplots(1, 2, figsize=(12, 4.2))
for ax, key, ttl in [(h1,"exact_match_rate","Exact-match rate (run-to-run agreement)"),
                     (h2,"validity_rate","Validity rate (agreement with reference)")]:
    M = np.array([[summary.get(f"{t}_{c}",{}).get(key, np.nan) for c in CONDS] for t in TASKS])
    im = ax.imshow(M, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(5)); ax.set_xticklabels([CLABEL[c] for c in CONDS], rotation=20, fontsize=8)
    ax.set_yticks(range(4)); ax.set_yticklabels(TASKS)
    for i in range(4):
        for j in range(5):
            v=M[i,j]
            if not np.isnan(v): ax.text(j,i,f"{v*100:.0f}",ha="center",va="center",fontsize=9)
    ax.set_title(ttl, fontsize=10); fig3.colorbar(im, ax=ax, fraction=0.046)
fig3.tight_layout(); fig3.savefig(HERE/"results"/"fig3_heatmaps.png", dpi=150)

# summary CSV
import csv
with open(HERE/"results"/"summary_v2.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["task","condition","n","mean","sd","cv","range","n_distinct",
        "exact_match_rate","cat_agreement","validity_rate","abs_err_ref"])
    for task in TASKS:
        for cond in CONDS:
            s=summary.get(f"{task}_{cond}")
            if s: w.writerow([task,cond,s["n"],f"{s['mean']:.5f}",f"{s['sd']:.5f}",f"{s['cv']:.4f}",
                f"{s['range']:.5f}",s["n_distinct"],f"{s['exact_match_rate']:.3f}",
                f"{s['cat_agreement']:.3f}",f"{s['validity_rate']:.3f}",f"{s['abs_err_ref']:.5f}"])
print("Wrote results/fig1_value_strips.png, fig2_reproducibility_gradient.png, fig3_heatmaps.png, summary_v2.csv")
