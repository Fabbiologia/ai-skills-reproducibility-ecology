#!/usr/bin/env python3
"""Generate the 20 condition prompt files (4 tasks x 5-rung ablation).
The ablation rungs are cumulative:
  C0 none      : bare task.
  C1 basic     : generic procedural steps, no specific choices.
  C2 contract  : fixes INPUT (dataset, columns, NaN/filter policy, scope) and
                 METHOD (exact estimator/test/metric). Leaves stochastic knobs free.
  C3 controls  : C2 + fixes all numeric/stochastic knobs (seed, split, scaling).
  C4 full      : C3 + validation checklist + explicit failure-mode prohibitions.
"""
from pathlib import Path
HERE = Path(__file__).parent
OUT = HERE / "prompts"
OUT.mkdir(exist_ok=True)
# Data paths embedded in the prompts are repo-relative, so agents must be run
# with the working directory set to the repository root (see README).
DATA = Path("data")

OUTPUT_CONTRACT = (
    "\nActually run the analysis in Python (python3); sklearn, scipy, pandas, numpy "
    "are installed. Report the REAL computed numbers, not estimates.\n\n"
    "Return ONLY a single JSON object as the very last line (no prose after it), "
    "with exactly these keys:\n"
    '{{"value": <float, the primary quantity below>, "secondary": <float or null>, '
    '"direction": <"positive"/"negative" or null>, "method": "<method/model/test used>", '
    '"params": "<key parameters: seed, split, scaling, scope, filters, NaN handling>", '
    '"n": <number of observations used>}}\n'
    "PRIMARY QUANTITY (`value`) = {primary}\n"
)

TASKS = {
 "T1": {
  "primary": "the correlation coefficient between the two variables",
  "task": (
    "DATA ANALYSIS TASK\n\n"
    f"The file {DATA/'iris.csv'} contains the iris dataset (150 rows; columns include "
    "'sepal length (cm)' and 'sepal width (cm)'). Report the correlation between sepal "
    "length and sepal width, and whether the relationship is positive or negative."),
  "C1": ("1. Load the iris data.\n2. Compute the correlation between sepal length and sepal width.\n"
         "3. Report the coefficient and whether it is positive or negative."),
  "C2": ("INPUT CONTRACT: load all 150 rows from the CSV; use columns 'sepal length (cm)' and "
         "'sepal width (cm)'; do not filter or split by species; use every row.\n"
         "METHOD: compute the POOLED Pearson correlation across all 150 rows with "
         "scipy.stats.pearsonr(sepal_length, sepal_width); take the coefficient r."),
  "C3": ("No stochastic parameters are involved: the pooled Pearson correlation is fully "
         "determined by the input contract and method above; compute it directly."),
  "C4": ("VALIDATION CHECKLIST: [ ] n==150  [ ] method is pooled Pearson (not per-species, not "
         "Spearman/Kendall)  [ ] -1<=r<=1.\n"
         "FAILURE MODES TO AVOID: do NOT compute the correlation within each species and average "
         "it (Simpson's paradox flips the sign); do NOT use Spearman/Kendall; do NOT drop rows."),
 },
 "T2": {
  "primary": "the test-set classification accuracy (0-1)",
  "task": (
    "DATA ANALYSIS TASK\n\n"
    f"The file {DATA/'penguins.csv'} contains the Palmer Penguins dataset (344 rows; columns: "
    "species, island, bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g, sex; "
    "some cells are missing). Train a model to predict each penguin's SEX from its body "
    "measurements, and report the test-set classification accuracy."),
  "C1": ("1. Load the penguins data.\n2. Prepare features and the sex label.\n3. Split into train "
         "and test sets.\n4. Train a classifier and report its test accuracy."),
  "C2": ("INPUT CONTRACT: predictors = the four morphological columns [bill_length_mm, "
         "bill_depth_mm, flipper_length_mm, body_mass_g]; target = sex. Drop rows with any missing "
         "value in those five columns (do not impute). Do not use island or species as predictors.\n"
         "METHOD: model = sklearn.linear_model.LogisticRegression(max_iter=2000), default params."),
  "C3": ("STOCHASTIC CONTROLS (fix all): standardize the four predictors with "
         "sklearn.preprocessing.StandardScaler (fit on train only, e.g. via make_pipeline); split "
         "with sklearn.model_selection.train_test_split using EXACTLY test_size=0.2, "
         "random_state=42, stratify=y; compute accuracy with sklearn.metrics.accuracy_score."),
  "C4": ("VALIDATION CHECKLIST: [ ] rows with NaN in the 5 columns dropped (n_used==333)  "
         "[ ] n_test==67  [ ] random_state==42 and stratify used  [ ] StandardScaler fit on train "
         "only  [ ] model is LogisticRegression.\n"
         "FAILURE MODES TO AVOID: do NOT use a different model; do NOT omit random_state (it makes "
         "the split vary run to run); do NOT skip scaling (LogisticRegression will not converge and "
         "accuracy becomes unstable); do NOT impute missing values; do NOT use cross-validation "
         "instead of the specified holdout; do NOT leak the test set into scaling."),
 },
 "T4": {
  "primary": "the mean per-transect fish biomass for the reserve",
  "task": (
    "DATA ANALYSIS TASK\n\n"
    f"The file {DATA/'ltem_cabo_pulmo_2023.csv'} contains reef-fish visual-transect survey data "
    "from Cabo Pulmo National Park (Gulf of California) for the year 2023. Each ROW is one "
    "species record on one transect, with columns: Reef, Habitat, Transect, Species, Quantity, "
    "Size, Area, Biomass (the biomass of that record; blank/NaN for records that carry no biomass "
    "value). Report the mean per-transect fish biomass for the reserve — i.e. the community "
    "biomass on a transect, averaged across transects."),
  "C1": ("1. Load the survey data.\n2. Compute the fish biomass on each transect.\n"
         "3. Average that across transects and report it."),
  "C2": ("INPUT CONTRACT: a transect survey unit = a unique (Reef, Transect) combination; use the "
         "`Biomass` column as the per-record biomass; treat blank/NaN Biomass records as carrying "
         "no biomass (skip them in sums, do not fill with zero-inflating rows). Do not re-normalise "
         "by Area (Biomass is already the record's biomass, from a fixed 250 m^2 transect).\n"
         "METHOD: for each (Reef, Transect) survey unit, SUM the Biomass column across its records; "
         "then take the MEAN of those per-transect totals across all survey units."),
  "C3": ("No stochastic parameters are involved: given the survey-unit definition and aggregation "
         "above, the mean per-transect biomass is fully determined; compute it directly."),
  "C4": ("VALIDATION CHECKLIST: [ ] survey unit is (Reef, Transect)  [ ] you SUMMED within transect "
         "BEFORE averaging across transects  [ ] ~41 transect units  [ ] per-transect totals are of "
         "order 0.1-14, not ~0.1 overall.\n"
         "FAILURE MODES TO AVOID: do NOT average the row-level Biomass values directly (that is a "
         "per-record mean and under-counts community biomass by ~30x); do NOT divide by Area again; "
         "do NOT drop transects or reefs; do NOT count blank-Biomass records as zeros that dilute "
         "the mean; do NOT weight by Quantity or Size (Biomass already accounts for them)."),
 },
 "T3": {
  "primary": "the effect size for the difference in body mass among species",
  "task": (
    "DATA ANALYSIS TASK\n\n"
    f"The file {DATA/'penguins.csv'} contains the Palmer Penguins dataset (columns include "
    "species and body_mass_g; some body_mass_g values are missing). Test whether body mass "
    "differs among the three penguin species, and report a single effect-size value for that "
    "difference (and, as `secondary`, the p-value)."),
  "C1": ("1. Load the penguins data.\n2. Compare body mass across the three species.\n"
         "3. Report an effect size for the difference and a p-value."),
  "C2": ("INPUT CONTRACT: response = body_mass_g, group = species (3 groups). Drop rows with "
         "missing body_mass_g or species (do not impute).\n"
         "METHOD: one-way ANOVA via scipy.stats.f_oneway across the three species groups; report "
         "p-value as `secondary`. Effect size = eta-squared = SS_between / SS_total computed from "
         "the same groups; report eta-squared as `value`."),
  "C3": ("No stochastic parameters are involved: given the input contract and method, eta-squared "
         "and the p-value are fully determined; compute them directly."),
  "C4": ("VALIDATION CHECKLIST: [ ] rows with missing body_mass_g/species dropped (n==342)  "
         "[ ] test is one-way ANOVA (f_oneway)  [ ] effect size is eta-squared in [0,1].\n"
         "FAILURE MODES TO AVOID: do NOT report Cohen's d / omega-squared / epsilon-squared instead "
         "of eta-squared; do NOT use Kruskal-Wallis or pairwise t-tests as the primary test; do NOT "
         "impute missing values; do NOT report multiple p-values."),
 },
}

