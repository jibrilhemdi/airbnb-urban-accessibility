PYTHON ?= .venv/bin/python
.DEFAULT_GOAL := study-status
.PHONY: study-status study-design study-test study-setup study-geography-freeze study-geography-audit study-test-db
study-status:
	$(PYTHON) -m src.study.cli status
study-design:
	$(PYTHON) -m src.study.cli design
study-test:
	$(PYTHON) -m unittest discover -s tests -p 'test_study*.py' -v
study-test-db:
	THESIS_STUDY_DB_TEST=1 $(PYTHON) -m unittest discover -s tests -p 'test_study_store.py' -v
study-setup:
	$(PYTHON) -m src.study.cli setup
study-geography-freeze:
	$(PYTHON) -m src.study.cli geography-freeze
study-geography-audit:
	$(PYTHON) -m src.study.cli geography-audit
.PHONY: study-context-freeze study-context-audit
study-context-freeze:
	$(PYTHON) -m src.study.cli context-freeze
study-context-audit:
	$(PYTHON) -m src.study.cli context-audit

STUDY_CITY ?= copenhagen
STUDY_SCHEME ?= neighbourhood
.PHONY: study-sample-freeze study-prefit-freeze study-within-city study-transfer study-association study-spatial study-robustness study-training-sensitivity study-measurements study-finish study-report study-preservation
study-sample-freeze:
	$(PYTHON) -m src.study.cli sample-freeze
study-prefit-freeze:
	$(PYTHON) -m src.study.cli prefit-freeze
study-within-city:
	$(PYTHON) -m src.study.cli within-city --city "$(STUDY_CITY)" --scheme "$(STUDY_SCHEME)"
study-transfer:
	$(PYTHON) -m src.study.cli transfer
study-association:
	$(PYTHON) -m src.reporting.study_diagnostics
study-spatial:
	$(PYTHON) -m src.reporting.study_spatial
study-robustness:
	$(PYTHON) -m src.reporting.study_robustness --city "$(STUDY_CITY)"
study-training-sensitivity:
	$(PYTHON) -m src.reporting.study_training_sensitivity --city "$(STUDY_CITY)"
study-measurements:
	$(PYTHON) -m src.reporting.study_measurement_sensitivity
study-finish:
	$(PYTHON) scripts/study_finish_queue.py
study-report:
	$(PYTHON) -m src.reporting.study_report
study-preservation:
	$(PYTHON) scripts/study_preservation.py --verify-store --database

# Historical commands and migration identities are preserved in archive/.
.PHONY: compile test integration-test
compile:
	$(PYTHON) -m compileall -q src scripts tests
test:
	$(PYTHON) -m unittest discover -s tests -v
integration-test:
	THESIS_STUDY_DB_TEST=1 $(PYTHON) -m unittest discover -s tests -p 'test_study*.py' -v

.PHONY: thesis-outputs thesis-synthesis thesis-check thesis-science-check thesis-release
thesis-outputs:
	$(PYTHON) -m src.reporting.thesis_outputs
thesis-synthesis:
	$(PYTHON) -m src.reporting.thesis_synthesis
thesis-check:
	$(PYTHON) -m src.reporting.thesis_validate
thesis-science-check:
	$(PYTHON) -m src.reporting.thesis_validate --science
thesis-release:
	$(PYTHON) -m src.reporting.thesis_release
