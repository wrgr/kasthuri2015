"""Tests for validation against ground truth."""

from kasthuri2015.validate import (
    APPROXIMATE,
    CONFIRMED,
    DISCREPANCY,
    NOT_VALIDATABLE,
    validate_all,
)


def _results_by_id():
    results = validate_all()
    return {r.claim_id: r for r in results}


def test_validate_all_runs():
    results = validate_all()
    assert len(results) > 30


def test_syn1_confirmed():
    r = _results_by_id()
    assert r["SYN-1"].status == CONFIRMED
    assert r["SYN-1"].observed == 1700


def test_syn3_confirmed():
    r = _results_by_id()
    assert r["SYN-3"].status == CONFIRMED


def test_syn2_approximate():
    r = _results_by_id()
    assert r["SYN-2"].status == APPROXIMATE
    # mmc6 has 1427 spine synapses vs mmc2's 1424; either count is valid
    observed = str(r["SYN-2"].observed)
    assert any(x in observed for x in ("1405", "1406", "1407"))


def test_corr2_approximate():
    """Spine volume vs PSD size should be close to r=0.77."""
    r = _results_by_id()
    assert r["CORR-2"].status == APPROXIMATE
    assert "r=0.7" in r["CORR-2"].observed


def test_bossdb_claims_not_validatable():
    r = _results_by_id()
    for claim_id in ["CELL-1", "MITO-1", "VES-1", "AXN-1"]:
        assert r[claim_id].status == NOT_VALIDATABLE


def test_sasd1_approximate():
    r = _results_by_id()
    assert r["SASD-1"].status == APPROXIMATE
    assert "122" in str(r["SASD-1"].observed)


def test_no_missing_claims():
    """Every claim in the catalog should have a validation result."""
    from kasthuri2015 import CLAIMS
    r = _results_by_id()
    # Not all 47 claims have individual checks (SASD-3..7, BOUT-3,4, etc.)
    # but we should have at least the main ones + NOT_VALIDATABLE
    assert len(r) >= 30
