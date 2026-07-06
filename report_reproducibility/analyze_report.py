#!/usr/bin/env python3
"""Score the report-reproducibility experiment.
Reads results_report.json (per-report records with the generator's numbers and the
judge's rubric grades) and references_report.json. Reports, per condition:
  (A) skill coherence  : how often the report used the skill-specified statistics
  (B) report reproducibility : do independent reports agree on the numbers
  (C) conclusion agreement   : do the reports state the same key claims
  (D) validity               : do the numbers match the canonical references
Writes a summary and a figure."""
import json, statistics as st
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
recs = [r for r in json.loads((HERE / "results_report.json").read_text()) if r.get("ok")]
REF = json.loads((HERE / "references_report.json").read_text())
CONDS = ["C0", "C1", "C2"]
CLABEL = {"C0": "C0 no skill", "C1": "C1 structure", "C2": "C2 full skill"}
# numeric tolerances
TOL = {"q1_r": 0.01, "q2_effect": 0.01, "q3_accuracy": 0.01}
REFVAL = {"q1_r": REF["Q1_flipper_mass_pearson"], "q2_effect": REF["Q2_eta2"], "q3_accuracy": REF["Q3_sex_accuracy"]}
SPECIES = list(REF["Q4_species_mean_mass"].keys())

by = defaultdict(list)
for r in recs:
    by[r["cond"]].append(r)

def num_repro(vals, tol):
    vals = [v for v in vals if v is not None]
    if not vals: return dict(n=0, sd=None, exact=None, distinct=None)
    uniq = []
    for v in sorted(vals):
        if not uniq or abs(v - uniq[-1]) > tol: uniq.append(v)
    mk = Counter(round(v / tol) for v in vals).most_common(1)[0][1]
    return dict(n=len(vals), sd=st.pstdev(vals) if len(vals) > 1 else 0.0,
                exact=mk / len(vals), distinct=len(uniq))

def valid_rate(vals, ref, tol):
    vals = [v for v in vals if v is not None]
    return sum(1 for v in vals if abs(v - ref) <= tol) / len(vals) if vals else None

def q4_dispersion(records):
    # mean per-species SD across reports; and validity vs reference means
    sds, valids = [], []
    for sp in SPECIES:
        xs = [float(r["q4_means"].get(sp)) for r in records if r.get("q4_means") and r["q4_means"].get(sp) is not None]
        if len(xs) > 1: sds.append(st.pstdev(xs))
        ref = REF["Q4_species_mean_mass"][sp]
        if xs: valids.append(sum(1 for x in xs if abs(x - ref) <= 1.0) / len(xs))
    return (st.mean(sds) if sds else None, st.mean(valids) if valids else None)

def report_match_rate(records):
    # fraction of reports whose (q1,q2,q3, q4-means) all match the modal report
    keys = []
    for r in records:
        k = (round((r.get("q1_r") or 0) / TOL["q1_r"]),
             round((r.get("q2_effect") or 0) / TOL["q2_effect"]),
             round((r.get("q3_accuracy") or 0) / TOL["q3_accuracy"]),
             tuple(round(float(r["q4_means"].get(sp, 0))) for sp in SPECIES) if r.get("q4_means") else ())
        keys.append(k)
    return Counter(keys).most_common(1)[0][1] / len(keys)

JITEMS = ["q1_pooled_pearson", "q2_anova_eta2", "q3_logreg_seed42_scaled", "q4_species_means", "structure_ok", "missing_listwise"]
CITEMS = ["concl_gentoo_heaviest", "concl_mass_differs", "concl_sex_pred", "concl_flipper_positive"]

