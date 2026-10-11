"""Persist a municipal income evidence review; never approve missing definitions/data."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text

from src.db.connection import get_engine
from src.db.sources import prepare_source, register_records
from src.ingestion.common import PROJECT_ROOT, read_manifest, sha256_file, write_json
from src.pipeline.investigate_income_harmonisation import official_crosswalk
from src.pipeline.storage import export, load_artifact, persist

CONFIG_PATH = PROJECT_ROOT / 'config/municipal_income_investigation.json'
PRIOR_ARCHIVE = PROJECT_ROOT / 'archive/income_investigations/kkind5_ifor35_20261004'
CITY_DOC = 'data/raw/copenhagen_statbank/2026-10-04/income_harmonisation/copenhagen_statbank_documentation.pdf'
CITY_INFO = 'data/raw/copenhagen_statbank/2026-10-04/income_harmonisation/KKIND5_information.html'
FRB_DOC = 'data/raw/frederiksberg_municipality/2026-10-04/municipal_income_review/boligredegoerelsen_2025.pdf'
CITY_SCALE_DOC = 'data/raw/copenhagen_statbank/2026-10-04/municipal_income_review/city_poverty_equivalisation_2025.pdf'
CONTACT_URL = 'https://www.frederiksberg.dk/kommunen/forvaltning-og-fakta-om-kommunen/kontakt'


def definition_comparison():
    """Explicit manual review of saved authoritative documents, not inferred definitions."""
    attributes = [
        ('Income concept', 'Person-assigned equivalised family disposable income (C p.20).', 'No matching municipal statistic identified; see rejected measures F.', 'unresolved'),
        ('Register variable', 'IND and BEF; exact KKIND5 variable/version unspecified (C pp.19–20; K).', 'F note 12 names IND; exact matching variable unavailable.', 'unresolved'),
        ('Family/household definition', 'Single/couple families and resident children; operational version unconfirmed (C pp.20–21).', 'F p.6 defines address-based single/couple families with resident children under 25; target linkage unconfirmed.', 'unresolved'),
        ('Equivalisation scale', 'Weighted family size (C p.20); P p.31 gives 1/0.5/0.3 for poverty methods, but its link to KKIND5 is unconfirmed.', 'No numeric equivalisation scale supplied for a matching statistic.', 'unresolved'),
        ('Statistical population', 'Year-end residents in families with a fully taxable adult (C p.20).', 'Matching eligible-person population unavailable.', 'unresolved'),
        ('Age/eligibility rules', 'No individual 15+ restriction stated for KKIND5; full-tax family requirement (C p.20).', 'F personal-income figures are 15+; not the target population (F p.7, note 2).', 'incompatible'),
        ('Tax-liability requirements', 'At least one fully taxable adult; detailed implementation unconfirmed (C p.20).', 'Matching full-tax family filter not provided.', 'unresolved'),
        ('Zero income treatment', 'KKIND5-specific rule unconfirmed; do not transplant personal-income zero exclusion (C p.20).', 'Matching zero rule unavailable.', 'unresolved'),
        ('Negative income treatment', 'KKIND5-specific handling not supplied.', 'Matching negative-income rule unavailable.', 'unresolved'),
        ('Missing income treatment', 'Table-specific income missingness/filter not supplied.', 'Matching missing-income rule unavailable.', 'unresolved'),
        ('Decile construction', 'Ten equal person groups by equivalised income, conceptually (C p.20).', 'No matching ten-decile means identified.', 'unresolved'),
        ('Tie handling / group counts', 'Finite-count/tie handling and exact eligible counts unavailable.', 'No matching decile counts or tie rules identified.', 'unresolved'),
        ('Price basis', 'Raw table DKK; base year/nominal interpretation unconfirmed (K).', 'F figures have figure-specific price years; target basis unavailable.', 'unresolved'),
        ('Reference year', 'Saved KKIND5 data explicitly select 2024 (K and selection).', 'F income figures use 2022; no matching 2024 value identified.', 'incompatible'),
        ('Unit', 'DKK (K).', 'F monetary figures are DKK; no matching income value.', 'compatible with qualification'),
        ('Geography', 'Ten official city districts in frozen V3 crosswalk (K).', 'One municipality/one V3 peer area; target figure unavailable.', 'compatible with qualification'),
        ('Geographic reference date', 'Residence at year-end (C p.19); operational linkage/version unconfirmed.', 'Matching 2024 residence linkage/date unavailable.', 'unresolved'),
        ('Suppression/rounding', 'General primary/secondary suppression documented; KKIND5 rounding rules unavailable (C p.3).', 'Matching suppression/rounding rules unavailable.', 'unresolved'),
    ]
    return [dict(attribute=a, copenhagen=c, frederiksberg=f, status=s,
                 city_document=CITY_DOC, city_table_information=CITY_INFO,
                 city_scale_support_document=CITY_SCALE_DOC,
                 frederiksberg_document=FRB_DOC,
                 qualification='Frederiksberg column describes reviewed leads; no matching target statistic exists in the collected evidence.')
            for a, c, f, s in attributes]


def area_coverage():
    """Represent missing evidence as NULL for every proposed income, without fallback."""
    rows = []
    for code, area in official_crosswalk().items():
        frb = code == '147'
        rows.append({**area, 'source_geography': code, 'target_year': 2024,
                     'intended_source_institution': 'Frederiksberg Municipality' if frb else 'Copenhagen Municipality',
                     'candidate_source_table': None if frb else 'KKIND5',
                     'price_basis': None, 'proposed_harmonised_income_dkk': None,
                     'status': 'matching_municipal_statistic_not_obtained' if frb else 'definition_not_verified',
                     'primary_eligible': False})
    return sorted(rows, key=lambda r: r['analysis_area'])


def source_reviews(config):
    rows = [dict(source_path=d['path'], source_name=d['name'], source_url=d['url'],
                 institution=d.get('institution', 'Frederiksberg Municipality'), reference_year=d['reference_year'],
                 unit=d['unit'], price_basis=d['price_basis'], relevant_definition=d['definition'],
                 role=d['role'], matching_2024_equivalised_mean_found=False,
                 accepted_for_primary=False) for d in config['documents']]
    return rows


def evidence_request():
    return f'''# Draft evidence request to Frederiksberg Municipality

**Draft only — not sent.** Route to the team responsible for register-based analyses/Boligredegørelsen through the [official contact page]({CONTACT_URL}); municipal switchboard: 3821 2121. A dedicated income-statistics recipient has not been verified.

**Emne: Ækvivaleret disponibel indkomst for Frederiksberg, indkomståret 2024**

Kære Frederiksberg Kommune

Til mit MSc-speciale har jeg brug for gennemsnitlig ækvivaleret disponibel indkomst i 2024 for Frederiksberg-borgere, beregnet efter samme eller dokumenterbart tilsvarende definition som Københavns Kommunes [KKIND5](https://kk.statistikbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=KKIND5&PLanguage=1). Kan I henvise til en offentlig kilde eller levere én aggregeret middelværdi med dokumentation?

Kan I samtidig oplyse:

- præcis variabel, registerkilde og version hos Danmarks Statistik;
- familiedefinition, ækvivaleringsskala med numeriske vægte og personfordeling;
- populationsfilter, alders- og skattepligtskrav samt bopælsdato;
- indkomstår og nominelle/faste priser med eventuelt basisår;
- behandling af nul, negative og manglende indkomster;
- afrundings- og diskretionsregler?

Hvis en direkte middelværdi ikke findes, vil ti decilgennemsnit med personantal og regler for decildannelse/ties være nyttige. Bekræft gerne, om opgørelsen kan sammenlignes med KKIND5, og angiv kendte definitionsforskelle. Jeg har set jeres Boligredegørelse 2025, men dens personlige/familieindkomsttal for 2022 dokumenterer ikke det ønskede mål for 2024. Jeg efterspørger kun aggregerede tal og metodeoplysninger.

Med venlig hilsen
[Navn og institution]
'''


def render_report(comparison, reviews, coverage, evidence, result, config):
    matrix = '\n'.join(f"| {r.attribute} | {r.copenhagen} | {r.frederiksberg} | {r.status} |" for r in comparison.itertuples())
    inventory = '\n'.join(f"| [{Path(r.local_path).name}](../{r.local_path}) | {r.source_file_id} | `{r.sha256}` |" for r in evidence.sort_values('local_path').itertuples())
    reviewed = '\n'.join(f"| [{r.source_name}]({r.source_url}) | {r.role} | {r.relevant_definition} | No |" for r in reviews.itertuples())
    missing = '\n'.join(f"| {r.analysis_area_name} | `{r.analysis_area}` | {r.candidate_source_table or 'Not obtained'} | NULL | {r.status} |" for r in coverage.itertuples())
    queries = '\n'.join('- `' + q + '`' for q in config['search_log']['queries'])
    frb_files = sum(d.get('institution', 'Frederiksberg Municipality') == 'Frederiksberg Municipality' for d in config['documents'])
    city_files = len(config['documents']) - frb_files
    return f'''# Income harmonisation — municipal-source investigation

**Decision, 4 October 2026: unresolved; primary modelling remains blocked.** Copenhagen Municipality KKIND5 is the district candidate. No matching Frederiksberg Municipality-issued 2024 equivalised mean or ten-decile table was identified in the reviewed public material. Missing target data and definitions prevent verification; no primary context value or final eleven-area income table was implemented.

This is PostgreSQL investigation `{config['investigation_id']}`. The existing guard remains `unverified`; the V3 refactor, income/density M0 controls and eleven peer areas are preserved. Frederiksberg is one analysis area without a special indicator. A shared register provider does not establish identical variables, weighting or filters.

## Authoritative evidence and definitions

References: [C: Copenhagen Statistics Bank documentation, printed pp.19–21; suppression p.3](https://www.kk.dk/sites/default/files/2021-11/KK%20Statistikbank%20dokumentation_04112021.pdf); [K: KKIND5 information](https://kk.statistikbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=KKIND5&PLanguage=1&TabStrip=Info); [F: Frederiksberg Boligredegørelsen 2025, pp.6–7, 20, 44, 51, 66 and endnotes 2/12 on p.75](https://www.frederiksberg.dk/media/yvnpnuwn/boligredegoerelsen-2025.pdf); [P: Copenhagen poverty-methods report 2025, p.31](https://www.kk.dk/sites/default/files/2025-11/Bilag%201.%20%28B%C3%B8rne-%29fattigdom%20i%20K%C3%B8benhavn%202025_t.pdf).

The Frederiksberg column describes available leads, not an obtained matching target statistic. `Incompatible` applies to the specified published alternative; `unresolved` does not assert that a matching unpublished statistic cannot exist. Geography/unit qualifications alone do not establish harmonisation. No material row is verified equivalent.

| Attribute | Copenhagen Municipality | Frederiksberg Municipality | Harmonised? |
| --- | --- | --- | --- |
{matrix}

## Public-source search and rejected alternatives

F uses Statistics Denmark research registers. Its 2022 before-tax personal-income figures cover residents aged 15+ (INDKP222; note 2). Its IND disposable-income figures concern selected persons or families; figure 4.5 is a family mean for families with children. Note 12 does not document equivalisation, a matching eligible-person filter or a 2024 all-resident mean. These figures cannot supply the required value. Publication year 2025 is not income year 2024. No figure was digitised, inflation-adjusted, combined or silently substituted.

| Official reviewed source | Role | Recorded definition/scope | Matching 2024 target found? |
| --- | --- | --- | --- |
{reviewed}

The municipal facts, financial key-figure and publication-index pages and linked planning/accounts reports were inspected alongside F. Search terms included:

{queries}

Search date: {config['search_log']['date']}. {config['search_log']['scope_limit']} No municipal downloadable matching table or decile dataset was obtained. Website search coverage and unpublished administrative data are not exhaustively observable; failure to find is not proof of absence.

The expanded search also found [Frederiksberg's 2019 sustainable-development mapping, p.33](https://baeredygtig.frederiksberg.dk/media/vhnl1cng/kortlaegning_verdensmaal.pdf): sex-specific annual disposable-income figures, without the required 2024 equivalised population definition. They were not combined into a mean. P documents numeric weights 1/0.5/0.3 in Copenhagen's poverty methods, but uses a different, restricted poverty population. No table-specific KKIND5 processing link was found; the scale is supporting evidence, not verified equivalence.

## Prespecified computation and QA

The target remains the eligible-person mean of family-equivalised disposable income after taxes/interest, with the same income year, price basis, family definition, scale, person allocation and eligibility/zero/negative/missing rules across both municipal sources.

For deciles: `income[g] = sum_d n[g,d] * mean[g,d] / sum_d n[g,d]`, using authoritative eligible-person counts. `sum_d mean[g,d] / 10` is permitted only if producers confirm equivalent equal-person grouping and document finite-count/tie handling sufficiently to justify it. An explicitly matching municipality-issued direct Frederiksberg mean may be used instead. None of these conditions is currently met for the new pair. No Airbnb data or predictive performance enters a source/transformation decision.

Different administrative geography is acceptable: ten City districts and one Frederiksberg municipality, with equivalent statistical concept and denominator. It does not require a modelling dummy. National IFOR35 is reserved for methodological support and QA under this proposed route and is not used to populate the missing municipal value.

Copenhagen district-to-municipality QA requires appropriate income-eligible 2024 district/unassigned counts. They remain unavailable, so reconstruction is **NULL**. The earlier separately published municipal decile-mean comparison differed by **329 DKK (0.0965%)**; it remains contextual QA from the previous route, not a binding national-identity requirement for a municipal route. Its exact cause is unconfirmed.

The former 1-DKK rounding-only envelope remains a conditional diagnostic for nearest-whole-DKK means with exact weights. It is not a new unconditional approval tolerance. Small explained national/municipal differences can be acceptable after the two municipal definitions are verified; authoritative explanations must support them. No discrepancy has been explained by conjecture, and no new empirical materiality threshold was selected without a matching Frederiksberg value.

## Eleven-area evidence coverage — not a final income table

The frozen official crosswalk supplies names/codes (source EPSG:4326; no spatial transformation performed). All proposed harmonised incomes remain NULL. The previously computed inspection candidates remain in their original SQL investigation and exports, without promotion to primary context.

| Official area | analysis_area | Municipal candidate | Proposed harmonised income | Evidence status |
| --- | --- | --- | --- | --- |
{missing}

## Provenance and reproducibility

{frb_files} new official Frederiksberg files and {city_files} new City methods file are immutable. Their source institution, URL, acquisition timestamp, extent, document/reference year, unit, price basis, review role, file size and SHA-256 are recorded; unsupported metadata fields are explicitly NULL. The five reused City files retain their original identities/checksums. Source registration is in `meta.source_files`; definition review, search log, source reviews, coverage and diagnostics are in `v3_analysis.artifacts`. Aggregate CSV/JSON/report exports are read back from PostgreSQL and are not alternative analytical sources.

| Saved evidence | SQL source ID | SHA-256 |
| --- | --- | --- |
{inventory}

Reproduce with `make municipal-income-evidence`, then `make income-audit`. Rules: `config/municipal_income_investigation.json`. SQL/export metadata: `outputs/tables/reproducibility/municipal_income_investigation_metadata.json`. Source inventory: `outputs/tables/data/municipal_income_source_inventory.csv`. The reviewed matrix and area-coverage exports are under `outputs/tables/area_context`.

The previous KKIND5/IFOR35 investigation (code, report, configs, exports, logs and DOCX copies) is preserved byte-for-byte with a checksum manifest in `archive/income_investigations/kkind5_ifor35_20261004`; its PostgreSQL run and all raw KKIND3/INDKP106/KKIND5/IFOR35 evidence remain intact. The initial seven-file municipal review is also preserved in `archive/income_investigations/municipal_income_harmonisation_20261004` and its original SQL record; this expanded review has a separate investigation ID. The prior 195-file freeze is preserved in `config/frozen_inputs_before_municipal_income_investigation.json`; an explicit evidence-only extension adds {len(config['documents'])} files. The original 178 inputs and the 793-file V2 archive remain unchanged.

## Contact-ready gap and stop condition

The [Frederiksberg request draft](frederiksberg_income_evidence_request.md) asks for a matching direct 2024 mean or decile means/counts and its exact register-variable/version, family definition, numeric equivalisation scale, population/age/full-tax filter, residence date, price basis, zero/negative/missing treatment and suppression/rounding/tie rules. It has **not been sent**. Public contact routing is documented, without inventing a specialist recipient.

Copenhagen also needs table-specific confirmation linking the supported numeric scale to KKIND5, plus its variable/version, operational family/population rules, raw price basis and decile/rounding/suppression treatment. The [official 2026 City publication](https://indrebylokaludvalg.kk.dk/sites/default/files/2026-06/260317%20N%C3%B8gletalskatalog%20-%20Indre%20By%202026%20-%20Til%20Bydelsplan.pdf) describes a price-adjusted chart and a 15+ caption despite citing KKIND5; it cannot override the table-specific eligible-family population or establish the raw basis. Those publication/table ambiguities require producer clarification.

The guard cannot pass until a real Frederiksberg municipal value and the material definitions above are supported by authoritative evidence. No final income table, primary replacement, primary model or full rerun was produced. Current clean listings: {result['current_clean_listing_rows']}; primary-model artifact rows: {result['primary_model_artifact_rows']}.
'''


def run():
    config = json.loads(CONFIG_PATH.read_text())
    design = json.loads((PROJECT_ROOT / 'config/research_design.json').read_text())
    if config['status'] != 'unverified' or design['income_harmonisation']['status'] != 'unverified':
        raise RuntimeError('This incomplete evidence review cannot certify harmonisation')
    for archive_root in [PRIOR_ARCHIVE, PROJECT_ROOT / 'archive/income_investigations/municipal_income_harmonisation_20261004']:
        archive = json.loads((archive_root / 'checksums.json').read_text())
        for path, digest in archive['files'].items():
            if sha256_file(archive_root / path) != digest:
                raise RuntimeError('Previous income investigation archive changed: ' + path)
    required = {d['path'] for d in config['documents']} | {CITY_DOC, CITY_INFO,
        'data/raw/copenhagen_statbank/2026-10-04/income_harmonisation/KKIND5_2024.csv',
        'data/raw/copenhagen_statbank/2026-10-04/income_harmonisation/KKIND5_2024_selection.json',
        'data/raw/copenhagen_statbank/2026-10-04/income_harmonisation/city_income_publication_2026.pdf'}
    entries = [e for e in read_manifest()['files'] if e['local_path'] in required]
    if {e['local_path'] for e in entries} != required:
        raise RuntimeError('Required municipal/City evidence missing from manifest')
    records = [prepare_source(PROJECT_ROOT / e['local_path'], manifest={e['local_path']: e}) for e in entries]
    run_id = config['investigation_id']
    metadata = {'version': 'municipal_income_investigation_v3', 'status': 'blocked',
                'scope': 'Municipal income evidence only; no primary context adoption or model fitting',
                'source_sha256': {e['local_path']: e['sha256'] for e in entries},
                'config_sha256': sha256_file(CONFIG_PATH),
                'code_sha256': {p: sha256_file(PROJECT_ROOT / p) for p in [
                    'src/pipeline/review_municipal_income_sources.py', 'src/ingestion/acquire_municipal_income_evidence.py']},
                'previous_investigation_id': 'income_harmonisation_20261004',
                'previous_municipal_investigation_id': config['previous_municipal_investigation_id'],
                'previous_archive_manifest_sha256': sha256_file(PRIOR_ARCHIVE / 'checksums.json'),
                'crosswalk_source_crs_epsg': 4326, 'spatial_operation': 'none; official code/name reuse',
                'primary_models_fitted': False, 'messages_sent': False,
                'national_source_role': config['national_IFOR35_role'],
                'commands': ['make municipal-income-evidence', 'make income-audit', 'make preflight']}
    engine = get_engine()
    try:
        ids = dict(zip([e['local_path'] for e in entries], register_records(engine, records), strict=True))
        evidence = [{**e, 'source_file_id': ids[e['local_path']]} for e in entries]
        with engine.begin() as conn:
            previous = conn.scalar(text('SELECT metadata FROM v3_analysis.runs WHERE run_id=:id'), {'id': run_id})
            if previous and (previous['source_sha256'] != metadata['source_sha256'] or previous['config_sha256'] != metadata['config_sha256']):
                raise RuntimeError('Frozen evidence/rules changed; register a new investigation version')
            conn.execute(text("INSERT INTO v3_analysis.runs(run_id,status,metadata) VALUES(:id,'income_investigation_blocked',CAST(:metadata AS jsonb)) "
                              "ON CONFLICT(run_id) DO UPDATE SET metadata=EXCLUDED.metadata,finished_at=now()"),
                         {'id': run_id, 'metadata': json.dumps(metadata)})
            result = {'status': 'blocked', 'matching_frederiksberg_municipal_mean_dkk': None,
                      'reconstructed_copenhagen_municipality_dkk': None,
                      'guard_status': design['income_harmonisation']['status'],
                      'national_values_used_as_primary': False,
                      'matching_public_statistic_not_identified': True,
                      'claim_scope': config['search_log']['scope_limit'],
                      'current_clean_listing_rows': conn.scalar(text('SELECT count(*) FROM v3_clean.airbnb_listings')),
                      'primary_model_artifact_rows': conn.scalar(text("SELECT count(*) FROM v3_analysis.artifacts WHERE family='primary_models'"))}
            artifacts = {'municipal_income_definition_comparison': definition_comparison(),
                         'municipal_income_source_reviews': source_reviews(config),
                         'municipal_income_area_coverage': area_coverage(),
                         'municipal_income_source_evidence': evidence,
                         'municipal_income_search_log': [config['search_log']],
                         'municipal_income_diagnostics': [result]}
            for artifact, rows in artifacts.items():
                persist(conn, run_id, 'area_context', artifact, rows)
        with engine.connect() as conn:
            frames = {a: load_artifact(conn, run_id, 'area_context', a) for a in artifacts}
        for artifact in ['municipal_income_definition_comparison', 'municipal_income_source_reviews', 'municipal_income_area_coverage']:
            export('area_context', artifact + '.csv', frames[artifact])
        export('data', 'municipal_income_source_inventory.csv', frames['municipal_income_source_evidence'])
        result = frames['municipal_income_diagnostics'].iloc[0].to_dict()
        write_json(PROJECT_ROOT / 'outputs/tables/area_context/municipal_income_diagnostics.json', result)
        (PROJECT_ROOT / 'reports/income_harmonisation_status.md').write_text(render_report(
            frames['municipal_income_definition_comparison'], frames['municipal_income_source_reviews'],
            frames['municipal_income_area_coverage'], frames['municipal_income_source_evidence'], result, config))
        (PROJECT_ROOT / 'reports/frederiksberg_income_evidence_request.md').write_text(evidence_request())
        write_json(PROJECT_ROOT / 'outputs/tables/reproducibility/municipal_income_investigation_metadata.json',
                   {**metadata, 'investigation_id': run_id, 'registered_evidence_files': len(entries),
                    'new_municipal_files': len(config['documents']),
                    'new_frederiksberg_files': sum(d.get('institution', 'Frederiksberg Municipality') == 'Frederiksberg Municipality' for d in config['documents']), **result})
        return result
    finally:
        engine.dispose()


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
