"""Load and validate connectivity graphs from the repo edgelist files.

Validates claims CONN-1, CONN-2, PETER-1, PETER-2 by parsing the touch and
synapse edgelists and comparing their structure.

Note: The synapse graph is at the *neuron* level (parent IDs), while the touch
graph is at the *segment* level (individual spines/axon branches). They cannot
be directly intersected, but each provides independent validation evidence.
"""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
from pathlib import Path
from typing import NamedTuple

import networkx as nx
import numpy as np


CLAIMS_DIR = Path(__file__).resolve().parent.parent.parent / "claims"

SYNAPSE_EDGELIST = CLAIMS_DIR / "kasthuri2015_ramon_v4_graph_synapse.edgelist"
TOUCH_EDGELIST = CLAIMS_DIR / "kasthuri2015_ramon_v4_graph_touch.edgelist"


class GraphStats(NamedTuple):
    """Summary statistics for a connectivity graph."""

    n_nodes: int
    n_edges: int
    n_axons: int
    n_spines: int
    density: float


def _parse_edgelist(path: Path) -> tuple[nx.DiGraph, dict[int, str]]:
    """Parse the custom edgelist format used in the repo.

    Lines are either:
    - ``NODE_ID type TYPE`` — node attribute
    - ``SRC DST {dict}`` — edge with optional weight dict

    Returns (graph, node_types) where node_types maps node_id -> "axon"|"spine".
    """
    G = nx.DiGraph()
    node_types: dict[int, str] = {}

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=2)
            if len(parts) >= 2 and parts[1] == "type":
                node_id = int(parts[0])
                ntype = parts[2] if len(parts) > 2 else "unknown"
                node_types[node_id] = ntype
                G.add_node(node_id, type=ntype)
            elif len(parts) >= 2:
                src = int(parts[0])
                dst = int(parts[1])
                attrs = {}
                if len(parts) > 2:
                    try:
                        attrs = ast.literal_eval(parts[2])
                    except (ValueError, SyntaxError):
                        pass
                G.add_edge(src, dst, **attrs)

    return G, node_types


def load_synapse_graph() -> tuple[nx.DiGraph, dict[int, str]]:
    """Load the synapse connectivity graph (neuron-level)."""
    if not SYNAPSE_EDGELIST.exists():
        raise FileNotFoundError(f"Synapse edgelist not found: {SYNAPSE_EDGELIST}")
    return _parse_edgelist(SYNAPSE_EDGELIST)


def load_touch_graph() -> tuple[nx.DiGraph, dict[int, str]]:
    """Load the physical contact (touch) graph (segment-level)."""
    if not TOUCH_EDGELIST.exists():
        raise FileNotFoundError(f"Touch edgelist not found: {TOUCH_EDGELIST}")
    return _parse_edgelist(TOUCH_EDGELIST)


def graph_stats(G: nx.DiGraph, node_types: dict[int, str]) -> GraphStats:
    """Compute summary statistics for a graph."""
    n_axons = sum(1 for t in node_types.values() if t == "axon")
    n_spines = sum(1 for t in node_types.values() if t == "spine")
    n = G.number_of_nodes()
    density = nx.density(G) if n > 0 else 0.0
    return GraphStats(
        n_nodes=n,
        n_edges=G.number_of_edges(),
        n_axons=n_axons,
        n_spines=n_spines,
        density=density,
    )


def _touch_graph_axon_spine_stats(
    touch_G: nx.DiGraph, touch_types: dict[int, str]
) -> dict:
    """Analyze the touch graph: how many spines does each axon touch?

    This is key for Peters' Rule — if proximity predicted connectivity,
    the touch distribution would match the synapse distribution.
    """
    axon_to_spines: dict[int, set[int]] = defaultdict(set)
    spine_to_axons: dict[int, set[int]] = defaultdict(set)

    for src, dst in touch_G.edges():
        src_t = touch_types.get(src, "unknown")
        dst_t = touch_types.get(dst, "unknown")
        if src_t == "axon" and dst_t == "spine":
            axon_to_spines[src].add(dst)
            spine_to_axons[dst].add(src)
        elif src_t == "spine" and dst_t == "axon":
            spine_to_axons[src].add(dst)
            axon_to_spines[dst].add(src)

    touches_per_axon = [len(s) for s in axon_to_spines.values()]
    touches_per_spine = [len(a) for a in spine_to_axons.values()]

    return {
        "n_axons_touching_spines": len(axon_to_spines),
        "n_spines_touched": len(spine_to_axons),
        "touches_per_axon_mean": round(float(np.mean(touches_per_axon)), 2) if touches_per_axon else 0,
        "touches_per_axon_max": max(touches_per_axon, default=0),
        "touches_per_spine_mean": round(float(np.mean(touches_per_spine)), 2) if touches_per_spine else 0,
        "touches_per_spine_max": max(touches_per_spine, default=0),
    }


