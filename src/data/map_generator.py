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


def generate(seed: int | None = None) -> List[List[Dict]]:
    if seed is not None:
        random.seed(seed)

    LEVELS = 15
    MAX_PER_ROW = 6
    nid = 0
    graph: List[List[Dict]] = []

    # Start row count: 10% ->1, 35% ->2, 55% ->3
    r = random.random() * 100
    if r < 10:
        start_count = 1
    elif r < 45:
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
            # do not consider pairs where either node was already produced by a merge in this level
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
    for lvl in range(1, LEVELS):
        prev = graph[lvl - 1]
        prev_count = len(prev)
        row: List[Dict] = []

        # Special rows
        # Move rest rows earlier: now rest rows are at 6th and 13th positions (1-based).
        # For 0-based indices: rest rows are lvl == 5 or lvl == 12.
        # Behavior:
        #  - If the previous row has 3 or fewer nodes, preserve that count and create one rest node per previous node (one-to-one).
        #  - If the previous row has more than 3 nodes, merge adjacent parents until exactly 3 rest nodes remain.
        if lvl == 5 or lvl == 13:
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

        if lvl == 6:
            # Treasure row should not branch from rest: prefer one-to-one mapping from prev rest nodes.
            # If there are more prev nodes than MAX_PER_ROW, group adjacent parents into MAX_PER_ROW groups.
            if prev_count <= MAX_PER_ROW:
                for p in prev:
                    row.append({'id': nid, 'level': lvl, 'parents': [p['id']], 'type': 'treasure'})
                    nid += 1
            else:
                # Reduce prev nodes to MAX_PER_ROW by repeatedly merging adjacent pairs (pairwise merges only).
                temp = []
                for p in prev:
                    temp.append({'id': None, 'parents': [p['id']]})
                # reduce to MAX_PER_ROW using non-overlapping pairwise merges
                need = len(temp) - MAX_PER_ROW
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

        # Normal growth: each parent spawns 1-3 children (weighted)
        for p in prev:
            rr = random.random()
            if rr < 0.6:
                c = 1
            elif rr < 0.9:
                c = 2
            else:
                c = 3
            for _ in range(c):
                row.append({'id': nid, 'level': lvl, 'parents': [p['id']], 'type': 'normal'})
                nid += 1

        # If this row is immediately before a rest-full row (i.e. levels 4 and 12 -> next are 5 and 13),
        # ensure it is merged down to at most 3 nodes so that the rest row receives three inputs.
        if lvl in (4, 12):
            need = len(row) - 3
            if need > 0:
                row, nid = pairwise_merge_k(row, need, nid)

        # deterministic rule: if prev_count == 6, force merge to 3 nodes
        if prev_count == 6:
            need = len(row) - 3
            if need > 0:
                row, nid = pairwise_merge_k(row, need, nid)

        # probabilistic merges based on prev_count
        merge_chance = 0.0
        if prev_count >= 6:
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
        # Prevent consecutive elite/rest along a single-parent chain
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
        if lvl == 5 or lvl == 13:
            for n in graph[lvl]:
                n['type'] = 'rest'
        elif lvl == 6:
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
            allowed = []
            if lvl < 4:
                allowed = [('monster', 70), ('event', 30)]
            else:
                allowed = [('monster', 30), ('elite', 15), ('event', 32), ('shop', 8), ('rest', 15)]

            # sample with simple weight, but enforce non-consecutive for elite/rest
            choices = [t for t, w in allowed]
            weights = [w for t, w in allowed]
            # normalized random choice
            pick = random.choices(choices, weights=weights, k=1)[0]
            # if picked elite/rest but parent already same type, fallback to monster
            if pick in ('elite', 'rest') and not can_be_nonconsecutive(n, pick):
                pick = 'monster'
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
            c['type'] = kind
            placed.append(c)
        return placed

    elites = pick_guaranteed('elite', 3)
    shops = pick_guaranteed('shop', 3)

    # Final pass: convert any remaining unknowns to monster
    for lvl in range(1, LEVELS - 1):
        for n in graph[lvl]:
            if 'type' not in n or n['type'] is None:
                n['type'] = 'monster'

    return graph
