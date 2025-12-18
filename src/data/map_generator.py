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
        # minimum required non-empty steps on any start->boss path; if None, defaults to LEVELS-2
        'MIN_REQUIRED_STEPS': None,
    }


def generate(seed: int | None = None, params: Dict | None = None) -> List[List[Dict]]:
    # Establish a reproducible internal seed for each invocation so problematic maps can be reproduced.
    if seed is not None:
        used_seed = int(seed)
        random.seed(used_seed)
    else:
        used_seed = random.randrange(2 ** 32)
        random.seed(used_seed)

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
        Returns (new_list, new_next_id).
        Each merged node will have 'id' set to next_id (incremented) and 'parents' as union.
        Selection prefers pairs with smallest combined parent set size.
        """
        if k <= 0 or len(nodes_list) < 2:
            return nodes_list, next_id
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
            return nodes_list, next_id
        merges_set = set(merges)
        new_list = []
        i = 0
        while i < n:
            if i in merges_set:
                a = nodes_list[i]
                b = nodes_list[i + 1]
                merged_parents = list(set(a.get('parents', []) + b.get('parents', [])))
                merged = {'id': next_id, 'level': a.get('level', b.get('level')), 'parents': merged_parents, 'merged_from': True}
                next_id += 1
                new_list.append(merged)
                i += 2
            else:
                new_list.append(nodes_list[i])
                i += 1
        return new_list, next_id

    # build subsequent levels
    # auxiliary vars for "3連続変化無しで強制分岐/結合"ルール
    no_change_run = 0
    pending_action_level = None
    PRE_TREASURE_ROWS = [r - 1 for r in TREASURE_ROWS]
    boss_pre_rest = max(REST_ROWS) if REST_ROWS else None
    excluded_levels_for_forcing = set()
    if boss_pre_rest is not None:
        excluded_levels_for_forcing.add(boss_pre_rest)
        if boss_pre_rest - 1 >= 0:
            excluded_levels_for_forcing.add(boss_pre_rest - 1)

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
                    temp, nid = pairwise_merge_k(temp, need, nid)
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
                    temp, nid = pairwise_merge_k(temp, need, nid)
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

            # --- detect simple crossing pattern between two adjacent parents and resolve ---
            # For each adjacent parent pair (pl, pr) in previous row, if there exist children
            # cl (to the right) connected to pl and cr (to the left) connected to pr such that
            # their positions cross (index_cl > index_cr), remove one of the two edges with 50/50 chance.
            # Safety: do not remove an edge if it would orphan the child (i.e., child has only that parent).
            if len(prev) >= 2 and len(row) >= 2:
                # build mapping from parent id to list of child indices
                parent_to_children_idxs = {}
                for idx, node in enumerate(row):
                    for pid in node.get('parents', []):
                        parent_to_children_idxs.setdefault(pid, []).append(idx)

                for i_parent in range(len(prev) - 1):
                    pl = prev[i_parent]['id']
                    pr = prev[i_parent + 1]['id']
                    left_idxs = parent_to_children_idxs.get(pl, [])
                    right_idxs = parent_to_children_idxs.get(pr, [])
                    if not left_idxs or not right_idxs:
                        continue
                    # examine all pairs for crossing
                    for li in left_idxs:
                        for ri in right_idxs:
                            # crossing when left-parent's child is to the right of right-parent's child
                            if li > ri:
                                left_node = row[li]
                                right_node = row[ri]
                                # edges considered: (pl -> left_node) and (pr -> right_node)
                                # decide randomly which to remove, but ensure we don't orphan
                                choice = random.choice([0, 1])
                                removed = False
                                if choice == 0:
                                    # try remove pr->right_node
                                    if len(right_node.get('parents', [])) > 1:
                                        right_node['parents'] = [p for p in right_node.get('parents', []) if p != pr]
                                        removed = True
                                    else:
                                        # try the other edge if safe
                                        if len(left_node.get('parents', [])) > 1:
                                            left_node['parents'] = [p for p in left_node.get('parents', []) if p != pl]
                                            removed = True
                                else:
                                    # try remove pl->left_node
                                    if len(left_node.get('parents', [])) > 1:
                                        left_node['parents'] = [p for p in left_node.get('parents', []) if p != pl]
                                        removed = True
                                    else:
                                        if len(right_node.get('parents', [])) > 1:
                                            right_node['parents'] = [p for p in right_node.get('parents', []) if p != pr]
                                            removed = True
                                # if removed, update parent_to_children_idxs to avoid double-handling
                                if removed:
                                    parent_to_children_idxs = {}
                                    for idx2, node2 in enumerate(row):
                                        for pid2 in node2.get('parents', []):
                                            parent_to_children_idxs.setdefault(pid2, []).append(idx2)
                                    # continue scanning this parent pair for other crossings
                                # After attempting safe edge removals, perform a small swap-pass to fix remaining crossings
                                # without changing topology. This avoids orphaning while correcting ordering.
                                swap_iter = 0
                                while True:
                                    swapped = False
                                    # rebuild mapping
                                    parent_to_children_idxs = {}
                                    for idx2, node2 in enumerate(row):
                                        for pid2 in node2.get('parents', []):
                                            parent_to_children_idxs.setdefault(pid2, []).append(idx2)
                                    for i_parent2 in range(len(prev) - 1):
                                        pl2 = prev[i_parent2]['id']
                                        pr2 = prev[i_parent2 + 1]['id']
                                        left_idxs2 = parent_to_children_idxs.get(pl2, [])
                                        right_idxs2 = parent_to_children_idxs.get(pr2, [])
                                        for li2 in list(left_idxs2):
                                            for ri2 in list(right_idxs2):
                                                if li2 > ri2:
                                                    # swap the two nodes in this row to remove crossing
                                                    row[li2], row[ri2] = row[ri2], row[li2]
                                                    swapped = True
                                                    break
                                            if swapped:
                                                break
                                        if swapped:
                                            break
                                    swap_iter += 1
                                    if not swapped or swap_iter >= 8:
                                        break

        # If this row is immediately before a rest-full row,
        # ensure it is merged down to at most 3 nodes so that the rest row receives three inputs.
        if lvl in PRE_REST_ROWS:
            need = len(row) - 3
            if need > 0:
                row, nid = pairwise_merge_k(row, need, nid)

        # deterministic rule: if prev_count == MAX_PER_ROW, force merge to 3 nodes
        if prev_count == MAX_PER_ROW:
            need = len(row) - 3
            if need > 0:
                row, nid = pairwise_merge_k(row, need, nid)

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
            row, nid = pairwise_merge_k(row, need, nid)

        # detect branching (a parent producing multiple children) for this level
        parent_child_counts = {}
        for node in row:
            for pid in node.get('parents', []):
                parent_child_counts[pid] = parent_child_counts.get(pid, 0) + 1
        branch_occurred = any(cnt > 1 for cnt in parent_child_counts.values())

        # detect merges if any node carries 'merged_from'
        merges_performed = any(n.get('merged_from') for n in row)

        # If an action was scheduled to be performed on this level (redirect from PRE_REST/PRE_TREASURE), do it now
        if pending_action_level == lvl:
            if lvl not in excluded_levels_for_forcing:
                if len(row) >= 2:
                    a = row[0]
                    b = row[1]
                    merged_parents = list(set(a.get('parents', []) + b.get('parents', [])))
                    merged = {'id': nid, 'level': lvl, 'parents': merged_parents, 'merged_from': True}
                    nid += 1
                    row = [merged] + row[2:]
                    merges_performed = True
                else:
                    # attempt branching: add a child for parent with fewest children
                    if lvl - 1 >= 0 and graph[lvl - 1]:
                        prev_parents = graph[lvl - 1]
                        counts = {p['id']: 0 for p in prev_parents}
                        for node in row:
                            for pid in node.get('parents', []):
                                if pid in counts:
                                    counts[pid] += 1
                        pick_pid = min(counts.keys(), key=lambda k: counts[k])
                        new_node = {'id': nid, 'level': lvl, 'parents': [pick_pid], 'type': 'normal'}
                        nid += 1
                        row.append(new_node)
                        branch_occurred = True
            pending_action_level = None

        # determine whether this level saw any change
        changed = branch_occurred or merges_performed

        # update no-change run counter
        if not changed:
            no_change_run += 1
        else:
            no_change_run = 0

        # if 3 consecutive no-change levels seen, schedule/perform forced change
        if no_change_run >= 3:
            target = lvl
            # if target is immediately before fixed rest/treasure, redirect to that fixed row
            if target in PRE_REST_ROWS or target in PRE_TREASURE_ROWS:
                redirect = target + 1
                if redirect < LEVELS and redirect not in excluded_levels_for_forcing:
                    pending_action_level = redirect
                    no_change_run = 0
                else:
                    # fallback: try to act on current level
                    if target not in excluded_levels_for_forcing:
                        if len(row) >= 2:
                            a = row[0]
                            b = row[1]
                            merged_parents = list(set(a.get('parents', []) + b.get('parents', [])))
                            merged = {'id': nid, 'level': target, 'parents': merged_parents, 'merged_from': True}
                            nid += 1
                            row = [merged] + row[2:]
                            no_change_run = 0
                        else:
                            if target - 1 >= 0 and graph[target - 1]:
                                prev_parents = graph[target - 1]
                                counts = {p['id']: 0 for p in prev_parents}
                                for node in row:
                                    for pid in node.get('parents', []):
                                        if pid in counts:
                                            counts[pid] += 1
                                pick_pid = min(counts.keys(), key=lambda k: counts[k])
                                new_node = {'id': nid, 'level': target, 'parents': [pick_pid], 'type': 'normal'}
                                nid += 1
                                row.append(new_node)
                                no_change_run = 0
            else:
                if target not in excluded_levels_for_forcing:
                    if len(row) >= 2:
                        a = row[0]
                        b = row[1]
                        merged_parents = list(set(a.get('parents', []) + b.get('parents', [])))
                        merged = {'id': nid, 'level': target, 'parents': merged_parents, 'merged_from': True}
                        nid += 1
                        row = [merged] + row[2:]
                        no_change_run = 0
                    else:
                        if target - 1 >= 0 and graph[target - 1]:
                            prev_parents = graph[target - 1]
                            counts = {p['id']: 0 for p in prev_parents}
                            for node in row:
                                for pid in node.get('parents', []):
                                    if pid in counts:
                                        counts[pid] += 1
                            pick_pid = min(counts.keys(), key=lambda k: counts[k])
                            new_node = {'id': nid, 'level': target, 'parents': [pick_pid], 'type': 'normal'}
                            nid += 1
                            row.append(new_node)
                            no_change_run = 0

        # Coalesce any nodes that share an identical multi-parent set into a single merged node.
        # This avoids duplicated children that create unavoidable X-connections.
        parentset_to_indices = {}
        for idx, node in enumerate(row):
            pset = frozenset(node.get('parents', []))
            parentset_to_indices.setdefault(pset, []).append(idx)
        if any(len(idxs) > 1 and len(pset) > 1 for pset, idxs in parentset_to_indices.items()):
            new_row = []
            handled = set()
            for idx, node in enumerate(row):
                if idx in handled:
                    continue
                pset = frozenset(node.get('parents', []))
                idxs = parentset_to_indices.get(pset, [])
                if len(pset) > 1 and len(idxs) > 1:
                    # create a single merged node placed at the first occurrence
                    merged = {'id': nid, 'level': lvl, 'parents': list(pset), 'merged_from': True}
                    nid += 1
                    new_row.append(merged)
                    for j in idxs:
                        handled.add(j)
                else:
                    new_row.append(node)
                    handled.add(idx)
            row = new_row

        graph.append(row)
        # ensure at least 2 nodes for non-first, non-boss rows
        if lvl != 0 and lvl != LEVELS - 1:
            while len(graph[-1]) < 2:
                src_node = graph[-1][0]
                new_node = {'id': nid, 'level': lvl, 'parents': list(src_node.get('parents', [])), 'type': src_node.get('type', 'monster')}
                nid += 1
                graph[-1].append(new_node)

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

    # Final topological coalesce pass:
    # For each level, if multiple nodes share the exact same parent set, merge them into a single node
    # and update children to point to the merged node. This preserves topology while removing
    # duplicate multi-parent children that create unavoidable visual crossings.
    for lvl_idx in range(1, len(graph) - 1):
        lvl_nodes = graph[lvl_idx]
        # group by parent-set
        groups = {}
        for n in lvl_nodes:
            pset = frozenset(n.get('parents', []))
            groups.setdefault(pset, []).append(n)
        changed = False
        for pset, nodes_group in list(groups.items()):
            if len(nodes_group) <= 1 or len(pset) <= 1:
                continue
            # create merged node
            merged_id = nid
            merged_node = {'id': merged_id, 'level': lvl_idx, 'parents': list(pset), 'merged_from': True}
            nid += 1
            # replace nodes in level with merged_node (keep original order: place merged at first occurrence)
            first_idx = min(lvl_nodes.index(n) for n in nodes_group)
            new_lvl = []
            for i, n in enumerate(lvl_nodes):
                if n in nodes_group:
                    if i == first_idx:
                        new_lvl.append(merged_node)
                    # skip other duplicates
                else:
                    new_lvl.append(n)
            graph[lvl_idx] = new_lvl
            # update children in next level to point to merged_id instead of any of the originals
            next_lvl = graph[lvl_idx + 1]
            orig_ids = set(n['id'] for n in nodes_group)
            for child in next_lvl:
                parents = child.get('parents', [])
                new_parents = []
                replaced = False
                for pid in parents:
                    if pid in orig_ids:
                        if not replaced:
                            new_parents.append(merged_id)
                            replaced = True
                        # else skip additional duplicates
                    else:
                        new_parents.append(pid)
                child['parents'] = new_parents
            changed = True
        if changed:
            # rebuild id map if needed (loop continues)
            pass

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
            new_nodes, new_nid = pairwise_merge_k(lvl_nodes, need, nid)
            # if pairwise succeeded in reducing length, accept result
            if len(new_nodes) < len(lvl_nodes):
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

    # Skips disabled: map generator no longer marks any node as 'empty'/'skip'.
    # (Previous skip-placement and safety-cleanup logic was removed.)

    # Final pass: convert any remaining unknowns to monster
    for lvl in range(1, LEVELS - 1):
        for n in graph[lvl]:
            if 'type' not in n or n['type'] is None:
                n['type'] = 'monster'

    # detect remaining crossings and log seed for repro if any
    try:
        if _detect_crossings(graph):
            print(f"MAP_CROSSING_SEED={used_seed}")
    except Exception:
        # safe: never let logging break generation
        pass
    return graph


def _detect_crossings(graph: List[List[Dict]]) -> bool:
    """Return True if any crossing pattern (left-parent->right-child crossing) exists in the graph."""
    for lvl in range(1, len(graph)):
        prev = graph[lvl - 1]
        row = graph[lvl]
        if not prev or not row:
            continue
        # build mapping parent id -> list of child indices
        parent_children = {}
        for idx, node in enumerate(row):
            for pid in node.get('parents', []):
                parent_children.setdefault(pid, []).append(idx)
        # check adjacent parent pairs
        for i in range(len(prev) - 1):
            pl = prev[i]['id']
            pr = prev[i + 1]['id']
            left_idxs = parent_children.get(pl, [])
            right_idxs = parent_children.get(pr, [])
            if not left_idxs or not right_idxs:
                continue
            for li in left_idxs:
                for ri in right_idxs:
                    if li > ri:
                        return True
    return False


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
