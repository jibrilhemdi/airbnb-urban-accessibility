"""Active research entry point. Each stage exposes its actual completion status."""
from __future__ import annotations

import argparse
import json

from src.study.specification import load_design


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['status', 'design'])
    args = parser.parse_args(argv)
    design, cities = load_design()
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