RUNG_HEADER = {
 "C1": "--- SKILL: {name} (basic) ---",
 "C2": "--- SKILL: {name} v1.0 (input + method contract) ---",
 "C3": "--- SKILL: {name} v1.0 (contract + fixed controls) ---",
 "C4": "--- SKILL: {name} v1.0 (full contract) ---",
}
SKILL_NAME = {"T1":"iris-sepal-correlation","T2":"penguins-sex-classifier",
              "T3":"penguins-mass-anova","T4":"ltem-reef-fish-biomass"}

def build(task_id, cond, spec):
    t = spec["task"]
    oc = OUTPUT_CONTRACT.format(primary=spec["primary"])
    if cond == "C0":
        return t + "\n" + oc
    name = SKILL_NAME[task_id]
    parts = [t, "\n" + RUNG_HEADER[cond].format(name=name)]
    # cumulative rungs
    if cond in ("C1",):
        parts.append("Follow this procedure:\n" + spec["C1"])
    if cond in ("C2","C3","C4"):
        parts.append(spec["C2"])
    if cond in ("C3","C4"):
        parts.append(spec["C3"])
    if cond in ("C4",):
        parts.append(spec["C4"])
    parts.append("--- END SKILL ---\n")
    return "\n".join(parts) + oc

def main(tasks):
    written = []
    for tid, spec in tasks.items():
        for cond in ["C0","C1","C2","C3","C4"]:
            fn = OUT / f"{tid}_{cond}.txt"
            fn.write_text(build(tid, cond, spec))
            written.append(fn.name)
    print(f"wrote {len(written)} files:", ", ".join(written))

if __name__ == "__main__":
    main(TASKS)
