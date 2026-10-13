# Three-city urban accessibility research

The study compares accessibility measurement, within-city nightly asking-price
prediction, geographic generalization and directional relative-price transfer
across Copenhagen–Frederiksberg, Oslo and Stockholm.

All three predictive ladders, three complete-case association ladders, six
transfer directions and required robustness checks are complete. The researcher
raised the uniform association missingness eligibility limit from 5% to 10%
after observing Stockholm's 5.89% missingness. This
[post-observation amendment](docs/analysis/association_missingness_amendment_20261013.md)
is disclosed; the 147 bedroom blanks remain unfilled. Predictive models and
transfers were preserved after dependency verification.

Read the [publication report](docs/analysis/research_report_publication.md),
[generated findings](docs/analysis/findings.md),
[release audit](docs/analysis/release_audit.json),
[specification](docs/analysis/preanalysis_specification.md) and
[execution log](docs/analysis/execution_log.md).

Use one pinned dependency file and the audited Python environment:

```sh
python -m pip install -r requirements.txt
make study-status
make study-test
make integration-test
make compile
```

Active configuration is in `config/study/`, analysis code in `src/study/`,
source-provenance adapters in `src/provenance/` and reports in `docs/analysis/`.
PostgreSQL/PostGIS is authoritative; one `.env` holds both connection namespaces,
documented in `.env.example`. Credentials, raw sources, private memberships, models and row-level
predictions stay ignored. Public figures use aggregate cells with n≥5.

Previous instructions, code, configurations, audits and results are consolidated
in [archive/](docs/analysis/archive_manifest.json), with original bytes resolved
by checksums. Applied migration filenames and persisted source/database identities
remain unchanged. The discarded historical ZIP is explicitly excluded at the
researcher's request. Historical workflows can be reproduced from their recorded
Git checkpoints; they do not govern the active scientific design.

Work continues on the required existing `v4` branch; `main` and `v3` stay unchanged.
Completed fit selectors refuse accidental refitting. Reproduction commands and
verification evidence are in [reproducibility](docs/analysis/reproducibility.md).
