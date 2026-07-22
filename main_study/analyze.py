#!/usr/bin/env python3
"""Analyse the confirmatory run with the TASK as the unit of replication.

The pilot study was rejected for pooling repeated runs of one prompt as if they
were independent replicates. Here each task contributes ONE number per arm (the
proportion of its runs that reached the reference), and the tests are paired
across the twelve tasks. Runs within a task are treated as repeated measures of
that task, never as independent observations.
"""
import csv, json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).parent
REFS = json.loads((HERE / "references.json").read_text())
rows = list(csv.DictReader(open(HERE / "run_records.csv")))
ARMS = ["none", "skill", "code"]

# ---- task-level summary: one proportion per (task, arm), pooling providers ----
cell = defaultdict(list)
for r in rows:
    cell[(r["task"], r["arm"])].append(r)

task_rate, task_fail = {}, {}
for (t, a), rr in cell.items():
    task_rate[(t, a)] = np.mean([1.0 if x["correct"] == "True" else 0.0 for x in rr])
    task_fail[(t, a)] = np.mean([1.0 if x["value"] in ("", "None") else 0.0 for x in rr])

tasks = list(REFS.keys())
print("PER-TASK ACCURACY (proportion of runs reaching the reference; 10 runs per cell)")
print(f"{'task':28}{'fork':12}{'none':>8}{'skill':>8}{'code':>8}")
for t in tasks:
    f = REFS[t]["fork"]
    print(f"{t:28}{f:12}" + "".join(f"{task_rate[(t,a)]:>8.2f}" for a in ARMS))

# ---- paired tests across tasks (n = 12 tasks, the experimental unit) ----
print("\nPAIRED COMPARISONS ACROSS THE 12 TASKS (task is the unit of replication)")
def paired(a, b):
    x = np.array([task_rate[(t, a)] for t in tasks])
    y = np.array([task_rate[(t, b)] for t in tasks])
    d = x - y
    nz = d[d != 0]
    if len(nz) == 0:
        return np.mean(x), np.mean(y), float("nan"), 0
    w = stats.wilcoxon(x, y, zero_method="wilcox")
    return np.mean(x), np.mean(y), w.pvalue, int((d > 0).sum())

for a, b in [("skill", "none"), ("code", "none"), ("skill", "code")]:
    ma, mb, p, wins = paired(a, b)
    print(f"  {a:5} vs {b:5}: mean {ma:.2f} vs {mb:.2f}   Wilcoxon p = {p:.4f}   "
          f"tasks where {a} higher: {wins}/12")

# ---- by fork type ----
print("\nMEAN TASK-LEVEL ACCURACY BY FORK TYPE (3 tasks each)")
print(f"{'fork':14}{'none':>8}{'skill':>8}{'code':>8}")
forks = ["aggregation", "scope", "missing", "randomness"]
for f in forks:
    ft = [t for t in tasks if REFS[t]["fork"] == f]
    print(f"{f:14}" + "".join(f"{np.mean([task_rate[(t,a)] for t in ft]):>8.2f}" for a in ARMS))

# ---- how many tasks are at ceiling without any instruction? ----
ceiling = [t for t in tasks if task_rate[(t, "none")] >= 0.9]
binding = [t for t in tasks if task_rate[(t, "none")] < 0.9]
print(f"\ntasks already correct without instruction (>=0.9): {len(ceiling)}/12")
for t in ceiling:
    print(f"   ceiling: {t}")
print(f"tasks with a real fork (<0.9 without instruction): {len(binding)}/12")
for t in binding:
    print(f"   binding: {t:28} none={task_rate[(t,'none')]:.2f} "
          f"skill={task_rate[(t,'skill')]:.2f} code={task_rate[(t,'code')]:.2f}")

if binding:
    print("\nRESTRICTED TO THE TASKS THAT ACTUALLY CONTAIN A FORK")
    for a, b in [("skill", "none"), ("code", "none"), ("skill", "code")]:
        x = np.array([task_rate[(t, a)] for t in binding])
        y = np.array([task_rate[(t, b)] for t in binding])
        try:
            p = stats.wilcoxon(x, y, zero_method="wilcox").pvalue
        except ValueError:
            p = float("nan")
        print(f"  {a:5} vs {b:5}: mean {x.mean():.2f} vs {y.mean():.2f}   p = {p:.4f}")

# ---- consensus on a wrong answer: the headline hazard ----
print("\nCONSENSUS ON A WRONG ANSWER (no-skill runs, tasks with a fork)")
for t in binding:
    vals = [round(float(x["value"]), 4) for x in cell[(t, "none")]
            if x["value"] not in ("", "None")]
    if not vals:
        continue
    counts = defaultdict(int)
    for v in vals:
        counts[v] += 1
    top, n = max(counts.items(), key=lambda kv: kv[1])
    ref = REFS[t]["reference"]
    agree = n / len(vals)
    wrong = abs(top - ref) > REFS[t]["tolerance"]
    if wrong and agree >= 0.5:
        print(f"   {t:28} {n}/{len(vals)} runs agreed on {top} (reference {ref:.4f})")

# ---- provider agreement ----
print("\nBY PROVIDER (mean task-level accuracy)")
for prov in sorted({r["provider"] for r in rows}):
    line = f"  {prov:8}"
    for a in ARMS:
        vals = []
        for t in tasks:
            rr = [x for x in cell[(t, a)] if x["provider"] == prov]
            if rr:
                vals.append(np.mean([1.0 if x["correct"] == "True" else 0.0 for x in rr]))
        line += f"{np.mean(vals):>8.2f}"
    print(line)

json.dump({f"{t}|{a}": task_rate[(t, a)] for t in tasks for a in ARMS},
          open(HERE / "task_rates.json", "w"), indent=2)
print("\nWrote main_study/task_rates.json")
