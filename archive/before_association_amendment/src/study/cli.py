"""Active research entry point. Each stage exposes its actual completion status."""
from __future__ import annotations

import argparse
import json

from src.study.specification import load_design
from src.ingestion.common import PROJECT_ROOT


def completion_status(root=PROJECT_ROOT):
    path=root/'docs/analysis/release_audit.json'
    if not path.exists():
        return {'status':'IMPLEMENTATION_IN_PROGRESS','final_samples_frozen':None,'models_fitted':None,
                'completed_transfer_directions':None,'full_rerun_complete':False}
    audit=json.loads(path.read_text())
    return {'status':'COMPLETE' if audit['full_rerun_complete'] else 'PARTIAL_BLOCKED_INFERENCE',
            'final_samples_frozen':audit['primary_prediction_cities_complete']==3,
            'models_fitted':audit['primary_prediction_cities_complete']>0,
            'completed_transfer_directions':6 if audit['six_transfer_directions_complete'] else None,
            'full_rerun_complete':audit['full_rerun_complete'],'blocker':audit.get('blocker'),
            'release_audit':'docs/analysis/release_audit.json'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['status', 'design', 'setup', 'geography-freeze', 'geography-audit','context-freeze','context-audit','accessibility-freeze','sample-freeze','prefit-freeze','within-city','transfer'])
    parser.add_argument('--city',choices=['copenhagen','oslo','stockholm'])
    parser.add_argument('--scheme',action='append')
    args = parser.parse_args(argv)
    design, cities = load_design()
    if args.command=='sample-freeze':
        from src.study.sample_freeze import freeze
        freeze();return 0
    if args.command=='prefit-freeze':
        from src.study.evaluation import freeze_prefit
        freeze_prefit();return 0
    if args.command=='within-city':
        if args.city is None:parser.error('--city is required')
        valid={'neighbourhood','random'}|{f'blocks_{size}m_origin_{origin}' for size in [1000,1500,2000] for origin in ['0_0','0p5_0p5']}
        if args.scheme and any(s not in valid for s in args.scheme):parser.error('Unknown frozen validation scheme')
        label='all' if args.scheme is None else '_'.join(args.scheme)
        if (PROJECT_ROOT/'runs'/args.city/('within_city_'+label+'_selection.json')).exists():
            parser.error('Completed selector exists; audit it or provision explicit new run/output identities')
        from src.study.evaluation import run_within_city
        run_within_city(args.city,args.scheme);return 0
    if args.command=='transfer':
        if (PROJECT_ROOT/'runs/transfer/selection.json').exists():
            parser.error('Completed transfer selector exists; audit it or provision explicit new run/output identities')
        from src.study.evaluation import run_transfer
        run_transfer();return 0
    if args.command=='accessibility-freeze':
        from src.study.workflows import freeze_accessibility
        freeze_accessibility()
        return 0
    if args.command in {'context-freeze','context-audit'}:
        from src.study.workflows import freeze_context,audit_context
        result=freeze_context() if args.command=='context-freeze' else audit_context()
        print(json.dumps({c:{'status':s['status'],'eligible_context_missing_n':s['eligible_context_missing_n'],
                             'density_units':len(s['density_units']),'civic_osm_id':s['civic_anchor']['osm_id']} for c,s in result.items()},indent=2))
        return 2 if any(s['blockers'] for s in result.values()) else 0
    if args.command == 'setup':
        from src.study.store import setup, get_engine
        engine = get_engine()
        try:
            print(json.dumps({'applied':setup(engine)}))
        finally:
            engine.dispose()
        return 0
    if args.command in {'geography-freeze','geography-audit'}:
        from src.study.workflows import freeze_geography, audit_geography
        result = freeze_geography() if args.command == 'geography-freeze' else audit_geography()
        print(json.dumps({c:{'status':v['geography']['status'],'operational_count':v['geography']['operational_count'],
                             'reference':{k:v['reference'][k] for k in ('reference_n','mean_log_price','geometric_mean_price')}}
                          for c,v in result.items()},indent=2,ensure_ascii=False))
        return 2 if any(v['geography']['blockers'] for v in result.values()) else 0
    if args.command == 'design':
        print(json.dumps(design, indent=2, ensure_ascii=False))
        return 0
    status=completion_status(PROJECT_ROOT)
    print(json.dumps({'design_id': design['design_id'], **status,
                     'operational_counts': {c: cities[c]['operational_count'] for c in cities},
                     }, indent=2))
    return 0 if status['full_rerun_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
