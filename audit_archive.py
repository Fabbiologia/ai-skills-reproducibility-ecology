#!/usr/bin/env python3
"""Audit the structural completeness and known provenance gaps of the archive."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
errors: list[str] = []
warnings: list[str] = []
passes: list[str] = []


def load(relative: str):
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing required file: {relative}")
        return []
    return json.loads(path.read_text())


def audit_scalar_arm(relative: str, language: str) -> None:
    records = load(relative)
    expected = {(f"T{task}", f"C{cond}"): 10 for task in range(1, 5) for cond in range(5)}
    observed = Counter((r.get("task"), r.get("condition")) for r in records)
    if len(records) == 200 and observed == expected:
        passes.append(f"{language}: 200 records; 20 complete cells of 10")
    else:
        errors.append(f"{language}: expected 200 records and 10 per task-condition cell")
    if records and all(r.get("value") is not None for r in records):
        passes.append(f"{language}: every archival run has a primary value")
    else:
        warnings.append(f"{language}: one or more archival runs lack a primary value")
    if records and not any(isinstance(r.get("provenance"), dict) for r in records):
        warnings.append(f"{language}: archival records do not identify model/provider/decoding settings")


def audit_reports(relative: str, label: str) -> None:
    records = load(relative)
    observed = Counter(r.get("cond") for r in records)
    if len(records) == 24 and observed == {"C0": 8, "C1": 8, "C2": 8}:
        passes.append(f"{label}: 24 records; 8 per condition")
    else:
        errors.append(f"{label}: expected 24 records and 8 per condition")
    retained = sum(bool(r.get("report_md")) for r in records)
    if retained != len(records):
        warnings.append(f"{label}: full graded report text retained for {retained}/{len(records)} records")
    if records and not any(isinstance(r.get("provenance"), dict) for r in records):
        warnings.append(f"{label}: archival records do not identify generator/judge model settings")


audit_scalar_arm("results_v2.json", "Python arm")
audit_scalar_arm("results_v2_R.json", "R arm")
audit_reports("report_reproducibility/results_report.json", "Standard report")
audit_reports("report_reproducibility/results_hard.json", "Hard report")

for folder in ["prompts", "prompts_r"]:
    count = len(list((ROOT / folder).glob("T[1-4]_C[0-4].txt")))
    if count == 20:
        passes.append(f"{folder}: 20 prompt files")
    else:
        errors.append(f"{folder}: expected 20 prompt files, found {count}")

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
