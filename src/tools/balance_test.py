import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.data.map_generator import generate, balance_choices, get_default_params
import copy, pprint

def row_avg_score(graph):
    score_map = {'monster':0,'event':1,'shop':1.5,'rest':0.5,'treasure':2.0,'elite':3.0,'boss':5.0,'start':0}
    return [sum([score_map.get(n.get('type'),0) for n in lvl])/len(lvl) for lvl in graph]

if __name__ == '__main__':
    params = get_default_params()
    g = generate(42, params)
    before = row_avg_score(g)
    pprint.pprint({'before_row_avg': before})

    g2 = copy.deepcopy(g)
    balance_choices(g2, params, threshold=1.5)
    after = row_avg_score(g2)
    pprint.pprint({'after_row_avg': after})

    changes = []
    for lidx, (l1, l2) in enumerate(zip(g, g2)):
        for n1 in l1:
            n2 = next((x for x in l2 if x['id'] == n1['id']), None)
            if n2 and n1.get('type') != n2.get('type'):
                changes.append((lidx+1, n1['id'], n1.get('type'), n2.get('type')))

    pprint.pprint({'changes': changes})
    print('\nSample map types (after):')
    for i, lvl in enumerate(g2):
        print(f'Level {i+1}:', [n.get('type') for n in lvl])
