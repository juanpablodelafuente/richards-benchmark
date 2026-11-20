"""Supplementary check cited in the text but absent from the original RUNS list.

Usage: python check_polmann_50s.py --output reproductions/polmann_50s.json
A supplied archive file is never overwritten.
"""
import argparse
import json
from pathlib import Path
import richards_revised as R

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('Output already exists. Choose a new path.')
    r = R.run(R.make_case('polmann'), 'explicit', 50., wall_limit=float('inf'))
    meta = {k: v for k, v in r.items() if k not in ('z', 'psi', 'theta', 'daily_S')}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(meta, indent=2) + '\n', encoding='utf-8')
    print(r['status'], r['reason'])
