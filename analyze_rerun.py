#!/usr/bin/env python3
"""Analyse the token-cost and cross-model re-run (Experiment 1 extension).

Reads a workflow transcript directory: journal.jsonl (one result line per agent,
with the echoed run_id and computed value) and agent-<id>.jsonl (per-turn API
usage). Completion cost per run is the sum of output_tokens across the agent's
turns, a cache-independent measure of how much the agent generated. Static cost
per skill level is the tiktoken length of the prompt file (computed separately).

Usage: analyze_rerun.py <transcript_dir> [--venv-python <path-to-tiktoken-python>]

Two sub-studies:
  token      opus only, all five conditions -> static + dynamic cost, four questions.
  multimodel opus/sonnet/haiku at C0 and C4 -> cross-model convergence.
The design is descriptive and exploratory, consistent with the main experiment.
"""
import json, sys, glob, os, subprocess, statistics as st
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).parent
TDIR = Path(sys.argv[1])
VENV_PY = None
if "--venv-python" in sys.argv:
    VENV_PY = sys.argv[sys.argv.index("--venv-python") + 1]

REF = json.loads((HERE / "data" / "references.json").read_text())
TOL = {"T1": 1e-3, "T2": 1e-3, "T3": 1e-3, "T4": 1e-2}
TASKS = ["T1", "T2", "T3", "T4"]
CONDS = ["C0", "C1", "C2", "C3", "C4"]
PRIMARY = "opus"

# ---------- static prompt cost (tiktoken via the venv, char count always) ----------
def static_cost():
    rows = {}
    for f in sorted(glob.glob(str(HERE / "prompts" / "T*_C*.txt"))):
        name = os.path.basename(f).replace(".txt", "")
        t, c = name.split("_")
        rows.setdefault(t, {})[c] = {"chars": len(open(f).read())}
    if VENV_PY:
        code = ("import tiktoken,glob,os,json;enc=tiktoken.get_encoding('cl100k_base');"
                "d={};\n"
                "import sys\n"
                "for f in sorted(glob.glob(sys.argv[1])):\n"
                " n=os.path.basename(f).replace('.txt','');t,c=n.split('_');"
                "d.setdefault(t,{})[c]=len(enc.encode(open(f).read()))\n"
                "print(json.dumps(d))")
        out = subprocess.run([VENV_PY, "-c", code, str(HERE / "prompts" / "T*_C*.txt")],
                             capture_output=True, text=True)
        try:
            tok = json.loads(out.stdout.strip())
            for t in rows:
                for c in rows[t]:
                    rows[t][c]["tok"] = tok.get(t, {}).get(c)
        except Exception:
            pass
    return rows

# ---------- parse transcripts for per-run completion tokens ----------
def sum_output_tokens(agent_id):
    f = TDIR / f"agent-{agent_id}.jsonl"
    if not f.exists():
        return None
    total = 0
    def find_usage(d):
        if isinstance(d, dict):
            if "output_tokens" in d and "input_tokens" in d:
                return d
            for v in d.values():
                r = find_usage(v)
                if r:
                    return r
        if isinstance(d, list):
            for v in d:
                r = find_usage(v)
                if r:
                    return r
        return None
    for line in open(f):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        u = find_usage(o)
        if u:
            total += u.get("output_tokens", 0) or 0
    return total

def load_records_from_csv(csv_path):
    import csv
    recs = []
    for r in csv.DictReader(open(csv_path)):
        recs.append({
            "agentId": None, "run_id": r["run_id"], "task": r["task"], "condition": r["condition"],
            "model": r["model"], "rep": r["rep"],
            "value": float(r["value"]) if r["value"] not in ("", "None", None) else None,
            "code_lines": int(r["code_lines"]) if r.get("code_lines") not in ("", "None", None) else None,
            "completion_tokens": int(r["completion_tokens"]) if r.get("completion_tokens") not in ("", "None", None) else None,
        })
    return recs

def load_records():
    # Reproducible mode: if given the archived records CSV, read it directly
    # (no session transcripts needed). Otherwise parse the workflow transcripts.
    if str(TDIR).endswith(".csv"):
        return load_records_from_csv(TDIR)
    recs = []
    jf = TDIR / "journal.jsonl"
    for line in open(jf):
        o = json.loads(line)
        if o.get("type") != "result":
            continue
        aid = o["agentId"]
        r = o["result"]
        rid = r.get("run_id") or ""
        parts = rid.split("_")
        if len(parts) < 4:
            continue
        task, cond, model = parts[0], parts[1], parts[2]
        rep = parts[3]
        if task not in TASKS or cond not in CONDS:
            continue
        recs.append({
            "agentId": aid, "run_id": rid, "task": task, "condition": cond,
            "model": model, "rep": rep,
            "value": r.get("value"),
            "code_lines": r.get("code_lines"),
            "completion_tokens": sum_output_tokens(aid),
        })
    return recs

