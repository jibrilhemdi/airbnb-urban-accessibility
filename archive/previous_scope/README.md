# Airbnb urban accessibility thesis — Version 3

The active project uses a purpose-based pipeline and PostgreSQL/PostGIS as its authoritative persistent analytical layer. Immutable raw sources remain locally under `data/raw`. The previous committed version is available on the `v2` Git branch; local analysis archives, result freezes and checksums remain in `archive/legacy_v2`.

The public `v3` branch contains source code, tests, SQL migrations, methodological documentation and configuration. Datasets, metadata exports, database dumps, archives, generated reports/results, supporting Word documents, credentials and packaging ZIPs are excluded. The source-derived income acceptance file `config/qualified_income_decision.json` also remains local. Running the empirical pipeline requires these local inputs and the PostgreSQL/PostGIS database, including the frozen dataset certificate under `outputs/tables/analysis_dataset`; a fresh clone alone cannot reproduce the existing results. Source checksums and acquisition references remain in the frozen-input configuration. No raw files or scientific settings were changed to prepare this branch.

The frozen design compares M0, ME, MW and MEW over 11 peer `analysis_area` units. M0 includes property, prespecified amenities, host/rental variables, log population density, harmonised income and City Hall centrality. Rail and deduplicated bus accessibility remain separate core measures. The baseline assumes 5.0 km/h, a 10-minute network budget and an 833 m rounded Euclidean analogue. See [the protocol](docs/preanalysis_specification.md) and [migration audit](docs/migration_rerun_audit.md).

```sh
make compile
make test
make db-check
make db-migrate
make smoke
make preflight
make pipeline
```

The full runner verifies frozen inputs, qualified income acceptance and a fresh V3 namespace. The explicit income amendment adopts Copenhagen Municipality KKIND5 and Statistics Denmark nominal IFOR35 for 2024 with a common arithmetic mean of ten decile means. See [the protocol](docs/preanalysis_specification.md) for the qualified income decision. Income remains core; mandatory M0/ME/MW/MEW_no_income models use the same sample, saved folds, preprocessing and tuning budget. `make income-audit` validates and exports the authoritative SQL source freeze. Earlier investigations and the unsent enquiry draft remain preserved locally. `make income-docs` reproduces the current amendment in both local supporting DOCX copies. Run `make preflight`, then `make pipeline` once it passes.

Rebuild the thesis figure gallery from completed SQL results with `make reporting`. Open `reports/reporting_figures_v3.html` for pastel figures and PNG downloads. Reporting refreshes have their own audit certificate; the original empirical run and certificate remain preserved. See `docs/reproducibility.md` for provenance and figure disclosure rules.
