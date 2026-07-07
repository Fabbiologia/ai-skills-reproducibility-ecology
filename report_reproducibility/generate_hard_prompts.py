#!/usr/bin/env python3
"""Generate the 3 HARD report-task condition prompts. Same 3-condition ablation as
the standard report, but the six analyses each have wide, genuine method forks
(cluster count, cross-validation vs holdout, model selection, bootstrap vs t
interval, pooled vs per-species correlation, and scaling before PCA). Data path is
repo-relative; run agents with the working directory at the repository root."""
from pathlib import Path
OUT = Path(__file__).parent / "prompts_hard"
OUT.mkdir(exist_ok=True)

TASK = (
"REPORT WRITING TASK\n\n"
"Write a short morphometric analysis report on the Palmer Penguins dataset in the file "
"data/penguins.csv (columns: species, island, bill_length_mm, bill_depth_mm, "
"flipper_length_mm, body_mass_g, sex; some cells are missing). Answer these six questions "
"and end with a conclusion:\n"
"  Q1. Group the penguins into clusters from their four body measurements. How many clusters "
"are there, and what is the clustering quality (silhouette score)?\n"
"  Q2. How accurately can species be predicted from the four body measurements? Report an accuracy.\n"
"  Q3. Build a regression model for body mass and report its adjusted R-squared.\n"
"  Q4. Give a 95% confidence interval for the mean flipper length.\n"
"  Q5. What is the correlation between bill length and bill depth?\n"
"  Q6. Run a principal component analysis of the four measurements and report the percent of "
"variance on the first component.\n"
"Actually run the analysis in Python (sklearn, scipy, pandas, numpy are installed) and use the "
"real computed numbers, not estimates.\n")

STRUCTURE = (
"--- SKILL: penguin-morphometrics-structure ---\n"
"Write the report with these sections, in order: 1. Title; 2. Data and methods (state how you "
"handled missing values and which method you used for each question); 3. Results, one short "
"subsection per question (Q1 to Q6), each stating the number(s); 4. Conclusion (one paragraph). "
"Use appropriate methods for each question.\n"
"--- END SKILL ---\n")

SKILL = (
"--- SKILL: penguin-morphometrics-analysis v1.0 ---\n"
"Write the report with these sections, in order: 1. Title; 2. Data and methods; 3. Results with "
"one subsection per question (Q1 to Q6); 4. Conclusion (one paragraph).\n\n"
"MISSING DATA: for each analysis, drop rows with any missing value in the columns that analysis "
"uses (listwise deletion). Do not impute.\n\n"
"METHOD FOR EACH QUESTION (use exactly this, do not substitute):\n"
"  Q1: standardise the four measurements with StandardScaler, then KMeans with n_clusters=3, "
"random_state=42, n_init=10. Report the number of clusters (3) and the silhouette_score on the "
"standardised data. Use k=3 (the three species); do not search for a different k.\n"
"  Q2: 5-fold cross-validation with cross_val_score(cv=5) of a pipeline of StandardScaler and "
"LogisticRegression(max_iter=2000), predicting species from the four measurements; report the "
"mean cross-validation accuracy. Do not use a single train/test split.\n"
"  Q3: ordinary least squares linear regression of body_mass_g on bill_length_mm + bill_depth_mm "
"+ flipper_length_mm (these three predictors only; no species term, no interactions, no "
"transformation); report the adjusted R-squared.\n"
"  Q4: a 95% confidence interval for the mean flipper_length_mm using the t method "
"(mean plus and minus t times the standard error). Do not bootstrap.\n"
"  Q5: the pooled Pearson correlation of bill_length_mm and bill_depth_mm across all rows; report "
"r. Do not compute it within each species and do not use Spearman.\n"
"  Q6: PCA of the four measurements AFTER standardising them with StandardScaler; report the "
"percent of variance explained by the first component. You must standardise before the PCA.\n\n"
"The Conclusion must state, in plain words: that there are about three clusters matching the "
"species; that species are predictable with high accuracy; that the size measurements explain "
"most of the variation in body mass; that bill length and bill depth are negatively correlated "
"overall; and that the first principal component captures a majority of the variance.\n"
"--- END SKILL ---\n")

OUTPUT = (
"\nWhen finished, return the structured result the workflow asks for: for each question the "
"number(s) and the method you used (q1_k, q1_sil, q1_method; q2_acc, q2_method; q3_adjr2, "
"q3_predictors; q4_ci_low, q4_ci_high, q4_method; q5_corr, q5_scope; q6_pc1_pct, q6_scaled), the "
"list of section headings, your conclusion paragraph, and report_md (the full report as markdown).\n")

files = {
 "C0_none.txt": TASK + OUTPUT,
 "C1_structure.txt": TASK + "\n" + STRUCTURE + OUTPUT,
 "C2_skill.txt": TASK + "\n" + SKILL + OUTPUT,
}
for name, text in files.items():
    (OUT / name).write_text(text)
print("wrote", len(files), "hard report prompts:", ", ".join(files))
