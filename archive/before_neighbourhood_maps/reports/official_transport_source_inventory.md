# Official transport source inventory

## Analytical source decision — 2026-10-04

**User decision: do not use this official transport SHP collection in the thesis analysis. Retain the existing OSM transport inputs.** The archived official files, operator evidence and PostGIS source-quality assessment are retained as reference material only. Existing-status candidate records are audit results, not approved analytical inputs. This decision concerns the assessed transport collection; it does not change the use of official municipal boundaries or other official sources already used in the thesis. See the dated decision in `docs/decision_log.md`.

The archive currently contains **11 distinct official datasets**, **13 original SHP files** across **2 dated acquisitions**, and **93 raw/source-metadata files**. Original ZIPs and unmodified extracted shapefile bundles remain under `data/raw/official_transport/YYYY-MM-DD/`.

This is the single cumulative report. Each download regenerates it from all saved acquisition records, retaining dated entries below. The inventory uses the most recently acquired version of each dataset; earlier raw versions remain immutable. An acquisition date records when the source was downloaded, not when the infrastructure was built, updated or operational.

Sources: [City of Copenhagen public WFS](https://wfs-kbhkort.kk.dk/k101/ows?service=WFS&version=1.0.0&request=GetCapabilities) and its [Open Data DK catalogue](https://www.opendata.dk/city-of-copenhagen). These are provider-supplied SHP exports, not conversions from OSM.

## Current inventory

| Dataset / directory | Acquired | Features | Source CRS | Catalogue licence | Limitations |
|---|---|---:|---|---|---|
| `cykeldata_kk` | 2026-10-03 | 3,386 | EPSG:4326 | CC-BY-4.0 | Combined cycling infrastructure/routes; inspect route types before use. |
| `vejmidte_geodk_labels` | 2026-10-03 | 18,423 | EPSG:4326 | CC-BY-4.0 | Provider describes this as road-name/code data for map labels; routing suitability unverified. |
| `cykelsti` | 2026-10-03 | 1,911 | EPSG:25832 | Not verified for individual layer | Cycle-track layer; completeness and attribute meanings unverified. |
| `cykelrute_total` | 2026-10-03 | 34 | EPSG:25832 | Not verified for individual layer | Service explicitly includes planned and future supercycle routes; do not treat all as existing. |
| `stimidter_parker` | 2026-10-03 | 1,669 | EPSG:25832 | Not verified for individual layer | Park-path centre lines; not a complete pedestrian network. |
| `sti_frberg` | 2026-10-03 | 781 | EPSG:25832 | Not verified for individual layer | Frederiksberg-named path layer served by Copenhagen; originating custodian and completeness unverified. |
| `fodgaengerfelt` | 2026-10-03 | 3,597 | EPSG:25832 | Not verified for individual layer | Pedestrian-crossing markings; not a pedestrian routing network. |
| `jernbane_oversigtskort` | 2026-10-03 | 300 | EPSG:25832 | Not verified for individual layer | Railway overview geometry; operating status and metro coverage unverified; no timetables. |
| `jernbane_ovs_omegn` | 2026-10-03 | 147 | EPSG:25832 | Not verified for individual layer | Surrounding-area railway overview geometry; no timetables. |
| `station_oversigtskort` | 2026-10-03 | 133 | EPSG:25832 | Not verified for individual layer | Station overview layer; station types, entrances and completeness unverified. |
| `stoppesteder_movia` | 2026-10-04 | 1,154 | EPSG:25832 | Not verified for individual layer | Movia stop layer served by Copenhagen; municipality coverage, stop types and infrastructure vintage require assessment; no timetables. |

## Can these replace the current OSM inputs?

**A full replacement is not established.** The official files are candidates for source validation; no analytical source has been replaced.

| Current or proposed input | Official candidate | Replacement status |
|---|---|---|
| Rail/metro/S-train destination points | `station_oversigtskort` (133 archived features) | Candidate after checking current operating status, duplicates, coordinate meaning, complete buffered study-area coverage and vintage. Counts alone do not establish completeness. |
| Bus-stop destination points | `stoppesteder_movia` (1,154 archived features) | Candidate after validation; establish Copenhagen, Frederiksberg and surrounding-buffer coverage. See the source municipality labels below. |
| Walking routing graph | Road-label centre lines, park paths, `sti_frberg` and crossing markings | No complete connected pedestrian graph has been validated. Check access rules, connectivity, bridge/underpass levels, entrances and buffer coverage before substitution. |
| Cycling network | Cycle tracks and cycling/supercycle routes | Useful source layers; filter existing versus planned/projected infrastructure and validate legal directions, connections and cross-municipal coverage. Cycling is not an input in the frozen primary analysis. |
| Railway alignment maps | Two railway overview layers | Useful map context, but not operating services or timetables. |
| Food/social and cultural/tourist destinations | No replacement acquired in this transport collection | Existing OSM destination sets remain required for the current analysis. |
| Timetable-sensitive transit accessibility | No GTFS/NeTEx acquired | Unavailable from this SHP collection. |

The frozen comparison uses the same canonical station/food/culture points and walking graph for its Euclidean and walking measures. Replacing station or stop points may still require the OSM walking graph; changing a destination source changes the resulting features. Validate sources without using outcome values or test-fold model scores to choose them. Any analytical replacement follows the documented scientific-version workflow, rather than overwriting frozen v1.

## Source attribute checks

These counts are reproduced from the original SHP attributes. They describe provider labels, not a spatial boundary assignment, verified operational status, or evidence of complete network coverage. Missing labels remain explicitly missing. No spatial transformation is performed.

| Dataset | Source field | Source value | Rows |
|---|---|---|---:|
| `station_oversigtskort` | `objekt_typ` | S-station | 80 |
| `station_oversigtskort` | `objekt_typ` | Metrostation | 45 |
| `station_oversigtskort` | `objekt_typ` | Anden station | 8 |
| `station_oversigtskort` | `kommune` | København | 65 |
| `station_oversigtskort` | `kommune` | Lyngby-Taarbæk | 9 |
| `station_oversigtskort` | `kommune` | Frederiksberg | 8 |
| `station_oversigtskort` | `kommune` | Rudersdal | 5 |
| `station_oversigtskort` | `kommune` | Gladsaxe | 5 |
| `station_oversigtskort` | `kommune` | Hvidovre | 4 |
| `station_oversigtskort` | `kommune` | Tårnby | 2 |
| `station_oversigtskort` | `kommune` | Allerød | 2 |
| `station_oversigtskort` | `kommune` | Rødovre | 1 |
| `station_oversigtskort` | `kommune` | Gentofte | 1 |
| `station_oversigtskort` | `kommune` | Missing (NULL) | 31 |
| `stoppesteder_movia` | `kommune` | København | 1,149 |
| `stoppesteder_movia` | `kommune` | Københavns | 5 |
| `cykeldata_kk` | `status` | Eksisterende | 3,065 |
| `cykeldata_kk` | `status` | Planlagt | 294 |
| `cykeldata_kk` | `status` | Projekteret | 27 |
| `cykeldata_kk` | `kommune` | København | 3,220 |
| `cykeldata_kk` | `kommune` | Frederiksberg | 14 |
| `cykeldata_kk` | `kommune` | Hvidovre | 13 |
| `cykeldata_kk` | `kommune` | Gentofte | 10 |
| `cykeldata_kk` | `kommune` | Lyngby-Taarbaek | 9 |
| `cykeldata_kk` | `kommune` | Rudersdal | 8 |
| `cykeldata_kk` | `kommune` | Brøndby | 8 |
| `cykeldata_kk` | `kommune` | Furesø | 7 |
| `cykeldata_kk` | `kommune` | Hillerød | 7 |
| `cykeldata_kk` | `kommune` | Rødovre | 7 |
| `cykeldata_kk` | `kommune` | Hørsholm | 6 |
| `cykeldata_kk` | `kommune` | Gladsaxe | 6 |
| `cykeldata_kk` | `kommune` | Allerød | 6 |
| `cykeldata_kk` | `kommune` | Albertslund | 6 |
| `cykeldata_kk` | `kommune` | Egedal | 5 |
| `cykeldata_kk` | `kommune` | Frederikssund | 5 |
| `cykeldata_kk` | `kommune` | Tårnby | 5 |
| `cykeldata_kk` | `kommune` | Glostrup | 5 |
| `cykeldata_kk` | `kommune` | Roskilde | 5 |
| `cykeldata_kk` | `kommune` | Ballerup | 4 |
| `cykeldata_kk` | `kommune` | Fredensborg | 4 |
| `cykeldata_kk` | `kommune` | Ishøj | 3 |
| `cykeldata_kk` | `kommune` | Vallensbaek | 3 |
| `cykeldata_kk` | `kommune` | Herlev | 3 |
| `cykeldata_kk` | `kommune` | Helsingør | 3 |
| `cykeldata_kk` | `kommune` | Høje Taastrup | 3 |
| `cykeldata_kk` | `kommune` | Gribskov | 2 |
| `cykeldata_kk` | `kommune` | Solrød | 1 |
| `cykeldata_kk` | `kommune` | Køge | 1 |
| `cykeldata_kk` | `kommune` | Vallensbæk | 1 |
| `cykeldata_kk` | `kommune` | Lyngby-Taarbæk | 1 |
| `cykeldata_kk` | `kommune` | Halsnæs | 1 |
| `cykeldata_kk` | `kommune` | Missing (NULL) | 4 |
| `cykelrute_total` | `rute_statu` | Planlagt rute | 20 |
| `cykelrute_total` | `rute_statu` | Projekteret rute | 12 |
| `cykelrute_total` | `rute_statu` | Anlagt rute | 2 |
| `sti_frberg` | `feat_type` | Vejmidte_brudt | 781 |
| `sti_frberg` | `komnavn` | Frederiksberg | 781 |

Source cycling status labels distinguish existing, planned and projected infrastructure; none are silently recoded. Station labels include S-train, metro and other stations; the independent operating-status assessment below is separate from these raw labels. The Copenhagen-served `sti_frberg` has Frederiksberg labels; that does not establish a complete municipality walking network.

## Existing-infrastructure completeness assessment

Assessment date: **2026-10-04**. Assessment ID: `official_transport_existing_only_v1_ce9347851419f4bf`. **The acquired SHP collection does not establish a complete replacement for OSM.**

Only explicit existing source labels or corroboration by current operator records qualify as existing candidates. Planned, projected and unknown status are excluded from `spatial.official_transport_existing_candidates`; original records remain immutable. This is a source-assessment view, not an analytical replacement. An existing record is not necessarily a usable routing edge or verified station entrance.

| Dataset | Total | Existing candidates | Planned | Projected | Unknown | Missing/empty geometry | Invalid geometry |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cykeldata_kk` | 3,386 | 3,065 | 294 | 27 | 0 | 0 | 0 |
| `cykelrute_total` | 34 | 2 | 20 | 12 | 0 | 0 | 0 |
| `cykelsti` | 1,911 | 0 | 0 | 0 | 1,911 | 9 | 0 |
| `fodgaengerfelt` | 3,597 | 0 | 0 | 0 | 3,597 | 102 | 1 |
| `jernbane_oversigtskort` | 300 | 0 | 0 | 0 | 300 | 1 | 0 |
| `jernbane_ovs_omegn` | 147 | 0 | 0 | 0 | 147 | 0 | 0 |
| `station_oversigtskort` | 133 | 44 | 0 | 0 | 89 | 0 | 0 |
| `sti_frberg` | 781 | 0 | 0 | 0 | 781 | 0 | 0 |
| `stimidter_parker` | 1,669 | 0 | 0 | 0 | 1,669 | 0 | 0 |
| `stoppesteder_movia` | 1,154 | 865 | 0 | 0 | 289 | 0 | 0 |
| `vejmidte_geodk_labels` | 18,423 | 0 | 0 | 0 | 18,423 | 0 | 0 |

### Bus stops: independent official comparison

Reference: [Movia official stop service](https://geoservices.moviatrafik.dk/arcgis/rest/services/WebGIS/bus_webGIS/MapServer/1). Archive complete object-ID queries and every returned page for BUS records in the EPSG:25832 envelope of the municipal union buffered 2,000 m. The comparison below selects reference records whose validity interval includes the assessment date, then assigns them by actual official boundary geometry. Exact stop numbers identify matches; proximity alone does not merge stops.

| Scope | Current operator BUS records | IDs present in SHP | Matched ID within 25 m | Matched ID within 100 m | IDs absent from SHP |
|---|---:|---:|---:|---:|---:|
| Copenhagen | 981 | 862 | 697 | 832 | 119 |
| Frederiksberg | 164 | 3 | 3 | 3 | 161 |
| Municipal union | 1,145 | 865 | 700 | 835 | 280 |
| Union + 1,500 m buffer | 1,607 | 865 | 700 | 835 | 742 |

### Stations and railway maps

The [Metro operator's operating-line station list](https://m.dk/da/) contains 44 unique names; 43 match SHP metro names after documented case/whitespace/parenthetical normalization. Unmatched operator names: københavns lufthavn. Uncorroborated SHP names: Lufthavnen. A name difference is not proof of a missing geographic station; unresolved aliases stay unknown.

Same-type station-name duplicates are retained for review, without automatic merging:

| Type | Name | Source records | Maximum separation (m) |
|---|---|---:|---:|
| Metrostation | Frederiksberg | 2 | 81.41 |

S-train/other-station operating status and completeness have not been independently established. Railway overview geometry supplies neither operating services nor station entrances or schedules. Do not replace the entire station set from a metro name comparison.

### Geographic scope

Counts use actual geometry intersections with official boundaries in EPSG:25832, not source municipality labels. Line/polygon records may intersect several scopes, so counts are not additive. The existing 1,500 m extraction buffer retains its database name `planned_15min_extraction`; that name describes an analysis extent, not proposed infrastructure.

| Dataset | Scope | All intersecting records | Existing candidates |
|---|---|---:|---:|
| `cykeldata_kk` | Copenhagen | 3,252 | 3,034 |
| `cykeldata_kk` | Frederiksberg | 33 | 16 |
| `cykeldata_kk` | Municipal union | 3,258 | 3,036 |
| `cykeldata_kk` | Union + 1,500 m buffer | 3,280 | 3,045 |
| `cykelrute_total` | Copenhagen | 25 | 2 |
| `cykelrute_total` | Frederiksberg | 6 | 1 |
| `cykelrute_total` | Municipal union | 25 | 2 |
| `cykelrute_total` | Union + 1,500 m buffer | 26 | 2 |
| `cykelsti` | Copenhagen | 1,893 | 0 |
| `cykelsti` | Frederiksberg | 18 | 0 |
| `cykelsti` | Municipal union | 1,898 | 0 |
| `cykelsti` | Union + 1,500 m buffer | 1,902 | 0 |
| `fodgaengerfelt` | Copenhagen | 3,466 | 0 |
| `fodgaengerfelt` | Frederiksberg | 31 | 0 |
| `fodgaengerfelt` | Municipal union | 3,482 | 0 |
| `fodgaengerfelt` | Union + 1,500 m buffer | 3,494 | 0 |
| `jernbane_oversigtskort` | Copenhagen | 125 | 0 |
| `jernbane_oversigtskort` | Frederiksberg | 12 | 0 |
| `jernbane_oversigtskort` | Municipal union | 129 | 0 |
| `jernbane_oversigtskort` | Union + 1,500 m buffer | 153 | 0 |
| `jernbane_ovs_omegn` | Copenhagen | 4 | 0 |
| `jernbane_ovs_omegn` | Municipal union | 4 | 0 |
| `jernbane_ovs_omegn` | Union + 1,500 m buffer | 59 | 0 |
| `station_oversigtskort` | Copenhagen | 62 | 35 |
| `station_oversigtskort` | Frederiksberg | 11 | 8 |
| `station_oversigtskort` | Municipal union | 73 | 43 |
| `station_oversigtskort` | Union + 1,500 m buffer | 81 | 44 |
| `sti_frberg` | Copenhagen | 28 | 0 |
| `sti_frberg` | Frederiksberg | 780 | 0 |
| `sti_frberg` | Municipal union | 781 | 0 |
| `sti_frberg` | Union + 1,500 m buffer | 781 | 0 |
| `stimidter_parker` | Copenhagen | 1,667 | 0 |
| `stimidter_parker` | Municipal union | 1,667 | 0 |
| `stimidter_parker` | Union + 1,500 m buffer | 1,669 | 0 |
| `stoppesteder_movia` | Copenhagen | 1,153 | 864 |
| `stoppesteder_movia` | Frederiksberg | 1 | 1 |
| `stoppesteder_movia` | Municipal union | 1,154 | 865 |
| `stoppesteder_movia` | Union + 1,500 m buffer | 1,154 | 865 |
| `vejmidte_geodk_labels` | Copenhagen | 8,368 | 0 |
| `vejmidte_geodk_labels` | Frederiksberg | 667 | 0 |
| `vejmidte_geodk_labels` | Municipal union | 8,971 | 0 |
| `vejmidte_geodk_labels` | Union + 1,500 m buffer | 13,132 | 0 |

### Walking and cycling network suitability

A complete pedestrian graph cannot be certified from these files: road-label centre lines, park paths, Frederiksberg paths and crossing markings lack verified existence status and consistent pedestrian permissions, directions, entrance connections and crossing/bridge levels. They are excluded from strict existing candidates until corroborated. The explicit existing cycling subset also lacks a validated routing topology and complete cross-municipal coverage.

Exact-endpoint connectivity is a diagnostic, with no snapping, invented gap links or intersection noding. It does not prove that separated components are physically disconnected, nor that geometric crossings are traversable. Z coordinates are retained where supplied.

| Raw-geometry diagnostic | Line records | Endpoint nodes | Edges | Components | Largest component nodes |
|---|---:|---:|---:|---:|---:|
| Existing-labelled cycling | 3,067 | 3,357 | 3,053 | 347 | 739 |
| Unverified walking geometry (ineligible) | 20,872 | 27,713 | 20,949 | 7,811 | 102 |

Identical EWKB geometry duplicates are counted, not removed:

| Dataset | Duplicate geometry groups | Excess records |
|---|---:|---:|
| `cykeldata_kk` | 37 | 37 |
| `cykelsti` | 11 | 12 |
| `fodgaengerfelt` | 3 | 3 |

### OSM discrepancy checks

OSM is a comparison source, not ground truth. Fixed 50/100/250 m nearest-point checks flag representation differences; they do not certify coverage, entrances or identity and are not tuned using prices, outcomes or model performance.

| Kind | Official subset | Scope | OSM points | Within 50 m | Within 100 m | Within 250 m |
|---|---|---|---:|---:|---:|---:|
| station | all source rows (diagnostic only) | Copenhagen | 56 | 47 | 55 | 56 |
| station | all source rows (diagnostic only) | Frederiksberg | 9 | 9 | 9 | 9 |
| station | all source rows (diagnostic only) | Municipal union | 65 | 56 | 64 | 65 |
| station | all source rows (diagnostic only) | Union + 1,500 m buffer | 76 | 61 | 72 | 73 |
| station | existing only | Copenhagen | 56 | 30 | 33 | 35 |
| station | existing only | Frederiksberg | 9 | 6 | 7 | 7 |
| station | existing only | Municipal union | 65 | 36 | 40 | 42 |
| station | existing only | Union + 1,500 m buffer | 76 | 37 | 41 | 43 |
| bus | all source rows (diagnostic only) | Copenhagen | 1,326 | 1,151 | 1,236 | 1,302 |
| bus | all source rows (diagnostic only) | Frederiksberg | 189 | 5 | 11 | 33 |
| bus | all source rows (diagnostic only) | Municipal union | 1,515 | 1,156 | 1,247 | 1,335 |
| bus | all source rows (diagnostic only) | Union + 1,500 m buffer | 2,022 | 1,157 | 1,251 | 1,351 |
| bus | existing only | Copenhagen | 1,326 | 1,065 | 1,157 | 1,257 |
| bus | existing only | Frederiksberg | 189 | 5 | 7 | 28 |
| bus | existing only | Municipal union | 1,515 | 1,070 | 1,164 | 1,285 |
| bus | existing only | Union + 1,500 m buffer | 2,022 | 1,070 | 1,168 | 1,301 |

### Date, persistence and reproducibility

The 3–4 October dates are acquisition dates. The operator comparison describes 4 October 2026, not a complete reconstruction of the thesis's June 2026 infrastructure. SHP infrastructure vintages remain unverified. Explicit cycling status labels have no verified effective date. Current-date existence alone is insufficient for historical substitution.

Authoritative source copies, per-record decisions and results are stored in PostGIS `raw.official_transport_source_features`, `meta.official_transport_feature_status` and `meta.official_transport_assessments`. `outputs/tables/official_transport/assessment.json` is a reproducible aggregate export from these tables, not a separate source of truth. Operator evidence is retained under `data/raw/official_transport_validation/2026-10-04/`, with URLs, acquisition timestamps, query extent, EPSG:25832 and SHA-256 recorded in the source manifest. Metro reference names have no invented coordinates. Original source dimensions remain in `geom_source`; planar checks use a derived 2D `geom_25832`.

Reproduce the assessment and update this same report:

```sh
.venv/bin/python -m src.pipeline.assess_official_transport --assessed-on 2026-10-04
```

The assessment adds source-quality tables and migration 018. Frozen scientific artifact hashes are verified before and after; no primary destinations, walking graph, features, folds or models are replaced. The live provenance registry and schema now include this audit extension, so the whole live database is not identical to the frozen snapshot.

## Acquisition history

Dated collections are additive source acquisitions. A later acquisition does not by itself establish newer infrastructure, corrected data or a replacement for an earlier layer.

### 2026-10-03

Archive: `data/raw/official_transport/2026-10-03/`. 10 datasets, 12 SHP files and 83 raw/source-metadata files.

Added to the cumulative inventory: `cykeldata_kk`, `vejmidte_geodk_labels`, `cykelsti`, `cykelrute_total`, `stimidter_parker`, `sti_frberg`, `fodgaengerfelt`, `jernbane_oversigtskort`, `jernbane_ovs_omegn`, `station_oversigtskort`.

Initial acquisition: cycling, road-label centre lines, park/Frederiksberg paths, crossings, railway overview lines and station points. Mixed geometry in `cykelsti` and `stimidter_parker` produced separate line and point SHP files. The bus-stop layer was already advertised in the saved service metadata but was missed in the initial selection.

Verify this dated archive and regenerate the cumulative report:

```sh
.venv/bin/python -m src.ingestion.download_official_transport --retrieval-date 2026-10-03 --datasets cykeldata_kk vejmidte_geodk_labels cykelsti cykelrute_total stimidter_parker sti_frberg fodgaengerfelt jernbane_oversigtskort jernbane_ovs_omegn station_oversigtskort --register-provenance
```

### 2026-10-04

Archive: `data/raw/official_transport/2026-10-04/`. 1 dataset, 1 SHP file and 10 raw/source-metadata files.

Added to the cumulative inventory: `stoppesteder_movia`.

Added the previously missed `stoppesteder_movia` stop layer in a separate collection. This corrects the acquisition omission; it is not evidence that the provider first published bus stops on this date. The 3 October source archive is unchanged.

Subsequent source assessment: archived independent Metro/Movia operator evidence and applied an existing-only candidate policy. Geographic checks establish missing bus-stop IDs in Frederiksberg, Copenhagen and the study buffer; cycling planned/projected records are excluded. Full pedestrian/cycling routing suitability and historical June 2026 completeness remain unestablished. Results and dates are maintained in this same report.

Verify this dated archive and regenerate the cumulative report:

```sh
.venv/bin/python -m src.ingestion.download_official_transport --retrieval-date 2026-10-04 --datasets stoppesteder_movia --register-provenance
```

## Provenance, verification and remaining access gaps

ZIP integrity, SHP/SHX/DBF/PRJ components, readable CRS and feature counts were checked during acquisition. Each returned count matched an independently archived WFS `resultType=hits` response; those counts establish response completeness, not real-world coverage. SHA-256, original URLs, acquisition timestamps, advertised EPSG:4326 extents, actual SHP bounds/CRS and fields are retained in each `acquisition_metadata.json` and `data/metadata/source_manifest.json`.

Catalogue-linked licences are recorded where available. Individual WFS layers without licence metadata require confirmation before reuse or redistribution. Infrastructure vintages remain unknown; catalogue modification dates are not used as source dates. Raw sources and source-manifest hashes are preserved. PostgreSQL/PostGIS `meta.source_files` stores registered provenance; no geometry from this collection has been imported into analytical feature tables.

The 3 October investigation confirmed [GeoDanmark60_SHP](https://confluence.kds.dk/pages/viewpage.action?pageId=25724273), including municipal downloads in EPSG:25832. It remains unacquired because the documented service requires registered account credentials. The documented legacy extract service is retiring on 15 January 2027; check the provider's current access route when obtaining access.

The direct map configuration linked by [Frederiksberg's cycling page](https://www.frederiksberg.dk/by-bolig-og-miljoe/trafik/kom-rundt-i-byen/cyklister) returned HTTP 404 in the 3 October investigation. No direct Frederiksberg SHP export was verified; the original custodian of the Copenhagen-served `sti_frberg` is unverified.

[Rejseplanen](https://labs.rejseplanen.dk/hc/da/articles/24750139021341-Oversigt-over-udstillede-data) documents separate schedule and stop-data access. No GTFS was acquired. The SHP station/stop geometry does not supply timetable-sensitive accessibility.

Existing dated archives are checked without another download or replacement. Use a new acquisition date for a new immutable collection. Future runs update this same report and add a dated history entry. `--register-provenance` registers only the selected collection, without changing analytical tables, routing, models, folds or the scientific freeze.
