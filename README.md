# Skills as the new packages: a standard for good AI analysis skills

Reproducibility repository for the manuscript **"Skills as the new packages: an
evidence-based standard for good AI analysis skills and a curated repository for
ecology"** (target journal: *Methods in Ecology and Evolution*).

The paper argues that AI skills are becoming a reusable unit of analysis, like R
packages on CRAN, and uses two controlled experiments to work out what a skill must
contain and be tested for to deserve a place in a curated repository for Model
Context Protocol (MCP) servers and skills.

This repository contains everything needed to reproduce the experiment, its figures
and statistics, and to rebuild the manuscript and Supporting Information documents
from source.

---

## What the study does

AI *skills* are reusable, structured instructions for LLM and agent tools. No earlier
study had directly tested whether they improve the **output reproducibility** of
ecological analyses. This repository holds a controlled experiment that tests it: a
fully crossed **4 (task) by 5 (skill level) by 2 (language: Python and R) by 10
(replicate) = 400-run** design in which independent LLM agents each run an analysis
and return a structured result. The five skill levels add one kind of instruction at
a time (none, basic, contract, controls, full), so the experiment shows which part of
a skill does the work, and the two languages test whether different code reaches the
same answer. A short literature review sets the context and is not a formal
systematic review.

**Headline result:** skills improve output reproducibility through *constraint*, not
verbosity, and the decisive feature is task-dependent. Fix the stochastic controls
(seed/split/scaling) where randomness exists, and fix the input/method contract where
a domain convention is ambiguous. Reproducibility and validity are separable: an
analysis can be perfectly consistent yet consistently wrong. Python and R give the
same answer for the deterministic tasks, but not for the classifier, where the two
languages use different random number generators.

---

## Repository structure

```
for_submission/
├── README.md                     ← this file
├── LICENSE                       ← MIT (code) + data/docs terms below
├── CITATION.cff                  ← citation metadata
├── requirements.txt              ← Python dependencies (tested versions)
├── environment.yml               ← conda alternative
├── Makefile                      ← reproduce / build targets
├── Dockerfile                    ← containerised reproduction of analysis + docs
├── REPORT_v2.md                  ← plain-text findings report
│
├── generate_prompts.py           ← writes the 20 Python condition prompts (the independent variable)
├── generate_prompts_r.py         ← writes the 20 R condition prompts
├── run_experiment.workflow.js    ← orchestration that launched the 200 Python agent runs
├── run_experiment_r.workflow.js  ← orchestration that launched the 200 R agent runs
├── analyze_v2.py                 ← scores the Python arm; regenerates its tables + figures
├── analyze_cross_language.py     ← scores R and the Python-vs-R comparison; draws the comparison figure
├── generate_prisma_flow.py       ← draws the literature-selection diagram (Figure S1)
├── results_v2.json               ← the 200 Python run-level records (raw experimental data)
├── results_v2_R.json             ← the 200 R run-level records (raw experimental data)
│
├── data/                         ← input datasets + canonical references
│   ├── iris.csv
│   ├── penguins.csv
│   ├── ltem_cabo_pulmo_2023.csv.README.md  ← real reef-fish data NOT included; available on request
│   ├── references.json           ← Python reference values
│   └── references_R.json         ← R reference values (T2 differs: 0.8657)
├── prompts/                      ← the 20 Python condition prompts (T{1..4}_C{0..4}.txt)
├── prompts_r/                    ← the 20 R condition prompts (T{1..4}_C{0..4}.txt)
├── results/                      ← generated: summary tables (json/csv) + figures (png)
├── report_reproducibility/       ← second experiment: whole-report reproducibility + skill coherence
│   ├── FINDINGS.md               ← results write-up
│   ├── generate_report_prompts.py, run_report_experiment.workflow.js, analyze_report.py
│   ├── prompts/ (C0/C1/C2), results_report.json, references_report.json
│   └── results/fig_report_reproducibility.png
└── manuscript/                   ← Word documents + build scripts
    ├── Manuscript_AI_Skills_Reproducibility_MEE.docx
    ├── Supporting_Information_AI_Skills_Reproducibility_MEE.docx
    ├── Cover_Letter_MEE.docx / .md
    ├── theme.js, build_manuscript.js, build_si.js
    └── package.json
```

