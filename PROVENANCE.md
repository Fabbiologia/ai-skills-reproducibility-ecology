# Provenance and audit status

This note records limitations that must remain visible in peer review and any public archive.

- The 2026 archival scalar-result records do not contain the exact LLM model identifier, provider release, harness version, or decoding configuration. These settings must not be reconstructed from memory. The workflow scripts now refuse to create a new run set until those fields are declared and then store them with every record.
- The standard and hard report archives retain structured values and judge grades, but not the full `report_md` text that the judge saw. The report-level findings are therefore exploratory and cannot be independently regraded from the current JSON files. The corrected workflows now retain `report_md` and provenance for future runs.
- The experiment was not preregistered. Fisher tests are exploratory summaries of two visible transition points and do not justify inference to all ecological tasks.
- The LTEM Cabo Pulmo CSV is restricted and excluded by `.gitignore`; its aggregate outputs are archived, and access instructions are in `data/ltem_cabo_pulmo_2023.csv.README.md`. The deterministic downstream analysis and document build do not require the restricted file, but end-to-end rerunning of Task T4 does.
- The Python and R classifier arms use different language-native estimators and random-number implementations. They are a cross-implementation comparison, not evidence of bitwise cross-language equivalence for one algorithm.

Run `python audit_archive.py` before submission. Warnings describe known historical gaps; errors indicate a broken archive structure.
