"""Explicit V4 command surface; no automatic V3 runner fallback."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.v4.cities import CITIES, VERSION
from src.v4.identity import Paths, Scope
from src.v4.persistence import get_engine, migrate
from src.v4.reporting import report
from src.v4.runtime import preflight, run


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('setup', 'preflight', 'run', 'report'))
    parser.add_argument('--version', required=True, choices=(VERSION,))
    parser.add_argument('--city', required=True, choices=CITIES)
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--offline', action='store_true', help='read-only config checks; database remains unchecked/BLOCKED')
    parser.add_argument('--env', type=Path, default=None, help='V4-prefixed connection settings only (setup/report)')
    args = parser.parse_args(argv)
    engine = None
    try:
        scope = Scope(args.version, args.city, args.snapshot, args.run_id)
        if args.command in {'preflight', 'run'}:
            if args.env is not None:
                raise ValueError('--env supported by setup/report only; preflight/run use .env.v4 or V4_DB_*')
            result = (preflight if args.command == 'preflight' else run)(scope, offline=args.offline)
        else:
            if args.offline:
                raise ValueError('setup/report require a dedicated database')
            engine = get_engine() if args.env is None else get_engine(args.env)
            if args.command == 'setup':
                result = {'status': 'SETUP_COMPLETE', 'applied_migrations': migrate(engine), 'research_executed': False}
            else:
                with engine.connect() as conn:
                    conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                    result = report(conn, Paths(scope))
        print(json.dumps(result, indent=2))
        return 2 if result['status'] == 'BLOCKED' else 0
    except (RuntimeError, ValueError) as error:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error), 'research_executed': False}))
        return 2
    except Exception as error:
        # Do not print SQL parameters, connection strings or private records.
        print(json.dumps({'status': 'BLOCKED', 'reason': type(error).__name__, 'research_executed': False}))
        return 2
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
