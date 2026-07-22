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
    # Weight the six scientific questions equally. Q1 and Q4 each have two
    # numeric fields and pass only when both fields match their references.
    question_validity = {
        "Q1": st.mean([1 if (abs(r["q1_k"] - QSPEC["q1_k"][0]) <= QSPEC["q1_k"][1]
                                  and abs(r["q1_sil"] - QSPEC["q1_sil"][0]) <= QSPEC["q1_sil"][1]) else 0
                           for r in rs]),
        "Q2": perq["q2_acc"]["valid"],
        "Q3": perq["q3_adjr2"]["valid"],
        "Q4": st.mean([1 if (abs(r["q4_ci_low"] - QSPEC["q4_ci_low"][0]) <= QSPEC["q4_ci_low"][1]
                                  and abs(r["q4_ci_high"] - QSPEC["q4_ci_high"][0]) <= QSPEC["q4_ci_high"][1]) else 0
                           for r in rs]),
        "Q5": perq["q5_corr"]["valid"],
        "Q6": perq["q6_pc1_pct"]["valid"],
    }
    mean_valid = st.mean(question_validity.values())
    # where divergence happens: method choices
    k_choices = dict(Counter(r.get("q1_k") for r in rs))
    scaled_pca = dict(Counter(r.get("q6_scaled") for r in rs))
    scope5 = dict(Counter((r.get("q5_scope") or "?")[:14] for r in rs))
    summary[cond] = dict(n=len(rs), adherence=adh, item_rates=item_rates, perq=perq,
                         whole_match=wm, mean_valid=mean_valid,
                         question_validity=question_validity,
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

# ---- figure: A standard report, B hard report, C where the hard report forked ----
# Restructured per reviewer request into three panels with a colour-blind-safe
# (Okabe-Ito) palette and named analyses rather than q-codes.
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OK = {"C0": "#999999", "C1": "#E69F00", "C2": "#0072B2"}
CLAB = {"C0": "No skill", "C1": "Structure only", "C2": "Full skill"}

# The standard-report summary is produced separately by analyze_report.py.
std_path = HERE / "results" / "report_summary.json"
std = json.loads(std_path.read_text()) if std_path.exists() else {}

mets = ["Skill\ncoherence", "Whole-report\nagreement", "Validity"]
xm = np.arange(len(mets)); w = 0.26

def panel_bars(ax, summ, keys, title):
    for i, cond in enumerate(CONDS):
        s = summ.get(cond)
        if not s: continue
        ys = [(s.get(keys[0]) or 0) * 100, (s.get(keys[1]) or 0) * 100, (s.get(keys[2]) or 0) * 100]
        bars = ax.bar(xm + (i - 1) * w, ys, w, label=CLAB[cond], color=OK[cond])
        for b, v in zip(bars, ys):
            ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(xm); ax.set_xticklabels(mets, fontsize=9); ax.set_ylim(0, 112)
    ax.set_title(title, fontsize=11, loc="left", fontweight="bold")
    ax.grid(axis="y", ls=":", alpha=0.4)

fig, axes = plt.subplots(1, 3, figsize=(15.6, 4.8),
                         gridspec_kw={"width_ratios": [1.1, 1.1, 0.9]})
panel_bars(axes[0], std, ("adherence", "report_match", "mean_valid"), "A  Standard report (four analyses)")
axes[0].set_ylabel("percent")
panel_bars(axes[1], summary, ("adherence", "whole_match", "mean_valid"), "B  Hard report (six analyses with forks)")

# Panel C: the only two numeric fields that diverged, named.
axC = axes[2]
QN = ["q2_acc", "q3_adjr2"]
QNLABEL = {"q2_acc": "Species\naccuracy", "q3_adjr2": "Body-mass\nmodel R²"}
xq = np.arange(len(QN))
for i, cond in enumerate(CONDS):
    s = summary.get(cond)
    if not s: continue
    ys = [(s["perq"][f]["exact"] or 0) * 100 for f in QN]
    bars = axC.bar(xq + (i - 1) * w, ys, w, label=CLAB[cond], color=OK[cond])
    for b, v in zip(bars, ys):
        axC.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}", ha="center", va="bottom", fontsize=8)
axC.set_xticks(xq); axC.set_xticklabels([QNLABEL[q] for q in QN], fontsize=9)
axC.set_ylabel("modal agreement across reports (%)"); axC.set_ylim(0, 112)
axC.set_title("C  Where the hard report forked", fontsize=11, loc="left", fontweight="bold")
axC.grid(axis="y", ls=":", alpha=0.4)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.99), ncol=3, frameon=False, fontsize=9.5)
fig.tight_layout(rect=[0, 0.02, 1, 0.92])
fig.savefig(HERE / "results" / "fig_hard_report.png", dpi=200, bbox_inches="tight")
print("Wrote results/fig_hard_report.png")
