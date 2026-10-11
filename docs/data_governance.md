# Data governance

Raw files are immutable, including the pre-existing unlabelled `data/raw/municipalities.zip`. Its checksum is frozen, but its source/acquisition/extent provenance is unknown. `config/unverified_raw_files.json` explicitly excludes it from analytical source registration with a visible warning; verified official boundary sources supply the geography. No missing provenance is invented.

PostgreSQL/PostGIS is the authoritative analytical store. Source rows remain in immutable all-text `raw` tables, source registration in `meta`, and current derived records in independent V3 schemas. Aggregate CSVs and figures are exports. Private coordinates, inner-fold membership, OOF losses and per-observation SHAP remain database artifacts. The local legacy database dump and archived exploratory notebook contain private data and are excluded from Git.

Never statistically impute listed price or log price. Preserve predictor missingness until a recorded, training-fitted preprocessing operation. Do not use outer outcomes for taxonomy, accessibility, speed, decay, geometry, feature or tuning decisions. All metric operations use EPSG:25832 and source coordinates EPSG:4326. Data provenance remains source-specific, with URL, acquisition date, extent, checksum and explicit unknowns.
