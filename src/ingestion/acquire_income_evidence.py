"""Acquire immutable official income metadata; never approve harmonisation here."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from src.ingestion.common import PROJECT_ROOT, USER_AGENT, sha256_bytes, update_manifest, utc_now
from src.ingestion.download_copenhagen_statbank import parse_options

DATE = '2026-10-04'
CITY_ROOT = Path('data/raw/copenhagen_statbank') / DATE / 'income_harmonisation'
DST_ROOT = Path('data/raw/municipality_statbank') / DATE / 'income_harmonisation'
CITY_SELECT = 'https://kk.statistikbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=KKIND5&PLanguage=1'
CITY_INFO = CITY_SELECT + '&TabStrip=Info'
DST_INFO = 'https://www.statbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=IFOR35&PLanguage=1&TabStrip=Info'
DOCUMENTS = [
    (CITY_ROOT, 'KKIND5_selection.html', CITY_SELECT, 'City of Copenhagen Statbank', 'Copenhagen districts and available administrative groupings'),
    (CITY_ROOT, 'KKIND5_information.html', CITY_INFO, 'City of Copenhagen Statbank', 'Copenhagen districts and available administrative groupings'),
    (CITY_ROOT, 'copenhagen_statbank_documentation.pdf', 'https://www.kk.dk/sites/default/files/2021-11/KK%20Statistikbank%20dokumentation_04112021.pdf', 'City of Copenhagen', 'Copenhagen Municipality'),
    (DST_ROOT, 'IFOR35_information.html', DST_INFO, 'Statistics Denmark StatBank', 'Danish municipalities'),
    (DST_ROOT, 'income_statistical_presentation.html', 'https://www.dst.dk/en/Statistik/dokumentation/documentationofstatistics/income-statistics/statistical-presentation', 'Statistics Denmark', 'Denmark'),
    (DST_ROOT, 'income_distribution.html', 'https://www.dst.dk/en/Statistik/emner/arbejde-og-indkomst/indkomst-og-loen/indkomstfordeling', 'Statistics Denmark', 'Denmark'),
    (DST_ROOT, 'IFOR35_linked_documentation.html', 'https://www.dst.dk/documentationofstatistics/807ba2cb-a9ca-4400-9c6a-3400bfff2359', 'Statistics Denmark', 'Denmark'),
    (CITY_ROOT, 'city_income_publication_2026.pdf', 'https://indrebylokaludvalg.kk.dk/sites/default/files/2026-06/260317%20N%C3%B8gletalskatalog%20-%20Indre%20By%202026%20-%20Til%20Bydelsplan.pdf', 'City of Copenhagen', 'Copenhagen districts'),
    (DST_ROOT, 'income_statistics_2024.pdf', 'https://www.dst.dk/Site/Dst/SingleFiles/kvaldeklbilag.aspx?filename=3568f78c-1850-44fa-997c-f002605ec4c3Income_Statistics_2024&ext=.pdf', 'Statistics Denmark', 'Denmark'),
    (DST_ROOT, 'AEKVIVADISP_13.html', 'https://www.dst.dk/da/Statistik/dokumentation/Times/personindkomst/aekvivadisp-13', 'Statistics Denmark', 'Denmark'),
    (DST_ROOT, 'AEKVIVADISP.html', 'https://www.dst.dk/da/Statistik/dokumentation/Times/personindkomst/aekvivadisp', 'Statistics Denmark', 'Denmark'),
    (DST_ROOT, 'FAMAEKVIVADISP_population.html', 'https://www.dst.dk/da/TilSalg/data-til-forskning/generelt-om-data/dokumentation-af-data/hoejkvalitetsvariable/familieindkomst/famaekvivadisp', 'Statistics Denmark', 'Denmark'),
]


def save_payload(root, name, payload, url, provider, extent, *, request=None, content_type=None):
    path = PROJECT_ROOT / root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError('Immutable evidence already exists; use its saved bytes: ' + str(path))
    with path.open('xb') as handle:
        handle.write(payload)
    entry = {'provider':provider,'asset':name,'source_url':url,
             'local_path':path.relative_to(PROJECT_ROOT).as_posix(),
             'downloaded_at_utc':utc_now(),'size_bytes':len(payload),'sha256':sha256_bytes(payload),
             'geographic_extent':extent,'status':'downloaded','content_type':content_type,
             'caveats':'Income harmonisation investigation evidence; not approved for primary context.'}
    if request is not None:
        entry['request'] = request
    update_manifest([entry])
    return entry


def acquire_metadata():
    session=requests.Session();session.headers['User-Agent']=USER_AGENT
    for root,name,url,provider,extent in DOCUMENTS:
        path=PROJECT_ROOT/root/name
        if path.exists():
            print('Using preserved evidence '+path.relative_to(PROJECT_ROOT).as_posix(),flush=True)
            continue
        response=session.get(url,timeout=60);response.raise_for_status()
        save_payload(root,name,response.content,response.url,provider,extent,content_type=response.headers.get('Content-Type'))
        print('Saved '+name,flush=True)
    name='IFOR35_tableinfo.json'
    if not (PROJECT_ROOT/DST_ROOT/name).exists():
        request={'table':'IFOR35','format':'JSON','lang':'en'}
        url='https://api.statbank.dk/v1/tableinfo'
        response=session.post(url,json=request,timeout=60);response.raise_for_status();response.json()
        save_payload(DST_ROOT,name,response.content,url,'Statistics Denmark StatBank','Danish municipalities',request=request,content_type=response.headers.get('Content-Type'))
    city_html=(PROJECT_ROOT/CITY_ROOT/'KKIND5_selection.html').read_bytes().decode('iso-8859-1')
    options=parse_options(city_html)
    national=json.loads((PROJECT_ROOT/DST_ROOT/name).read_text())
    print(json.dumps({'KKIND5_options':{k:[v for v in values if k!='var1' or v[0]=='TOT' or v[0].startswith('10')] for k,values in options.items()},
                     'IFOR35_variables':national.get('variables'),'IFOR35_notes':national.get('note')},ensure_ascii=False,indent=2))
    for root,name,_,_,_ in DOCUMENTS:
        if name.endswith('.html') and ('information' in name):
            soup=BeautifulSoup((PROJECT_ROOT/root/name).read_bytes(),'html.parser')
            print(name+': '+soup.get_text(' ',strip=True)[-10000:])


def acquire_deciles():
    from src.ingestion.download_copenhagen_statbank import build_selection
    session=requests.Session();session.headers['User-Agent']=USER_AGENT
    if not (PROJECT_ROOT/CITY_ROOT/'KKIND5_2024.csv').exists():
        metadata=json.loads((PROJECT_ROOT/'data/raw/copenhagen_statbank/2026-09-29/metadata/KKIND3.json').read_text())
        districts=metadata['selected_codes']['var1']
        spec={'table':'KKIND5','subject_code':'305','description':'Income harmonisation investigation: all ten deciles for ten official districts and Copenhagen total, 2024',
              'selections':{'var1':['1000',*districts],'var2':[str(i) for i in range(1,11)],'var3':['2024']}}
        payload,selection,_=build_selection(session,spec)
        save_payload(CITY_ROOT,'KKIND5_2024.csv',payload,selection['response_url'],'City of Copenhagen Statbank','Ten Copenhagen districts and Copenhagen municipality total',request=spec['selections'],content_type='text/csv')
        save_payload(CITY_ROOT,'KKIND5_2024_selection.json',json.dumps(selection,ensure_ascii=False,indent=2).encode(),CITY_SELECT,'City of Copenhagen Statbank','Ten Copenhagen districts and Copenhagen municipality total',request=spec['selections'],content_type='application/json')
    if not (PROJECT_ROOT/DST_ROOT/'IFOR35_2024.csv').exists():
        request={'table':'IFOR35','format':'CSV','lang':'en','valuePresentation':'Value',
                 'variables':[{'code':'DECILGEN','values':[f'{i}DC' for i in range(1,11)]},
                              {'code':'KOMMUNEDK','values':['101','147']},
                              {'code':'PRISENHED','values':['006','005']},
                              {'code':'Tid','values':['2024']}]}
        url='https://api.statbank.dk/v1/data'
        response=session.post(url,json=request,timeout=60);response.raise_for_status()
        save_payload(DST_ROOT,'IFOR35_2024.csv',response.content,response.url,'Statistics Denmark StatBank','Copenhagen and Frederiksberg municipalities',request=request,content_type=response.headers.get('Content-Type'))
        save_payload(DST_ROOT,'IFOR35_2024_selection.json',json.dumps(request,indent=2).encode(),url,'Statistics Denmark StatBank','Copenhagen and Frederiksberg municipalities',request=request,content_type='application/json')
    print('Income decile data acquired; no harmonisation status changed.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--deciles',action='store_true');args=parser.parse_args()
    if args.deciles: acquire_deciles()
    else: acquire_metadata()
