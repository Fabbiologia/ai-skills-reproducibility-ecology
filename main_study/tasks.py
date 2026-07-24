#!/usr/bin/env python3
"""Task set for the confirmatory study.

Twelve ecological analysis tasks spanning four fork types and four datasets.
A "fork" is a point where a competent analyst could reasonably compute something
different from the same question; the specification pins it down.

Each task carries:
  question  the informally posed question, with the fork left open (what an
            ecologist would actually type)
  spec      the formal contract that closes the fork
  ref_a/b   two INDEPENDENT implementations of the specified estimand

The reference is accepted only when the two implementations agree. That is what
makes it defensible: once the estimand is stated, the answer is determined by
arithmetic, not by our preference. Run this file to compute and verify them.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).parent
DATA = HERE.parent / "data"
PDATA = HERE / "data"

IRIS = DATA / "iris.csv"
PENG = DATA / "penguins.csv"
PORTAL = PDATA / "portal_surveys.csv"
REEF = DATA / "ltem_cabo_pulmo_2023.csv"

SEP_L, SEP_W = "sepal length (cm)", "sepal width (cm)"


def _clf_accuracy(X, y, seed=42, test_size=0.2):
    """Fixed protocol shared by the model-fitting tasks."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.metrics import accuracy_score
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size,
                                          random_state=seed, stratify=y)
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    m.fit(Xtr, ytr)
    return float(accuracy_score(yte, m.predict(Xte)))


# ----------------------------------------------------------------------------
# F1  AGGREGATION: what is the sampling unit before you average?
# ----------------------------------------------------------------------------
def reef_a():
    d = pd.read_csv(REEF)
    return float(d.groupby(["Reef", "Transect"])["Biomass"].sum().mean())


def reef_b():
    d = pd.read_csv(REEF)
    tot = {}
    for reef, tr, b in zip(d["Reef"], d["Transect"], d["Biomass"]):
        tot.setdefault((reef, tr), 0.0)
        if pd.notna(b):
            tot[(reef, tr)] += float(b)
    return float(np.mean(list(tot.values())))


def portal_abund_a():
    d = pd.read_csv(PORTAL)
    return float(d[d.taxa == "Rodent"].groupby(["plot_id", "year"]).size().mean())


def portal_abund_b():
    d = pd.read_csv(PORTAL)
    c = {}
    for p, y, t in zip(d["plot_id"], d["year"], d["taxa"]):
        if t == "Rodent":
            c[(p, y)] = c.get((p, y), 0) + 1
    return float(sum(c.values()) / len(c))


def portal_rich_a():
    d = pd.read_csv(PORTAL)
    r = d[(d.taxa == "Rodent") & d.species_id.notna()]
    return float(r.groupby(["plot_id", "year"])["species_id"].nunique().mean())


def portal_rich_b():
    d = pd.read_csv(PORTAL)
    s = {}
    for p, y, sp, t in zip(d["plot_id"], d["year"], d["species_id"], d["taxa"]):
        if t == "Rodent" and isinstance(sp, str) and sp == sp:
            s.setdefault((p, y), set()).add(sp)
    return float(np.mean([len(v) for v in s.values()]))


# ----------------------------------------------------------------------------
# F2  SCOPE: pooled across groups, or within them?
# ----------------------------------------------------------------------------
def iris_corr_a():
    d = pd.read_csv(IRIS)
    return float(stats.pearsonr(d[SEP_L], d[SEP_W])[0])


def iris_corr_b():
    d = pd.read_csv(IRIS)
    return float(np.corrcoef(d[SEP_L].values, d[SEP_W].values)[0, 1])


def peng_corr_a():
    d = pd.read_csv(PENG).dropna(subset=["bill_length_mm", "bill_depth_mm"])
    return float(stats.pearsonr(d["bill_length_mm"], d["bill_depth_mm"])[0])


