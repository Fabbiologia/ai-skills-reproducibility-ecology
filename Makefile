# Reproducibility targets.
#
# This repository holds the study, not the paper: the twelve tasks, the data, the
# 360 run records, the analysis and the figures. Everything below regenerates from
# the archived records without calling any model. The `runs` target calls paid
# model interfaces, so it is never part of `reproduce`.

PYTHON ?= python3

.PHONY: help setup refs analyze figures anon standard audit check reproduce runs all clean

help:               ## list the available targets
	@grep -hE '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | expand -t22

setup:              ## install Python dependencies
	$(PYTHON) -m pip install -r requirements.txt

refs:               ## recompute every reference value with two independent implementations
	$(PYTHON) main_study/tasks.py

analyze:            ## task-level statistics from the archived run records
	$(PYTHON) main_study/analyze.py

figures:            ## draw Figure 1 (design) and Figures 2 and 3 (results)
	$(PYTHON) main_study/make_design_figure.py
	$(PYTHON) main_study/make_figures.py

anon:               ## refuse to publish if anything on this branch identifies the authors
	$(PYTHON) check_anonymity.py

standard:           ## validate the proposed machine-readable specification manifests
	$(PYTHON) registry_standard/validate_skills.py

audit:              ## check archive completeness and print known provenance gaps
	$(PYTHON) audit_archive.py

check: standard audit anon  ## repository checks that generate nothing

reproduce: refs analyze figures  ## every number and figure in the paper, without calling a model

runs:               ## re-run the experiment; calls paid model interfaces and overwrites the records
	@echo "This calls paid model interfaces and overwrites main_study/run_records.csv."
	@echo "Set OPENAI_API_KEY and GEMINI_API_KEY, then run: $(PYTHON) main_study/run.py 5"

all: reproduce check ## reproduce everything and run the repository checks

clean:              ## remove generated outputs, keeping the raw run records and the data
	rm -f main_study/task_rates.json main_study/analysis_summary.json main_study/*.png
