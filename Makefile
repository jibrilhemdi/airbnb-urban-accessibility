PYTHON ?= .venv/bin/python
.PHONY: db-up db-down db-connect db-psql db-diagnose db-migrate db-check db-register compile test integration-test preflight smoke pipeline reproduce audit candidates migration-audit income-evidence income-deciles income-audit income-docs municipal-income-evidence

db-up:
	docker compose --env-file .env up -d --wait --wait-timeout 120 db

db-down:
	docker compose --env-file .env down

db-connect:
	$(PYTHON) -m src.db.cli connect

db-psql:
	docker compose --env-file .env exec db sh -c 'exec psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

db-diagnose:
	$(PYTHON) -m src.db.diagnose

db-migrate:
	$(PYTHON) -m src.db.cli migrate

db-check:
	$(PYTHON) -m src.db.cli check

db-register:
	$(PYTHON) -m src.db.cli register-sources

compile:
	$(PYTHON) -m compileall src

test:
	$(PYTHON) -m unittest discover -s tests -v

integration-test:
	THESIS_DB_TEST=1 THESIS_V3_INTEGRATION=1 $(PYTHON) -m unittest discover -s tests -v

preflight:
	$(PYTHON) -m src.pipeline.run_pipeline --preflight

smoke:
	$(PYTHON) -m src.pipeline.run_pipeline --smoke

candidates:
	$(PYTHON) -m src.pipeline.build_tuning_candidates

pipeline reproduce:
	$(PYTHON) -m src.pipeline.run_pipeline --run

audit:
	$(PYTHON) -m src.pipeline.audit_reproducibility --repository-only

migration-audit:
	$(PYTHON) -m src.pipeline.build_migration_audit

income-evidence:
	$(PYTHON) -m src.ingestion.acquire_income_evidence

income-deciles:
	$(PYTHON) -m src.ingestion.acquire_income_evidence --deciles

income-audit:
	$(PYTHON) -m src.pipeline.qualified_income

municipal-income-evidence:
	$(PYTHON) -m src.ingestion.acquire_municipal_income_evidence

income-docs:
	$(PYTHON) -m src.pipeline.update_income_documentation

.PHONY: reporting
reporting:
	$(PYTHON) -m src.pipeline.render_reporting_figures

# V4 commands require explicit identity; setup never creates/drops databases.
V4_ARGS = --version "$(VERSION)" --city "$(CITY)" --snapshot "$(SNAPSHOT)" --run-id "$(RUN_ID)"
.PHONY: v4-setup v4-test v4-test-db v4-preflight v4-run v4-report
v4-setup:
	$(PYTHON) -m src.v4.cli setup $(V4_ARGS)

v4-test:
	THESIS_V4_DB_TEST=0 $(PYTHON) -m unittest discover -s tests -p 'test_v4*.py' -v

v4-test-db:
	THESIS_V4_DB_TEST=1 $(PYTHON) -m unittest discover -s tests -p 'test_v4_persistence.py' -v

v4-preflight:
	$(PYTHON) -m src.v4.cli preflight $(V4_ARGS) $(V4_PREFLIGHT_FLAGS)

v4-run:
	$(PYTHON) -m src.v4.cli run $(V4_ARGS) $(V4_PREFLIGHT_FLAGS)

v4-report:
	$(PYTHON) -m src.v4.cli report $(V4_ARGS)

.PHONY: v4-acquire v4-ingest v4-listing-audit
v4-acquire:
	$(PYTHON) -m src.v4.listings acquire $(V4_ARGS)

v4-ingest:
	$(PYTHON) -m src.v4.listings ingest $(V4_ARGS)

v4-listing-audit:
	$(PYTHON) -m src.v4.listings audit $(V4_ARGS)

.PHONY: v4-stockholm-boundary
v4-stockholm-boundary:
	$(PYTHON) -m src.v4.stockholm_boundary ingest $(V4_ARGS) --previous-run-id $(PREVIOUS_RUN_ID)
