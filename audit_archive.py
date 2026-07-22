#!/usr/bin/env python3
"""Audit the structural completeness of the archive and print known provenance gaps.

The main study is checked strictly: twelve tasks, three arms, ten runs per cell,
a written specification for every task, and no kind of open choice confined to a
single dataset. The supporting runs are checked for completeness only, because
they carry no inference.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
errors: list[str] = []
warnings: list[str] = []
passes: list[str] = []


def load_json(relative: str):
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing required file: {relative}")
        return None
    return json.loads(path.read_text())


# ---------------------------------------------------------------- main study
refs = load_json("main_study/references.json")
if refs is not None:
    if len(refs) == 12:
        passes.append("main study: 12 tasks defined")
    else:
        errors.append(f"main study: expected 12 tasks, found {len(refs)}")
    forks = Counter(t["fork"] for t in refs.values())
    if set(forks) == {"aggregation", "scope", "missing", "randomness"} and set(forks.values()) == {3}:
        passes.append("main study: four kinds of open choice, three tasks each")
    else:
        errors.append(f"main study: unbalanced kinds of open choice: {dict(forks)}")
    datasets: dict[str, set] = {t["fork"]: set() for t in refs.values()}
    for t in refs.values():
        datasets[t["fork"]].add(t["dataset"])
    confined = [f for f, d in datasets.items() if len(d) == 1]
    if confined:
        errors.append(f"main study: kinds of choice confined to one dataset: {confined}")
    else:
        passes.append("main study: no kind of choice is confined to a single dataset")
    incomplete = [k for k, t in refs.items() if not t.get("spec") or "tolerance" not in t]
    if incomplete:
        errors.append(f"main study: tasks lacking a specification or a tolerance: {incomplete}")
    else:
        passes.append("main study: every task carries a written specification and a tolerance")

records_path = ROOT / "main_study/run_records.csv"
if not records_path.is_file():
    errors.append("missing required file: main_study/run_records.csv")
else:
    rows = list(csv.DictReader(records_path.open()))
    cells = Counter((r["task"], r["arm"]) for r in rows)
    if len(rows) == 360 and set(cells.values()) == {10}:
        passes.append("main study: 360 run records in 36 complete cells of 10")
    else:
        errors.append(f"main study: expected 360 records in cells of 10, found {len(rows)} "
                      f"in cells of {sorted(set(cells.values()))}")
    if rows and all(r.get("model") for r in rows):
        passes.append("main study: every run record names the model that produced it")
    else:
        errors.append("main study: some run records do not name a model")

# ----------------------------------------------------------- supporting runs
for name, relative in [("Python arm", "supporting_runs/results_v2.json"),
                       ("R arm", "supporting_runs/results_v2_R.json")]:
    recs = load_json(relative)
    if recs is None:
        continue
    if len(recs) == 200:
        passes.append(f"supporting runs, {name}: 200 records")
    else:
        errors.append(f"supporting runs, {name}: expected 200 records, found {len(recs)}")
    if not any(isinstance(r.get("provenance"), dict) for r in recs):
        warnings.append(f"supporting runs, {name}: records do not identify model, provider or decoding settings")

for label, relative in [("standard report", "supporting_runs/report_reproducibility/results_report.json"),
                        ("hard report", "supporting_runs/report_reproducibility/results_hard.json")]:
    recs = load_json(relative)
    if recs is None:
        continue
    if len(recs) == 24 and Counter(r.get("cond") for r in recs) == {"C0": 8, "C1": 8, "C2": 8}:
        passes.append(f"supporting runs, {label}: 24 records, 8 per condition")
    else:
        errors.append(f"supporting runs, {label}: expected 24 records and 8 per condition")
    if sum(bool(r.get("report_md")) for r in recs) != len(recs):
        warnings.append(f"supporting runs, {label}: the full graded report text is not retained")

for folder in ["supporting_runs/prompts", "supporting_runs/prompts_r"]:
    count = len(list((ROOT / folder).glob("T[1-4]_C[0-4].txt")))
    if count == 20:
        passes.append(f"{folder}: 20 prompt files")
    else:
        errors.append(f"{folder}: expected 20 prompt files, found {count}")

if (ROOT / "transfer_runs/transfer_records.csv").is_file():
    passes.append("transfer runs: records present")
else:
    warnings.append("transfer runs: records absent")

# ------------------------------------------------------------ restricted data
if (ROOT / "data/ltem_cabo_pulmo_2023.csv").exists():
    warnings.append("restricted LTEM CSV is present locally; confirm it is excluded from the public archive")
elif (ROOT / "data/ltem_cabo_pulmo_2023.csv.README.md").is_file():
    passes.append("restricted LTEM CSV is absent and its access note is present")

for message in passes:
    print(f"PASS: {message}")
for message in warnings:
    print(f"WARN: {message}")
for message in errors:
    print(f"ERROR: {message}")
print(f"\nArchive audit: {len(passes)} passed, {len(warnings)} warnings, {len(errors)} errors")
sys.exit(1 if errors else 0)
