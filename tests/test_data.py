"""Tests for ground truth data loading."""

from kasthuri2015.data import (
    excitatory,
    inhibitory,
    load_synapse_table,
    valid_spine_volume,
    valid_vesicles,
)


def test_load_synapse_table():
    df = load_synapse_table()
    assert len(df) == 1700
    assert "axon_type" in df.columns
    assert "is_spine" in df.columns


def test_column_count():
    df = load_synapse_table()
    assert len(df.columns) == 24  # 25 minus the empty trailing column


def test_axon_type_distribution():
    df = load_synapse_table()
    counts = df["axon_type"].value_counts()
    assert counts[0] == 1610   # excitatory
    assert counts[1] == 87     # inhibitory


def test_spine_vs_shaft():
    df = load_synapse_table()
    assert (df["is_spine"] == 1).sum() == 1424
    assert (df["is_spine"] == 0).sum() == 275


def test_excitatory_filter():
    df = load_synapse_table()
    exc = excitatory(df)
    assert len(exc) == 1610


def test_inhibitory_filter():
    df = load_synapse_table()
    inh = inhibitory(df)
    assert len(inh) == 87


def test_valid_vesicles():
    df = load_synapse_table()
    vv = valid_vesicles(df)
    assert len(vv) > 700
    assert len(vv) < 900
    assert (vv["vesicle_count"] > 0).all()


def test_valid_spine_volume():
    df = load_synapse_table()
    sv = valid_spine_volume(df)
    assert len(sv) > 1100
    assert (sv["spine_volume"] > 0).all()
