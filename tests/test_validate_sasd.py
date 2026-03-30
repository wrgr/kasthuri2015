"""Tests for SASD validation."""

from kasthuri2015.validate_sasd import (
    compute_all_pairwise_diffs,
    groups_to_dataframe,
    load_sasd_data,
    validate_sasd,
)


def test_load_sasd_data():
    groups = load_sasd_data()
    assert len(groups) == 28  # 28 SASD groups


def test_groups_to_dataframe():
    groups = load_sasd_data()
    data = groups_to_dataframe(groups)
    assert len(data["spineid"]) == 59  # 59 total spines
    assert len(data["pair_id"]) == 59


def test_pair_counts_match_paper():
    """Paper reports SASD=35, DASD=166, SADD=8, DADD=1502."""
    groups = load_sasd_data()
    data = groups_to_dataframe(groups)
    pairs = compute_all_pairwise_diffs(data)
    labels = pairs["sasd_label"]
    assert (labels == "SASD").sum() == 35
    assert (labels == "DASD").sum() == 166
    assert (labels == "SADD").sum() == 8
    assert (labels == "DADD").sum() == 1502


def test_validate_sasd_spine_volume_significant():
    """Spine volume should be the most significant feature."""
    results = validate_sasd(n_permutations=500)
    sv = results["sasd_vs_rest"]["log_spinevolume"]
    # Should be significant (paper: p=3.4e-4)
    assert sv["p_value"] < 0.01
    # SASD pairs should be more similar (positive diff)
    assert sv["observed_diff"] > 0


def test_validate_sasd_pair_counts():
    results = validate_sasd(n_permutations=100)
    pc = results["pair_counts"]
    assert pc["SASD"] == 35
    assert pc["DASD"] == 166
    assert pc["total"] == 1711
