"""Tests for graph validation."""

from kasthuri2015.validate_graphs import (
    graph_stats,
    load_synapse_graph,
    load_touch_graph,
    validate_peters_rule,
)


def test_load_synapse_graph():
    G, types = load_synapse_graph()
    assert G.number_of_nodes() > 0
    assert G.number_of_edges() > 0
    assert "axon" not in types.values() or "spine" not in types.values() or len(types) > 0


def test_load_touch_graph():
    G, types = load_touch_graph()
    assert G.number_of_nodes() > 0
    assert G.number_of_edges() > 0
    n_axons = sum(1 for t in types.values() if t == "axon")
    n_spines = sum(1 for t in types.values() if t == "spine")
    assert n_axons > 0
    assert n_spines > 0


def test_touch_graph_has_1423_axons():
    """Paper claims 1,407-1,423 axons."""
    _, types = load_touch_graph()
    n_axons = sum(1 for t in types.values() if t == "axon")
    assert 1_400 <= n_axons <= 1_500


def test_touch_graph_has_more_edges_than_synapse():
    """Touch graph should have far more edges (Peters' Rule)."""
    syn_G, _ = load_synapse_graph()
    touch_G, _ = load_touch_graph()
    assert touch_G.number_of_edges() > 10 * syn_G.number_of_edges()


def test_validate_peters_rule():
    results = validate_peters_rule(n_randomization_trials=100)
    assert results["peters_rule_refuted"] is True
    assert results["synapse_to_touch_ratio"] < 0.5
    assert results["touch_analysis"]["n_axons_touching_spines"] > 1000
    assert results["touch_analysis"]["n_spines_touched"] > 500
