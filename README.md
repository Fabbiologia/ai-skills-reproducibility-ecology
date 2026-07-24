# Repeated AI analyses of ecological data agree on wrong answers until the method is written down

> **Anonymised copy for double-anonymous peer review.** This is the `review`
> branch. The citation and licence metadata are anonymised and the institutions
> that hold the restricted data are not named. Everything needed to check the
> analysis is present and unchanged. The identified version is released on
> acceptance.

Code and data for the study of that title, prepared for *Methods in Ecology and
Evolution*. Everything needed to check every number and redraw every figure is
here, and none of it requires calling a model. The manuscript itself is not
archived here.

## What the study asks

An ecologist can describe an analysis to an artificial-intelligence tool in ordinary
words and receive a number. The study asks how often that number is correct, whether
writing the method down as a reusable specification improves matters, and whether it
does so more than supplying a working script.

Twelve tasks on four ecological datasets each pose a question the way an ecologist
would ask it, leaving one analytical choice open. Four kinds of open choice are
covered, with three tasks each, and no kind is confined to a single dataset:

| kind of open choice | what is left undecided |
|---|---|
| sampling unit | what is averaged over before a mean is taken |
| scope | whether an estimate is pooled across groups or computed within them |
| missing records | how absent values, and rows absent altogether, are treated |
| fitting a model | the split of the data, the random seed, the scaling |

Every task ran under three conditions, namely the question alone, the question with a
written specification, and the question with a working script for a different task of
the same kind. Each condition ran ten times across models from two companies, giving
360 runs. **The unit of replication is the task**, so each task contributes one
proportion per condition and conditions are compared across the twelve tasks with
paired Wilcoxon signed-rank tests. Repeated runs of one task are treated as repeated
measures of that task and never as independent observations.

**What was found.** The question alone reached the reference in 59 per cent of runs
across all twelve tasks and in 3 per cent on the five tasks where the choice was
genuinely open. A written specification raised these to 96 and 90 per cent, a working
script to 75 and 44 per cent. The specification beat the script across tasks
(P = 0.031) while the script was not distinguishable from no instruction (P = 0.094).

Agreement between runs tracked correctness poorly. The script made runs agree with
one another on 11 of 12 tasks, exactly as often as the specification did, while
reaching the correct value far less often, and on one task **all ten runs given a
working script returned the same wrong number**. Repeating the analysis, rewriting it
in a second language, or trying another company's model would each have confirmed
that error.

## Layout

```
for_submission/
├── main_study/            the twelve tasks: all inference rests on this
│   ├── tasks.py           task definitions; every reference computed twice, independently
│   ├── references.json    the twelve questions, specifications, references and tolerances
│   ├── run.py             the harness: 12 tasks x 3 conditions x 2 models x 5 repeats
│   ├── run_records.csv     the 360 run records
│   ├── analyze.py         task-level statistics, paired tests, agreement, sensitivity
│   ├── make_design_figure.py  Figure 1, the design schematic
│   ├── make_figures.py    Figures 2 and 3
│   └── data/portal_surveys.csv
├── transfer_runs/         how far a specification carries when the data are presented differently
├── supporting_runs/       earlier runs reported as description only, with no test applied
│   ├── results_v2.json, results_v2_R.json      the Python and R arms
│   ├── analyze_cross_language.py               Python against R
│   ├── crossprovider_harness.py, analyze_providers.py   five models, three companies
│   ├── report_reproducibility/                 whole-report runs
│   ├── prompts/, prompts_r/                    the prompts as they were sent
│   └── results/                                summary tables
├── registry_standard/     proposed machine-readable manifest for a shared collection
├── data/                  iris, penguins, and the access note for the restricted reef data
├── audit_archive.py       structural and provenance audit
├── PROVENANCE.md          known gaps, stated rather than papered over
└── Makefile               make help
```

## Reproducing it

Python 3.11 or later.

```bash
make setup && make reproduce
```

`make reproduce` recomputes every reference value with two independent
implementations, regenerates the statistics from the archived run records, and
redraws the three figures. It calls no model and is deterministic, so every number
in the paper can be checked against the records without spending anything.
`make check` runs the archive audit and validates the proposed manifests.
`make help` lists the targets.

To re-run the experiment itself, set `OPENAI_API_KEY` and `GEMINI_API_KEY` and run
`python main_study/run.py 5`. This calls paid interfaces, costs money, and will not
reproduce the archived records exactly, because the models sample at a temperature of
one. That is the phenomenon under study rather than a defect of the harness.

### In a container

```bash
docker build -t spec-repro . && docker run --rm -v "$PWD:/work" spec-repro
```

## Two layers of reproducibility, kept apart

Everything downstream of the run records is deterministic and regenerates here. The
run records themselves came from calling models, and calling them again will give
different records. The main study names the models it used, `gpt-4.1` and
`gemini-pro-latest`, and the temperature, which was left at its default of one.

The supporting runs are older and their records do not carry the model identifier or
the decoding settings for every run, and the whole-report records do not retain the
full text that was graded. This is one reason those runs are reported as description
with no test applied, and it is stated in the manuscript as well as in
`PROVENANCE.md`. It is a gap in the record, not something to be reconstructed from
memory.

## Data

- **iris.csv** — Fisher's iris measurements, via scikit-learn.
- **penguins.csv** — Palmer Penguins (Horst, Hill and Gorman 2020; data from Gorman et
  al. 2014), via seaborn. CC0.
- **portal_surveys.csv** — twenty six years of rodent capture records from the Portal
  Project long-term survey.
- **ltem_cabo_pulmo_2023.csv** — **not distributed here**. A 2023 extract of reef-fish
  transect records from the Long-Term Ecological Monitoring programme in Cabo Pulmo
  National Park, Gulf of California. Available on request from the monitoring programme; see
  `data/ltem_cabo_pulmo_2023.csv.README.md`. The deterministic reproduction does not
  need it. Re-running the two reef-fish tasks does.

Code is released under the MIT License. Text and figures are intended for release
under CC-BY 4.0 on publication.

## Citing

See `CITATION.cff`. Please cite the manuscript once published, and this repository
with its Zenodo DOI until then.

## What this repository does not contain

The manuscript, the Supporting Information, the title page and the cover letter
are not archived here, nor are the scripts that build them. This repository is the
study rather than the paper. The figures it produces are the figures the paper
prints, and the analysis it runs produces every number the paper quotes, so the
two can be checked against one another without the documents being present.

## What the study does not show

Twelve tasks on four datasets is a small sample of ecological analysis, and each kind
of open choice rests on three tasks. Two companies' models were used in the main
study. The reference values are correct given the quantity each task states, but the
choice of quantity is ours; an ecologist could define a survey unit differently and be
right to do so. What the results show is that the value returned without a
specification did not match the quantity the question intended, not that one
convention is universally correct. The tasks are single steps rather than multi-step
analyses in which one choice feeds the next.