def peng_corr_b():
    d = pd.read_csv(PENG).dropna(subset=["bill_length_mm", "bill_depth_mm"])
    return float(np.corrcoef(d["bill_length_mm"].values, d["bill_depth_mm"].values)[0, 1])


def portal_corr_a():
    d = pd.read_csv(PORTAL)
    d = d[d.taxa == "Rodent"].dropna(subset=["hindfoot_length", "weight"])
    return float(stats.pearsonr(d["hindfoot_length"], d["weight"])[0])


def portal_corr_b():
    d = pd.read_csv(PORTAL)
    d = d[d.taxa == "Rodent"].dropna(subset=["hindfoot_length", "weight"])
    return float(np.corrcoef(d["hindfoot_length"].values, d["weight"].values)[0, 1])


# ----------------------------------------------------------------------------
# F3  MISSING DATA: absent records, and rows that are absent altogether
# ----------------------------------------------------------------------------
def peng_mass_a():
    d = pd.read_csv(PENG)
    d = d[d.species == "Gentoo"].dropna(subset=["sex", "body_mass_g"])
    return float(d[d.sex == "Female"]["body_mass_g"].mean())


def peng_mass_b():
    d = pd.read_csv(PENG)
    v = [m for sp, sx, m in zip(d["species"], d["sex"], d["body_mass_g"])
         if sp == "Gentoo" and isinstance(sx, str) and sx == "Female" and pd.notna(m)]
    return float(sum(v) / len(v))


def portal_dm_a():
    d = pd.read_csv(PORTAL)
    return float(d[d.species_id == "DM"]["weight"].dropna().mean())


def portal_dm_b():
    d = pd.read_csv(PORTAL)
    v = [w for s, w in zip(d["species_id"], d["weight"]) if s == "DM" and pd.notna(w)]
    return float(sum(v) / len(v))


def portal_zero_a():
    """Implicit zeros: plot-years with no rodent captures are absent from the
    file but are real zeros, so the full plot x year grid must be used."""
    d = pd.read_csv(PORTAL)
    r = d[d.taxa == "Rodent"]
    plots, years = sorted(d.plot_id.unique()), sorted(d.year.unique())
    idx = pd.MultiIndex.from_product([plots, years], names=["plot_id", "year"])
    return float(r.groupby(["plot_id", "year"]).size().reindex(idx, fill_value=0).mean())


def portal_zero_b():
    d = pd.read_csv(PORTAL)
    n_units = d.plot_id.nunique() * d.year.nunique()
    n_rod = int((d.taxa == "Rodent").sum())
    return float(n_rod / n_units)


# ----------------------------------------------------------------------------
# F4  RANDOMNESS: seed, split and scaling in a fitted model
# ----------------------------------------------------------------------------
PENG_X = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]


def peng_clf_a():
    d = pd.read_csv(PENG).dropna(subset=PENG_X + ["sex"])
    return _clf_accuracy(d[PENG_X].values, d["sex"].values)


def peng_clf_b():
    d = pd.read_csv(PENG)
    d = d[~d[PENG_X + ["sex"]].isna().any(axis=1)]
    return _clf_accuracy(d[PENG_X].to_numpy(), d["sex"].to_numpy())


IRIS_X = [SEP_L, SEP_W, "petal length (cm)", "petal width (cm)"]


def iris_clf_a():
    d = pd.read_csv(IRIS)
    return _clf_accuracy(d[IRIS_X].values, d["target"].values)


def iris_clf_b():
    d = pd.read_csv(IRIS)
    return _clf_accuracy(d[IRIS_X].to_numpy(), d["target"].to_numpy())


def portal_clf_a():
    d = pd.read_csv(PORTAL)
    d = d[d.species_id.isin(["DM", "DO"])].dropna(subset=["weight", "hindfoot_length"])
    return _clf_accuracy(d[["weight", "hindfoot_length"]].values, d["species_id"].values)


