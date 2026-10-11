"""Persist and report source-validation diagnostics without approving core income."""
from __future__ import annotations

import csv
import io
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.db.connection import get_engine
from src.db.sources import prepare_source, register_records
from src.ingestion.acquire_income_evidence import CITY_ROOT, DST_ROOT
from src.ingestion.common import PROJECT_ROOT, read_manifest, sha256_file, write_json
from src.ingestion.download_copenhagen_statbank import decode_csv
from src.pipeline.protocol import AREA_NAMES, canonical_hash
from src.pipeline.storage import export, persist, load_artifact

INVESTIGATION_ID='income_harmonisation_20261004'
CONFIG_PATH=PROJECT_ROOT/'config/income_harmonisation_investigation.json'


def numeric_cell(value, *, zero_is_suppression=False):
    """No missing-value conversion; a zero suppression marker is ambiguous."""
    try:
        number=Decimal(value.strip())
    except (InvalidOperation,AttributeError):
        raise ValueError('Missing, suppressed or invalid income cell: '+repr(value)) from None
    if not number.is_finite() or (zero_is_suppression and number==0):
        raise ValueError('Nonfinite or ambiguous suppressed income cell: '+repr(value))
    return number


def decile_mean(values, weights=None):
    if len(values)!=10:
        raise ValueError('All ten reported decile means are required')
    values=[numeric_cell(str(v)) for v in values]
    if weights is None:
        return sum(values)/Decimal(10)
    if len(weights)!=10:
        raise ValueError('One authoritative population weight is required per decile')
    weights=[numeric_cell(str(w)) for w in weights]
    if any(w<=0 for w in weights):
        raise ValueError('Decile population weights must be positive')
    return sum(v*w for v,w in zip(values,weights))/sum(weights)


def reconstruct_municipality(area_means, eligible_person_counts):
    if set(area_means)!=set(eligible_person_counts) or not area_means:
        raise ValueError('Exact income-eligible weights required for every included geography')
    counts={k:numeric_cell(str(v)) for k,v in eligible_person_counts.items()}
    if any(c<=0 for c in counts.values()):
        raise ValueError('Income-eligible counts must be positive')
    return sum(numeric_cell(str(area_means[k]))*n for k,n in counts.items())/sum(counts.values())


def official_crosswalk():
    root=PROJECT_ROOT/'data/raw/official_boundaries/2026-09-29'
    districts=json.loads((root/'copenhagen_districts.geojson').read_text())['features']
    lookup={str(1000+int(f['properties']['bydel_nr'])):
            {'analysis_area':f"cph_{int(f['properties']['bydel_nr']):02d}",
             'analysis_area_name':f['properties']['navn']} for f in districts}
    frb=json.loads((root/'frederiksberg_municipality.geojson').read_text())['properties']
    lookup['147']={'analysis_area':'frederiksberg_'+str(frb['kode']).zfill(4),'analysis_area_name':frb['navn']}
    if set(r['analysis_area'] for r in lookup.values())!=set(AREA_NAMES):
        raise RuntimeError('Official frozen crosswalk does not match the eleven V3 peer areas')
    return lookup


def parse_city():
    root=PROJECT_ROOT/CITY_ROOT
    path=root/'KKIND5_2024.csv'
    metadata=json.loads((root/'KKIND5_2024_selection.json').read_text())
    codes=metadata['selected_codes'];labels=metadata['selected_labels']
    if codes['var2']!=[str(i) for i in range(1,11)] or codes['var3']!=['2024']:
        raise RuntimeError('Unexpected City decile ordering/year')
    geographic_codes=dict(zip(labels['var1'],codes['var1'],strict=True))
    rows=decode_csv(path.read_bytes());records=[]
    for row in rows:
        if len(row)!=12 or row[0]!='2024' or row[1] not in geographic_codes:
            raise RuntimeError('Unexpected City CSV layout/label/year')
        records.append({'source_table':'KKIND5','source_geography':geographic_codes[row[1]],
                        'source_geography_label':row[1],'year':'2024','price_basis':'not_confirmed',
                        'deciles':[str(numeric_cell(v)) for v in row[2:]],'source_path':path.relative_to(PROJECT_ROOT).as_posix(),
                        'source_checksum':sha256_file(path)})
    if len(records)!=11 or {r['source_geography'] for r in records}!=set(codes['var1']):
        raise RuntimeError('Missing or duplicated City geography')
    return records


