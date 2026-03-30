"""Tests for kasthuri2015 claims enumeration."""

from kasthuri2015 import CLAIMS, Claim, get_claim, list_claims
from kasthuri2015.claims import ClaimID


def test_all_ten_claims_registered():
    assert len(CLAIMS) == 10


def test_list_claims_sorted():
    claims = list_claims()
    assert [c.id for c in claims] == list(range(10))


def test_get_claim_by_int():
    c = get_claim(3)
    assert c.id == ClaimID.SYNAPSES
    assert c.reported_values["synapse_count"] == 1_700


def test_get_claim_by_enum():
    c = get_claim(ClaimID.VESICLES)
    assert c.reported_values["vesicle_count"] == 162_259


def test_claim_is_frozen():
    c = get_claim(0)
    try:
        c.title = "changed"  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass


def test_each_claim_has_title_and_notebook():
    for claim in list_claims():
        assert claim.title
        assert claim.notebook
