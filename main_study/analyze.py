#!/usr/bin/env python3
"""Analyse the study with the TASK as the unit of replication.

Each task contributes ONE number per arm, the proportion of its runs that reached
the reference, and arms are compared across the twelve tasks with paired tests.
Runs within a task are repeated measures of that task, never independent
observations.

Two things this script is careful about.

Failed runs. A run can fail for two unrelated reasons. The model may return a
script that crashes or prints nothing usable, which is a property of the arm and
counts against it. Or the call to the provider may fail on a network or quota
error, which has nothing to do with the arm and happened to fall unevenly across
arms. The primary analysis therefore drops provider errors and keeps every other
failure as an incorrect answer. Both alternatives are reported alongside, because
the choice changes one of the comparisons and the reader should see that.

Agreement. Whether runs agree with each other is measured separately from whether
they are right, since the point of the paper is that these are different
properties. Values are grouped at the task's own tolerance, so agreement means
"close enough to count as the same answer" rather than "identical to n decimals".
"""
import csv, json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats

HERE = Path(__file__).parent
REFS = json.loads((HERE / "references.json").read_text())
rows = list(csv.DictReader(open(HERE / "run_records.csv")))
ARMS = ["none", "code", "skill"]
TASKS = list(REFS)

IS_PROVIDER_ERROR = lambda r: r["error"].startswith("api")
HAS_NUMBER = lambda r: r["value"] not in ("", "None")

INCLUSIONS = {
    "primary (provider errors dropped)": lambda r: not IS_PROVIDER_ERROR(r),
    "all runs": lambda r: True,
    "only runs returning a number": HAS_NUMBER,
}


def task_rates(include):
    cell = defaultdict(list)
    for r in rows:
        if include(r):
            cell[(r["task"], r["arm"])].append(r)
    return {k: np.mean([x["correct"] == "True" for x in v]) for k, v in cell.items()}, cell


def paired(rate, a, b, tasks=TASKS):
    x = np.array([rate[(t, a)] for t in tasks])
    y = np.array([rate[(t, b)] for t in tasks])
    d = x - y
    nz = int((d != 0).sum())
    p = stats.wilcoxon(x, y, zero_method="wilcox").pvalue if nz else float("nan")
    return x.mean(), y.mean(), p, int((d > 0).sum()), int((d < 0).sum()), nz


def boot_ci(rate, a, b, tasks=TASKS, n=20000, seed=1):
    d = np.array([rate[(t, a)] - rate[(t, b)] for t in tasks])
    rng = np.random.default_rng(seed)
    bs = rng.choice(d, (n, len(d)), replace=True).mean(axis=1)
    return d.mean(), *np.percentile(bs, [2.5, 97.5])


def consensus(values, tol):
    """Largest group of values that agree within the task's tolerance."""
    if not values:
        return 0, 0, None, 0
    groups = []
    for v in sorted(values):
        for g in groups:
            if abs(v - g[0]) <= tol:
                g.append(v)
                break
        else:
            groups.append([v])
    best = max(groups, key=len)
    return len(best), len(values), float(np.mean(best)), len(groups)


rate, cell = task_rates(INCLUSIONS["primary (provider errors dropped)"])

print("=" * 78)
print("PER-TASK ACCURACY  (primary analysis: provider errors dropped)")
print("=" * 78)
print(f"{'task':28}{'kind of choice':14}" + "".join(f"{a:>8}" for a in ARMS))
for t in TASKS:
    print(f"{t:28}{REFS[t]['fork']:14}" + "".join(f"{rate[(t,a)]:>8.2f}" for a in ARMS))
print(f"{'MEAN':42}" + "".join(f"{np.mean([rate[(t,a)] for t in TASKS]):>8.2f}" for a in ARMS))

print("\nPAIRED COMPARISONS ACROSS THE 12 TASKS (task is the unit of replication)")
for a, b in [("skill", "none"), ("code", "none"), ("skill", "code")]:
    ma, mb, p, up, dn, nz = paired(rate, a, b)
    md, lo, hi = boot_ci(rate, a, b)
    print(f"  {a:5} vs {b:5}: {ma:.2f} vs {mb:.2f}   difference {md:+.2f} "
          f"[95% CI {lo:+.2f}, {hi:+.2f}]   Wilcoxon p = {p:.4f}")
    print(f"{'':17}higher on {up} tasks, lower on {dn}, tied on {12-nz}; "
          f"the test rests on the {nz} tasks that differ")

print("\nSENSITIVITY: the same three comparisons under three ways of counting failures")
print(f"  {'runs included':34}" + "".join(f"{c:>22}" for c in
      ("skill vs none", "code vs none", "skill vs code")))
for label, inc in INCLUSIONS.items():
    rt, _ = task_rates(inc)
    line = f"  {label:34}"
    for a, b in [("skill", "none"), ("code", "none"), ("skill", "code")]:
        ma, mb, p, *_ = paired(rt, a, b)
        line += f"{ma:.2f}/{mb:.2f} p={p:.3f}".rjust(22)
    print(line)
