#!/usr/bin/env python3
"""Refuse to publish the review branch if anything identifies the authors.

Anonymous GitHub can substitute terms in text files but cannot rewrite the inside
of a .docx or .pptx, which are ZIP archives, so this checks those too. Run it on
the review branch before updating the anonymised repository.
"""
import re, subprocess, sys, zipfile
from pathlib import Path

TERMS = re.compile(r"Favoretto|Rivera|Solorzano|Plymouth|Aburto|Scripps|fabio|"
                   r"Fabbiologia|MEE-26-07-694|UniversityofPlymouth|/Users/", re.I)
FORBIDDEN = ["manuscript/Title_Page_Specifications.docx",
             "manuscript/Cover_Letter_Specifications.docx",
             "manuscript/build_title_page2.js",
             "manuscript/build_cover_letter2.js"]

SELF = Path(__file__).name          # this file lists the terms, so it always matches

files = [f for f in subprocess.run(["git", "ls-files"], capture_output=True,
                                   text=True).stdout.split() if f != SELF]
problems = []

for f in FORBIDDEN:
    if f in files:
        problems.append(f"{f} must not be tracked on the review branch")

for f in files:
    p = Path(f)
    if f.endswith((".docx", ".pptx", ".xlsx")):
        try:
            z = zipfile.ZipFile(f)
        except Exception:
            continue
        for n in z.namelist():
            hit = TERMS.search(z.read(n).decode("utf8", "ignore"))
            if hit:
                problems.append(f"{f} contains '{hit.group(0)}' inside {n}")
    elif p.is_file() and p.stat().st_size < 4_000_000:
        try:
            hit = TERMS.search(p.read_text(errors="ignore"))
        except Exception:
            continue
        if hit:
            problems.append(f"{f} contains '{hit.group(0)}'")

for m in problems:
    print("  LEAK:", m)
print(f"\nAnonymity check: {len(files)} tracked files, {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