def boot_ci(vals, nboot=5000, seed=0):
    vals = np.array([v for v in vals if v is not None], dtype=float)
    if len(vals) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = [rng.choice(vals, len(vals), replace=True).mean() for _ in range(nboot)]
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))

def rank_biserial(a, b):
    a, b = np.array(a, float), np.array(b, float)
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    U, _ = stats.mannwhitneyu(a, b, alternative="two-sided")
    return float(1 - 2 * U / (len(a) * len(b)))

def make_figures(stat, comp_by_cond, prim, mm, models):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    OK_BLUE, OK_ORANGE, OK_GREEN, OK_GREY = "#0072B2", "#D55E00", "#009E73", "#999999"
    x = np.arange(len(CONDS), dtype=float)
    CLAB = ["C0\nnone", "C1\nbasic", "C2\ncontract", "C3\ncontrols", "C4\nfull"]

    # ---- Token-cost figure: static input vs dynamic generation ----
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 4.5))
    static_mean = [st.mean([(stat[t][c].get("tok") or 0) for t in TASKS]) for c in CONDS]
    axA.bar(x, static_mean, 0.62, color=OK_BLUE)
    for xi, v in zip(x, static_mean):
        axA.text(xi, v + 6, f"{v:.0f}", ha="center", va="bottom", fontsize=8.5)
    axA.set_xticks(x); axA.set_xticklabels(CLAB, fontsize=8.5)
    axA.set_ylabel("prompt size (tokens)")
    axA.set_title("A  Static cost: the skill prompt", fontsize=11, loc="left", fontweight="bold")
    axA.grid(axis="y", ls=":", alpha=0.4); axA.spines[["top", "right"]].set_visible(False)

    data = [comp_by_cond.get(c, []) for c in CONDS]
    parts = axB.boxplot(data, positions=x, widths=0.55, patch_artist=True,
                        medianprops=dict(color="black", lw=1.5), showfliers=False)
    for pc in parts["boxes"]:
        pc.set_facecolor(OK_ORANGE); pc.set_alpha(0.55)
    for j, c in enumerate(CONDS):
        ys = comp_by_cond.get(c, [])
        xs = np.random.default_rng(3 + j).normal(j, 0.05, len(ys))
        axB.scatter(xs, ys, s=16, color=OK_ORANGE, edgecolor="white", lw=0.3, zorder=3)
    axB.set_xticks(x); axB.set_xticklabels(CLAB, fontsize=8.5)
    axB.set_ylabel("completion tokens per run")
    axB.set_title("B  Dynamic cost: what the agent generated", fontsize=11, loc="left", fontweight="bold")
    axB.grid(axis="y", ls=":", alpha=0.4); axB.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(HERE / "results" / "fig_token_cost.png", dpi=200)
    print("Wrote results/fig_token_cost.png")

    # ---- Multi-model convergence figure: the two non-ceiling tasks ----
    # Provider-agnostic size-tier labels (paper is prepared for double-anonymous review).
    TIER = {"opus": "Large model", "sonnet": "Medium model", "haiku": "Small model"}
    TIER_ORDER = ["opus", "sonnet", "haiku"]
    mtasks = ["T2", "T4"]
    TITLE = {"T2": "T2  Stochastic classifier", "T4": "T4  Reef-fish biomass"}
    ms = [m for m in TIER_ORDER if m in models] + [m for m in sorted(models) if m not in TIER_ORDER]
    mcolors = {m: col for m, col in zip(ms, [OK_BLUE, OK_GREEN, OK_GREY, OK_ORANGE][:len(ms)])}
    fig2, axes2 = plt.subplots(1, 2, figsize=(11.5, 4.4))
    w = 0.8 / max(len(ms), 1)
    for ax, t in zip(axes2, mtasks):
        xc = np.arange(2)  # C0, C4
        for i, m in enumerate(ms):
            ys = []
            for c in ["C0", "C4"]:
                key = f"{m}_{c}_{t}"
                ys.append(mm[key]["valid"] * 100 if key in mm else np.nan)
            ax.bar(xc + (i - (len(ms) - 1) / 2) * w, ys, w, label=TIER.get(m, m), color=mcolors[m])
        ax.axhline(100, ls=":", color="#9ca3af", lw=1)
        ax.set_xticks(xc); ax.set_xticklabels(["C0 none", "C4 full"], fontsize=9)
        ax.set_ylim(0, 112); ax.set_ylabel("runs matching reference (%)")
        ax.set_title(TITLE[t], fontsize=11, loc="left", fontweight="bold")
        ax.grid(axis="y", ls=":", alpha=0.4); ax.spines[["top", "right"]].set_visible(False)
    handles, labels = axes2[0].get_legend_handles_labels()
    fig2.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.99),
                ncol=len(ms), frameon=False, fontsize=9.5, title=None)
    fig2.tight_layout(rect=[0, 0, 1, 0.9])
    fig2.savefig(HERE / "results" / "fig_multimodel.png", dpi=200)
    print("Wrote results/fig_multimodel.png")


