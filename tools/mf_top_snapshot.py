import argparse
import random
import sys
import os
from typing import Any, Dict, List, Optional

import requests

# Ensure parent directory (project root) is on path to import app.py
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import helper functions from app.py
try:
    from app import _mf_parse_series, _mf_metrics, _mf_consistency, _mf_recovery_days
except Exception as e:
    print("ERROR: Unable to import helpers from app.py:", e, file=sys.stderr)
    sys.exit(1)


def _http_get_json(url: str, timeout: int = 20) -> Any:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _weighted_score(pairs: List):
    total_w = 0.0
    total_v = 0.0
    for val, wt, tf in pairs:
        if val is None:
            continue
        v = tf(val) if tf else val
        total_v += v * wt
        total_w += wt
    return (total_v / total_w) if total_w > 0 else None


def score_fund(detail: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    series = _mf_parse_series(detail.get('data', []))
    if len(series) < 60:
        return None
    m = _mf_metrics(series)
    r = m.get('returns', {}) if m else {}
    vol = m.get('volatility_ann')
    mdd = m.get('max_drawdown')
    sharpe = m.get('sharpe')
    cons = _mf_consistency(series)
    rec_days = _mf_recovery_days(series)

    curr = _weighted_score([
        (r.get('1Y'), 0.5, None),
        (r.get('3Y'), 0.2, None),
        (sharpe, 0.3, None),
        (vol, 0.1, lambda x: -x),
        (mdd, 0.1, lambda x: -abs(x)),
    ])
    rec_score = None
    if rec_days is not None:
        rec_score = max(0.0, 1.0 - min(rec_days, 365) / 365.0)
    pred = _weighted_score([
        (r.get('3M'), 0.35, None),
        (r.get('1M'), 0.25, None),
        ((cons or {}).get('positive_month_ratio_1Y'), 0.2, None),
        (vol, 0.1, lambda x: -x),
        (rec_score, 0.1, None),
    ])

    return {
        'metrics': m,
        'scores': {'current': curr, 'predicted': pred},
        'consistency': cons,
        'recovery_days': rec_days,
    }


def main():
    ap = argparse.ArgumentParser(description='Snapshot top mutual funds (current & predicted) using MFAPI')
    ap.add_argument('--limit', type=int, default=10, help='Number of funds to show per list')
    ap.add_argument('--sample', type=int, default=120, help='Number of schemes to scan (random sample)')
    ap.add_argument('--randomize', type=int, default=1, help='Shuffle schemes before sampling (1/0)')
    ap.add_argument('--filter', type=str, default='', help='Substring to filter schemes (name or code)')
    args = ap.parse_args()

    schemes = _http_get_json('https://api.mfapi.in/mf')
    flt = args.filter.lower().strip()
    if flt:
        schemes = [s for s in schemes if flt in (s.get('schemeName') or '').lower() or flt in str(s.get('schemeCode'))]

    if args.randomize:
        random.shuffle(schemes)
    sample = max(10, min(args.sample, len(schemes)))
    pool = schemes[:sample]

    rows = []
    for s in pool:
        code = s.get('schemeCode')
        name = s.get('schemeName')
        try:
            detail = _http_get_json(f'https://api.mfapi.in/mf/{code}', timeout=25)
            scored = score_fund(detail)
            if not scored:
                continue
            returns = (scored['metrics'] or {}).get('returns', {}) if scored.get('metrics') else {}
            rows.append({
                'schemeCode': code,
                'schemeName': name,
                'scores': scored['scores'],
                'returns': returns,
            })
        except Exception:
            continue

    top_curr = sorted(rows, key=lambda x: (x['scores']['current'] or -1e9), reverse=True)[: args.limit]
    top_pred = sorted(rows, key=lambda x: (x['scores']['predicted'] or -1e9), reverse=True)[: args.limit]

    def fmt(row):
        r = row.get('returns', {})
        return f"{row['schemeCode']:>6} | {row['schemeName'][:70]:70} | 1M={r.get('1M')} 3M={r.get('3M')} 1Y={r.get('1Y')} | Curr={row['scores']['current']:.3f} Pred={row['scores']['predicted']:.3f}"

    print('\nTop Current Performers:')
    for i, row in enumerate(top_curr, 1):
        print(f"{i:2}. {fmt(row)}")

    print('\nTop Predicted Performers:')
    for i, row in enumerate(top_pred, 1):
        print(f"{i:2}. {fmt(row)}")


if __name__ == '__main__':
    main()