def portal_clf_b():
    d = pd.read_csv(PORTAL)
    d = d[d.species_id.isin(["DM", "DO"])]
    d = d[~d[["weight", "hindfoot_length"]].isna().any(axis=1)]
    return _clf_accuracy(d[["weight", "hindfoot_length"]].to_numpy(), d["species_id"].to_numpy())


# ----------------------------------------------------------------------------
TASKS = [
    dict(id="A1_reef_biomass", fork="aggregation", dataset="reef", tol=1e-2,
         file=str(REEF), ref_a=reef_a, ref_b=reef_b,
         question="Report the mean per-transect fish biomass for the reserve, that is, the "
                  "community biomass on a transect averaged across transects.",
         spec="A survey unit is a unique (Reef, Transect) combination. Use the Biomass column "
              "as the per-record biomass and treat records with no biomass value as contributing "
              "nothing. Do not re-normalise by Area. Sum biomass within each survey unit, then "
              "take the mean of those per-unit totals."),
    dict(id="A2_portal_abundance", fork="aggregation", dataset="portal", tol=1e-2,
         file=str(PORTAL), ref_a=portal_abund_a, ref_b=portal_abund_b,
         question="How many rodents were captured per plot per year, on average?",
         spec="Restrict to records where taxa is 'Rodent'. A sampling unit is a unique "
              "(plot_id, year) combination that appears in the data. Count the records in each "
              "unit, then report the mean of those counts across units."),
    dict(id="A3_portal_richness", fork="aggregation", dataset="portal", tol=1e-2,
         file=str(PORTAL), ref_a=portal_rich_a, ref_b=portal_rich_b,
         question="What is the mean rodent species richness of a plot in a year?",
         spec="Restrict to records where taxa is 'Rodent' and species_id is present. A sampling "
              "unit is a unique (plot_id, year) combination that appears in the data. Richness is "
              "the number of distinct species_id values in a unit. Report the mean richness "
              "across units."),

    dict(id="S1_iris_corr", fork="scope", dataset="iris", tol=1e-3,
         file=str(IRIS), ref_a=iris_corr_a, ref_b=iris_corr_b,
         question="What is the correlation between sepal length and sepal width?",
         spec="Compute a single Pearson correlation over all rows pooled together, without "
              "splitting or conditioning on species."),
    dict(id="S2_penguin_bill_corr", fork="scope", dataset="penguins", tol=1e-3,
         file=str(PENG), ref_a=peng_corr_a, ref_b=peng_corr_b,
         question="What is the correlation between bill length and bill depth?",
         spec="Compute a single Pearson correlation over all rows pooled together, without "
              "splitting or conditioning on species. Use only rows where both measurements are "
              "present."),
    dict(id="S3_portal_hf_weight_corr", fork="scope", dataset="portal", tol=1e-3,
         file=str(PORTAL), ref_a=portal_corr_a, ref_b=portal_corr_b,
         question="How strongly are hindfoot length and body weight related in this rodent "
                  "community?",
         spec="Restrict to records where taxa is 'Rodent'. Compute a single Pearson correlation "
              "over all such rows pooled together, without splitting or conditioning on species. "
              "Use only rows where both measurements are present."),

    dict(id="M1_penguin_gentoo_mass", fork="missing", dataset="penguins", tol=1e-2,
         file=str(PENG), ref_a=peng_mass_a, ref_b=peng_mass_b,
         question="What is the mean body mass of female Gentoo penguins?",
         spec="Restrict to species 'Gentoo'. Drop records where either sex or body_mass_g is "
              "missing, then report the mean body_mass_g of the records with sex 'Female'."),
    dict(id="M2_portal_dm_weight", fork="missing", dataset="portal", tol=1e-2,
         file=str(PORTAL), ref_a=portal_dm_a, ref_b=portal_dm_b,
         question="What is the mean weight of Dipodomys merriami (species_id 'DM')?",
         spec="Restrict to records with species_id 'DM'. Exclude records whose weight is missing; "
              "do not treat a missing weight as zero. Report the mean of the remaining weights."),
    dict(id="M3_portal_implicit_zeros", fork="missing", dataset="portal", tol=1e-2,
         file=str(PORTAL), ref_a=portal_zero_a, ref_b=portal_zero_b,
         question="Across the whole survey, what is the mean number of rodents caught in a plot "
                  "in a year?",
         spec="Restrict to records where taxa is 'Rodent'. The sampling units are every "
              "combination of a plot_id and a year that occur anywhere in the file, so a plot-year "
              "with no rodent records is a real zero and must be counted as zero rather than "
              "omitted. Report the mean count over all such units."),

    dict(id="R1_penguin_sex_clf", fork="randomness", dataset="penguins", tol=1e-3,
         file=str(PENG), ref_a=peng_clf_a, ref_b=peng_clf_b,
         question="How accurately can a penguin's sex be predicted from its body measurements?",
         spec="Predictors are bill_length_mm, bill_depth_mm, flipper_length_mm and body_mass_g; "
              "the target is sex. Drop records with any missing value among those five columns. "
              "Standardise the predictors with StandardScaler fitted on the training data only "
              "(use a pipeline). Split with train_test_split(test_size=0.2, random_state=42, "
              "stratify=y). Fit LogisticRegression(max_iter=2000). Report accuracy on the held-out "
              "test set."),
    dict(id="R2_iris_species_clf", fork="randomness", dataset="iris", tol=1e-3,
         file=str(IRIS), ref_a=iris_clf_a, ref_b=iris_clf_b,
         question="How accurately can the iris species be predicted from the four measurements?",
         spec="Predictors are the four measurement columns; the target is the 'target' column. "
              "Standardise the predictors with StandardScaler fitted on the training data only "
              "(use a pipeline). Split with train_test_split(test_size=0.2, random_state=42, "
              "stratify=y). Fit LogisticRegression(max_iter=2000). Report accuracy on the held-out "
              "test set."),
    dict(id="R3_portal_species_clf", fork="randomness", dataset="portal", tol=1e-3,
         file=str(PORTAL), ref_a=portal_clf_a, ref_b=portal_clf_b,
         question="How accurately can the two Dipodomys species (DM and DO) be told apart from "
                  "weight and hindfoot length?",
         spec="Restrict to records with species_id 'DM' or 'DO' and drop records missing weight or "
              "hindfoot_length. Predictors are weight and hindfoot_length; the target is "
              "species_id. Standardise the predictors with StandardScaler fitted on the training "
              "data only (use a pipeline). Split with train_test_split(test_size=0.2, "
              "random_state=42, stratify=y). Fit LogisticRegression(max_iter=2000). Report accuracy "
              "on the held-out test set."),
]


def build(verbose=True):
    out = {}
    if verbose:
        print(f"{'task':28}{'fork':12}{'impl A':>18}{'impl B':>18}  agree")
    for t in TASKS:
        a, b = t["ref_a"](), t["ref_b"]()
        agree = abs(a - b) <= 1e-9 * max(1.0, abs(a))
        if verbose:
            print(f"{t['id']:28}{t['fork']:12}{a:>18.10f}{b:>18.10f}  {agree}")
        if not agree:
            raise AssertionError(f"{t['id']}: independent implementations disagree ({a} vs {b})")
        # relative to the repository root: an absolute path would only work on the
        # machine that generated the file, and the archive has to run from a clone
        rel = str(Path(t["file"]).resolve().relative_to(HERE.parent))
        out[t["id"]] = dict(fork=t["fork"], dataset=t["dataset"], file=rel,
                            question=t["question"], spec=t["spec"],
                            reference=a, tolerance=t["tol"])
    (HERE / "references.json").write_text(json.dumps(out, indent=2))
    if verbose:
        print(f"\nAll {len(out)} references verified by two independent implementations.")
        print("Wrote main_study/references.json")
    return out


if __name__ == "__main__":
    build()
