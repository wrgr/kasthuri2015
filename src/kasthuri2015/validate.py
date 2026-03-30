"""Unified validation runner for all Kasthuri 2015 claims.

Usage::

    from kasthuri2015.validate import run_all
    results = run_all()

Or from the command line::

    python -m kasthuri2015.validate
"""

from __future__ import annotations

import json
import sys
import time


def run_graph_validation() -> dict:
    """Validate graph/connectivity claims."""
    from kasthuri2015.validate_graphs import validate_peters_rule
    return validate_peters_rule()


def run_sasd_validation(n_permutations: int = 1_000) -> dict:
    """Validate SASD pair claims."""
    from kasthuri2015.validate_sasd import validate_sasd
    return validate_sasd(n_permutations=n_permutations)


def run_all(n_permutations: int = 1_000) -> dict:
    """Run all validations and return combined results."""
    results = {}

    t0 = time.time()
    results["graphs"] = run_graph_validation()
    results["graphs"]["elapsed_s"] = round(time.time() - t0, 2)

    t0 = time.time()
    results["sasd"] = run_sasd_validation(n_permutations=n_permutations)
    results["sasd"]["elapsed_s"] = round(time.time() - t0, 2)

    return results


def main() -> None:
    """CLI entry point."""
    n_perm = 1_000
    if "--full" in sys.argv:
        n_perm = 10_000

    print(f"Running validations (n_permutations={n_perm})...")
    results = run_all(n_permutations=n_perm)

    # Summary
    g = results["graphs"]
    print("\n=== Graph Validation ===")
    print(f"Synapse graph: {g['synapse_graph']['n_nodes']} nodes, "
          f"{g['synapse_graph']['n_edges']} edges")
    print(f"Touch graph:   {g['touch_graph']['n_nodes']} nodes, "
          f"{g['touch_graph']['n_edges']} edges")
    print(f"Synapse/touch edge ratio: {g['synapse_to_touch_ratio']:.4f}")
    print(f"Peters' Rule refuted: {g['peters_rule_refuted']}")
    ta = g["touch_analysis"]
    print(f"Touch graph: {ta['n_axons_touching_spines']} axons touch "
          f"{ta['n_spines_touched']} spines (mean {ta['touches_per_spine_mean']} axons/spine)")
    sr = g["synapse_redundancy"]
    print(f"Synapse graph: {sr['total_edges']} edges, "
          f"max out-degree={sr['max_out_degree']}, mean={sr['mean_out_degree']}")
    print(f"Multi-synapse neurons: {g['actual_multi_synapse_neurons']}")
    print(f"Randomization: {g['trials_exceeding_actual']}/{g['randomization_trials']} "
          f"trials exceeded actual (p={g['randomization_p_value']:.4f})")
    print(f"Elapsed: {g['elapsed_s']:.1f}s")

    s = results["sasd"]
    print("\n=== SASD Validation ===")
    print(f"Groups: {s['n_groups']}, Spines: {s['n_spines']}")
    print(f"Pair counts: {s['pair_counts']}")
    print("\nSASD vs non-SASD (permutation test):")
    for feat, res in s["sasd_vs_rest"].items():
        sig = "***" if res["p_value"] < 0.001 else "**" if res["p_value"] < 0.01 else "*" if res["p_value"] < 0.05 else ""
        print(f"  {feat:25s}: diff={res['observed_diff']:+.4f}  p={res['p_value']:.4f} {sig}")
    print(f"Elapsed: {s['elapsed_s']:.1f}s")

    # Dump full JSON
    if "--json" in sys.argv:
        print("\n" + json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
