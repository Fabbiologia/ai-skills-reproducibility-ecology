#!/usr/bin/env python3
"""Generate the 20 R-language condition prompt files (4 tasks x 5-rung ablation),
the R counterpart of generate_prompts.py. Same tasks and skill ladder, but the
method contracts name R functions, and agents run the analysis with Rscript.
Data paths are repo-relative, so run agents with the working directory at the
repository root."""
from pathlib import Path
HERE = Path(__file__).parent
OUT = HERE / "prompts_r"
OUT.mkdir(exist_ok=True)
DATA = Path("data")

OUTPUT_CONTRACT = (
    "\nActually run the analysis in R (call Rscript; the packages stats, dplyr, and "
    "readr are available). Report the REAL computed numbers, not estimates.\n\n"
    "Return ONLY a single JSON object as the very last line (no prose after it), "
    "with exactly these keys:\n"
    '{{"value": <float, the primary quantity below>, "secondary": <float or null>, '
    '"direction": <"positive"/"negative" or null>, "method": "<method/model/test used>", '
    '"params": "<key parameters: seed, split, scaling, scope, filters, NA handling>", '
    '"n": <number of observations used>}}\n'
    "PRIMARY QUANTITY (`value`) = {primary}\n"
)

TASKS = {
 "T1": {
  "primary": "the correlation coefficient between the two variables",
  "task": (
    "DATA ANALYSIS TASK (R)\n\n"
    "R has the iris dataset built in (data(iris); columns Sepal.Length and "
    "Sepal.Width). Report the correlation between sepal length and sepal width, and "
    "whether the relationship is positive or negative."),
  "C1": ("1. Load the iris data.\n2. Compute the correlation between sepal length and sepal width.\n"
         "3. Report the coefficient and whether it is positive or negative."),
  "C2": ("INPUT CONTRACT: use all 150 rows of the built-in iris; use columns Sepal.Length and "
         "Sepal.Width; do not filter or split by Species.\n"
         "METHOD: compute the POOLED Pearson correlation across all 150 rows with "
         "cor(iris$Sepal.Length, iris$Sepal.Width) (method = 'pearson', the default)."),
  "C3": ("No random parameters are involved: the pooled Pearson correlation is fully determined "
         "by the contract and method above; compute it directly."),
  "C4": ("VALIDATION CHECK LIST: n == 150; method is pooled Pearson (not by Species, not Spearman "
         "or Kendall); the value is between -1 and 1.\n"
         "DO NOT: compute the correlation within each Species and average it (Simpson's paradox "
         "flips the sign); use method = 'spearman' or 'kendall'; drop any rows."),
 },
 "T2": {
  "primary": "the test-set classification accuracy (0-1)",
  "task": (
    "DATA ANALYSIS TASK (R)\n\n"
    f"The file {DATA/'penguins.csv'} holds the Palmer Penguins data (344 rows; columns species, "
    "island, bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g, sex; some cells are "
    "NA). Train a model to predict each penguin's sex from its body measurements, and report the "
    "test-set classification accuracy."),
  "C1": ("1. Load the penguins data.\n2. Prepare the four body-measurement predictors and the sex "
         "label.\n3. Split into a training set and a test set.\n4. Train a classifier and report "
         "its test accuracy."),
  "C2": ("INPUT CONTRACT: predictors are the four columns bill_length_mm, bill_depth_mm, "
         "flipper_length_mm, body_mass_g; target is sex as a factor. Drop rows with any NA in those "
         "five columns (do not impute). Do not use island or species as predictors.\n"
         "METHOD: model = glm(sex ~ ., family = binomial) fitted on the training set (logistic "
         "regression); predict on the test set with type = 'response' and a 0.5 threshold; accuracy "
         "= mean(predicted == actual)."),
  "C3": ("RANDOM CONTROLS (fix all): set.seed(42) before splitting. Make a stratified 80/20 "
         "train/test split by sex with base R using exactly:\n"
         "  set.seed(42)\n"
         "  train_idx <- unlist(lapply(split(seq_len(nrow(d)), d$sex),\n"
         "                             function(ix) sample(ix, round(0.8 * length(ix)))))\n"
         "where d is the cleaned data frame (rows with NA removed, sex as a factor). Train on "
         "d[train_idx, ] and test on d[-train_idx, ]. (Scaling the predictors does not change a "
         "glm fit, so it is not required.)"),
  "C4": ("VALIDATION CHECK LIST: rows with NA in the five columns dropped (n_used == 333); "
         "n_test == 67; set.seed(42) and the exact split above were used; model is glm binomial; "
         "accuracy between 0 and 1.\n"
         "DO NOT: use a different model (randomForest, knn, tree, svm); omit set.seed (that makes "
         "the split vary run to run); change the split rule; impute NA; use cross-validation "
         "instead of the specified holdout."),
 },
 "T3": {
  "primary": "the effect size for the difference in body mass among species",
  "task": (
    "DATA ANALYSIS TASK (R)\n\n"
    f"The file {DATA/'penguins.csv'} holds the Palmer Penguins data (columns include species and "
    "body_mass_g; some body_mass_g values are NA). Test whether body mass differs among the three "
    "penguin species, and report a single effect-size value for that difference (and, as "
    "`secondary`, the p-value)."),
  "C1": ("1. Load the penguins data.\n2. Compare body mass across the three species.\n"
         "3. Report an effect size for the difference and a p-value."),
  "C2": ("INPUT CONTRACT: response is body_mass_g, group is species (3 groups). Drop rows with NA "
         "in body_mass_g or species (do not impute).\n"
         "METHOD: one-way ANOVA with aov(body_mass_g ~ species); report the p-value as `secondary`. "
         "Effect size = eta-squared = SS_between / SS_total from the same ANOVA table; report "
         "eta-squared as `value`."),
  "C3": ("No random parameters are involved: given the contract and method, eta-squared and the "
         "p-value are fully determined; compute them directly."),
  "C4": ("VALIDATION CHECK LIST: rows with NA dropped (n == 342); test is one-way ANOVA (aov); "
         "effect size is eta-squared in [0, 1].\n"
         "DO NOT: report Cohen's d, omega-squared, or epsilon-squared instead of eta-squared; use "
         "kruskal.test or pairwise t-tests as the primary test; impute NA; report several p-values."),
 },
 "T4": {
  "primary": "the mean per-transect fish biomass for the reserve",
  "task": (
    "DATA ANALYSIS TASK (R)\n\n"
    f"The file {DATA/'ltem_cabo_pulmo_2023.csv'} holds reef-fish visual-transect survey data from "
    "Cabo Pulmo National Park (Gulf of California) for 2023. Each ROW is one species record on one "
    "transect, with columns Reef, Habitat, Transect, Species, Quantity, Size, Area, Biomass (the "
    "biomass of that record; NA for records with no biomass value). Report the mean per-transect "
    "fish biomass for the reserve, that is the community biomass on a transect, averaged across "
    "transects."),
  "C1": ("1. Load the survey data.\n2. Compute the fish biomass on each transect.\n"
         "3. Average that across transects and report it."),
  "C2": ("INPUT CONTRACT: a transect survey unit is a unique (Reef, Transect) combination; use the "
         "Biomass column as the per-record biomass; treat NA Biomass as no biomass (use na.rm = "
         "TRUE in the sums). Do not re-scale by Area (Biomass is already the record's biomass).\n"
         "METHOD: for each (Reef, Transect) unit, SUM Biomass across its records; then take the "
         "MEAN of those per-transect totals across all units (for example with dplyr: group_by("
         "Reef, Transect), summarise(tot = sum(Biomass, na.rm = TRUE)), then mean(tot))."),
  "C3": ("No random parameters are involved: given the unit definition and the aggregation, the "
         "mean per-transect biomass is fully determined; compute it directly."),
  "C4": ("VALIDATION CHECK LIST: the unit is (Reef, Transect); you SUMMED within a transect BEFORE "
         "averaging across transects; about 39 transect units; per-transect totals are of order "
         "0.1 to 14, not about 0.1 overall.\n"
         "DO NOT: average the row-level Biomass values directly (that under-counts biomass by about "
         "30 times); divide by Area; drop transects or reefs; weight by Quantity or Size."),
 },
}

RUNG_HEADER = {
 "C1": "--- SKILL: {name} (basic) ---",
 "C2": "--- SKILL: {name} v1.0 (input + method contract) ---",
 "C3": "--- SKILL: {name} v1.0 (contract + fixed controls) ---",
 "C4": "--- SKILL: {name} v1.0 (full contract) ---",
}
SKILL_NAME = {"T1":"iris-sepal-correlation-r","T2":"penguins-sex-classifier-r",
              "T3":"penguins-mass-anova-r","T4":"ltem-reef-fish-biomass-r"}

def build(task_id, cond, spec):
    t = spec["task"]
    oc = OUTPUT_CONTRACT.format(primary=spec["primary"])
    if cond == "C0":
        return t + "\n" + oc
    name = SKILL_NAME[task_id]
    parts = [t, "\n" + RUNG_HEADER[cond].format(name=name)]
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

def main():
    written = []
    for tid, spec in TASKS.items():
        for cond in ["C0","C1","C2","C3","C4"]:
            fn = OUT / f"{tid}_{cond}.txt"
            fn.write_text(build(tid, cond, spec))
            written.append(fn.name)
    print(f"wrote {len(written)} R prompt files to prompts_r/:", ", ".join(written))

if __name__ == "__main__":
    main()
