# Do AI skills improve the output reproducibility of ecological analyses? A controlled ablation experiment

**Companion empirical study to** *ChatMPA_PRISMA_Review_AI_Skills_Reproducibility*.
The review's principal finding was that the intersection **AI skills × output
reproducibility × ecology is empirically empty** — no primary study has directly
tested it. This experiment is a direct, purpose-built test that fills that gap and
implements the design proposed in the review's Section 4.3.

**Status:** completed. 200/200 runs successful. **Date:** 2026-07-02.

---

## 1. Design

A fully-crossed **4 (task) × 5 (skill-richness) factorial with 10 independent
replicate runs per cell = 200 runs**. Each run is a fresh autonomous agent given a
**byte-identical** prompt, required to *actually execute Python* and return a
structured result. Within a cell the only thing that varies is the agent's own
run-to-run stochasticity — operationalising exactly the "run-to-run output
variability" the review flags as the distinctive risk LLMs introduce
(Themes 2 and 4). All materials are self-contained and re-runnable.

### 1.1 Tasks (chosen to span reproducibility failure modes and domains)

| ID | Dataset | Domain | Dominant "fork" (source of divergence) | Reference value |
|----|---------|--------|----------------------------------------|-----------------|
| **T1** | iris | classic/botanical | correlation *scope* — Simpson's paradox (pooled −0.118 vs within-species +0.575), a **sign-flip** trap | r = −0.1176 |
| **T2** | Palmer penguins | ecology | **stochastic** ML choices (model, split, seed, scaling) predicting sex | acc = 0.8806 |
| **T3** | Palmer penguins | ecology | *effect-size metric* / test choice for body-mass difference among species | η² = 0.6697 |
| **T4** | **LTEM reef-fish (real marine survey, Cabo Pulmo 2023)** | marine ecology | *transect-aggregation recipe* (survey-unit definition); naive row-mean is ~30× too low | 3.4642 |

References are the value produced by the canonical (C4-specified) recipe, computed
independently. T4's reference equals the value the operational LTEM database tool
reports for the same region-year, giving the detailed skill external validity.

### 1.2 Conditions — a cumulative feature ablation (the independent variable)

Each rung *adds* structure to the previous one, so differences between adjacent
rungs isolate the contribution of a specific skill feature:

| Rung | Adds | Isolates |
|------|------|----------|
| **C0 none** | bare task | baseline agent default |
| **C1 basic** | generic procedural steps ("load; do the analysis; report"). *More verbose, no constraints.* | effect of verbosity without constraint |
| **C2 contract** | fixes the **input** (dataset, columns, NaN/filter policy, survey-unit/scope) and the **method** (exact estimator/test/metric) | effect of specifying *what to compute* |
| **C3 +controls** | fixes all **stochastic knobs** (random seed, split ratio, scaling) | effect of *stochastic control* |
| **C4 full** | adds **validation checklist + explicit failure-mode prohibitions** | effect of *anti-pattern warnings* |

### 1.3 Outcome measures (output-level, per the review's definition)

Scored across the 10 runs in each cell: **run-to-run** — SD, CV, number of distinct
answers (within tolerance), exact-match rate (fraction equal to the modal answer);
and **validity** — fraction matching the reference within tolerance. Categorical
agreement (method/direction) also recorded. Environment: scikit-learn 1.9.0,
scipy 1.16.3, numpy 2.4.6.

---

## 2. Results

### 2.1 Summary table (10 runs per cell)

| Task | Cond | SD | #distinct | Exact-match | **Validity** | \|Δref\| |
|------|------|-----|-----------|-------------|--------------|---------|
| **T1** iris corr | C0–C4 | 0.000 | 1 | 100% | 100% | 0.000 |
| **T2** penguin clf | C0 none | 0.0061 | 2 | 50% | 50% | 0.006 |
| | C1 basic | 0.0090 | 3 | 60% | **30%** | 0.012 |
| | C2 contract | 0.0086 | 3 | 50% | 40% | 0.005 |
| | **C3 +controls** | **0.000** | **1** | **100%** | **100%** | 0.000 |
| | C4 full | 0.000 | 1 | 100% | 100% | 0.000 |
| **T3** penguin ANOVA | C0–C4 | 0.000 | 1 | 100% | 100% | 0.000 |
| **T4** LTEM biomass | C0 none | 0.000 | 1 | 100% | **0%** | 0.169 |
| | C1 basic | 0.000 | 1 | 100% | **0%** | 0.169 |
| | **C2 contract** | 0.000 | 1 | 100% | **100%** | 0.000 |
| | C3 +controls | 0.000 | 1 | 100% | 100% | 0.000 |
| | C4 full | 0.000 | 1 | 100% | 100% | 0.000 |

Figures: `results/fig1_value_strips.png` (all values by condition),
`fig2_reproducibility_gradient.png` (SD/CV gradient), `fig3_heatmaps.png`
(reproducibility vs validity heatmaps).

### 2.2 Inferential tests

- **T2 run-to-run agreement** rose from 16/30 (low-skill C0–C2) to 20/20
  (high-skill C3–C4): Fisher exact **p = 2.2×10⁻⁴**. Low-skill pooled SD = 0.0086,
  bootstrap 95% CI [0.0063, 0.0109] (**excludes 0**); high-skill SD = 0.0000.
