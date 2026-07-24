# Reproducibility targets.
#
# The deterministic layer regenerates every number, figure and document in the
# paper from the archived run records, without calling any model. The `runs`
# target calls paid model interfaces, so it is never part of `reproduce`.

PYTHON ?= python3

.PHONY: help setup refs analyze figures docs editable anon standard audit check reproduce runs all clean

help:               ## list the available targets
	@grep -hE '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | expand -t22

setup:              ## install Python and Node dependencies
	$(PYTHON) -m pip install -r requirements.txt
	cd manuscript && npm install

refs:               ## recompute every reference value with two independent implementations
	$(PYTHON) main_study/tasks.py

analyze:            ## task-level statistics from the archived run records
	$(PYTHON) main_study/analyze.py

figures:            ## draw Figure 1 (design) and Figures 2 and 3 (results)
	$(PYTHON) main_study/make_design_figure.py
	$(PYTHON) main_study/make_figures.py

docs:               ## rebuild the manuscript and Supporting Information (.docx)
	cd manuscript && node build_paper2.js && node build_si2.js

editable:           ## rebuild the editable PowerPoint of the design schematic (overwrites your edits)
	cd manuscript && node build_design_pptx.js

verify:             ## check the built documents still agree with the analysis
	$(PYTHON) verify_documents.py

standard:           ## validate the proposed machine-readable specification manifests
	$(PYTHON) registry_standard/validate_skills.py

anon:               ## refuse to publish if anything on this branch identifies the authors
	$(PYTHON) check_anonymity.py

audit:              ## check archive completeness and print known provenance gaps
	$(PYTHON) audit_archive.py

check: standard audit anon  ## repository checks that generate nothing

reproduce: refs analyze figures docs  ## everything in the paper, without calling a model

runs:               ## re-run the experiment; calls paid model interfaces and overwrites the records
	@echo "This calls paid model interfaces and overwrites main_study/run_records.csv."
	@echo "Set OPENAI_API_KEY and GEMINI_API_KEY, then run: $(PYTHON) main_study/run.py 5"

all: reproduce check ## reproduce everything and run the repository checks

clean:              ## remove generated outputs, keeping the raw run records and the data
	rm -f main_study/task_rates.json main_study/*.png
	rm -f manuscript/*.pdf
	rm -rf manuscript/_preview
