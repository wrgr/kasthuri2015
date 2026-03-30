"""Tests for kasthuri2015 claims enumeration."""

from kasthuri2015 import (
    CATEGORIES,
    CLAIMS,
    Claim,
    claims_by_category,
    get_claim,
    list_categories,
    list_claims,
    summary_table,
)


def test_claim_count():
    assert len(CLAIMS) == 47


def test_list_claims_returns_all():
    assert len(list_claims()) == len(CLAIMS)


def test_get_claim_by_id():
    c = get_claim("SYN-1")
    assert c.title == "Total synapse count and density"
    assert c.reported_values["synapse_count"] == 1_700


def test_get_claim_unknown_raises():
    try:
        get_claim("FAKE-99")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_claim_is_frozen():
    c = get_claim("IMG-1")
    try:
        c.title = "changed"  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass


def test_each_claim_has_title_and_category():
    for claim in list_claims():
        assert claim.title, f"{claim.id} missing title"
        assert claim.category, f"{claim.id} missing category"
        assert claim.category in CATEGORIES, f"{claim.id} has unknown category"


def test_each_claim_has_paper_quote():
    for claim in list_claims():
        assert claim.paper_quote, f"{claim.id} missing paper_quote"


def test_filter_by_category():
    synapses = list_claims(category="synapses")
    assert len(synapses) >= 1
    assert all(c.category == "synapses" for c in synapses)


def test_list_categories():
    cats = list_categories()
    assert len(cats) == 12
    assert "synapses" in cats
    assert "boutons" in cats
    assert "correlations" in cats
    assert "segmentation" in cats


def test_claims_by_category_covers_all():
    grouped = claims_by_category()
    total = sum(len(v) for v in grouped.values())
    assert total == len(CLAIMS)


def test_summary_table():
    table = summary_table()
    assert "SYN-1" in table
    assert "PETER-1" in table
    lines = table.strip().split("\n")
    # header + separator + one line per claim
    assert len(lines) == 2 + len(CLAIMS)


def test_unique_ids():
    ids = [c.id for c in list_claims()]
    assert len(ids) == len(set(ids))


def test_peters_rule_claims():
    peter = list_claims(category="peters_rule")
    assert len(peter) == 2


def test_sasd_claims():
    sasd = list_claims(category="sasd")
    assert len(sasd) == 8


def test_new_categories_populated():
    assert len(list_claims(category="boutons")) == 4
    assert len(list_claims(category="spine_properties")) == 3
    assert len(list_claims(category="correlations")) == 4
    assert len(list_claims(category="segmentation")) == 2
    assert len(list_claims(category="synapses")) == 4
    assert len(list_claims(category="organelles")) >= 6
