# Provenance and audit status

This note records limitations that must stay visible in peer review and in any public
archive. Run `python audit_archive.py` before submission. Warnings describe known
gaps in the historical record; errors mean the archive structure is broken.

## The main study

- The 360 run records name the model that produced each run, the arm, the task, the
  returned value and the outcome of executing the returned script. The models were
  requested by the identifiers `gpt-4.1` and `gemini-pro-latest`, and the sampling
  temperature was left at its default value of one.
- Because the temperature is one, re-running the harness will not reproduce the
  archived records. The variation between runs is the phenomenon under study.
- Every reference value was computed twice by implementations written independently
  of one another, one using the operations of a data-analysis library and one as a
  direct loop over the records, and a reference was accepted only where the two
  agreed. `python main_study/tasks.py` recomputes both and re-checks the agreement.
- Tolerances were fixed before the runs, but they were chosen by us.
- A reference is correct given the quantity its task states, and the choice of
  quantity is ours. For a question such as what counts as a survey unit, an ecologist
  could state a different quantity and be right to do so.

## The supporting runs

These are reported in the manuscript as description, with no statistical test applied
and no conclusion resting on them. The reasons are recorded here.

- They cover four tasks, which is too few to compare conditions with the task as the
  unit of replication in the way the twelve tasks allow.
- Their records do not carry the exact model identifier, provider release, harness
  version or decoding configuration for every run. These must not be reconstructed
  from memory. The workflow scripts now refuse to start a new run set until those
  fields are declared, and then store them with every record.
- The whole-report archives retain the structured values and the grades but not the
  full report text that was graded, so those runs cannot be regraded independently
  from the current files. The corrected workflows retain the text and the provenance
  for any future run.
- The Python and R arms use each language's own estimator and its own random-number
  implementation. They are a comparison between implementations, not evidence of
  bitwise equivalence for one algorithm, which is why the manuscript reports the
  classifier task returning 0.8806 in one language and 0.8657 in the other as a limit
  on what a specification can fix.

## Data

- The LTEM Cabo Pulmo reef-fish extract is restricted and excluded by `.gitignore`.
  Its aggregate outputs are archived and the access note is in
  `data/ltem_cabo_pulmo_2023.csv.README.md`. The deterministic reproduction does not
  need the file. Re-running the two reef-fish tasks does.

## Registration

The study was not preregistered.
