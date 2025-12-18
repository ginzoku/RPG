# -*- coding: utf-8 -*-
"""
Map generator closely following MAP_LOGIC.md rules.

Produces a list of 15 levels. Each level is a list of node dicts:
  { 'id': int, 'level': int, 'parents': list[int], 'type': str }

This implementation is deterministic in structure (uses randomness for choices)
and ensures a single top-level `generate(seed=None)` function.
"""
import random
from typing import List, Dict


def get_default_params() -> Dict:
    return {
        'LEVELS': 16,
        'MAX_PER_ROW': 5,
        # start row weights for [1,2,3] counts (percent)
        'start_weights': [10, 35, 55],
        # per-node type probabilities (used for lvl >= 5 rows)
        'type_probs': {'monster': 35, 'elite': 10, 'event': 32, 'shop': 8, 'rest': 15},
        # early rows (lvl < 4) allowed distribution
        'early_probs': {'monster': 50, 'event': 42, 'shop': 8},
        # fixed special rows (0-based indices)
        'rest_rows': [5],
        'treasure_rows': [9],
        # placement caps (excluding fixed/guaranteed placements)
        'REST_CAP': 5,
        'ELITE_EXTRA_CAP': 2,
        'SHOP_EXTRA_CAP': 3,
        # branch/boost tuning
        'ENFORCE_MONSTER_THRESHOLD': 3,
        'BRANCH_MONSTER_THRESHOLD': 3,
        'REST_BOOST_MON_RUN': 0.5,
        'REST_BOOST_AFTER_ELITE': 0.15,
        'REST_BOOST_NO_REST_LEVEL': 8,
        'REST_BOOST_NO_REST_AMOUNT': 0.20,
        # penalty/discount multipliers
        'REST_PENALTY_AFTER_TREASURE': 0.5,
        # branching tuning: if a branch hasn't reached this width (excluding rest/treasure rows), boost branching probability
        'BRANCH_WIDTH_TARGET': 4,
        'BRANCH_BOOST_PROB': 0.15,
        # guaranteed counts
        'GUARANTEED_ELITES': 3,
        'GUARANTEED_SHOPS': 3,
        # skip-node probability: mark node as 'empty' but keep it in topology
        'SKIP_NODE_PROB': 0.25,
        # multiplicative factor for skip probability in low region (lvl < first_rest_level)
        'SKIP_LOW_REGION_MULT': 0.6,
        # avoid placing skips immediately after a rest row when possible
        'AVOID_POST_REST': True,
        # minimum required non-empty steps on any start->boss path; if None, defaults to LEVELS-2
        'MIN_REQUIRED_STEPS': None,
    }


