# -*- coding: utf-8 -*-
"""
Utilities for computing map node screen positions used by MapView and MapScene.

Functions:
 - compute_node_positions(graph, screen_width, screen_height, overlay_scroll, node_size=32, level_margin=80, level_spacing=80, h_padding=40)

Returns: (positions, per_level)
 - positions: dict[node_id] -> (cx, cy, r)
 - per_level: dict[level_idx] -> list of (node_dict, cx, cy)
"""
from typing import List, Dict, Tuple


def compute_node_positions(graph: List[List[Dict]], screen_width: int, screen_height: int, overlay_scroll: int | float = 0,
                           node_size: int = 32, level_margin: int = 80, level_spacing: int = 80, h_padding: int = 40) -> Tuple[Dict[int, Tuple[int, int, int]], Dict[int, List[Tuple[Dict, int, int]]]]:
    """Compute center positions for each node in the graph.

    graph: list of levels, each level is list of node dicts with 'id'
    Returns positions and per_level placements.
    """
    positions: Dict[int, Tuple[int, int, int]] = {}
    per_level: Dict[int, List[Tuple[Dict, int, int]]] = {}
    if not graph:
        return positions, per_level

    r = node_size // 2
    scroll = int(overlay_scroll or 0)
    for lvl_idx, nodes in enumerate(graph):
        y = int(level_margin + lvl_idx * level_spacing) - scroll
        count = len(nodes)
        if count == 0:
            continue
        total_w = count * node_size + (count - 1) * h_padding
        start_x = (screen_width - total_w) // 2
        row = []
        for i, node in enumerate(nodes):
            x = int(start_x + i * (node_size + h_padding))
            cx = x + r
            cy = y
            positions[node['id']] = (cx, cy, r)
            row.append((node, cx, cy))
        per_level[lvl_idx] = row
    return positions, per_level