def parse_national():
    root=PROJECT_ROOT/DST_ROOT;path=root/'IFOR35_2024.csv'
    metadata=json.loads((root/'IFOR35_tableinfo.json').read_text())
    variables={v['id']:{item['text']:item['id'] for item in v['values']} for v in metadata['variables']}
    rows=list(csv.DictReader(io.StringIO(path.read_bytes().decode('utf-8-sig')),delimiter=';'))
    groups={}
    for row in rows:
        try:
            geography=variables['KOMMUNEDK'][row['KOMMUNEDK']]
            price=variables['PRISENHED'][row['PRISENHED']]
            decile=int(variables['DECILGEN'][row['DECILGEN']].removesuffix('DC'))
        except (KeyError,ValueError):
            raise RuntimeError('Unexpected national CSV dimensions') from None
        if geography not in ['101','147'] or price not in ['005','006'] or row['TID']!='2024':
            raise RuntimeError('Unrequested national year/geography/price basis')
        key=(geography,price)
        if decile in groups.setdefault(key,{}):
            raise RuntimeError('Duplicate national decile')
        groups[key][decile]=str(numeric_cell(row['INDHOLD'],zero_is_suppression=metadata.get('suppressedDataValue')=='0'))
    if len(groups)!=4 or any(set(g)!=set(range(1,11)) for g in groups.values()):
        raise RuntimeError('Incomplete national deciles')
    return [{'source_table':'IFOR35','source_geography':geo,
             'source_geography_label':next(label for label,code in variables['KOMMUNEDK'].items() if code==geo),
             'year':'2024','price_basis':'nominal_current_prices' if price=='006' else 'constant_prices_base_not_in_metadata',
             'price_unit_code':price,'deciles':[groups[(geo,price)][i] for i in range(1,11)],
             'source_path':path.relative_to(PROJECT_ROOT).as_posix(),'source_checksum':sha256_file(path)}
            for geo,price in sorted(groups)]


def candidates():
    crosswalk=official_crosswalk();rows=parse_city()+parse_national()
    for row in rows:
        if row['source_table']=='KKIND5' and row['source_geography']!='1000':
            area=crosswalk[row['source_geography']]
            label=row['source_geography_label'].removeprefix('District - ').replace('/','-')
            if label!=area['analysis_area_name']:
                raise RuntimeError('City labels do not agree with the official V3 crosswalk')
            row.update(area)
        elif row['source_geography']=='147':
            row.update(crosswalk['147'])
        else:
            row.update(analysis_area=None,analysis_area_name='Copenhagen municipality total')
        row.update(candidate_unweighted_decile_mean_dkk=str(decile_mean(row['deciles'])),
                   transformation='sum of all ten reported decile means / 10; equal-person weighting conditional',
                   harmonisation_status='unverified',eligible_person_count=None,
                   statistical_population_note='Source-specific family eligibility and tie/rounding rules require confirmation')
    return rows


def diagnostics(rows):
    city=next(r for r in rows if r['source_table']=='KKIND5' and r['source_geography']=='1000')
    national=next(r for r in rows if r['source_table']=='IFOR35' and r['source_geography']=='101' and r['price_unit_code']=='006')
    c=numeric_cell(city['candidate_unweighted_decile_mean_dkk']);n=numeric_cell(national['candidate_unweighted_decile_mean_dkk'])
    return {'status':'blocked','scope':'income source validation; no primary modelling',
            'city_published_municipality_decile_mean_dkk':str(c),
            'official_IFOR35_municipality_decile_mean_dkk':str(n),
            'signed_difference_city_minus_national_dkk':str(c-n),
            'absolute_difference_dkk':str(abs(c-n)),
            'percentage_difference_city_minus_national':str((c-n)/n*100),
            'decile_differences_city_minus_national_dkk':[str(Decimal(a)-Decimal(b)) for a,b in zip(city['deciles'],national['deciles'])],
            'reconstructed_from_ten_districts_dkk':None,
            'reconstruction_status':'not_identifiable_without_exact_income_eligible_2024_district_and_unassigned_counts',
            'comparison_price_basis_compatibility':'KKIND5 price basis not proven; IFOR35 explicitly nominal',
            'rounding_rule_path':'config/income_harmonisation_investigation.json',
            'exceeds_conditional_one_dkk_rounding_envelope':abs(c-n)>Decimal(1),
            'evidence_gaps':['KKIND5 exact register-variable version, OECD scale and zero/missing rules',
                             'KKIND5 raw price basis/base year',
                             'Exact decile counts/tie handling and income-eligible district/unassigned weights',
                             'Provider reconciliation of the 329 DKK municipal mean difference, especially tenth decile'],
            'explanation':'Exact cause is unestablished. Population linkage, record version and decile construction may contribute; these are hypotheses, not confirmed explanations.'}