def generate(seed: int | None = None, params: Dict | None = None) -> List[List[Dict]]:
    if seed is not None:
        random.seed(seed)

    if params is None:
        params = get_default_params()

    LEVELS = params['LEVELS']
    MAX_PER_ROW = params['MAX_PER_ROW']
    START_WEIGHTS = params['start_weights']
    TYPE_PROBS = params['type_probs']
    EARLY_PROBS = params['early_probs']
    REST_ROWS = params['rest_rows']
    TREASURE_ROWS = params['treasure_rows']
    REST_CAP = params['REST_CAP']
    ELITE_EXTRA_CAP = params['ELITE_EXTRA_CAP']
    SHOP_EXTRA_CAP = params['SHOP_EXTRA_CAP']

    # Ensure the row immediately before the boss is always a rest row
    REST_ROWS = sorted(set(REST_ROWS) | {max(0, LEVELS - 2)})
    PRE_REST_ROWS = [r - 1 for r in REST_ROWS]

    # tuning params
    ENFORCE_MONSTER_THRESHOLD = params.get('ENFORCE_MONSTER_THRESHOLD', 3)
    BRANCH_MONSTER_THRESHOLD = params.get('BRANCH_MONSTER_THRESHOLD', 3)
    REST_BOOST_MON_RUN = params.get('REST_BOOST_MON_RUN', 0.25)
    REST_BOOST_AFTER_ELITE = params.get('REST_BOOST_AFTER_ELITE', 0.15)
    REST_BOOST_NO_REST_LEVEL = params.get('REST_BOOST_NO_REST_LEVEL', 8)
    REST_BOOST_NO_REST_AMOUNT = params.get('REST_BOOST_NO_REST_AMOUNT', 0.20)
    REST_PENALTY_AFTER_TREASURE = params.get('REST_PENALTY_AFTER_TREASURE', 0.5)

    nid = 0
    graph: List[List[Dict]] = []

    # helper to find node by id within current graph
    def find_node_by_id(nid_search: int):
        for lvl_nodes in graph:
            for nd in lvl_nodes:
                if nd['id'] == nid_search:
                    return nd
        return None

    BRANCH_WIDTH_TARGET = params.get('BRANCH_WIDTH_TARGET', 4)
    BRANCH_BOOST_PROB = params.get('BRANCH_BOOST_PROB', 0.15)

    # Start row count based on START_WEIGHTS
    r = random.random() * 100
    if r < START_WEIGHTS[0]:
        start_count = 1
    elif r < START_WEIGHTS[0] + START_WEIGHTS[1]:
        start_count = 2
    else:
        start_count = 3

    # first row
    first = []
    for i in range(start_count):
        first.append({'id': nid, 'level': 0, 'parents': [], 'type': 'start'})
        nid += 1
    graph.append(first)

    # helper: build a mapping of levels to nodes for ancestor computation
    def build_levels_map(g):
        return {i: g[i] for i in range(len(g))}

    def build_ancestors(node, levels_map):
        anc = set()
        stack = list(node.get('parents', []))
        while stack:
            pid = stack.pop()
            if pid in anc:
                continue
            anc.add(pid)
            for lvl_nodes in levels_map.values():
                for n in lvl_nodes:
                    if n['id'] == pid:
                        stack.extend(n.get('parents', []))
                        break
        return anc

    def pairwise_merge_k(nodes_list, k, next_id):
        """Merge up to k non-overlapping adjacent pairs in nodes_list.
        Returns (new_list, new_next_id, merge_map).
        merge_map maps original node ids to the new merged id when merges occur.
        Each merged node will have 'id' set to next_id (incremented) and 'parents' as union.
        Selection prefers pairs with smallest combined parent set size.
        """
        if k <= 0 or len(nodes_list) < 2:
            return nodes_list, next_id, {}
        n = len(nodes_list)
        # build candidate pairs; only allow pairs whose parent-union size <= 2
        pairs = []  # (score, i)
        for i in range(n - 1):
            a = nodes_list[i]
            b = nodes_list[i + 1]
            # skip non-dict placeholders (defensive) and already-merged markers
            if not isinstance(a, dict) or not isinstance(b, dict):
                continue
            if a.get('merged_from') or b.get('merged_from'):
                continue
            parents_a = set(a.get('parents', []))
            parents_b = set(b.get('parents', []))
            union_len = len(parents_a | parents_b)
            # avoid creating merged nodes that would represent >2 original parents
            if union_len > 2:
                continue
            score = union_len
            pairs.append((score, i))
        # sort by score ascending
        pairs.sort(key=lambda x: x[0])
        chosen = set()
        merges = []  # list of (i)
        for score, i in pairs:
            if len(merges) >= k:
                break
            if i in chosen or (i - 1) in chosen or (i + 1) in chosen:
                continue
            merges.append(i)
            chosen.add(i)
        if not merges:
            return nodes_list, next_id, {}
        merges_set = set(merges)
        new_list = []
        i = 0
        merge_map = {}
        while i < n:
            if i in merges_set:
                a = nodes_list[i]
                b = nodes_list[i + 1]
                merged_parents = list(set(a.get('parents', []) + b.get('parents', [])))
                merged = {'id': next_id, 'level': a.get('level', b.get('level')), 'parents': merged_parents, 'merged_from': True}
                # record which original ids were merged into this new id
                try:
                    aid = a['id']
                    bid = b['id']
                    merge_map[aid] = next_id
                    merge_map[bid] = next_id
                except Exception:
                    pass
                next_id += 1
                new_list.append(merged)
                i += 2
            else:
                new_list.append(nodes_list[i])
                i += 1
        return new_list, next_id, merge_map

    # build subsequent levels
    for lvl in range(1, LEVELS):
        prev = graph[lvl - 1]
        prev_count = len(prev)
        row: List[Dict] = []

        # Special rows
        # Behavior for configured rest rows (REST_ROWS):
        #  - If the previous row has 3 or fewer nodes, preserve that count and create one rest node per previous node (one-to-one).
        #  - If the previous row has more than 3 nodes, merge adjacent parents until exactly 3 rest nodes remain.
        if lvl in REST_ROWS:
            if prev_count <= 3:
                for p in prev:
                    row.append({'id': nid, 'level': lvl, 'parents': [p['id']], 'type': 'rest'})
                    nid += 1
                graph.append(row)
                # ensure at least 2 nodes for non-first, non-boss rows
                if lvl != 0 and lvl != LEVELS - 1:
                    while len(graph[-1]) < 2:
                        src_node = graph[-1][0]
                        new_node = {'id': nid, 'level': lvl, 'parents': list(src_node.get('parents', [])), 'type': src_node.get('type', 'monster')}
                        nid += 1
                        graph[-1].append(new_node)

                # helper to count children of a node in the next level
                def child_count_in_next_level(node_id, next_level_nodes):
                    return sum(1 for c in next_level_nodes if node_id in c.get('parents', []))

                # Prevent very long pure-linear runs (no branch/no-merge) of length LINEAR_RUN
                LINEAR_RUN = 3
                for start_lvl in range(1, max(1, LEVELS - LINEAR_RUN - 1)):
                    end_lvl = start_lvl + LINEAR_RUN - 1
                    target_lvl = end_lvl + 1
                    if target_lvl >= LEVELS - 1:
                        continue
                    # skip runs that include fixed rest or treasure rows
                    if any(l in REST_ROWS or l in TREASURE_ROWS for l in range(start_lvl, end_lvl + 1)):
                        continue
                    # check one-to-one for each adjacent pair in the run
                    linear = True
                    for l in range(start_lvl, end_lvl + 1):
                        if l + 1 >= len(graph):
                            linear = False
                            break
                        next_nodes = graph[l + 1]
                        for n in graph[l]:
                            if child_count_in_next_level(n['id'], next_nodes) != 1:
                                linear = False
                                break
                        if not linear:
                            break
                        for c in next_nodes:
                            if len(c.get('parents', [])) != 1:
                                linear = False
                                break
                        if not linear:
                            break
                    if not linear:
                        continue

                    # break linearity: prefer branching (add child) if room, otherwise merge
                    if len(graph[target_lvl]) < MAX_PER_ROW:
                        import random as _rand
                        parent_candidates = [n['id'] for n in graph[end_lvl]]
                        if parent_candidates:
                            pid = _rand.choice(parent_candidates)
                            new_node = {'id': nid, 'level': target_lvl, 'parents': [pid], 'type': 'normal'}
                            nid += 1
                            graph[target_lvl].append(new_node)
                    else:
                        # try a single merge on the target level
                        need = 1
                        new_row, nid, merge_map = pairwise_merge_k(graph[target_lvl], need, nid)
                        graph[target_lvl] = new_row
                        # if merges occurred, update parent refs in the following level
                        if merge_map and target_lvl + 1 < len(graph):
                            next_lvl = graph[target_lvl + 1]
                            for child in next_lvl:
                                new_parents = []
                                for p in child.get('parents', []):
                                    new_parents.append(merge_map.get(p, p))
                                # dedupe while preserving order
                                seen = set()
                                dedup = []
                                for pid in new_parents:
                                    if pid not in seen:
                                        seen.add(pid)
                                        dedup.append(pid)
                                child['parents'] = dedup
                continue
            else:
                # start by making one node per previous parent, then merge down to 3
                temp = []
                for p in prev:
                    temp.append({'id': nid, 'level': lvl, 'parents': [p['id']], 'type': 'rest'})
                    nid += 1
                # merge adjacent until 3 remain using non-overlapping pairwise merges
                need = len(temp) - 3
                if need > 0:
                    temp, nid, _ = pairwise_merge_k(temp, need, nid)
                row = temp
                graph.append(row)
                continue

        if lvl in TREASURE_ROWS:
            # Treasure row: prefer one-to-one mapping from previous nodes when there are <=3 parents.
            # If the previous row has more than 3 nodes, merge adjacent parents until exactly 3 remain,
            # similar to how rest rows are handled.
            if prev_count <= 3:
                for p in prev:
                    row.append({'id': nid, 'level': lvl, 'parents': [p['id']], 'type': 'treasure'})
                    nid += 1
            else:
                # start by making one node per previous parent, then merge down to 3
                temp = []
                for p in prev:
                    temp.append({'id': None, 'parents': [p['id']]})
                need = len(temp) - 3
                if need > 0:
                    temp, nid, _ = pairwise_merge_k(temp, need, nid)
                # finalize rows
                for t in temp:
                    if t.get('id') is None:
                        t['id'] = nid
                        nid += 1
                    new_node = {'id': t['id'], 'level': lvl, 'parents': list(set(t['parents'])), 'type': 'treasure'}
                    if t.get('merged_from'):
                        new_node['merged_from'] = True
                    row.append(new_node)
            graph.append(row)
            # ensure at least 2 nodes for non-first, non-boss rows
            if lvl != 0 and lvl != LEVELS - 1:
                while len(graph[-1]) < 2:
                    src_node = graph[-1][0]
                    new_node = {'id': nid, 'level': lvl, 'parents': list(src_node.get('parents', [])), 'type': src_node.get('type', 'monster')}
                    nid += 1
                    graph[-1].append(new_node)
            continue

        if lvl == LEVELS - 1:
            row.append({'id': nid, 'level': lvl, 'parents': [p['id'] for p in prev], 'type': 'boss'})
            nid += 1
            graph.append(row)
            # ensure at least 2 nodes for non-first, non-boss rows
            if lvl != 0 and lvl != LEVELS - 1:
                while len(graph[-1]) < 2:
                    src_node = graph[-1][0]
                    new_node = {'id': nid, 'level': lvl, 'parents': list(src_node.get('parents', [])), 'type': src_node.get('type', 'monster')}
                    nid += 1
                    graph[-1].append(new_node)
            continue

        # Normal growth: each parent spawns 1-2 children (weighted)
        # (Disallow spawn of 3 children from a single parent.)
        for p in prev:
            # determine if this branch has already reached target width; if not, boost branching
            def branch_reached_width(pid, target):
                cur = find_node_by_id(pid)
                visited = set()
                while cur is not None and cur['id'] not in visited:
                    visited.add(cur['id'])
                    lvl_idx = cur.get('level', None)
                    if lvl_idx is not None and lvl_idx not in REST_ROWS and lvl_idx not in TREASURE_ROWS:
                        if len(graph[lvl_idx]) >= target:
                            return True
                    parents = cur.get('parents', [])
                    if not parents:
                        break
                    cur = find_node_by_id(parents[0])
                return False

            rr = random.random()
            first_cut = 0.6
            if not branch_reached_width(p['id'], BRANCH_WIDTH_TARGET):
                first_cut = max(0.0, 0.6 - BRANCH_BOOST_PROB)
            # choose between 1 or 2 children only
            if rr < first_cut:
                c = 1
            else:
                c = 2
            for _ in range(c):
                row.append({'id': nid, 'level': lvl, 'parents': [p['id']], 'type': 'normal'})
                nid += 1

        # If this row is immediately before a rest-full row,
        # ensure it is merged down to at most 3 nodes so that the rest row receives three inputs.
        if lvl in PRE_REST_ROWS:
            need = len(row) - 3
            if need > 0:
                row, nid, _ = pairwise_merge_k(row, need, nid)

        # deterministic rule: if prev_count == MAX_PER_ROW, force merge to 3 nodes
        if prev_count == MAX_PER_ROW:
            need = len(row) - 3
            if need > 0:
                row, nid, _ = pairwise_merge_k(row, need, nid)

        # probabilistic merges based on prev_count
        merge_chance = 0.0
        if prev_count >= MAX_PER_ROW:
            merge_chance = 0.3
        elif prev_count >= 4:
            merge_chance = 0.3
        elif prev_count >= 3:
            merge_chance = 0.2

        # probabilistic merges: select non-overlapping adjacent pairs in one pass
        if merge_chance > 0 and len(row) > 1:
            # collect candidate indices where merge would be attempted
            candidates = []
            for i in range(len(row) - 1):
                if random.random() < merge_chance:
                    a = row[i]
                    b = row[i + 1]
                    union_len = len(set(a['parents']) | set(b['parents']))
                    # only consider merges that won't create >2 parent unions
                    if union_len > 2:
                        continue
                    score = union_len
                    candidates.append((score, i))
            candidates.sort(key=lambda x: x[0])
            # choose non-overlapping pairs
            chosen = set()
            merges = []
            for score, i in candidates:
                if i in chosen or (i - 1) in chosen or (i + 1) in chosen:
                    continue
                merges.append(i)
                chosen.add(i)
            if merges:
                # perform merges
                merges_set = set(merges)
                new_row = []
                j = 0
                nlen = len(row)
                while j < nlen:
                    if j in merges_set:
                        a = row[j]
                        b = row[j + 1]
                        merged = {'id': nid, 'level': lvl, 'parents': list(set(a['parents'] + b['parents'])), 'type': 'normal', 'merged_from': True}
                        nid += 1
                        new_row.append(merged)
                        j += 2
                    else:
                        new_row.append(row[j])
                        j += 1
                row = new_row

        # clamp to MAX_PER_ROW using non-overlapping pairwise merges
        if len(row) > MAX_PER_ROW:
            need = len(row) - MAX_PER_ROW
            row, nid, _ = pairwise_merge_k(row, need, nid)

        graph.append(row)
        # ensure at least 2 nodes for non-first, non-boss rows
        if lvl != 0 and lvl != LEVELS - 1:
            while len(graph[-1]) < 2:
                src_node = graph[-1][0]
                new_node = {'id': nid, 'level': lvl, 'parents': list(src_node.get('parents', [])), 'type': src_node.get('type', 'monster')}
                nid += 1
                graph[-1].append(new_node)

    # Post-process: prevent crossing connections.
    # For each level, sort the next level's nodes by the leftmost index of their parents
    # so that edges do not cross (i.e., children are ordered by parent position).
    for lvl in range(0, LEVELS - 1):
        # (apply ordering even next to special rows) - sort children by parent positions
        row = graph[lvl]
        next_row = graph[lvl + 1]
        # build parent index map for current row
        idx_map = {n['id']: i for i, n in enumerate(row)}

        # compute representative parent position (barycenter) for each child
        BIG = 1_000_000
        def parent_rep(node):
            ps = node.get('parents', [])
            keys = [idx_map.get(p, BIG) for p in ps]
            if not keys:
                return (BIG, BIG, BIG)
            mn = min(keys)
            mx = max(keys)
            avg = sum(keys) / len(keys)
            return (avg, mn, mx)

        # initial sort by barycenter (avg), then min, then max
        sorted_next = sorted(next_row, key=lambda n: parent_rep(n))

        # local improvement: try adjacent swaps if they reduce crossings between row and next_row
        def count_inversions(order):
            # order: list of child nodes; compute parent_reps in that order and count inversions
            reps = [parent_rep(n)[1] for n in order]  # use min parent index for inversion test
            inv = 0
            for i in range(len(reps)):
                for j in range(i + 1, len(reps)):
                    if reps[i] > reps[j]:
                        inv += 1
            return inv

        improved = True
        # limit iterations to avoid pathological loops
        iter_limit = max(10, len(sorted_next) * 3)
        it = 0
        while improved and it < iter_limit:
            improved = False
            it += 1
            for i in range(len(sorted_next) - 1):
                cur_inv = count_inversions(sorted_next)
                # test swap
                sorted_next[i], sorted_next[i + 1] = sorted_next[i + 1], sorted_next[i]
                new_inv = count_inversions(sorted_next)
                if new_inv < cur_inv:
                    improved = True
                    break
                # revert
                sorted_next[i], sorted_next[i + 1] = sorted_next[i + 1], sorted_next[i]

        # apply ordering
        if sorted_next != next_row:
            graph[lvl + 1] = sorted_next

    # Assign types according to MAP_LOGIC probabilities with constraints.
    # Base probabilities (per-node): monster 30%, elite 15%, event 32%, shop 8%, rest 15%
    levels_map = build_levels_map(graph)

    def can_be_nonconsecutive(node, t):
        # Prevent consecutive elite/rest/shop along a single-parent chain
        parents = node.get('parents', [])
        if not parents:
            return True
        # if any parent is of same type, disallow for elite/rest
        for pid in parents:
            for lvl_nodes in levels_map.values():
                for pn in lvl_nodes:
                    if pn['id'] == pid and pn.get('type') == t:
                        return False
        return True

    # Ensure guaranteed elites and shops later; first mark special fixed rows
    for lvl in range(LEVELS):
        if lvl in REST_ROWS:
            for n in graph[lvl]:
                n['type'] = 'rest'
        elif lvl in TREASURE_ROWS:
            for n in graph[lvl]:
                n['type'] = 'treasure'
        elif lvl == LEVELS - 1:
            for n in graph[lvl]:
                n['type'] = 'boss'

    # ensure first horizontal row (level 0) is all monsters
    for n in graph[0]:
        n['type'] = 'monster'

    # mark remaining nodes probabilistically, respecting basic constraints
    for lvl in range(1, LEVELS - 1):
        for n in graph[lvl]:
            if 'type' in n and n['type'] in ('rest', 'treasure', 'boss', 'monster'):
                continue
            # disallow elite/rest before level 4 (5th row onwards requirement)
            # build allowed types from params
            prev_has_rest = any(x.get('type') == 'rest' for x in graph[lvl - 1]) if lvl - 1 >= 0 else False
            next_has_rest = any(x.get('type') == 'rest' for x in graph[lvl + 1]) if lvl + 1 < LEVELS else False
            block_rest = prev_has_rest or next_has_rest
            if lvl < 4:
                allowed_items = list(EARLY_PROBS.items())
            else:
                allowed_items = list(TYPE_PROBS.items())
            # remove 'rest' option when it would create consecutive rest rows
            if block_rest:
                allowed = [(t, w) for t, w in allowed_items if t != 'rest']
            else:
                allowed = list(allowed_items)

            # sample with weights from allowed, but apply small contextual boosts
            choices = [t for t, w in allowed]
            weights = {t: float(w) for t, w in allowed}

            # helper: get node by id
            def get_node_by_id(nid):
                for lvl_nodes in graph:
                    for nn in lvl_nodes:
                        if nn['id'] == nid:
                            return nn
                return None

            # compute consecutive monsters along a single-parent chain (take max over parents)
            def consecutive_monsters_from_parent(pid):
                length = 0
                cur = get_node_by_id(pid)
                while cur is not None and cur.get('type') == 'monster':
                    length += 1
                    parents = cur.get('parents', [])
                    if not parents:
                        break
                    cur = get_node_by_id(parents[0])
                return length

            # compute consecutive events along a single-parent chain (take max over parents)
            def consecutive_events_from_parent(pid):
                length = 0
                cur = get_node_by_id(pid)
                while cur is not None and cur.get('type') == 'event':
                    length += 1
                    parents = cur.get('parents', [])
                    if not parents:
                        break
                    cur = get_node_by_id(parents[0])
                return length

            # boost rest likelihood if this node follows long monster runs or an elite parent
            if 'rest' in weights:
                # check each parent chain for long monster runs
                max_mon_run = 0
                for pid in n.get('parents', []):
                    run = consecutive_monsters_from_parent(pid)
                    if run > max_mon_run:
                        max_mon_run = run
                rest_boost = 1.0
                if max_mon_run >= BRANCH_MONSTER_THRESHOLD:
                    rest_boost += REST_BOOST_MON_RUN
                # small boost if any immediate parent is elite
                if any(get_node_by_id(pid) is not None and get_node_by_id(pid).get('type') == 'elite' for pid in n.get('parents', [])):
                    rest_boost += REST_BOOST_AFTER_ELITE

                # boost when this branch has never seen a rest and we're at/after configured level
                def branch_has_rest(pid):
                    cur = get_node_by_id(pid)
                    visited = set()
                    while cur is not None and cur['id'] not in visited:
                        visited.add(cur['id'])
                        if cur.get('type') == 'rest':
                            return True
                        parents = cur.get('parents', [])
                        if not parents:
                            break
                        cur = get_node_by_id(parents[0])
                    return False

                any_parent_has_rest = any(branch_has_rest(pid) for pid in n.get('parents', [])) if n.get('parents') else False
                if not any_parent_has_rest and lvl >= REST_BOOST_NO_REST_LEVEL:
                    rest_boost += REST_BOOST_NO_REST_AMOUNT  # small extra boost for long-no-rest branches
                # Do not penalize rest if immediate parent is treasure: apply uniform boost
                weights['rest'] = weights['rest'] * rest_boost

            # enforce non-consecutive rule for elite/rest by disallowing picks that violate it
            # convert weights to lists for sampling
            final_choices = []
            final_weights = []
            for t in choices:
                w = weights.get(t, 0.0)
                if w <= 0:
                    continue
                if t in ('elite', 'rest', 'shop') and not can_be_nonconsecutive(n, t):
                    # demote to zero weight if it would violate non-consecutive rule
                    continue
                # prevent creating a 4th consecutive 'event' along a single-parent chain
                if t == 'event':
                    max_event_run = 0
                    for pid in n.get('parents', []):
                        run = consecutive_events_from_parent(pid)
                        if run > max_event_run:
                            max_event_run = run
                    # if upstream run is already 3 or more, disallow another event (limit to 3)
                    if max_event_run >= 3:
                        continue
                final_choices.append(t)
                final_weights.append(w)

            # fallback: if no valid choices remain, default to monster
            if not final_choices:
                n['type'] = 'monster'
            else:
                pick = random.choices(final_choices, weights=final_weights, k=1)[0]
                n['type'] = pick

    # Guarantee at least 3 elites and 3 shops, placed after level 4, not on rest/treasure/boss/start
    def pick_guaranteed(kind, count):
        candidates = []
        for lvl in range(4, LEVELS - 1):
            for n in graph[lvl]:
                if n.get('type') in ('rest', 'treasure', 'boss', 'start'):
                    continue
                candidates.append(n)
        random.shuffle(candidates)
        placed = []
        # helper: build quick id->node map for child checks
        id_to_node_local = {n['id']: n for lvl_nodes in graph for n in lvl_nodes}
        for c in candidates:
            if len(placed) >= count:
                break
            # avoid same branch: simple check by ancestors intersection with already placed
            anc_c = build_ancestors(c, levels_map)
            conflict = False
            for p in placed:
                if c['level'] == p['level']:
                    conflict = True
                    break
                if anc_c & build_ancestors(p, levels_map):
                    conflict = True
                    break
            if conflict:
                continue
            # avoid creating consecutive same-type placements (e.g., shop after shop)
            # check immediate parents
            if not can_be_nonconsecutive(c, kind):
                continue
            # check immediate children to avoid creating parent->child same-type
            child_conflict = False
            for lvl_nodes in graph:
                for nn in lvl_nodes:
                    if c['id'] in nn.get('parents', []):
                        if nn.get('type') == kind:
                            child_conflict = True
                            break
                if child_conflict:
                    break
            if child_conflict:
                continue
            c['type'] = kind
            placed.append(c)
        return placed

    elites = pick_guaranteed('elite', 3)
    shops = pick_guaranteed('shop', 3)

    # Enforce placement caps (excluding fixed/guranteed placements):
    # - rest: max 5 outside fixed rest rows (levels 5 and 13)
    # - elite: max 5 additional elites besides the 3 guaranteed
    # - shop: max 3 additional shops besides the 3 guaranteed
    REST_CAP = 5
    ELITE_EXTRA_CAP = 5
    SHOP_EXTRA_CAP = 3

    # rest candidates (exclude fixed rest rows)
    rest_fixed_set = set(REST_ROWS)
    rest_candidates = [n for lvl_idx, lvl_nodes in enumerate(graph) if lvl_idx not in rest_fixed_set for n in lvl_nodes if n.get('type') == 'rest']
    if len(rest_candidates) > REST_CAP:
        keep = set(n['id'] for n in random.sample(rest_candidates, REST_CAP))
        for n in rest_candidates:
            if n['id'] not in keep:
                n['type'] = 'monster'

    # elites: preserve the guaranteed ones created by pick_guaranteed
    elite_fixed_ids = set(n['id'] for n in elites)
    extra_elites = [n for lvl_nodes in graph for n in lvl_nodes if n.get('type') == 'elite' and n['id'] not in elite_fixed_ids]
    if len(extra_elites) > ELITE_EXTRA_CAP:
        keep = set(n['id'] for n in random.sample(extra_elites, ELITE_EXTRA_CAP))
        for n in extra_elites:
            if n['id'] not in keep:
                n['type'] = 'monster'

    # shops: preserve the guaranteed ones created by pick_guaranteed
    shop_fixed_ids = set(n['id'] for n in shops)
    extra_shops = [n for lvl_nodes in graph for n in lvl_nodes if n.get('type') == 'shop' and n['id'] not in shop_fixed_ids]
    if len(extra_shops) > SHOP_EXTRA_CAP:
        keep = set(n['id'] for n in random.sample(extra_shops, SHOP_EXTRA_CAP))
        for n in extra_shops:
            if n['id'] not in keep:
                n['type'] = 'monster'

    # Ensure branches that haven't seen a monster/elite for a while
    # get at least one monster in that segment. This walks all paths
    # from start nodes and inserts a monster if the gap >= threshold.
    def enforce_monster_on_sparse_branches(graph, threshold=3):
        id_to_node = {n['id']: n for lvl in graph for n in lvl}
        children = {nid: [] for nid in id_to_node}
        for lvl_nodes in graph:
            for n in lvl_nodes:
                for p in n.get('parents', []):
                    if p in children:
                        children[p].append(n['id'])

        locked = set(['rest', 'treasure', 'boss', 'start'])

        # DFS with path tracking
        def dfs(node_id, path_ids):
            path_ids.append(node_id)
            # find last monster/elite index in path
            last_idx = -1
            for i, pid in enumerate(path_ids):
                t = id_to_node[pid].get('type')
                if t in ('monster', 'elite'):
                    last_idx = i
            gap = len(path_ids) - 1 - last_idx
            if gap >= threshold:
                # choose the first node after last monster/elite to convert
                target_idx = last_idx + 1
                if 0 <= target_idx < len(path_ids):
                    target_node = id_to_node[path_ids[target_idx]]
                    # Do not enforce monsters on early rows (levels 0-3)
                    if target_node.get('type') not in locked and target_node.get('level', 0) >= 4:
                        target_node['type'] = 'monster'
                        # after insertion, reset last_idx to target_idx
                        last_idx = target_idx
            # traverse children
            for cid in children.get(node_id, []):
                # avoid cycles by checking presence in current path
                if cid in path_ids:
                    continue
                dfs(cid, path_ids)
            path_ids.pop()

        # start DFS from all start nodes
        for start_node in graph[0]:
            dfs(start_node['id'], [])

    enforce_monster_on_sparse_branches(graph, threshold=ENFORCE_MONSTER_THRESHOLD)

    # Safety final clamp: ensure no row exceeds MAX_PER_ROW by pairwise merging as needed.
    # This is a protective post-process in case earlier steps expanded rows beyond the cap.
    # Use an iterative approach with a forced-merge fallback to guarantee progress
    # and avoid potential infinite loops when pairwise_merge_k cannot find valid pairs.
    max_per = params.get('MAX_PER_ROW', MAX_PER_ROW)
    for lvl_idx, lvl_nodes in enumerate(graph):
        # skip start and boss rows
        if lvl_idx == 0 or lvl_idx == LEVELS - 1:
            continue
        # if already within cap, continue
        if len(lvl_nodes) <= max_per:
            continue
        # iterative reduction with a safety cap on iterations
        iter_limit = max(10, len(lvl_nodes) * 2)
        it = 0
        while len(lvl_nodes) > max_per and it < iter_limit:
            need = len(lvl_nodes) - max_per
            new_nodes, new_nid, merge_map = pairwise_merge_k(lvl_nodes, need, nid)
            # if pairwise succeeded in reducing length, accept result
            if len(new_nodes) < len(lvl_nodes):
                # update child parent refs for this level if needed
                if merge_map and lvl_idx + 1 < len(graph):
                    for child in graph[lvl_idx + 1]:
                        new_parents = [merge_map.get(p, p) for p in child.get('parents', [])]
                        seen = set()
                        dedup = []
                        for pid in new_parents:
                            if pid not in seen:
                                seen.add(pid)
                                dedup.append(pid)
                        child['parents'] = dedup
                lvl_nodes = new_nodes
                nid = new_nid
            else:
                # fallback: perform a single forced merge of the first adjacent pair
                if len(lvl_nodes) >= 2:
                    a = lvl_nodes[0]
                    b = lvl_nodes[1]
                    merged_parents = list(set(a.get('parents', []) + b.get('parents', [])))
                    merged = {'id': nid, 'level': a.get('level', b.get('level')), 'parents': merged_parents, 'merged_from': True}
                    nid += 1
                    lvl_nodes = [merged] + lvl_nodes[2:]
                else:
                    break
            it += 1
        # final safety: if still oversized, truncate by merging tail into previous nodes until within cap
        while len(lvl_nodes) > max_per and len(lvl_nodes) >= 2:
            # merge the last two elements
            a = lvl_nodes[-2]
            b = lvl_nodes[-1]
            merged_parents = list(set(a.get('parents', []) + b.get('parents', [])))
            merged = {'id': nid, 'level': a.get('level', b.get('level')), 'parents': merged_parents, 'merged_from': True}
            nid += 1
            lvl_nodes = lvl_nodes[:-2] + [merged]
        graph[lvl_idx] = lvl_nodes

    # Optional skip-node rule: mark nodes as 'empty' (skip) but keep them in the graph topology.
    # - Skip doesn't apply to fixed treasure/rest/start/boss nodes
    # - Ensure at least params['LEVELS'] - 2 non-empty nodes on any start->boss path
    SKIP_PROB = params.get('SKIP_NODE_PROB', 0.06)
    # optional: reduce skip probability in low region (fraction)
    SKIP_LOW_REGION_MULT = params.get('SKIP_LOW_REGION_MULT', 0.5)
    # do not allow skips on nodes that are immediate children of a rest node
    AVOID_POST_REST = params.get('AVOID_POST_REST', True)
    min_required = params.get('MIN_REQUIRED_STEPS', None)
    if min_required is None:
        # use LEVELS-3 as requested
        min_required = max(0, params.get('LEVELS', LEVELS) - 3)

    skipped_nodes = []
    # determine first rest level (if any)
    first_rest_level = min(REST_ROWS) if REST_ROWS else LEVELS
    # build id->node map for ancestor checks
    id_to_node_pre = {n['id']: n for lvl in graph for n in lvl}
    # build children map for skip-time descendant checks
    id_to_node_pre = {n['id']: n for lvl in graph for n in lvl}
    children_pre = {nid: [] for nid in id_to_node_pre}
    for lvl_nodes in graph:
        for n in lvl_nodes:
            for p in n.get('parents', []):
                if p in children_pre:
                    children_pre[p].append(n['id'])

    def has_descendant_rest(nid):
        # DFS/BFS to find any descendant of nid that is a rest
        stack = list(children_pre.get(nid, []))
        seen = set()
        while stack:
            cid = stack.pop()
            if cid in seen:
                continue
            seen.add(cid)
            cn = id_to_node_pre.get(cid)
            if cn is not None and cn.get('type') == 'rest':
                return True
            # push children
            for cc in children_pre.get(cid, []):
                if cc not in seen:
                    stack.append(cc)
        return False

    # track occupied column indices (to avoid stacking skips vertically)
    # we'll treat column index as the node's index within its level list
    for_lvl_len = [len(graph[l]) for l in range(len(graph))]
    def is_col_occupied(level_idx, col_idx):
        for li, lvl_nodes in enumerate(graph):
            if li == level_idx:
                continue
            if col_idx < len(lvl_nodes):
                if lvl_nodes[col_idx].get('type') == 'empty':
                    return True
        return False

    for lvl in range(1, LEVELS - 1):
        for col_idx, node in list(enumerate(graph[lvl])):
            if node.get('type') in ('start', 'boss', 'rest', 'treasure', 'empty'):
                continue
            parents = node.get('parents', [])
            # For nodes before the first rest row, allow at most one skip per branch:
            # if any ancestor (not just immediate parent) in the same branch is already 'empty', disallow skipping.
            parent_empty = False
            if node.get('level', 0) < first_rest_level:
                anc_ids = build_ancestors(node, levels_map)
                for aid in anc_ids:
                    an = id_to_node_pre.get(aid)
                    if an is not None and an.get('type') == 'empty':
                        parent_empty = True
                        break
            else:
                # preserve previous behavior for deeper rows: check only immediate parents
                for pid in parents:
                    pnode = id_to_node_pre.get(pid)
                    if pnode is not None and pnode.get('type') == 'empty':
                        parent_empty = True
                        break
            if parent_empty:
                continue
            # avoid creating pattern: rest -> (this node empty) -> rest
            # if any ancestor is rest AND any descendant is rest, disallow skipping
            ancestor_has_rest = False
            anc_ids = build_ancestors(node, levels_map)
            for aid in anc_ids:
                an = id_to_node_pre.get(aid)
                if an is not None and an.get('type') == 'rest':
                    ancestor_has_rest = True
                    break
            if ancestor_has_rest and has_descendant_rest(node['id']):
                continue
            # compute effective skip probability with level-based multiplier
            eff_prob = SKIP_PROB
            if node.get('level', 0) < first_rest_level:
                eff_prob = SKIP_PROB * SKIP_LOW_REGION_MULT
            # avoid placing if same column already has an empty elsewhere
            if is_col_occupied(lvl, col_idx):
                eff_prob = 0.0
            # avoid immediate post-rest skips if configured
            if AVOID_POST_REST:
                is_post_rest = False
                for pid in parents:
                    pp = id_to_node_pre.get(pid)
                    if pp is not None and pp.get('type') == 'rest':
                        is_post_rest = True
                        break
                if is_post_rest:
                    eff_prob = 0.0

            if random.random() < eff_prob:
                node['_orig_type'] = node.get('type')
                node['type'] = 'empty'
                skipped_nodes.append({'id': node['id'], 'orig_type': node['_orig_type']})

    # If any skips happened, ensure minimal non-empty nodes along any start->boss path
    if skipped_nodes:
        id_to_node = {n['id']: n for lvl in graph for n in lvl}
        children = {nid: [] for nid in id_to_node}
        for lvl_nodes in graph:
            for n in lvl_nodes:
                for p in n.get('parents', []):
                    if p in children:
                        children[p].append(n['id'])

        import heapq

        def min_nonempty_cost(start_id, target_ids):
            pq = [(0, start_id)]
            best = {start_id: 0}
            while pq:
                cost, nid = heapq.heappop(pq)
                if nid in target_ids:
                    return cost
                if cost != best.get(nid, 1e9):
                    continue
                for c in children.get(nid, []):
                    node_c = id_to_node.get(c)
                    if node_c is None:
                        continue
                    add = 0 if node_c.get('type') == 'empty' else 1
                    newc = cost + add
                    if newc < best.get(c, 1e9):
                        best[c] = newc
                        heapq.heappush(pq, (newc, c))
            return None

        start_ids = [n['id'] for n in graph[0]]
        boss_ids = [n['id'] for lvl in graph for n in lvl if n.get('type') == 'boss']

        def compute_min_cost():
            min_cost = None
            for s in start_ids:
                c = min_nonempty_cost(s, set(boss_ids))
                if c is None:
                    continue
                if min_cost is None or c < min_cost:
                    min_cost = c
            return 0 if min_cost is None else min_cost

        cur_cost = compute_min_cost()
        idx = len(skipped_nodes) - 1
        while cur_cost < min_required and idx >= 0:
            rec = skipped_nodes[idx]
            nid = rec['id']
            node = id_to_node.get(nid)
            if node is None or node.get('type') != 'empty':
                idx -= 1
                continue
            # restore node
            node['type'] = node.get('_orig_type', rec.get('orig_type', 'monster'))
            if '_orig_type' in node:
                del node['_orig_type']
            cur_cost = compute_min_cost()
            idx -= 1

        # Ensure at least 2 skips remain in the final graph (best-effort without violating min_required)
        # Count current empties in low/high regions
        current_skips = sum(1 for lvl in graph for n in lvl if n.get('type') == 'empty')
        low_skips = sum(1 for lvl_idx, lvl in enumerate(graph) for n in lvl if n.get('type') == 'empty' and lvl_idx < first_rest_level)
        high_skips = sum(1 for lvl_idx, lvl in enumerate(graph) for n in lvl if n.get('type') == 'empty' and lvl_idx >= first_rest_level)
        # Ensure at least one empty in low and one in high (best-effort without violating min_required)
        # We'll attempt to add missing empties per-region.
        need_low = 1 if low_skips < 1 else 0
        need_high = 1 if high_skips < 1 else 0
        if need_low or need_high:
            # candidates: nodes that are not special/locked and currently non-empty
            candidates_low = []
            candidates_high = []
            for lvl_idx in range(1, LEVELS - 1):
                for n in graph[lvl_idx]:
                    if n.get('type') in ('start', 'boss', 'rest', 'treasure', 'empty'):
                        continue
                    if 'locked_ids' in locals() and n['id'] in locked_ids:
                        continue
                    # avoid creating consecutive skips: skip if any parent is empty
                    parent_empty = False
                    for pid in n.get('parents', []):
                        pn = None
                        for lvl_nodes in graph:
                            for nn in lvl_nodes:
                                if nn['id'] == pid:
                                    pn = nn
                                    break
                            if pn is not None:
                                break
                        if pn is not None and pn.get('type') == 'empty':
                            parent_empty = True
                            break
                    if parent_empty:
                        continue
                    # split into low/high relative to first_rest_level
                    # avoid immediate children of rest rows when forming candidates
                    is_post_rest = False
                    for pid in n.get('parents', []):
                        pn = id_to_node_pre.get(pid)
                        if pn is not None and pn.get('type') == 'rest':
                            is_post_rest = True
                            break
                    if lvl_idx < first_rest_level:
                        candidates_low.append(n)
                    else:
                        if not is_post_rest:
                            candidates_high.append(n)
                        else:
                            # push post-rest nodes to a separate bucket as lowest priority
                            # they'll be considered only if forced later
                            pass

            random.shuffle(candidates_low)
            random.shuffle(candidates_high)

            def try_place_one(lst, force=False):
                nonlocal current_skips
                best_candidate = None
                best_cost = -1
                for cand in lst:
                    orig = cand.get('type')
                    cand['type'] = 'empty'
                    new_cost = compute_min_cost()
                    if new_cost >= min_required:
                        current_skips += 1
                        return True
                    # collect best (least harmful) candidate when forcing
                    if force:
                        if new_cost > best_cost:
                            best_cost = new_cost
                            best_candidate = cand
                    # revert temporary change
                    cand['type'] = orig
                if force and best_candidate is not None:
                    # place the best candidate even if it violates min_required
                    best_candidate['_orig_type'] = best_candidate.get('_orig_type', best_candidate.get('type'))
                    best_candidate['type'] = 'empty'
                    current_skips += 1
                    return True
                return False

            # place low if needed
            if need_low:
                placed = try_place_one(candidates_low, force=False)
                if not placed:
                    # try forced placement
                    placed = try_place_one(candidates_low, force=True)
                if placed:
                    need_low = 0
            # place high if needed: distribute across levels to avoid clustering near a single level
            if need_high:
                # group candidates by level
                lvl_buckets = {}
                for c in candidates_high:
                    lvl_buckets.setdefault(c.get('level', 0), []).append(c)
                levels_sorted = sorted(lvl_buckets.keys())
                placed = 0
                # round-robin across levels to spread empties
                idx = 0
                while placed < need_high and levels_sorted:
                    lvl_key = levels_sorted[idx % len(levels_sorted)]
                    bucket = lvl_buckets.get(lvl_key, [])
                    if bucket:
                        cand = bucket.pop(random.randrange(len(bucket)))
                        # try placing without forcing first
                        orig = cand.get('type')
                        cand['type'] = 'empty'
                        new_cost = compute_min_cost()
                        if new_cost >= min_required:
                            placed += 1
                        else:
                            # revert and try forced placement in later pass
                            cand['type'] = orig
                    # remove empty buckets
                    if not bucket:
                        levels_sorted = [l for l in levels_sorted if lvl_buckets.get(l)]
                    idx += 1
                # if still short, try force-placing across levels (avoiding immediate post-rest where possible)
                if placed < need_high:
                    for lvl_key in sorted(lvl_buckets.keys()):
                        for cands in [lvl_buckets.get(lvl_key, [])]:
                            while cands and placed < need_high:
                                cand = cands.pop()
                                cand['_orig_type'] = cand.get('type')
                                cand['type'] = 'empty'
                                placed += 1
                            if placed >= need_high:
                                break
                        if placed >= need_high:
                            break
            # if still missing a high skip, try moving an existing low skip to high (restore low, then place high)
            if need_high:
                low_empties = [n for lvl_idx, lvl in enumerate(graph) for n in lvl if n.get('type') == 'empty' and lvl_idx < first_rest_level]
                moved = False
                for low_node in low_empties:
                    # attempt to restore low node
                    orig = low_node.pop('_orig_type', low_node.get('type', 'monster'))
                    low_node['type'] = orig
                    new_cost = compute_min_cost()
                    if new_cost < min_required:
                        # revert
                        low_node['type'] = 'empty'
                        low_node['_orig_type'] = orig
                        continue
                    # now try to place in high
                    if try_place_one(candidates_high, force=False) or try_place_one(candidates_high, force=True):
                        moved = True
                        need_high = 0
                        break
                    # revert if placement failed
                    low_node['type'] = 'empty'
                    low_node['_orig_type'] = orig
                # end moving loop
            # fallback: if after attempts we still have fewer than 2 skips, fill from any candidates until 2
            current_skips = sum(1 for lvl in graph for n in lvl if n.get('type') == 'empty')
            if current_skips < 2:
                combined = candidates_low + candidates_high
                for cand in combined:
                    if current_skips >= 2:
                        break
                    orig = cand.get('type')
                    cand['type'] = 'empty'
                    new_cost = compute_min_cost()
                    if new_cost < min_required:
                        cand['type'] = orig
                        continue
                    current_skips += 1

            # New policy: do NOT force any skips in low layers.
            # Instead, ensure two skips exist in the high region (lvl >= first_rest_level).
            high_skips = [(lvl_idx, n) for lvl_idx, lvl in enumerate(graph) for n in lvl if n.get('type') == 'empty' and lvl_idx >= first_rest_level]
            need = max(0, 2 - len(high_skips))
            if need > 0:
                placed = 0
                for lvl_idx in range(max(1, first_rest_level), LEVELS - 1):
                    for n in graph[lvl_idx]:
                        if n.get('type') in ('start', 'boss', 'rest', 'treasure', 'empty'):
                            continue
                        n['_orig_type'] = n.get('type')
                        n['type'] = 'empty'
                        placed += 1
                        if placed >= need:
                            break
                    if placed >= need:
                        break
                # final fallback: if still not enough, convert any remaining non-special nodes in high region
                if placed < need:
                    for lvl_idx in range(max(1, first_rest_level), LEVELS - 1):
                        for n in graph[lvl_idx]:
                            if n.get('type') in ('start', 'boss', 'rest', 'treasure', 'empty'):
                                continue
                            if n.get('type') != 'empty':
                                n['_orig_type'] = n.get('type')
                                n['type'] = 'empty'
                                placed += 1
                                if placed >= need:
                                    break
                        if placed >= need:
                            break

        # Post-skip cleanup: prevent pattern rest -> empty -> rest by restoring the middle node
        # Build id->node and children maps for checks
        id_to_node_cleanup = {n['id']: n for lvl in graph for n in lvl}
        children_cleanup = {nid: [] for nid in id_to_node_cleanup}
        for lvl_nodes in graph:
            for n in lvl_nodes:
                for p in n.get('parents', []):
                    if p in children_cleanup:
                        children_cleanup[p].append(n['id'])

        def has_descendant_rest_cleanup(nid):
            stack = list(children_cleanup.get(nid, []))
            seen = set()
            while stack:
                cid = stack.pop()
                if cid in seen:
                    continue
                seen.add(cid)
                cn = id_to_node_cleanup.get(cid)
                if cn is not None and cn.get('type') == 'rest':
                    return True
                stack.extend(children_cleanup.get(cid, []))
            return False

        def ancestors_cleanup(node):
            anc = set()
            stack = list(node.get('parents', []))
            while stack:
                pid = stack.pop()
                if pid in anc:
                    continue
                anc.add(pid)
                p = id_to_node_cleanup.get(pid)
                if p:
                    stack.extend(p.get('parents', []))
            return anc

        # restore empty nodes that connect two rest nodes along any branch
        for lvl in range(1, LEVELS - 1):
            for node in graph[lvl]:
                if node.get('type') != 'empty':
                    continue
                anc_ids = ancestors_cleanup(node)
                if any(id_to_node_cleanup.get(a, {}).get('type') == 'rest' for a in anc_ids) and has_descendant_rest_cleanup(node['id']):
                    # restore original type if known, else monster
                    node['type'] = node.pop('_orig_type', 'monster')
                    # also remove from skipped_nodes list if present
                    # (not critical but keeps skipped_nodes consistent)
                    for srec in list(skipped_nodes):
                        if srec.get('id') == node['id']:
                            skipped_nodes.remove(srec)

    # Final pass: convert any remaining unknowns to monster
    # Ensure forced high-region empties even if no probabilistic skips occurred
    first_rest = first_rest_level
    high_empties = [(lvl_idx, n) for lvl_idx, lvl in enumerate(graph) for n in lvl if n.get('type') == 'empty' and lvl_idx >= first_rest]
    if len(high_empties) < 2:
        need = 2 - len(high_empties)
        placed = 0
        for lvl_idx in range(max(1, first_rest), LEVELS - 1):
            for n in graph[lvl_idx]:
                if n.get('type') in ('start', 'boss', 'rest', 'treasure', 'empty'):
                    continue
                # avoid immediate children of rest rows when possible
                is_post_rest = False
                for pid in n.get('parents', []):
                    pn = None
                    for row in graph:
                        for pnn in row:
                            if pnn['id'] == pid and pnn.get('type') == 'rest':
                                is_post_rest = True
                                break
                        if is_post_rest:
                            break
                    if is_post_rest:
                        break
                if is_post_rest:
                    continue
                n['_orig_type'] = n.get('type')
                n['type'] = 'empty'
                placed += 1
                if placed >= need:
                    break
            if placed >= need:
                break
        # final fallback across whole graph
        if placed < need:
            for lvl_idx in range(1, LEVELS - 1):
                for n in graph[lvl_idx]:
                    if n.get('type') in ('start', 'boss', 'rest', 'treasure', 'empty'):
                        continue
                    # as a last resort allow post-rest nodes, but prefer others
                    if any((lambda pid: any(pn.get('id') == pid and pn.get('type') == 'rest' for row in graph for pn in row))(pid) for pid in n.get('parents', [])):
                        continue
                    n['_orig_type'] = n.get('type')
                    n['type'] = 'empty'
                    placed += 1
                    if placed >= need:
                        break
                if placed >= need:
                    break
            # if still not enough, reluctantly place on any remaining nodes (including post-rest)
            if placed < need:
                for lvl_idx in range(1, LEVELS - 1):
                    for n in graph[lvl_idx]:
                        if n.get('type') in ('start', 'boss', 'rest', 'treasure', 'empty'):
                            continue
                        n['_orig_type'] = n.get('type')
                        n['type'] = 'empty'
                        placed += 1
                        if placed >= need:
                            break
                    if placed >= need:
                        break

    for lvl in range(1, LEVELS - 1):
        for n in graph[lvl]:
            if 'type' not in n or n['type'] is None:
                n['type'] = 'monster'

    # Post-process: enforce maximum consecutive 'event' nodes along any start->boss path
    def enforce_max_consecutive_events(graph, cap=3):
        id_to_node = {n['id']: n for lvl in graph for n in lvl}
        children = {nid: [] for nid in id_to_node}
        for lvl_nodes in graph:
            for n in lvl_nodes:
                for p in n.get('parents', []):
                    if p in children:
                        children[p].append(n['id'])

        changed = True
        while changed:
            changed = False

            def dfs(nid, cur_run, visited):
                nonlocal changed
                if nid in visited:
                    return
                visited.add(nid)
                node = id_to_node.get(nid)
                if node is None:
                    visited.remove(nid)
                    return
                if node.get('type') == 'event':
                    cur_run += 1
                else:
                    cur_run = 0
                if cur_run > cap:
                    # convert this node to monster if allowed
                    if node.get('type') not in ('start', 'boss', 'rest', 'treasure'):
                        node['type'] = 'monster'
                        changed = True
                        visited.remove(nid)
                        return
                if node.get('type') == 'boss':
                    visited.remove(nid)
                    return
                for c in children.get(nid, []):
                    dfs(c, cur_run, visited)
                visited.remove(nid)

            for s in graph[0]:
                dfs(s['id'], 0, set())

            if changed:
                # rebuild maps to reflect modifications
                id_to_node = {n['id']: n for lvl in graph for n in lvl}
                children = {nid: [] for nid in id_to_node}
                for lvl_nodes in graph:
                    for n in lvl_nodes:
                        for p in n.get('parents', []):
                            if p in children:
                                children[p].append(n['id'])

    enforce_max_consecutive_events(graph, cap=3)

    # final validation and fixes to avoid disconnected/isolated nodes
    validate_and_fix_graph(graph)

    return graph


