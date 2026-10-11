"""Preserve official municipal income-source leads, without adopting their values."""
from __future__ import annotations

import json

import requests

from src.ingestion.acquire_income_evidence import save_payload
from src.ingestion.common import PROJECT_ROOT, USER_AGENT, update_manifest, sha256_file

CONFIG = PROJECT_ROOT / 'config/municipal_income_investigation.json'


def acquire():
    config = json.loads(CONFIG.read_text())
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    for document in config['documents']:
        path = PROJECT_ROOT / document['path']
        if path.exists():
            from src.ingestion.common import read_manifest
            previous = next(e for e in read_manifest()['files'] if e['local_path'] == document['path'])
            if previous['sha256'] != sha256_file(path):
                raise RuntimeError('Preserved municipal evidence differs from its checksum')
            print('Using preserved evidence: ' + path.name, flush=True)
            continue
        response = session.get(document['url'], timeout=60)
        response.raise_for_status()
        if path.suffix == '.pdf' and not response.content.startswith(b'%PDF'):
            raise ValueError('Expected PDF, received another content type: ' + document['url'])
        entry = save_payload(path.parent.relative_to(PROJECT_ROOT), path.name, response.content,
                             response.url, document.get('institution', 'Frederiksberg Municipality'),
                             document.get('geographic_extent', 'Frederiksberg Municipality'),
                             content_type=response.headers.get('Content-Type'))
        entry.update(source_page=document['url'], table=document['name'],
                     reference_year=document['reference_year'], unit=document['unit'],
                     price_basis=document['price_basis'], relevant_definition=document['definition'],
                     review_role=document['role'])
        update_manifest([entry])
        print('Saved ' + path.name, flush=True)
    print('Municipal evidence preserved; harmonisation remains unverified.', flush=True)


if __name__ == '__main__':
    acquire()
