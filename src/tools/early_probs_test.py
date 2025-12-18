# -*- coding: utf-8 -*-
from src.data.map_generator import generate, get_default_params
from collections import Counter

def main():
    params = get_default_params()
    cnt = Counter()
    nodes_total = 0
    for s in range(1000):
        g = generate(seed=s, params=params)
        for lvl in range(1,4):
            for n in g[lvl]:
                cnt[n['type']] += 1
                nodes_total += 1
    print('LEVELS=', params['LEVELS'])
    print('rest_rows=', params['rest_rows'])
    print('sampled nodes (levels 1-3)=', nodes_total)
    for t,c in cnt.most_common():
        print(f"{t}: {c} ({c/nodes_total:.2%})")

if __name__ == '__main__':
    main()
