# -*- coding: utf-8 -*-
"""Bulk-test map generation for MAX_PER_ROW enforcement.

Run: python -m src.tools.map_bulk_test
"""
from src.data.map_generator import generate, get_default_params
import statistics


def main():
    params = get_default_params()
    maxp = params['MAX_PER_ROW']
    LEVELS = params['LEVELS']
    bad = []
    max_seen = 0
    examples = []
    for s in range(200):
        g = generate(seed=s, params=params)
        seen = [len(r) for r in g]
        local_max = max(seen)
        if local_max > max_seen:
            max_seen = local_max
        # check any non-start/non-boss row exceeding cap
        for lvl, cnt in enumerate(seen):
            if lvl == 0 or lvl == LEVELS - 1:
                continue
            if cnt > maxp:
                bad.append((s, lvl, cnt))
                break
        if len(examples) < 20 and any(c > maxp for c in seen):
            examples.append((s, seen))
    print('params[MAX_PER_ROW]=', maxp)
    print('samples=', 200)
    print('bad_count=', len(bad))
    print('max_seen_across_samples=', max_seen)
    if examples:
        print('examples (up to 20):')
        for ex in examples[:10]:
            print(' seed=', ex[0], ' row_counts=', ex[1])


if __name__ == '__main__':
    main()