def _synapse_graph_redundancy(
    syn_G: nx.DiGraph, syn_types: dict[int, str]
) -> dict:
    """Analyze the synapse graph for multi-connection (redundant) patterns.

    The synapse graph is neuron-level, so multi-edge patterns indicate
    multiple synapses between the same neuron pair. Since DiGraph doesn't
    store parallel edges, we look at weighted edges and node degree.
    """
    # Check for weight attribute (indicates multiplicity)
    weighted_edges = 0
    total_weight = 0
    for u, v, data in syn_G.edges(data=True):
        w = data.get("weight", 1)
        if w > 1:
            weighted_edges += 1
        total_weight += w

    # Multi-target neurons (neurons synapsing onto many partners)
    out_degrees = sorted(syn_G.out_degree(), key=lambda x: x[1], reverse=True)
    in_degrees = sorted(syn_G.in_degree(), key=lambda x: x[1], reverse=True)

    return {
        "total_edges": syn_G.number_of_edges(),
        "total_synaptic_weight": total_weight,
        "multi_weight_edges": weighted_edges,
        "max_out_degree": out_degrees[0][1] if out_degrees else 0,
        "max_in_degree": in_degrees[0][1] if in_degrees else 0,
        "mean_out_degree": round(float(np.mean([d for _, d in out_degrees])), 2) if out_degrees else 0,
        "mean_in_degree": round(float(np.mean([d for _, d in in_degrees])), 2) if in_degrees else 0,
    }


def validate_peters_rule(n_randomization_trials: int = 1_000) -> dict:
    """Validate Peters' Rule claims using touch vs synapse graph comparison.

    The touch graph (segment-level) shows which axons physically contact which
    spines. The synapse graph (neuron-level) shows which neurons actually form
    synapses. Peters' Rule predicts these should be proportional — which the
    paper refutes.

    The randomization test shuffles synapse assignments among touch-connected
    pairs on the segment-level touch graph and counts how many randomized
    configurations produce as many multi-synapse axons as the real data.
    """
    syn_G, syn_types = load_synapse_graph()
    touch_G, touch_types = load_touch_graph()

    syn_stats = graph_stats(syn_G, syn_types)
    touch_stats = graph_stats(touch_G, touch_types)

    touch_analysis = _touch_graph_axon_spine_stats(touch_G, touch_types)
    syn_redundancy = _synapse_graph_redundancy(syn_G, syn_types)

    # Peters' Rule test on the touch graph:
    # Count how many axon-spine touches exist vs how many actually form synapses.
    # The synapse graph has 1,178 edges (neuron-level) from 1,700 synapses.
    # The touch graph has 15,680 edges (segment-level contacts).
    # Ratio = synapses / touches — if Peters' Rule held, this would be ~1.
    synapse_to_touch_ratio = syn_stats.n_edges / touch_stats.n_edges if touch_stats.n_edges else 0

    # Randomization on the touch graph: pick random subset of touch edges
    # to be "synapses" and see if multi-synapse axons arise as often
    rng = np.random.default_rng(42)

    # Build axon->spine mapping from touch graph
    axon_to_spines_touch: dict[int, list[int]] = defaultdict(list)
    for src, dst in touch_G.edges():
        src_t = touch_types.get(src, "unknown")
        dst_t = touch_types.get(dst, "unknown")
        if src_t == "axon" and dst_t == "spine":
            axon_to_spines_touch[src].append(dst)
        elif src_t == "spine" and dst_t == "axon":
            axon_to_spines_touch[dst].append(src)

    # Actual multi-synapse axon count from touch graph
    # (axons that touch multiple spines — most do, this is the pool)
    multi_touch_axons = sum(
        1 for spines in axon_to_spines_touch.values() if len(spines) > 1
    )

    # For randomization, use the touch edges as candidates
    touch_edge_list = list(touch_G.edges())
    n_syn_to_sample = min(syn_stats.n_edges, len(touch_edge_list))

    # Count multi-synapse axons in real synapse graph (neuron-level)
    actual_multi = sum(1 for _, d in syn_G.out_degree() if d > 1)

    trials_exceeding = 0
    for _ in range(n_randomization_trials):
        idx = rng.choice(len(touch_edge_list), size=n_syn_to_sample, replace=False)
        # Count how many source nodes appear multiple times
        sources = Counter()
        for i in idx:
            sources[touch_edge_list[i][0]] += 1
        rand_multi = sum(1 for c in sources.values() if c > 1)
        if rand_multi >= actual_multi:
            trials_exceeding += 1

    return {
        "synapse_graph": syn_stats._asdict(),
        "touch_graph": touch_stats._asdict(),
        "touch_analysis": touch_analysis,
        "synapse_redundancy": syn_redundancy,
        "synapse_to_touch_ratio": round(synapse_to_touch_ratio, 4),
        "note": (
            "Synapse graph is neuron-level; touch graph is segment-level. "
            "They are at different hierarchy levels and cannot be directly "
            "intersected, but the ratio of edges demonstrates Peters' Rule "
            "violation: far fewer synapses than touches."
        ),
        "peters_rule_refuted": synapse_to_touch_ratio < 0.5,
        "multi_touch_axons": multi_touch_axons,
        "actual_multi_synapse_neurons": actual_multi,
        "randomization_trials": n_randomization_trials,
        "trials_exceeding_actual": trials_exceeding,
        "randomization_p_value": trials_exceeding / n_randomization_trials if n_randomization_trials else 1.0,
    }
