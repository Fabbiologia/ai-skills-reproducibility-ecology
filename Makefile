# Reproducibility targets.
#
# The deterministic layer regenerates every number, figure and document in the
# paper from the archived run records, without calling any model. The `runs`
# target calls paid model interfaces, so it is never part of `reproduce`.

PYTHON ?= python3

.PHONY: help setup refs analyze figures docs verify standard audit check reproduce runs all clean

help:               ## list the available targets
	@grep -hE '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | expand -t22

setup:              ## install Python and Node dependencies
	$(PYTHON) -m pip install -r requirements.txt
	cd manuscript && npm install

refs:               ## recompute every reference value with two independent implementations
	$(PYTHON) main_study/tasks.py

analyze:            ## task-level statistics from the archived run records
	$(PYTHON) main_study/analyze.py

figures:            ## draw Figures 1 and 2
	$(PYTHON) main_study/make_figures.py

docs:               ## rebuild the manuscript, SI, title page and cover letter (.docx)
	cd manuscript && node build_paper2.js && node build_si2.js && node build_title_page2.js && node build_cover_letter2.js

verify:             ## check the built documents still agree with the analysis
	$(PYTHON) verify_documents.py

standard:           ## validate the proposed machine-readable specification manifests
	$(PYTHON) registry_standard/validate_skills.py

audit:              ## check archive completeness and print known provenance gaps
	$(PYTHON) audit_archive.py

check: standard audit verify  ## repository checks that generate nothing

reproduce: refs analyze figures docs verify  ## everything in the paper, without calling a model

runs:               ## re-run the experiment; calls paid model interfaces and overwrites the records
	@echo "This calls paid model interfaces and overwrites main_study/run_records.csv."
	@echo "Set OPENAI_API_KEY and GEMINI_API_KEY, then run: $(PYTHON) main_study/run.py 5"

all: reproduce check ## reproduce everything and run the repository checks

clean:              ## remove generated outputs, keeping the raw run records and the data
	rm -f main_study/task_rates.json main_study/*.png
	rm -f manuscript/*.pdf
	rm -rf manuscript/_preview
