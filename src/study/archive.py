"""Resolve preserved recorded paths after explicitly authorized archive moves."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from src.ingestion.common import PROJECT_ROOT,sha256_file


@lru_cache(maxsize=1)
def manifests():
    result=[]
    for name in ['docs/analysis/archive_manifest.json','archive/before_association_amendment/manifest.json',
                 'archive/before_figure_style/manifest.json','archive/before_output_cleanup/manifest.json']:
        path=PROJECT_ROOT/name
        if path.is_file():result.extend(json.loads(path.read_text())['files'])
    return result


def preserved_path(name,expected=None):
    relative=Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Recorded archive path must be project-relative')
    candidates=[PROJECT_ROOT/relative]
    candidates.extend(PROJECT_ROOT/r['archived_path'] for r in manifests()
                      if r['original_path']==str(relative) or expected is not None and r['sha256']==expected)
    if str(relative).startswith('history/'):
        candidates.append(PROJECT_ROOT/'archive'/str(relative)[len('history/'):])
    if str(relative)=='src/study/cli.py':candidates.append(PROJECT_ROOT/'archive/implementation/cli_before_release.py')
    if str(relative)=='src/study/evaluation.py':candidates.append(PROJECT_ROOT/'archive/implementation/evaluation_before_transfer_artifacts.py')
    for path in dict.fromkeys(candidates):
        if path.is_file() and (expected is None or sha256_file(path)==expected):return path
    raise ValueError('Recorded original bytes unavailable: '+str(relative))
