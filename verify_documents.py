#!/usr/bin/env python3
"""Check that the four submission documents agree with the analysis and with
each other.

The manuscript's prose is written by hand, so it can fall out of step with the
numbers when the analysis changes. This script reads the built .docx files and
the summary that main_study/analyze.py writes, and fails if any claim quoted in
the text no longer matches what the data say. Run it after `make docs`.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MS_DIR = ROOT / "manuscript"


def text(name: str) -> str:
    path = MS_DIR / name
    if not path.is_file():
        print(f"ERROR: {name} has not been built")
        sys.exit(1)
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf8")
    body = re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))
    for a, b in [("&amp;", "&"), ("&apos;", "'"), ("&quot;", '"'),
                 ("&lt;", "<"), ("&gt;", ">")]:
        body = body.replace(a, b)
    return " ".join(l.strip() for l in body.split("\n") if l.strip())


MS = text("Manuscript_Specifications_AI_Ecology.docx")
SI = text("Supporting_Information_Specifications.docx")
CL = text("Cover_Letter_Specifications.docx")
TP = text("Title_Page_Specifications.docx")

S = json.loads((ROOT / "main_study/analysis_summary.json").read_text())
rows = list(csv.DictReader(open(ROOT / "main_study/run_records.csv")))

means, comps, fails = S["means"], S["comparisons"], S["failures"]
a2_ref = S["tasks"]["A2_portal_abundance"]["reference"]
m3_script = [float(r["value"]) for r in rows
             if r["task"] == "M3_portal_implicit_zeros" and r["arm"] == "code"
             and r["value"] not in ("", "None")]
m3_cell = S["cells"]["M3_portal_implicit_zeros"]["code"]

# how many tasks reached agreement on four fifths of their runs, per arm
strong = {a: sum(1 for t in S["tasks"]
                 if S["cells"][t][a]["agree_total"]
                 and S["cells"][t][a]["agree_n"] / S["cells"][t][a]["agree_total"] >= 0.8)
          for a in ("none", "code", "skill")}

# every reference in the list must appear in the body text
refs = re.findall(r'^  "(.*)",$', (MS_DIR / "build_paper2.js").read_text(), re.M)
body = MS[MS.index("1  Introduction"):MS.index("References")]
uncited = [r.split(",")[0] for r in refs if r.split(",")[0] not in body]

CHECKS = [
    ("headline means appear in the manuscript",
     all(f"{round(means[a] * 100)} per cent" in MS for a in ("none", "code", "skill"))),
    ("cover letter quotes the same two means",
     f"{round(means['skill'] * 100)} per cent" in CL and f"{round(means['code'] * 100)} per cent" in CL),
    ("p-values in the manuscript match the analysis",
     f"P = {comps['skill_vs_none']['p']:.3f}" in MS and f"P = {comps['code_vs_none']['p']:.3f}" in MS),
    ("effect sizes and their intervals are quoted",
     f"{round(comps['skill_vs_none']['diff'] * 100)} percentage points" in MS
     and f"{round(comps['skill_vs_code']['diff'] * 100)} points" in MS),
    ("provider-error counts agree across manuscript and SI",
     f"{fails['none']['provider']}, {fails['code']['provider']} and {fails['skill']['provider']}" in MS
     and f"{fails['none']['provider']} runs of 120" in SI),
    ("unusable-code counts agree in the SI",
     f"{fails['none']['unusable']}, {fails['code']['unusable']} and {fails['skill']['unusable']}" in SI),
    ("the test on provider errors is quoted consistently",
     all(f"chi-square = {S['provider_error_test']['chi2']}" in d
         and f"P = {S['provider_error_test']['p']}" in d for d in (MS, SI))),
    ("the script arm really did agree on one wrong value on M3",
     m3_cell["agree_n"] == m3_cell["agree_total"] == 10 and not m3_cell["agree_is_reference"]),
    ("that value really does match the neighbouring reference to seven places",
     bool(m3_script) and max(abs(v - a2_ref) for v in m3_script) < 5e-7),
    ("the seven-decimal claim is made, and not overstated, in all three documents",
     all("seven decimal places" in d for d in (MS, SI, CL))
     and "exactly the reference value" not in CL),
    ("the agreement counts in the manuscript match the data",
     "the question alone produced agreement on eight of the twelve tasks, "
     "the script on eleven and the specification on eleven" in MS
     and (strong["none"], strong["code"], strong["skill"]) == (8, 11, 11)),
    ("the single-model caveat appears in the methods, the limitations and the SI",
     MS.count("resting on a single model") >= 2 and "resting on a single model" in SI
     and len(S["single_model_cells"]) == 3),
    ("the Supporting Information is announced in the cover letter",
     "Supporting Information" in CL),
    ("no dashes in prose, page ranges excepted",
     not any(ch in re.sub(r"\d+[–—]\d+", "", d) for d in (MS, SI, CL, TP)
             for ch in "–—")),
    ("three figures, numbered and referenced, with the per-task table in the SI",
     all(f"Figure {n}." in MS for n in (1, 2, 3))
     and all(x in MS for x in ("Figure 1,", "(Fig. 2)", "(Fig. 3)", "(Table 1)", "Table S2"))
     and "Figure 4." not in MS),
    ("the design schematic is the first figure and sits in the methods",
     MS.index("Figure 1. The design of the study") < MS.index("3  Results")),
    ("the abstract is within the 350-word limit",
     len(MS[MS.index("Abstract"):MS.index("Data and code for peer review")].split()) - 1 <= 350),
    ("every reference in the list is cited in the text", not uncited),
    ("the results section carries no interpretive framing",
     not any(w in MS[MS.index("3  Results"):MS.index("4  Discussion")]
             for w in ("deserves attention", "the clearest single case", "understates what happens",
                       "the informative ones", "is the practical difference", "therefore computed",
                       "would not have exposed", "the reason is visible"))),
    ("the section on what a specification needs is inside the discussion",
     MS.index("4.4  What a specification needs to contain") > MS.index("4  Discussion")),
]

failed = 0
for name, ok in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failed += not ok
if uncited:
    print(f"        uncited: {uncited}")
print(f"\nDocument check: {len(CHECKS) - failed} passed, {failed} failed")
sys.exit(1 if failed else 0)
