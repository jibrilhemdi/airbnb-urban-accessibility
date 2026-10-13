"""Active research entry point. Each stage exposes its actual completion status."""
from __future__ import annotations

import argparse
import json

from src.study.specification import load_design


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
        from src.study.evaluation import run_within_city
        run_within_city(args.city,args.scheme);return 0
    if args.command=='transfer':
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
    print(json.dumps({'design_id': design['design_id'], 'status': 'IMPLEMENTATION_IN_PROGRESS',
                     'operational_counts': {c: cities[c]['operational_count'] for c in cities},
                     'final_samples_frozen': False, 'models_fitted': False,
                     'completed_transfer_directions': 0}, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