print("  The specification beats the script on the full record and once provider errors")
print("  are dropped. Among runs that returned a number at all the two are not")
print("  distinguishable, because much of the script arm's disadvantage is that it")
print("  produced code that did not run. Both facts are reported in the paper.")

print("\nRUNS THAT RETURNED NO NUMBER, BY CAUSE")
print(f"  {'arm':8}{'provider error':>16}{'unusable script':>18}{'total':>8} of 120")
for a in ARMS:
    rr = [r for r in rows if r["arm"] == a]
    api = sum(1 for r in rr if IS_PROVIDER_ERROR(r))
    bad = sum(1 for r in rr if not HAS_NUMBER(r) and not IS_PROVIDER_ERROR(r))
    print(f"  {a:8}{api:>16}{bad:>18}{api+bad:>8}")

print("\nMEAN TASK-LEVEL ACCURACY BY KIND OF OPEN CHOICE (3 tasks each)")
print(f"  {'kind':14}" + "".join(f"{a:>8}" for a in ARMS))
for f in ["aggregation", "scope", "missing", "randomness"]:
    ft = [t for t in TASKS if REFS[t]["fork"] == f]
    print(f"  {f:14}" + "".join(f"{np.mean([rate[(t,a)] for t in ft]):>8.2f}" for a in ARMS))

ceiling = [t for t in TASKS if rate[(t, "none")] >= 0.9]
binding = [t for t in TASKS if rate[(t, "none")] < 0.9]
print(f"\nTASKS ALREADY CORRECT WITHOUT INSTRUCTION: {len(ceiling)}/12")
print(f"TASKS WHERE THE QUESTION LEFT A REAL CHOICE OPEN: {len(binding)}/12")
for t in binding:
    print(f"   {t:28}" + "".join(f"{rate[(t,a)]:>8.2f}" for a in ARMS))
if binding:
    print("  restricted to those tasks:")
    for a, b in [("skill", "none"), ("code", "none"), ("skill", "code")]:
        ma, mb, p, *_ = paired(rate, a, b, binding)
        print(f"    {a:5} vs {b:5}: {ma:.2f} vs {mb:.2f}   p = {p:.4f}")
    print(f"    (with {len(binding)} tasks the smallest attainable p is "
          f"{2/2**len(binding):.4f})")
print("\n  tasks where the specification did WORSE than no instruction:")
for t in TASKS:
    if rate[(t, "skill")] < rate[(t, "none")]:
        print(f"    {t:28} none={rate[(t,'none')]:.2f} skill={rate[(t,'skill')]:.2f}")

print("\nBY PROVIDER (mean task-level accuracy, primary analysis)")
print(f"  {'provider':10}" + "".join(f"{a:>8}" for a in ARMS))
for prov in sorted({r["provider"] for r in rows}):
    line = f"  {prov:10}"
    for a in ARMS:
        v = [np.mean([x["correct"] == "True" for x in cell[(t, a)] if x["provider"] == prov])
             for t in TASKS if any(x["provider"] == prov for x in cell[(t, a)])]
        line += f"{np.mean(v):>8.2f}"
    print(line)

print("\n" + "=" * 78)
print("AGREEMENT BETWEEN RUNS, MEASURED SEPARATELY FROM CORRECTNESS")
print("=" * 78)
print("share of runs returning a number that agree with each other within the task's")
print("tolerance, and whether the value they agree on is the reference\n")
print(f"{'task':28}" + "".join(f"{a:>20}" for a in ARMS))
agree = {}
for t in TASKS:
    line = f"{t:28}"
    for a in ARMS:
        v = [float(x["value"]) for x in cell[(t, a)] if HAS_NUMBER(x)]
        n, tot, val, ngroups = consensus(v, REFS[t]["tolerance"])
        if not tot:
            line += f"{'no runs':>20}"
            continue
        ok = abs(val - REFS[t]["reference"]) <= REFS[t]["tolerance"]
        agree[(t, a)] = (n / tot, ok)
        line += f"{n}/{tot} {'correct' if ok else 'WRONG':<7}".rjust(20)
    print(line)

print("\nAGREEMENT AND CORRECTNESS ARE DECOUPLED")
for a in ARMS:
    strong = [t for t in TASKS if agree.get((t, a), (0, True))[0] >= 0.8]
    wrong = [t for t in strong if not agree[(t, a)][1]]
    print(f"  {a:6}: {len(strong)}/12 tasks had at least 80% of runs on one value; "
          f"{len(wrong)} of those agreed on a WRONG value" + (f"  {wrong}" if wrong else ""))
print("  A collection that accepted a specification because its runs agreed would have")
print("  accepted those cases.")

json.dump({f"{t}|{a}": rate[(t, a)] for t in TASKS for a in ARMS},
          open(HERE / "task_rates.json", "w"), indent=2)
json.dump({f"{t}|{a}": agree.get((t, a)) for t in TASKS for a in ARMS},
          open(HERE / "task_agreement.json", "w"), indent=2)
print("\nWrote main_study/task_rates.json and main_study/task_agreement.json")
