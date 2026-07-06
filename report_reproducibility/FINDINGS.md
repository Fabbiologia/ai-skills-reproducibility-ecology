# Report-level reproducibility and skill coherence

A second experiment that raises the unit of output from a single number to a whole
data report, and asks the two questions directly: does a report use the statistics
the skill specifies (coherence), and do independent reports agree (replicability)?

## Design
Each agent writes a short data report on the Palmer Penguins dataset answering four
questions (Q1 correlation of flipper length and body mass; Q2 does body mass differ
among species, with a test and effect size; Q3 sex-prediction accuracy; Q4 mean body
mass per species) and a conclusion. Three conditions, 8 reports each (24 reports):

- **C0 none** — the questions only.
- **C1 structure** — a skill fixing the report sections but not the statistics.
- **C2 full skill** — a skill fixing the exact test, effect size, model, random seed,
  split, and missing-data rule for each question.

A second **judge agent** then grades each report against one fixed canonical rubric
(the same rubric for all three conditions), so coherence is scored the same way
everywhere. References for Q1 to Q4 were computed independently.

## Results (8 reports per condition)

| Metric | C0 none | C1 structure | C2 full skill |
|---|---|---|---|
| Skill coherence (adherence to specified statistics) | 79% | 83% | **100%** |
| Report reproducibility (independent reports agree on the numbers) | 100% | 100% | 100% |
| Conclusion agreement (same key claims) | 100% | 100% | 100% |
| Validity (numbers match the reference) | 75% | 75% | **100%** |

Per-item coherence shows where the gap is: Q1, Q2, and Q4 passed in every condition
(agents chose the standard method on their own), and the only failure was Q3. Without
the full skill, every report used a 75/25 train/test split, which is the machine-
learning library's default, instead of the 80/20 split the skill specifies. That one
free choice moved the reported accuracy from the canonical 0.8806 to 0.8929 in all
C0 and C1 reports.

## What this shows

1. **Replicability and coherence are different things, and the skill helps the second,
   not the first.** The reports were perfectly replicable in every condition: eight
   independent agents produced the same numbers and the same conclusions even with no
   skill. So for a standard report, replicability is high by default. The skill did
   not need to fix it.

2. **Only the full methods skill made the report coherent to the specified statistics
   (79% to 100%).** Fixing the report structure alone (C1) did not help the statistics;
   the analysis still used the wrong split. Coherence comes from specifying the
   methods, not the layout.

3. **A report can be reproducible yet wrong.** C0 and C1 reports were 100% replicable
   but only 75% valid, because they consistently used the library-default split rather
   than the specified one. This is the same reproducibility-is-not-validity point as
   the main experiment, now at the level of a whole report: independent agreement does
   not prove correctness, and a skill that pins the free choices is what aligns the
   report with the intended method.

4. **The skill mattered exactly at the free parameter.** The deterministic, standard
   parts of the report (a correlation, an ANOVA effect size, per-species means) were
   correct without a skill. The one place the skill changed the outcome was the
   train/test split, an unfixed choice that otherwise fell back to the tool default.
   This matches the main experiment: skills improve output by removing free choices.

## Limitations
One dataset, one report template with four analyses, one language (Python), a single
model provider, eight reports per condition, and a single-judge grader. The report is
a fairly standard task, so the default agreement is high; a longer or less standard
report with more free choices would likely show larger differences between conditions.
A larger study should add more report templates, a multi-judge grader with agreement
checks, and reports with more open method choices.

## Files
- `generate_report_prompts.py` writes the three condition prompts (`prompts/`).
- `run_report_experiment.workflow.js` generates and judges the 24 reports.
- `results_report.json` holds every report's structured output and judge grades.
- `analyze_report.py` scores coherence, reproducibility, and validity and draws
  `results/fig_report_reproducibility.png`.
- `references_report.json` holds the canonical values for Q1 to Q4.
