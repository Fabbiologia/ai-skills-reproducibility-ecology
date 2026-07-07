#!/usr/bin/env python3
"""Score the HARD report-reproducibility experiment (6 forky analyses).
Reads results_hard.json + references_hard.json. Reports per condition: skill
coherence (adherence), report reproducibility (per-question agreement + whole-report
match), validity vs reference, and where the divergence happens (method choices)."""
import json, statistics as st
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
recs = [r for r in json.loads((HERE / "results_hard.json").read_text()) if r.get("ok")]
REF = json.loads((HERE / "references_hard.json").read_text())
CONDS = ["C0", "C1", "C2"]
CLABEL = {"C0": "C0 no skill", "C1": "C1 structure", "C2": "C2 full skill"}

# question field -> (reference value, tolerance)
QSPEC = {
  "q1_k":       (REF["Q1_k"], 0.5),
  "q1_sil":     (REF["Q1_silhouette_k3"], 0.02),
  "q2_acc":     (REF["Q2_species_cv5_acc"], 0.01),
  "q3_adjr2":   (REF["Q3_bodymass_adjR2"], 0.02),
  "q4_ci_low":  (REF["Q4_flipper_ci_low"], 0.3),
  "q4_ci_high": (REF["Q4_flipper_ci_high"], 0.3),
  "q5_corr":    (REF["Q5_billLD_pooled_pearson"], 0.03),
  "q6_pc1_pct": (REF["Q6_pca_pc1_pct_scaled"], 1.5),
}
JITEMS = ["q1_kmeans_k3", "q2_cv5_logreg", "q3_ols_3morph", "q4_t_interval",
          "q5_pooled_pearson", "q6_pca_scaled", "structure_ok", "missing_listwise"]

by = defaultdict(list)
for r in recs:
    by[r["cond"]].append(r)

def agree(vals, tol):
    vals = [v for v in vals if v is not None]
    if not vals: return None, None, None
    uniq = []
    for v in sorted(vals):
        if not uniq or abs(v - uniq[-1]) > tol: uniq.append(v)
    mk = Counter(round(v / tol) for v in vals).most_common(1)[0][1]
    return mk / len(vals), len(uniq), (st.pstdev(vals) if len(vals) > 1 else 0.0)

def valid(vals, ref, tol):
    vals = [v for v in vals if v is not None]
    return (sum(1 for v in vals if abs(v - ref) <= tol) / len(vals)) if vals else None

def whole_match(records):
    keys = []
    for r in records:
        k = tuple(round((r.get(f) or 0) / tol) for f, (_, tol) in QSPEC.items())
        keys.append(k)
    return Counter(keys).most_common(1)[0][1] / len(keys)

print("=" * 96)
print("HARD REPORT: reproducibility, coherence, validity  (8 reports per condition)")
print("=" * 96)
summary = {}
for cond in CONDS:
    rs = by.get(cond, [])
    if not rs:
        print(f"\n{CLABEL[cond]}: none"); continue
    adh = st.mean([r["judge"]["adherence_score"] for r in rs if r.get("judge")])
    item_rates = {k: st.mean([1 if (r.get("judge") or {}).get(k) else 0 for r in rs]) for k in JITEMS}
    perq = {}
    for f, (ref, tol) in QSPEC.items():
        ex, dist, sd = agree([r.get(f) for r in rs], tol)
        perq[f] = dict(exact=ex, distinct=dist, sd=sd, valid=valid([r.get(f) for r in rs], ref, tol))
    wm = whole_match(rs)
    mean_valid = st.mean([perq[f]["valid"] for f in QSPEC if perq[f]["valid"] is not None])
    # where divergence happens: method choices
    k_choices = dict(Counter(r.get("q1_k") for r in rs))
    scaled_pca = dict(Counter(r.get("q6_scaled") for r in rs))
    scope5 = dict(Counter((r.get("q5_scope") or "?")[:14] for r in rs))
    summary[cond] = dict(n=len(rs), adherence=adh, item_rates=item_rates, perq=perq,
                         whole_match=wm, mean_valid=mean_valid,
                         q1_k=k_choices, q6_scaled=scaled_pca, q5_scope=scope5)
    print(f"\n### {CLABEL[cond]} (n={len(rs)})")
    print(f"  coherence (adherence) = {adh*100:.0f}%   whole-report match = {wm*100:.0f}%   validity = {mean_valid*100:.0f}%")
    print("  per-question agreement (exact%/distinct/valid%):")
    for f in QSPEC:
        pq = perq[f]
        print(f"     {f:11s} exact={(pq['exact'] or 0)*100:3.0f}%  distinct={pq['distinct']}  valid={(pq['valid'] or 0)*100:3.0f}%")
    print(f"  divergence: Q1 k-choices={k_choices}  Q6 scaled={scaled_pca}  Q5 scope={scope5}")

(HERE / "results" / "hard_summary.json").write_text(json.dumps(summary, indent=2, default=float))
print("\nWrote results/hard_summary.json")

# ---- figure ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
colors = {"C0": "#999999", "C1": "#e08214", "C2": "#2166ac"}
fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5.2))
# left: 3 summary metrics
mets = [("Skill coherence", "adherence"), ("Report match\n(all numbers agree)", "whole_match"), ("Validity", "mean_valid")]
x = np.arange(len(mets)); w = 0.25
for i, cond in enumerate(CONDS):
    s = summary.get(cond);
    if not s: continue
    vals = [(s["adherence"] or 0), s["whole_match"], (s["mean_valid"] or 0)]
    bars = axL.bar(x + (i - 1) * w, [v * 100 for v in vals], w, label=CLABEL[cond], color=colors[cond])
    for b, v in zip(bars, vals):
        axL.text(b.get_x() + b.get_width() / 2, v * 100 + 1, f"{v*100:.0f}", ha="center", va="bottom", fontsize=8)
axL.set_xticks(x); axL.set_xticklabels([m[0] for m in mets]); axL.set_ylabel("percent"); axL.set_ylim(0, 108)
axL.set_title("Summary metrics by condition", fontsize=11); axL.legend(fontsize=8); axL.grid(axis="y", ls=":", alpha=0.4)
# right: per-question report agreement (exact-match) by condition
QN = list(QSPEC.keys()); xq = np.arange(len(QN))
for i, cond in enumerate(CONDS):
    s = summary.get(cond)
    if not s: continue
    ys = [(s["perq"][f]["exact"] or 0) * 100 for f in QN]
    axR.bar(xq + (i - 1) * w, ys, w, label=CLABEL[cond], color=colors[cond])
axR.set_xticks(xq); axR.set_xticklabels([q.replace("_", "\n") for q in QN], fontsize=7)
axR.set_ylabel("run-to-run agreement (%)"); axR.set_ylim(0, 108)
axR.set_title("Per-analysis agreement across runs\n(low = reports diverge without the skill)", fontsize=11)
axR.legend(fontsize=8); axR.grid(axis="y", ls=":", alpha=0.4)
fig.suptitle("HARD report: does the skill make a forky report reproducible and coherent?",
             fontsize=13, fontweight="bold")
fig.tight_layout(); fig.savefig(HERE / "results" / "fig_hard_report.png", dpi=150)
print("Wrote results/fig_hard_report.png")