def main():
    stat = static_cost()
    recs = load_records()
    ok = [r for r in recs if r["value"] is not None]
    print(f"loaded {len(recs)} results ({len(ok)} with a value)")
    by_model = defaultdict(int)
    for r in recs:
        by_model[r["model"]] += 1
    print("by model:", dict(by_model))

    # ---------------- TOKEN SUB-STUDY (primary model only) ----------------
    prim = [r for r in ok if r["model"] == PRIMARY and r["completion_tokens"] is not None]
    tok_summary = {"static": stat, "dynamic": {}, "tests": {}}
    print("\n=== TOKEN COST (model=%s) ===" % PRIMARY)
    print(f"{'cond':5}{'static_tok':>11}{'n':>4}{'compl_med':>11}{'compl_mean':>12}{'compl_sd':>10}")
    comp_by_cond = {}
    for c in CONDS:
        rr = [r for r in prim if r["condition"] == c]
        comps = [r["completion_tokens"] for r in rr]
        comp_by_cond[c] = comps
        stat_tok = st.mean([stat[t][c].get("tok") or 0 for t in TASKS]) if VENV_PY else None
        med = st.median(comps) if comps else float("nan")
        mean = st.mean(comps) if comps else float("nan")
        sd = st.pstdev(comps) if len(comps) > 1 else 0.0
        tok_summary["dynamic"][c] = {"n": len(comps), "median": med, "mean": mean, "sd": sd,
                                      "static_tok_mean": stat_tok, "values": comps}
        print(f"{c:5}{(stat_tok or 0):>11.0f}{len(comps):>4}{med:>11.0f}{mean:>12.0f}{sd:>10.0f}")

    # Q1: net change C4-C0 and C2-C1 (completion tokens), bootstrap CI on the difference
    def diff_ci(ca, cb):
        a, b = comp_by_cond.get(ca, []), comp_by_cond.get(cb, [])
        if not a or not b:
            return None
        rng = np.random.default_rng(1)
        A, B = np.array(a, float), np.array(b, float)
        diffs = [rng.choice(A, len(A)).mean() - rng.choice(B, len(B)).mean() for _ in range(5000)]
        return {"point": float(A.mean() - B.mean()),
                "ci": (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)))}
    tok_summary["tests"]["net_C4_minus_C0"] = diff_ci("C4", "C0")
    tok_summary["tests"]["net_C2_minus_C1"] = diff_ci("C2", "C1")

    # Q2: pooled low (C0,C1) vs high (C3,C4) completion tokens
    low = comp_by_cond.get("C0", []) + comp_by_cond.get("C1", [])
    high = comp_by_cond.get("C3", []) + comp_by_cond.get("C4", [])
    if low and high:
        U, p = stats.mannwhitneyu(low, high, alternative="two-sided")
        tok_summary["tests"]["low_vs_high"] = {
            "n_low": len(low), "n_high": len(high),
            "median_low": st.median(low), "median_high": st.median(high),
            "U": float(U), "p": float(p), "rank_biserial": rank_biserial(low, high)}
        print(f"\nQ2 low(C0,C1) med={st.median(low):.0f} vs high(C3,C4) med={st.median(high):.0f}  "
              f"MWU p={p:.4g}  rb={rank_biserial(low, high):.3f}")

    # Q3: is C1 the most expensive level?
    means = {c: (st.mean(comp_by_cond[c]) if comp_by_cond[c] else float('nan')) for c in CONDS}
    tok_summary["tests"]["most_expensive_level"] = max(means, key=lambda c: means[c])
    print("Q3 most expensive level (mean completion):", tok_summary["tests"]["most_expensive_level"], means)

    # Q4: does cost track correctness? completion tokens of valid vs invalid runs
    def is_valid(r):
        return abs(r["value"] - REF[r["task"]]["value"]) <= TOL[r["task"]]
    valid_c = [r["completion_tokens"] for r in prim if is_valid(r)]
    invalid_c = [r["completion_tokens"] for r in prim if not is_valid(r)]
    if valid_c and invalid_c:
        U, p = stats.mannwhitneyu(valid_c, invalid_c, alternative="two-sided")
        tok_summary["tests"]["valid_vs_invalid"] = {
            "n_valid": len(valid_c), "n_invalid": len(invalid_c),
            "median_valid": st.median(valid_c), "median_invalid": st.median(invalid_c),
            "p": float(p)}
        print(f"Q4 valid med={st.median(valid_c):.0f} (n={len(valid_c)}) vs invalid med={st.median(invalid_c):.0f} "
              f"(n={len(invalid_c)})  MWU p={p:.4g}")

    # ---------------- MULTI-MODEL SUB-STUDY (C0/C4) ----------------
    print("\n=== CROSS-MODEL CONVERGENCE (C0 vs C4) ===")
    models = sorted(by_model.keys())
    mm = {}
    for m in models:
        for c in ["C0", "C4"]:
            for t in TASKS:
                rr = [r for r in ok if r["model"] == m and r["condition"] == c and r["task"] == t]
                vals = [r["value"] for r in rr]
                if not vals:
                    continue
                ref = REF[t]["value"]; tol = TOL[t]
                # modal agreement within tolerance
                clusters = []
                for v in sorted(vals):
                    if not clusters or v - clusters[-1][-1] > tol:
                        clusters.append([v])
                    else:
                        clusters[-1].append(v)
                modal = max(len(cl) for cl in clusters) / len(vals)
                valid = sum(1 for v in vals if abs(v - ref) <= tol) / len(vals)
                mm[f"{m}_{c}_{t}"] = {"n": len(vals), "modal": modal, "valid": valid,
                                       "median": st.median(vals), "values": vals}
                print(f"  {m:7} {c} {t}: n={len(vals)} agree={modal*100:3.0f}% valid={valid*100:3.0f}% "
                      f"median={st.median(vals):.4f} (ref {ref})")

    # cross-model: do the models agree with EACH OTHER (and the reference) per task/cond?
    cross = {}
    for c in ["C0", "C4"]:
        for t in TASKS:
            meds = {m: mm[f"{m}_{c}_{t}"]["median"] for m in models if f"{m}_{c}_{t}" in mm}
            if len(meds) < 2:
                continue
            spread = max(meds.values()) - min(meds.values())
            agree_ref = all(abs(v - REF[t]["value"]) <= TOL[t] for v in meds.values())
            cross[f"{c}_{t}"] = {"model_medians": meds, "spread": spread, "all_match_ref": agree_ref}
    print("\ncross-model spread of medians (max-min across models):")
    for k in sorted(cross):
        cc = cross[k]
        print(f"  {k}: spread={cc['spread']:.4f}  all_match_ref={cc['all_match_ref']}  {cc['model_medians']}")

    # ---------------- FIGURES ----------------
    make_figures(stat, comp_by_cond, prim, mm, models)

    out = {"token": tok_summary, "multimodel": mm, "cross_model": cross,
           "n_records": len(recs), "n_value": len(ok), "by_model": dict(by_model),
           "primary_model": PRIMARY, "reps_ok": len(ok)}
    (HERE / "results" / "rerun_summary.json").write_text(json.dumps(out, indent=2, default=float))
    # records csv
    import csv
    with open(HERE / "results" / "rerun_records.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["run_id", "task", "condition", "model", "rep", "value", "completion_tokens", "code_lines"])
        for r in recs:
            w.writerow([r["run_id"], r["task"], r["condition"], r["model"], r["rep"],
                        r["value"], r["completion_tokens"], r["code_lines"]])
    print("\nWrote results/rerun_summary.json and results/rerun_records.csv")
    return out

if __name__ == "__main__":
    main()