def minimize_crossings(graph: List[List[Dict]], passes: int = 6):
    """Iterative barycenter/median ordering (top-down and bottom-up) to reduce crossings.
    This reorders nodes in-place in `graph`.
    """
    if not graph:
        return graph
    L = len(graph)
    BIG = 1_000_000

    def barycenter_for_children(row, next_row):
        idx = {n['id']: i for i, n in enumerate(row)}
        def key(n):
            parents = n.get('parents', [])
            vals = [idx.get(p, BIG) for p in parents]
            if not vals:
                return (BIG, BIG)
            return (sum(vals) / len(vals), min(vals))
        next_row.sort(key=key)

    def barycenter_for_parents(row, next_row):
        child_idx = {n['id']: i for i, n in enumerate(next_row)}
        def key(n):
            refs = []
            for i, cn in enumerate(next_row):
                if n['id'] in cn.get('parents', []):
                    refs.append(i)
            if not refs:
                return (BIG, BIG)
            refs.sort()
            mid = refs[len(refs) // 2]
            return (mid, min(refs))
        row.sort(key=key)

    for _ in range(passes):
        # top-down pass
        for lvl in range(0, L - 1):
            barycenter_for_children(graph[lvl], graph[lvl + 1])
        # bottom-up pass
        for lvl in range(L - 1, 0, -1):
            barycenter_for_parents(graph[lvl - 1], graph[lvl])
    return graph


def remove_vertical_empty_stacks(graph: List[List[Dict]], max_iters: int = 100):
    """Attempt to avoid multiple 'empty' nodes aligned in the same column index by local swaps.
    This reorders nodes within levels (display order) to break vertical stacks where possible.
    """
    if not graph:
        return graph
    it = 0
    while it < max_iters:
        it += 1
        # build column map: col_idx -> list of (lvl_idx)
        col_map = {}
        changed = False
        for lvl_idx, lvl in enumerate(graph):
            for col_idx, n in enumerate(lvl):
                if n.get('type') == 'empty':
                    col_map.setdefault(col_idx, []).append(lvl_idx)
        # find any column with >1 empties
        conflict_cols = [c for c, lvls in col_map.items() if len(lvls) > 1]
        if not conflict_cols:
            break
        for c in conflict_cols:
            lvls = col_map[c]
            # resolve conflicts by swapping node within its level with neighbor where possible
            for lvl_idx in lvls[1:]:
                lvl = graph[lvl_idx]
                col_idx = c
                swapped = False
                # prefer swapping toward center (try left then right)
                for ni in (col_idx - 1, col_idx + 1):
                    if 0 <= ni < len(lvl):
                        lvl[col_idx], lvl[ni] = lvl[ni], lvl[col_idx]
                        changed = True
                        swapped = True
                        break
                if not swapped:
                    continue
        if not changed:
            break
    return graph


def ensure_parents_have_children(graph: List[List[Dict]]):
    """Ensure every parent node (except in the boss level) has at least one child.
    If a parent has no children in the next level, try to attach it to an existing child
    (prefer child with few parents), otherwise create a new child node in the next level.
    """
    if not graph:
        return graph
    L = len(graph)
    nid_max = max(n['id'] for lvl in graph for n in lvl) + 1
    for lvl in range(0, L - 1):
        next_row = graph[lvl + 1]
        for p in list(graph[lvl]):
            children = [n for n in next_row if p['id'] in n.get('parents', [])]
            if children:
                continue
            # find candidate child to adopt this parent
            best = None
            best_score = 999
            for idx, c in enumerate(next_row):
                par_count = len(c.get('parents', []))
                # prefer child with <2 parents
                score = par_count
                if par_count < 2 and score < best_score:
                    best = c
                    best_score = score
            if best is not None:
                # attach parent id to this child
                best['parents'] = list(dict.fromkeys(best.get('parents', []) + [p['id']]))
            else:
                # create new child node anchored to this parent
                new_node = {'id': nid_max, 'level': lvl + 1, 'parents': [p['id']], 'type': 'monster'}
                nid_max += 1
                # insert near middle of next_row
                insert_at = max(0, len(next_row) // 2)
                next_row.insert(insert_at, new_node)
    return graph


def validate_and_fix_graph(graph: List[List[Dict]]):
    """Post-generation validation: fix dangling parents, isolated nodes, and ensure connectivity.
    Modifies graph in-place.
    """
    if not graph:
        return graph
    L = len(graph)

    # helper maps
    id_to_level_index = {}
    for lvl_idx, lvl in enumerate(graph):
        for idx, n in enumerate(lvl):
            id_to_level_index[n['id']] = (lvl_idx, idx)

    # fix children' parents that reference ids not in previous level
    for lvl in range(1, L):
        prev_ids = [n['id'] for n in graph[lvl - 1]]
        prev_pos = {n['id']: i for i, n in enumerate(graph[lvl - 1])}
        for node in graph[lvl]:
            parents = node.get('parents', [])
            # keep only parents that exist in prev_ids
            valid = [p for p in parents if p in prev_ids]
            if valid:
                node['parents'] = valid
                continue
            # no valid parents: pick closest prev node by index similarity if possible
            # fallback: choose the prev node with fewest children
            best = None
            best_child_count = 1_000_000
            for p in graph[lvl - 1]:
                child_count = sum(1 for c in graph[lvl] if p['id'] in c.get('parents', []))
                if child_count < best_child_count:
                    best_child_count = child_count
                    best = p
            if best is not None:
                node['parents'] = [best['id']]

    # ensure every parent has at least one child (may add child)
    ensure_parents_have_children(graph)

    # ensure no node (except start/boss) is isolated (no parents and no children)
    id_to_node = {n['id']: n for lvl in graph for n in lvl}
    children = {nid: [] for nid in id_to_node}
    for lvl_nodes in graph:
        for n in lvl_nodes:
            for p in n.get('parents', []):
                if p in children:
                    children[p].append(n['id'])

    for lvl_idx in range(1, L - 1):
        for n in graph[lvl_idx]:
            par = n.get('parents', [])
            ch = children.get(n['id'], [])
            if not par and not ch:
                # attach to a nearby parent in prev level
                prev_lvl = graph[lvl_idx - 1]
                if prev_lvl:
                    # pick prev node with fewest children
                    best = min(prev_lvl, key=lambda p: len(children.get(p['id'], [])))
                    n['parents'] = [best['id']]
                    children[best['id']].append(n['id'])

    return graph



def balance_choices(graph: List[List[Dict]], params: Dict | None = None, threshold: float = 2.0) -> List[List[Dict]]:
    """Post-process the generated graph to reduce large expected-value gaps between choices.

    This is a simple heuristic:
    - Compute expected downstream score for each node (node_score + mean(child_expected)).
    - For each level with multiple nodes, if max - min > threshold, try to promote the lowest nodes
      to a better type (elite/shop/treasure) while respecting placement caps in params.
    Returns the mutated graph.
    """
    if params is None:
        params = get_default_params()

    # scoring for types (tunable)
    score_map = {
        'monster': 0.0,
        'event': 1.0,
        'shop': 1.5,
        'rest': 0.5,
        'treasure': 2.0,
        'elite': 3.0,
        'boss': 5.0,
        'start': 0.0,
    }

    # build id -> node mapping and children adjacency
    id_to_node = {}
    children = {}
    for lvl_nodes in graph:
        for n in lvl_nodes:
            id_to_node[n['id']] = n
            children[n['id']] = []
    for lvl_nodes in graph:
        for n in lvl_nodes:
            for p in n.get('parents', []):
                if p in children:
                    children[p].append(n['id'])

    # compute expected downstream values via reverse-topological order (bottom-up by level)
    LEVELS = len(graph)
    expected = {}
    # initialize boss level
    for lvl in range(LEVELS - 1, -1, -1):
        for n in graph[lvl]:
            nid = n['id']
            base = score_map.get(n.get('type', 'monster'), 0.0)
            childs = children.get(nid, [])
            if not childs:
                expected[nid] = base
            else:
                exp_children = [expected[cid] for cid in childs]
                expected[nid] = base + (sum(exp_children) / len(exp_children))

    # count current fixed/guaranteed placements to obey caps
    rest_fixed_rows = set(params.get('rest_rows', []))
    rest_existing = [n for lvl_idx, lvl in enumerate(graph) if lvl_idx not in rest_fixed_rows for n in lvl if n.get('type') == 'rest']
    elite_existing = [n for lvl in graph for n in lvl if n.get('type') == 'elite']
    shop_existing = [n for lvl in graph for n in lvl if n.get('type') == 'shop']
    rest_cap = params.get('REST_CAP', 5)
    elite_extra_cap = params.get('ELITE_EXTRA_CAP', 5)
    shop_extra_cap = params.get('SHOP_EXTRA_CAP', 3)

    # process each level
    for lvl_idx, lvl in enumerate(graph):
        if lvl_idx == 0 or lvl_idx == LEVELS - 1:
            continue
        if len(lvl) < 2:
            continue
        exps = [(expected[n['id']], n) for n in lvl]
        exps.sort(key=lambda x: x[0])
        low = exps[0][0]
        high = exps[-1][0]
        if high - low <= threshold:
            continue
        # attempt to promote lowest nodes one by one until gap reduced or caps hit
        for val, node in exps:
            if high - expected[node['id']] <= threshold:
                break
            # skip fixed types
            if node.get('type') in ('rest', 'treasure', 'boss', 'start'):
                continue
            # prefer promoting to shop then elite then treasure based on availability
            promoted = False
            # try shop (avoid consecutive shops along parent chain)
            if len([n for n in shop_existing if n.get('id')]) < (3 + shop_extra_cap):
                parents_ok = True
                for pid in node.get('parents', []):
                    pnode = id_to_node.get(pid)
                    if pnode is not None and pnode.get('type') == 'shop':
                        parents_ok = False
                        break
                if parents_ok:
                    node['type'] = 'shop'
                    shop_existing.append(node)
                    promoted = True
            # else try elite
            if not promoted and len(elite_existing) < (params.get('GUARANTEED_ELITES', 3) + elite_extra_cap):
                node['type'] = 'elite'
                elite_existing.append(node)
                promoted = True
            # else try treasure (only if not in rest_rows)
            if not promoted and lvl_idx not in params.get('rest_rows', []):
                node['type'] = 'treasure'
                promoted = True
            if promoted:
                # recompute expected downstream for this level upwards (simple recompute)
                for l2 in range(lvl_idx, -1, -1):
                    for n2 in graph[l2]:
                        nid2 = n2['id']
                        base2 = score_map.get(n2.get('type', 'monster'), 0.0)
                        childs2 = children.get(nid2, [])
                        if not childs2:
                            expected[nid2] = base2
                        else:
                            expected[nid2] = base2 + (sum(expected[cid] for cid in childs2) / len(childs2))
                # update high for current level
                exps = [(expected[nn['id']], nn) for nn in lvl]
                exps.sort(key=lambda x: x[0])
                high = exps[-1][0]

    return graph
