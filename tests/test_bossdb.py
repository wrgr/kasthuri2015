"""Tests for BossDB validation module.

Most tests are skipped if BossDB is unreachable or dependencies are missing,
so this suite can run offline without failure.
"""

import pytest

from kasthuri2015.bossdb import (
    APPROXIMATE,
    CONFIRMED,
    DISCREPANCY,
    NOT_VALIDATABLE,
    BossDBResult,
    bossdb_available,
    validate_bossdb,
)


# ---------------------------------------------------------------------------
# Smoke tests — always run (no network required)
# ---------------------------------------------------------------------------


def test_bossdb_result_dataclass():
    r = BossDBResult(
        claim_id="TEST-1",
        status=APPROXIMATE,
        expected="~100",
        observed=95,
        note="test",
    )
    assert r.claim_id == "TEST-1"
    assert r.source == "bossdb"


def test_status_constants():
    assert CONFIRMED == "CONFIRMED"
    assert APPROXIMATE == "APPROXIMATE"
    assert DISCREPANCY == "DISCREPANCY"
    assert NOT_VALIDATABLE == "NOT_VALIDATABLE"


def test_bossdb_available_returns_bool():
    result = bossdb_available(timeout=5)
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Network tests — skipped when BossDB is unreachable
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def bossdb_live():
    """Skip tests if BossDB is not reachable or deps are missing."""
    try:
        import requests  # noqa: F401
        import blosc  # noqa: F401
    except ImportError:
        pytest.skip("requests/blosc not installed")
    if not bossdb_available(timeout=10):
        pytest.skip("BossDB not reachable")


def test_validate_bossdb_returns_results(bossdb_live):
    results = validate_bossdb()
    assert len(results) >= 3  # CELL-1, SYN-1, CELL-2, CELL-3


def test_validate_bossdb_claim_ids(bossdb_live):
    results = validate_bossdb()
    ids = {r.claim_id for r in results}
    assert "CELL-1" in ids
    assert "SYN-1" in ids
    assert "CELL-2" in ids
    assert "CELL-3" in ids


def test_validate_bossdb_all_have_valid_status(bossdb_live):
    valid_statuses = {CONFIRMED, APPROXIMATE, DISCREPANCY, NOT_VALIDATABLE}
    results = validate_bossdb()
    for r in results:
        assert r.status in valid_statuses, f"{r.claim_id} has invalid status: {r.status}"


def test_cell1_neuron_count_approximate(bossdb_live):
    """CELL-1: neuron IDs in 3cylneuron_v1 should be close to paper's ~1600."""
    results = validate_bossdb()
    r = {res.claim_id: res for res in results}["CELL-1"]
    assert r.status in (APPROXIMATE, CONFIRMED), (
        f"Expected APPROXIMATE or CONFIRMED for CELL-1, got {r.status}: {r.observed}"
    )


def test_validate_all_with_bossdb(bossdb_live):
    """validate_all(include_bossdb=True) should replace some NOT_VALIDATABLE results."""
    from kasthuri2015.validate import NOT_VALIDATABLE as VNV
    from kasthuri2015.validate import validate_all

    without = validate_all(include_bossdb=False)
    with_bossdb = validate_all(include_bossdb=True)

    # Total count stays the same
    assert len(without) == len(with_bossdb)

    # Some NOT_VALIDATABLE entries should be replaced
    nv_without = sum(1 for r in without if r.status == VNV)
    nv_with = sum(1 for r in with_bossdb if r.status == VNV)
    assert nv_with < nv_without, "BossDB integration should reduce NOT_VALIDATABLE count"
