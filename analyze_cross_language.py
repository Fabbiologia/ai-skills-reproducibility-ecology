#!/usr/bin/env python3
"""Cross-language analysis: Python vs R.
Reads results_v2.json (Python) + results_v2_R.json (R) and the two reference files,
then reports (a) within-language reproducibility and validity per cell, and
(b) cross-language output equivalence (do Python and R agree within tolerance?).
Writes a combined table, a cross-language summary, and figures."""
import json, statistics as st
from collections import Counter, defaultdict
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

def modal(vals, tol):
    key = [round(v / tol) for v in vals]
    m = Counter(key).most_common(1)[0][0]
    return [v for v, k in zip(vals, key) if k == m][0]  # a representative modal value

def summarize(vals, ref, tol):
    sd = st.pstdev(vals) if len(vals) > 1 else 0.0
    uniq = []
    for v in sorted(vals):
        if not uniq or abs(v - uniq[-1]) > tol:
            uniq.append(v)
    mk = Counter(round(v / tol) for v in vals).most_common(1)[0][1]
    valid = sum(1 for v in vals if abs(v - ref) <= tol) / len(vals)
    return dict(n=len(vals), sd=sd, n_distinct=len(uniq), exact=mk / len(vals),
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
            row.append(f"{c}:SD={s['sd']:.3f},exact={s['exact']*100:.0f}%,valid={s['valid']*100:.0f}%")
        print(f"  {t} {TNAME[t]:<26} " + " | ".join(row))

print("\n" + "=" * 92)
print("CROSS-LANGUAGE OUTPUT EQUIVALENCE (Python modal vs R modal, within tolerance)")
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
        print(f"  {c}: Python={pm:.4f}  R={rm:.4f}  |diff|={abs(pm-rm):.4f}  equivalent={'YES' if agree else 'no'}")

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
fig.suptitle("Python vs R: output by skill level (10 runs per cell per language)",
             fontsize=12, fontweight="bold")
fig.tight_layout(); fig.savefig(HERE / "results" / "fig4_python_vs_r.png", dpi=150)
print("Wrote results/fig4_python_vs_r.png")