print("=" * 90)
print("REPORT REPRODUCIBILITY AND SKILL COHERENCE")
print("=" * 90)
summary = {}
for cond in CONDS:
    rs = by.get(cond, [])
    if not rs:
        print(f"\n{CLABEL[cond]}: no reports"); continue
    adh = [r["judge"]["adherence_score"] for r in rs if r.get("judge") and r["judge"].get("adherence_score") is not None]
    item_rates = {k: st.mean([1 if (r.get("judge") or {}).get(k) else 0 for r in rs]) for k in JITEMS}
    concl_rates = {k: st.mean([1 if (r.get("judge") or {}).get(k) else 0 for r in rs]) for k in CITEMS}
    q1 = num_repro([r.get("q1_r") for r in rs], TOL["q1_r"])
    q2 = num_repro([r.get("q2_effect") for r in rs], TOL["q2_effect"])
    q3 = num_repro([r.get("q3_accuracy") for r in rs], TOL["q3_accuracy"])
    q4sd, q4valid = q4_dispersion(rs)
    rmatch = report_match_rate(rs)
    valids = {"q1": valid_rate([r.get("q1_r") for r in rs], REFVAL["q1_r"], TOL["q1_r"]),
              "q2": valid_rate([r.get("q2_effect") for r in rs], REFVAL["q2_effect"], TOL["q2_effect"]),
              "q3": valid_rate([r.get("q3_accuracy") for r in rs], REFVAL["q3_accuracy"], TOL["q3_accuracy"]),
              "q4": q4valid}
    mean_valid = st.mean([v for v in valids.values() if v is not None])
    summary[cond] = dict(n=len(rs), adherence=st.mean(adh) if adh else None, item_rates=item_rates,
                         concl_rates=concl_rates, report_match=rmatch,
                         q1=q1, q2=q2, q3=q3, q4_sd=q4sd, valid=valids, mean_valid=mean_valid)
    print(f"\n### {CLABEL[cond]}  (n={len(rs)})")
    print(f"  (A) skill coherence  : mean adherence = {st.mean(adh)*100:.0f}%   items: " +
          ", ".join(f"{k.split('_')[0]}={item_rates[k]*100:.0f}%" for k in JITEMS))
    print(f"  (B) report reproducibility: whole-report match = {rmatch*100:.0f}%   "
          f"Q1 SD={q1['sd']:.3f} exact={q1['exact']*100:.0f}% | Q2 SD={q2['sd']:.3f} exact={q2['exact']*100:.0f}% | "
          f"Q3 SD={q3['sd']:.3f} exact={q3['exact']*100:.0f}% | Q4 meanSD={q4sd:.1f}")
    print(f"  (C) conclusion agreement: " + ", ".join(f"{k.replace('concl_','')}={concl_rates[k]*100:.0f}%" for k in CITEMS))
    print(f"  (D) validity vs reference: mean={mean_valid*100:.0f}%  "
          f"(Q1={valids['q1']*100:.0f}%, Q2={valids['q2']*100:.0f}%, Q3={valids['q3']*100:.0f}%, Q4={valids['q4']*100:.0f}%)")

(HERE / "results" / "report_summary.json").write_text(json.dumps(summary, indent=2, default=float))
print("\nWrote results/report_summary.json")

# ---- figure ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
metrics = [("Skill coherence\n(adherence)", "adherence"),
           ("Report match\n(numbers agree)", "report_match"),
           ("Validity\n(vs reference)", "mean_valid")]
x = np.arange(len(metrics)); w = 0.25
colors = {"C0": "#999999", "C1": "#e08214", "C2": "#2166ac"}
fig, ax = plt.subplots(figsize=(9, 5))
for i, cond in enumerate(CONDS):
    s = summary.get(cond)
    if not s: continue
    vals = [ (s["adherence"] or 0), s["report_match"], (s["mean_valid"] or 0) ]
    bars = ax.bar(x + (i - 1) * w, [v * 100 for v in vals], w, label=CLABEL[cond], color=colors[cond])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 100 + 1, f"{v*100:.0f}", ha="center", va="bottom", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([m[0] for m in metrics])
ax.set_ylabel("percent"); ax.set_ylim(0, 108)
ax.set_title("Report reproducibility and skill coherence by condition\n(penguin data report, 8 reports per condition)",
             fontsize=12, fontweight="bold")
ax.legend(); ax.grid(axis="y", ls=":", alpha=0.4)
fig.tight_layout(); fig.savefig(HERE / "results" / "fig_report_reproducibility.png", dpi=150)
print("Wrote results/fig_report_reproducibility.png")