def write_status_report(estimates,sources,result):
    city_url='https://www.kk.dk/sites/default/files/2021-11/KK%20Statistikbank%20dokumentation_04112021.pdf'
    national_url='https://www.dst.dk/Site/Dst/SingleFiles/kvaldeklbilag.aspx?filename=3568f78c-1850-44fa-997c-f002605ec4c3Income_Statistics_2024&ext=.pdf'
    selected=estimates.loc[(estimates.source_table=='KKIND5')&estimates.analysis_area.notna() |
                          (estimates.source_table=='IFOR35')&(estimates.source_geography=='147')&(estimates.price_unit_code=='006')]
    if len(selected)!=11:
        raise RuntimeError('Expected eleven explicitly unverified area candidates')
    value_rows='\n'.join(f"| {r.analysis_area_name} | `{r.analysis_area}` | {r.source_table} / {r.source_geography} | {r.candidate_unweighted_decile_mean_dkk} |" for r in selected.sort_values('analysis_area_name').itertuples())
    difference_rows='\n'.join(f'| {i} | {difference} |' for i,difference in enumerate(result['decile_differences_city_minus_national_dkk'],1))
    hash_rows='\n'.join(f"| [{Path(r.local_path).name}](../{r.local_path}) | {r.source_file_id} | `{r.sha256}` |" for r in sources.sort_values('local_path').itertuples())
    report=f'''# Income harmonisation investigation — KKIND5 / IFOR35

**Decision on 4 October 2026: not verified; stop before primary modelling.** The `income_harmonisation` guard remains enabled and unverified. No core income was replaced, no final harmonised eleven-area table was frozen, and no primary model/full pipeline was run. The original V3 refactor, twenty-one applied migration identities and legacy archive remain intact.

This report is regenerated by `src.pipeline.investigate_income_harmonisation` from private PostgreSQL investigation artifacts, official saved metadata and the prespecified investigation rules. The investigation is `{INVESTIGATION_ID}`, with scope limited to income-source validation. No Airbnb outcomes or model performance inform it.

## Evidence and definition comparison

References: [C: Copenhagen documentation, printed pp. 19–20]({city_url}); [N: Income Statistics 2024, sections 2.4–2.6]({national_url}); [T: IFOR35 information](https://www.statbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=IFOR35&PLanguage=1&TabStrip=Info); [V: register equivalised-income variable](https://www.dst.dk/da/Statistik/dokumentation/Times/personindkomst/aekvivadisp-13); [P: register-family population](https://www.dst.dk/da/TilSalg/data-til-forskning/generelt-om-data/dokumentation-af-data/hoejkvalitetsvariable/familieindkomst/famaekvivadisp); [K: KKIND5 information](https://kk.statistikbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=KKIND5&PLanguage=1&TabStrip=Info).

| Attribute | Copenhagen KKIND5 | Frederiksberg IFOR35 | Finding |
| --- | --- | --- | --- |
| Income concept | After-tax/interest family income including imputed rent; person-assigned (C p.20). | Equivalised family disposable income, including imputed rent (N §2.4). | Broad concept aligns. |
| Equivalisation | Weighted family size; weights/version not specified for this table (C). | Modified OECD: 1 / 0.5 / 0.3; E-family allocation (N, V). | KKIND5 exact variable/version needs confirmation. |
| Denominator | Year-end residents in families with a fully taxable adult (C p.20). | Persons in year-end families with an eligible adult resident throughout the year (N §2.6). | Broad population aligns; operational filter/linkage unverified. |
| Age | Distribution-family population; no individual 15+ restriction stated (C). | Includes family children; adult eligibility is required (N). | Do not apply the old personal-income 15+ denominator. |
| Zero income | KKIND5-specific rule not stated; personal-income mean zero exclusion is a separate concept (C). | IFOR35-specific zero rule not established from T/N. | Unresolved. |
| Negative income | KKIND5-specific handling not stated. | Negative losses can affect first decile (T footnote). | Unresolved for City processing. |
| Missing/suppressed | General primary/secondary suppression rules exist (C p.3); table-specific missing-income rule absent. | Register NULLs/eligibility described in V; API suppression marker is `0`. | No source cell filled; table-specific treatment unresolved. |
| Decile construction | Ten equal person groups, sorted by equivalised income (C p.20). | Ten equal person groups, sorted by equivalised income (N §2.4). | Equal weighting justified conceptually; finite counts/ties not supplied. |
| Population weights | Not included in selected table dimensions. | Not included in selected table dimensions. | Exact group and income-eligible district weights unavailable. |
| Price basis | DKK; no selectable price dimension or explicit raw base year (K). | `PRISENHED=006` nominal; `005` constant. | KKIND5 basis remains unconfirmed. |
| Reference year | Explicitly selected 2024 (`var3`). | Explicitly selected 2024 (`Tid`). | Common year available. |
| Unit | Table explicitly DKK (K). | Table unit label “Avg.”; register monetary unit DKK (V). | DKK interpretation retained provisionally; raw unit labels preserved. |
| Common framework | City calculations using Statistics Denmark Research Services (K), IND/BEF (C). | National income-statistics framework; documentation linked in table API (T/N). | Common register framework confirmed; identical processing not proven. |

The register-population documentation P explains full-tax-liability eligibility using `FAMANTALFSKATTEPLIGTIGE > 0`. This supports the conceptual link between the two population descriptions, but does not prove that KKIND5 implements that exact filter/version or identical geography linkage. Copenhagen itself warns of processing differences. No genuine denominator difference is asserted merely from differing wording.

The official [2026 City income publication](https://indrebylokaludvalg.kk.dk/sites/default/files/2026-06/260317%20N%C3%B8gletalskatalog%20-%20Indre%20By%202026%20-%20Til%20Bydelsplan.pdf) describes its KKIND5-based chart as price-adjusted. That does not establish the raw table's base year or whether adjustment occurred in the publication. In the downloaded IFOR35 2024 data, nominal and constant values agree for both selected municipalities; numerical agreement alone does not verify KKIND5's price basis.

## Formal transformation and QA rules

Let `mu[g,d]` be the reported mean for decile d in area g, and `n[g,d]` its income-eligible person count. The population mean is:

`income[g] = sum_d n[g,d] * mu[g,d] / sum_d n[g,d]`.

If each decile contains exactly one tenth of the eligible population, this reduces to `sum_d mu[g,d] / 10`. The two producers' conceptual equal-decile definitions support evaluating this prespecified candidate. They do not establish exact handling of indivisible population counts, tied family incomes, suppression and rounding. Exact or authoritative group weights would resolve that remaining precision question. No decile was dropped, clipped, filled or inferred from model results.

Municipality reconstruction requires `sum_g N[g] * income[g] / sum_g N[g]`, using the same income-eligible 2024 persons and any unassigned geography belonging to the official municipal denominator. **2026 total population, equal district weights and Airbnb listing counts are invalid substitutes.** Neither selected table supplies these district weights. Therefore the requested ten-district reconstruction is unavailable and explicitly NULL, rather than fabricated.

The QA rule was saved in `config/income_harmonisation_investigation.json` before downloading/comparing the decile data. If individual means are rounded to nearest whole DKK and exact population weights are known, two resulting weighted means differ by at most **1 DKK from rounding alone**. Rounding/tie rules are not fully documented, so this is a conditional diagnostic envelope, not an arbitrary equivalence tolerance. No tolerance was expanded after seeing the values.

## Copenhagen compatibility check

An additional direct check compares the two producers' published Copenhagen-municipality decile means. It is **not** a reconstruction from the ten districts and is conditional on confirming common price basis and exact decile weights.

| Quantity | DKK / status |
| --- | --- |
| Reconstruction from ten districts | Unavailable: exact income-eligible district/unassigned weights missing |
| KKIND5 published Copenhagen-total ten-decile arithmetic mean | {result['city_published_municipality_decile_mean_dkk']} |
| IFOR35 Copenhagen nominal ten-decile arithmetic mean | {result['official_IFOR35_municipality_decile_mean_dkk']} |
| Signed difference, City minus national | {result['signed_difference_city_minus_national_dkk']} |
| Absolute difference | {result['absolute_difference_dkk']} |
| Percentage difference relative to IFOR35 | {float(result['percentage_difference_city_minus_national']):.6f}% |

| Decile | City minus national mean, DKK |
| --- | --- |
{difference_rows}

The aggregate gap exceeds the conditional whole-DKK rounding envelope. It is about 0.0965%, so it should not be exaggerated as a large substantive income discrepancy. Nevertheless its cause is unresolved; the highest decile differs by 3,376 DKK. Source-date/version, population/geographic linkage and tie handling are possible explanations, **not established explanations**. The evidence cannot attribute the gap or force acceptance.

## Eleven-area candidate values — not harmonised core data

These are inspection arithmetic means only. All rows have status `unverified`; the City price basis and exact denominator/group rules remain unresolved. The official frozen V3 boundary crosswalk supplies names and identifiers, including its slash-to-hyphen normalisation. No neighbourhood mapping is invented. Frederiksberg remains one peer analysis area.

| Official area name | analysis_area | Table / source geography | Unverified candidate mean, DKK |
| --- | --- | --- | --- |
{value_rows}

All ten decile values, year, source geography, price basis, source ID, transformation and SHA-256 are retained in the SQL candidate artifacts and exported to `outputs/tables/area_context/income_candidate_decile_means.csv`. That file also includes municipality-total and alternate-price diagnostics, and is an export rather than a source of truth. No column is labelled harmonised area income.

## Evidence files, provenance and reproducibility

The following immutable files were acquired on 4 October 2026. URLs, request selections, acquisition timestamps, geographic extent, file sizes and checksums are recorded in `data/metadata/source_manifest.json`, `meta.source_files` and the SQL source-evidence artifacts. No spatial operation was performed; official crosswalk source CRS is EPSG:4326. Existing raw inputs were checked unchanged before an explicit append-only evidence freeze extension.

| Evidence file | PostgreSQL source ID | SHA-256 |
| --- | --- | --- |
{hash_rows}

PostgreSQL `v3_analysis.runs` contains a separately labelled `income_investigation_blocked` record. `v3_analysis.artifacts` stores `income_candidate_deciles`, `income_compatibility_diagnostics` and `income_source_evidence` under that investigation ID. This is not a primary-model or full-analysis run. Aggregate exports are regenerated by reading those SQL artifacts.

Commands: `.venv/bin/python -m src.ingestion.acquire_income_evidence`; the same command with `--deciles`; `.venv/bin/python -m src.pipeline.investigate_income_harmonisation`. Metadata: `outputs/tables/reproducibility/income_investigation_metadata.json`. Diagnostics: `outputs/tables/area_context/income_compatibility_diagnostics.json`. Inventory: `outputs/tables/data/income_source_inventory.csv`. Verification commands, test logs and preflight are retained in the reproducibility directory.

## Stop condition and precise evidence needed

To approve this pair, obtain authoritative table-specific confirmation of:

1. KKIND5's exact equivalised-income variable/version, numeric OECD scale, full-family eligibility filter, geography date and zero/negative/missing treatment, matched to IFOR35.
2. KKIND5's raw price basis/base year, and the national monetary unit interpretation.
3. Decile tie/indivisible-count/suppression/rounding rules, plus exact income-eligible 2024 district counts (and unassigned geography) or an authoritative weighted municipal reconstruction.
4. Reconciliation of the Copenhagen difference, especially the tenth decile, without performance-selected adjustments.

Published contacts are the Copenhagen analysis unit (`statistik@okf.kk.dk`) and the IFOR35 contact listed in its metadata (`jaq@dst.dk`). No messages have been sent. These are the questions needed for a producer clarification, not an instruction to weaken the guard.

The old KKIND3/INDKP106 evidence remains immutable and its earlier context audit is preserved in `archive/legacy_v2/reports`. The full pipeline remains blocked. Income stays required in M0; all eleven areas and core density remain specified, and no special dummy, separate context-model family or alternate income fallback has been introduced.
'''
    (PROJECT_ROOT/'reports/income_harmonisation_status.md').write_text(report)