- **T2 validity** rose from 12/30 to 20/20: Fisher exact **p = 8.4×10⁻⁶**.
- **T4 validity** rose from 0/20 (pre-contract C0–C1) to 30/30 (contract+ C2–C4):
  Fisher exact **p = 2.1×10⁻¹⁴**, while **reproducibility stayed 100% throughout**.

---

## 3. Findings

**F1 — Reproducibility is high by default; skills matter at the margin, not
everywhere.** Three of four tasks (T1, T3, T4) were 100% reproducible even with no
skill: capable agents converge on a dominant default (pooled Pearson; one-way
ANOVA with η²; sum-within-transect biomass). The catastrophic ~30× transect-mean
error was *never* made, even at C0. Fear of pervasive LLM chaos is overstated for
routine analyses — the leaks are specific and identifiable.

**F2 — Where genuine stochasticity exists, only fixing the stochastic controls
removes it (T2).** Specifying the method (C2) was *not enough*: with model fixed
but seed/split/scaling free, T2 still produced 3 distinct answers and 50% agreement.
Adding the seed/split/scaling controls (C3) collapsed variance to exactly zero
(20/20 identical, p = 2×10⁻⁴). The **random seed is the single highest-leverage
element for stochastic tasks** — and nothing below it in the ladder substitutes.

**F3 — Reproducibility ≠ validity, and they are fixed by different skill features
(T4).** The marine-biomass task was perfectly reproducible at every rung, yet
*systematically wrong* under no/basic skill: all 20 low-skill runs agreed on 3.2952
(they defined the survey unit as Reef+Habitat+Transect) versus the reference 3.4642
(Reef+Transect). The fix was the **input/method contract (C2)** — pinning the
survey-unit definition — not the seed and not failure-mode warnings. A consistent
pipeline can consistently reproduce the wrong number; only an explicit contract
aligns it. This is direct empirical support for the review's Theme 4.

**F4 — A basic (verbose-but-unconstraining) skill does not help and can hurt.**
For T2, the basic skill (C1) *increased* run-to-run SD (0.006→0.009) and *lowered*
validity (50%→30%) relative to no skill, because "train a classifier" invited free
model choice (agents drifted to RandomForest with varied splits) and pulled results
away from the reference. Verbosity is not the active ingredient — **constraint is**.
(A companion iris-classifier run showed the same direction more starkly: basic-skill
SD 0.044 vs 0.000 for the detailed skill.)

**F5 — Adding a skill essentially never degraded the fully-specified result.** C3
and C4 achieved 100% reproducibility and 100% validity on every task; the checklist
and failure-mode warnings (C3→C4) added no measurable harm and serve as cheap
insurance/guards even where they were not the binding constraint.

---

## 4. What a skill must contain to improve output reproducibility

Ranked by the contribution *observed here*, with the caveat that the binding
element is **task-dependent** — a good skill first identifies the task's dominant
fork, then constrains it:

1. **Fix the stochastic controls** — random seed / `random_state`, split ratio,
   scaling. Decisive whenever the task has any stochastic component (T2). Without
   it, results vary by construction; with it, they are identical.
2. **Fix the input/method contract** — dataset, columns, NaN/filter policy, the
   **unit of aggregation**, and the exact estimator/test/metric. Decisive whenever
   a domain convention is ambiguous (T4 survey unit; effect-size metric). This is
   what converts a reproducible-but-biased result into a correct one.
3. **State an output reference / tolerance** — so "reproducible" can be checked
   against "correct," not just against other runs.
4. **Explicit failure-mode prohibitions + validation checklist** — cheap guards
   that close known traps (per-species correlation; row-level biomass mean;
   dropping the seed). Low marginal cost, useful insurance.

**Elements that did *not* help on their own:** prose length, generic step lists,
and encouragement without fixed choices (rung C1 — the worst-performing skilled
condition). **Design rule for skill authors: a skill improves reproducibility in
proportion to the number of free choices it *removes*, not the number of words it
*adds*. Write skills as contracts (fixed parameters, exact calls, named unit
definitions, explicit prohibitions), not as tutorials.**

---

## 5. Limitations

Four tasks, three datasets, one model family (scikit-learn), one agent vendor, 10
replicates per cell. Three tasks had a strong correct default, so the ablation's
"stochastic-control" and "contract" effects rest on T2 and T4 respectively — clean
but each carried by one task. A single vendor/model means run-to-run variance here
reflects one system's stochasticity; cross-vendor variance is likely larger. The
experiment measures *output* reproducibility of scalar results; multi-step pipelines
with cascading choices (the review's motivating case) may behave differently. The
registered full study should: add ≥2 tasks per fork type, ≥20 replicates, a
"contract-without-seed" arm on additional stochastic tasks, multi-step ecological
workflows, and ≥2 model vendors; and pre-register tolerances per outcome.

## 6. Reproducibility of this experiment
`PROTOCOL`-equivalent design in §1; `data/` holds the exact CSVs (iris, penguins,
`ltem_cabo_pulmo_2023.csv`); `prompts/` holds all 20 byte-identical condition files
(the independent variable); `run_experiment.workflow.js` ran the 200 agents;
`results_v2.json` holds every run; `analyze_v2.py` reproduces all tables and
figures; `data/references.json` holds the canonical references.