---

## Two reproducibility layers

**1. Deterministic (fully reproducible here).** Everything downstream of the raw run
data — all tables, statistics, figures, and the Word documents — regenerates exactly
from `results_v2.json` with `analyze_v2.py` and the manuscript build scripts. This is
what the `Makefile` / `Dockerfile` reproduce.

**2. The agent runs (require an LLM-agent harness).** `results_v2.json` was produced by
`run_experiment.workflow.js` orchestrating 200 independent LLM coding agents (built on
a single underlying model) via the Claude Code agent/workflow harness. The prompts
(`generate_prompts.py`, `prompts/`) and orchestration are provided in full for
transparency, but **re-running the agents requires that harness and will not
bit-reproduce**, because the agents are stochastic — which is precisely the
phenomenon the experiment measures. The provided `results_v2.json` is the archival
run set for the paper.

---

## Quickstart — reproduce the analysis and documents

Requires Python 3.11+ and Node.js 18+.

```bash
# 1. install dependencies
pip install -r requirements.txt
cd manuscript && npm install && cd ..

# 2. regenerate all tables, statistics and figures from the raw run data
python analyze_v2.py

# 3. rebuild the manuscript and Supporting Information .docx
cd manuscript && node build_manuscript.js && node build_si.js && cd ..
```

Or use the Makefile:

```bash
make setup       # pip install + npm install
make reproduce   # analyze_v2.py + rebuild both .docx (deterministic)
make all         # also regenerate the prompt files
```

### Containerised (Docker)

```bash
docker build -t mee-repro .
docker run --rm -v "$PWD:/work" mee-repro   # runs `make reproduce`
```

The container reproduces the deterministic layer (statistics, figures, documents).

---

## Re-running the agent experiment (optional, needs the harness)

1. Edit `run_experiment.workflow.js` and set `REPO` to the absolute path of your
   checkout (agents need an absolute path to read each prompt file).
2. Regenerate the prompt files: `python generate_prompts.py` (they use repo-relative
   data paths, so run agents with the working directory at the repository root).
3. Execute `run_experiment.workflow.js` in the Claude Code workflow harness. It runs
   4 tasks × 5 conditions × 10 replicates with a 3× retry per cell and enforced
   structured output, returning the run array (overwrite `results_v2.json`).
4. `python analyze_v2.py` to re-score.

---

## Data provenance and licensing

- **iris.csv** — Fisher's iris data, via scikit-learn (`sklearn.datasets.load_iris`).
- **penguins.csv** — Palmer Penguins (Horst, Hill & Gorman 2020; data from Gorman et
  al. 2014), via seaborn. CC0.
- **ltem_cabo_pulmo_2023.csv** — **not included in this repository** (available on
  request from the Aburto Lab; see `data/ltem_cabo_pulmo_2023.csv.README.md`). A 2023
  extract (2,798 reef-fish records, 10 reefs,
  41 transect units) from the Long-Term Ecological Monitoring (LTEM) programme,
  Cabo Pulmo National Park, Gulf of California. Provided here solely to reproduce the
  analysis; please contact the Aburto Lab regarding reuse of the monitoring data.

**Code** (`*.py`, `*.js`) is released under the MIT License (`LICENSE`).
**Text and figures** (manuscript, SI, `results/*.png`) are intended for release under
CC-BY 4.0 on publication.

---

## Citation

See `CITATION.cff`. Please cite the manuscript once published; until then cite this
repository and the archived OSF/Zenodo DOI (to be added on submission).

## Software environment (tested)

Python 3; numpy 2.4.6; scipy 1.16.3; scikit-learn 1.9.0; matplotlib; pandas; seaborn.
Node.js with `docx` 9.7.x for document generation.