def run():
    rows=candidates();result=diagnostics(rows)
    manifest=read_manifest();entries=[e for e in manifest['files'] if '/income_harmonisation/' in e['local_path']]
    records=[prepare_source(PROJECT_ROOT/e['local_path'],manifest={e['local_path']:e}) for e in entries]
    engine=get_engine()
    try:
        ids=dict(zip([e['local_path'] for e in entries],register_records(engine,records),strict=True))
        for row in rows:
            row['source_file_id']=ids[row['source_path']]
        evidence=[{**entry,'source_file_id':ids[entry['local_path']]} for entry in entries]
        metadata={'version':'income_investigation_v3','scope':result['scope'],'status':'blocked',
                  'source_sha256':{e['local_path']:e['sha256'] for e in entries},
                  'investigation_config_sha256':sha256_file(CONFIG_PATH),
                  'source_code_sha256':sha256_file(Path(__file__)),'crosswalk_source_crs_epsg':4326,
                  'spatial_operation':'none; reuse official source codes/names','primary_models_fitted':False,
                  'commands':['.venv/bin/python -m src.ingestion.acquire_income_evidence',
                              '.venv/bin/python -m src.ingestion.acquire_income_evidence --deciles',
                              '.venv/bin/python -m src.pipeline.investigate_income_harmonisation']}
        with engine.begin() as conn:
            previous=conn.scalar(text('SELECT metadata FROM v3_analysis.runs WHERE run_id=:id'),{'id':INVESTIGATION_ID})
            if previous and (previous['source_sha256']!=metadata['source_sha256'] or previous['investigation_config_sha256']!=metadata['investigation_config_sha256']):
                raise RuntimeError('Frozen investigation sources/configuration changed; register another investigation version')
            conn.execute(text("INSERT INTO v3_analysis.runs(run_id,status,metadata) VALUES(:id,'income_investigation_blocked',CAST(:metadata AS jsonb)) "
                              "ON CONFLICT(run_id) DO UPDATE SET metadata=EXCLUDED.metadata,finished_at=now()"),
                         {'id':INVESTIGATION_ID,'metadata':json.dumps(metadata)})
            persist(conn,INVESTIGATION_ID,'area_context','income_candidate_deciles',rows)
            persist(conn,INVESTIGATION_ID,'area_context','income_compatibility_diagnostics',[result])
            persist(conn,INVESTIGATION_ID,'area_context','income_source_evidence',evidence)
        # All inspection exports are read back from the authoritative database.
        with engine.connect() as conn:
            estimates=load_artifact(conn,INVESTIGATION_ID,'area_context','income_candidate_deciles')
            sources=load_artifact(conn,INVESTIGATION_ID,'area_context','income_source_evidence')
            result=load_artifact(conn,INVESTIGATION_ID,'area_context','income_compatibility_diagnostics').iloc[0].to_dict()
            original_n=conn.scalar(text('SELECT count(*) FROM v3_clean.airbnb_listings'))
            model_n=conn.scalar(text("SELECT count(*) FROM v3_analysis.artifacts WHERE family='primary_models'"))
        write_status_report(estimates,sources,result)
        estimates['deciles']=estimates.deciles.map(json.dumps)
        export('area_context','income_candidate_decile_means.csv',estimates)
        export('data','income_source_inventory.csv',sources)
        write_json(PROJECT_ROOT/'outputs/tables/area_context/income_compatibility_diagnostics.json',result)
        write_json(PROJECT_ROOT/'outputs/tables/reproducibility/income_investigation_metadata.json',
                   {**metadata,'investigation_id':INVESTIGATION_ID,'registered_evidence_files':len(evidence),
                    'private_sql_candidate_records':len(estimates),'current_clean_listing_rows':original_n,
                    'primary_model_artifact_rows':model_n})
        return result
    finally:
        engine.dispose()


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
