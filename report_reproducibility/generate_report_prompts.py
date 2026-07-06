#!/usr/bin/env python3
"""Generate the 3 report-task condition prompts for the report-reproducibility
experiment. The task is a small ecological data report with four analyses and a
conclusion. The conditions differ only in the instruction block:
  C0 none      : the report task alone.
  C1 structure : adds the report structure (sections) but not the statistics.
  C2 skill     : adds the exact statistical method for each question, fixed
                 parameters, and a missing-data rule (the 'methods skill').
Data path is repo-relative; run agents with the working directory at the repo root."""
from pathlib import Path
OUT = Path(__file__).parent / "prompts"
OUT.mkdir(exist_ok=True)

TASK = (
"REPORT WRITING TASK\n\n"
"Write a short, self-contained data report on the Palmer Penguins dataset in the file "
"data/penguins.csv (columns: species, island, bill_length_mm, bill_depth_mm, "
"flipper_length_mm, body_mass_g, sex; some cells are missing). The report must answer "
"these four questions and end with a conclusion:\n"
"  Q1. What is the correlation between flipper length and body mass?\n"
"  Q2. Does body mass differ among the three species? Give a test and an effect size.\n"
"  Q3. How accurately can a penguin's sex be predicted from the four body measurements? "
"Give a test-set accuracy.\n"
"  Q4. What is the mean body mass of each species?\n"
"Actually run the analysis in Python (sklearn, scipy, pandas, numpy are installed) and "
"use the real computed numbers, not estimates.\n")

STRUCTURE = (
"--- SKILL: penguin-report-structure ---\n"
"Write the report with these sections, in this order:\n"
"  1. Title\n  2. Data and methods (say how you handled missing values and which method you used for each question)\n"
"  3. Results, with one short subsection per question (Q1, Q2, Q3, Q4), each stating the number(s)\n"
"  4. Conclusion (one paragraph summarising the main findings)\n"
"Use appropriate statistics for each question.\n"
"--- END SKILL ---\n")

SKILL = (
"--- SKILL: penguin-report-analysis v1.0 ---\n"
"Write the report with these sections, in order: 1. Title; 2. Data and methods; "
"3. Results with one subsection per question (Q1, Q2, Q3, Q4); 4. Conclusion (one paragraph).\n\n"
"MISSING DATA: for each analysis, drop rows with a missing value in the columns that "
"analysis uses (listwise deletion). Do not impute.\n\n"
"METHOD FOR EACH QUESTION (use exactly this):\n"
"  Q1: pooled Pearson correlation across all rows with scipy.stats.pearsonr(flipper_length_mm, "
"body_mass_g). Report r to 3 decimals. Do not use Spearman or a per-species correlation.\n"
"  Q2: one-way ANOVA with scipy.stats.f_oneway across the three species; effect size = "
"eta-squared = SS_between / SS_total. Report the p-value and eta-squared. Do not use "
"Kruskal-Wallis or pairwise t-tests as the main test, and do not report a different effect size.\n"
"  Q3: predictors are the four body-measurement columns; target is sex. Standardise the "
"predictors with StandardScaler; split with train_test_split(test_size=0.2, random_state=42, "
"stratify=y); model is LogisticRegression(max_iter=2000); report accuracy_score to 4 decimals. "
"Do not use a different model, do not omit random_state, do not skip scaling.\n"
"  Q4: mean of body_mass_g for each species (after dropping missing body_mass_g). Report each "
"species mean to 1 decimal.\n\n"
"The Conclusion must state, in plain words: that body mass differs strongly and significantly "
"among species with Gentoo the heaviest; that flipper length and body mass are positively "
"correlated; and the sex-prediction accuracy.\n"
"--- END SKILL ---\n")

OUTPUT = (
"\nWhen finished, return the structured result the workflow asks for: the number and the "
"method for each question, the species means, the section headings you used, the conclusion "
"paragraph, and the full report as markdown text.\n")

files = {
 "C0_none.txt": TASK + OUTPUT,
 "C1_structure.txt": TASK + "\n" + STRUCTURE + OUTPUT,
 "C2_skill.txt": TASK + "\n" + SKILL + OUTPUT,
}
for name, text in files.items():
    (OUT / name).write_text(text)
print("wrote", len(files), "report prompts:", ", ".join(files))
