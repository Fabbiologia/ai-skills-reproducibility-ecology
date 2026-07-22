# Reproducibility targets for the MEE skills-reproducibility study.
# The deterministic layer (analyze, docs) regenerates everything from results_v2.json.

PYTHON ?= python3

.PHONY: setup prompts analyze prisma xlang report figures docs standard audit check reproduce all clean

setup:              ## install Python and Node dependencies
	$(PYTHON) -m pip install -r requirements.txt
	cd manuscript && npm install

prompts:            ## regenerate the Study 1 (Python + R) and Study 2 (report) prompt files
	$(PYTHON) generate_prompts.py
	$(PYTHON) generate_prompts_r.py
	cd report_reproducibility && $(PYTHON) generate_report_prompts.py && $(PYTHON) generate_hard_prompts.py

analyze:            ## regenerate Python result tables, statistics and figures from results_v2.json
	$(PYTHON) analyze_v2.py

xlang:              ## regenerate R + cross-language results and the Python-vs-R figure
	$(PYTHON) analyze_cross_language.py

prisma:             ## regenerate the literature selection diagram (Figure S1)
	$(PYTHON) generate_prisma_flow.py

report:             ## regenerate Study 2 (report-level) results and figures
	cd report_reproducibility && $(PYTHON) analyze_report.py && $(PYTHON) analyze_hard_report.py

figures: analyze xlang prisma report   ## all figures + statistics (Studies 1 and 2)

docs:               ## rebuild the manuscript, SI, cover letter and title page (.docx)
	cd manuscript && node build_manuscript.js && node build_si.js && node build_cover_letter.js && node build_title_page.js

standard:           ## validate proposed skill-repository manifests
	$(PYTHON) repository_standard/validate_skills.py

audit:              ## audit archive completeness and print known provenance warnings
	$(PYTHON) audit_archive.py

check: standard audit  ## run non-generating repository checks

reproduce: figures docs   ## deterministic reproduction: stats + figures + documents

all: prompts figures docs check ## also regenerate prompts and run repository checks

clean:              ## remove generated outputs (keeps raw results_v2*.json and data)
	rm -f results/summary_v2.json results/summary_v2.csv results/cross_language_summary.json results/*.png
	rm -f manuscript/*.pdf
	rm -rf manuscript/_preview
