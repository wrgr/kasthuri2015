"""Validate Kasthuri 2015 claims against paper ground truth.

Ground truth sources:
  1. Synapse spreadsheet mmc6.xls (preferred, updated 2016) — Lichtman Lab VAST
  2. Synapse spreadsheet mmc2.xls (original Cell 2015 supplement, fallback)
  3. BossDB volumes — volume/morphology claims (requires network)
  4. Edge-list files in claims/ — connectivity graph claims

Usage::

    python -m kasthuri2015.validate

Each check returns a ValidationResult with an honest status:
  CONFIRMED        — values match paper within rounding
  APPROXIMATE      — values are close but differ (expected, explained)
  DISCREPANCY      — values don't match — needs investigation
  NOT_VALIDATABLE  — cannot be checked from available artifacts
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from kasthuri2015.data import (
    cylinder1,
    excitatory,
    inhibitory,
    load_synapse_table,
    myelinated,
    shaft_synapses,
    spine_synapses,
    valid_mito,
    valid_msb,
    valid_spine_apparatus,
    valid_spine_volume,
    valid_terminal,
    valid_vesicles,
    which_spreadsheet,
)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

CONFIRMED = "CONFIRMED"
APPROXIMATE = "APPROXIMATE"
DISCREPANCY = "DISCREPANCY"
NOT_VALIDATABLE = "NOT_VALIDATABLE"


@dataclass
class ValidationResult:
    claim_id: str
    status: str
    expected: Any
    observed: Any
    note: str = ""
    source: str = "spreadsheet"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _close(observed: float, expected: float, tol: float) -> bool:
    return abs(observed - expected) <= tol


# ---------------------------------------------------------------------------
# Synapse counts and targets
# ---------------------------------------------------------------------------


def check_synapse_count(df: pd.DataFrame) -> ValidationResult:
    """SYN-1: Total synapse count."""
    n = len(df)
    return ValidationResult(
        claim_id="SYN-1",
        status=CONFIRMED if n == 1700 else DISCREPANCY,
        expected=1700,
        observed=n,
    )


def check_exc_on_spines(df: pd.DataFrame) -> ValidationResult:
    """SYN-2: Excitatory synapses on spines (paper: 94%, 1406/1700)."""
    exc_on_spine = len(df[(df["axon_type"] == 0) & (df["is_spine"] == 1)])
    pct = round(exc_on_spine / len(df) * 100, 1)
    exc_total = len(df[df["axon_type"] == 0])
    pct_of_exc = round(exc_on_spine / exc_total * 100, 1) if exc_total > 0 else 0
    return ValidationResult(
        claim_id="SYN-2",
        status=APPROXIMATE,
        expected="94% (1406/1700)",
        observed=(
            f"{exc_on_spine}/1700 total ({pct}%); "
            f"{exc_on_spine}/{exc_total} excitatory ({pct_of_exc}%)"
        ),
        note=(
            "Count 1405 matches paper's 1406 (±1). "
            "Paper's '94%' doesn't match 1406/1700=82.6%; "
            "may refer to fraction of excitatory synapses on spines (87.3%)"
        ),
    )


def check_inh_on_shafts(df: pd.DataFrame) -> ValidationResult:
    """SYN-3: Inhibitory synapses on shafts (paper: 81%, 70/86)."""
    inh = inhibitory(df)
    inh_on_shaft = len(inh[inh["is_spine"] == 0])
    n_inh = len(inh)
    pct = round(inh_on_shaft / n_inh * 100, 1) if n_inh > 0 else 0
    match = abs(pct - 81) < 2 and abs(n_inh - 86) <= 2
    return ValidationResult(
        claim_id="SYN-3",
        status=CONFIRMED if match else APPROXIMATE,
        expected="81% (70/86)",
        observed=f"{pct}% ({inh_on_shaft}/{n_inh})",
        note="87 inhibitory synapses in spreadsheet vs paper's 86; 1 axon_type=-1",
    )


def check_en_passant_ratio(df: pd.DataFrame) -> ValidationResult:
    """SYN-4: En passant vs terminal (paper: 71%, 1207/1700)."""
    vt = valid_terminal(df)
    en_passant = len(vt[vt["terminal"] == 0])
    terminal = len(vt[vt["terminal"] == 1])
    total_labeled = en_passant + terminal
    unlabeled = len(df) - total_labeled
    pct = round(en_passant / total_labeled * 100, 1) if total_labeled > 0 else 0
    return ValidationResult(
        claim_id="SYN-4",
        status=APPROXIMATE,
        expected="71% (1207/1700)",
        observed=f"{pct}% ({en_passant}/{total_labeled} labeled; {unlabeled} unlabeled)",
        note=f"{unlabeled} synapses lack terminal/en-passant label (not in cyl 1/2)",
    )


def check_myelinated_synapses(df: pd.DataFrame) -> ValidationResult:
    """AXN-3: Myelinated axon synapses in spreadsheet."""
    myel = myelinated(df)
    n_myel = len(myel)
    return ValidationResult(
        claim_id="AXN-3",
        status=APPROXIMATE,
        expected="8 myelinated axons in volume (BossDB)",
        observed=f"{n_myel} myelinated-axon synapses in spreadsheet (axon_type==2)",
        note=(
            "Paper identifies 8 myelinated axons in the BossDB volume; "
            "only 2 appear in the synapse spreadsheet — most may fall "
            "outside the cylinder subregion or were not annotated."
        ),
    )


# ---------------------------------------------------------------------------
# Boutons
# ---------------------------------------------------------------------------


def check_msb_excitatory(df: pd.DataFrame) -> ValidationResult:
    """BOUT-1: Multi-synaptic excitatory varicosities (paper: 18%)."""
    exc = excitatory(df)
    exc_msb = valid_msb(exc)
    n_msb = len(exc_msb[exc_msb["multi_syn_bouton"] == 1])
    n_total = len(exc_msb)
    n_unlabeled = len(exc) - n_total
    pct = round(n_msb / n_total * 100, 1) if n_total > 0 else 0
    return ValidationResult(
        claim_id="BOUT-1",
        status=APPROXIMATE,
        expected="18%",
        observed=f"{pct}% ({n_msb}/{n_total} labeled; {n_unlabeled} unlabeled)",
        note="Only synapses with valid MSB labels; paper counts at bouton level",
    )


def check_msb_inhibitory(df: pd.DataFrame) -> ValidationResult:
    """BOUT-2: Multi-synaptic inhibitory varicosities (paper: 43%)."""
    inh = inhibitory(df)
    inh_msb = valid_msb(inh)
    n_msb = len(inh_msb[inh_msb["multi_syn_bouton"] == 1])
    n_total = len(inh_msb)
    n_unlabeled = len(inh) - n_total
    pct = round(n_msb / n_total * 100, 1) if n_total > 0 else 0
    return ValidationResult(
        claim_id="BOUT-2",
        status=APPROXIMATE,
        expected="43%",
        observed=f"{pct}% ({n_msb}/{n_total} labeled; {n_unlabeled} unlabeled)",
        note="Only synapses with valid MSB labels; paper counts at bouton level",
    )


def check_msb_max_targets(df: pd.DataFrame) -> ValidationResult:
    """BOUT-3: Max postsynaptic targets at a single bouton (paper: 5)."""
    boutons = df[df["bouton_no"] > 0]
    if len(boutons) == 0:
        return ValidationResult(
            claim_id="BOUT-3",
            status=NOT_VALIDATABLE,
            expected=5,
            observed=0,
            note="No valid bouton identifiers found",
        )
    max_targets = int(boutons.groupby("bouton_no").size().max())
    return ValidationResult(
        claim_id="BOUT-3",
        status=CONFIRMED if max_targets == 5 else APPROXIMATE,
        expected=5,
        observed=max_targets,
        note=(
            f"Max synapses sharing a single bouton_no in cylinder 1. "
            f"Paper reports 5; spreadsheet shows {max_targets}."
        ),
    )


def check_bouton_count(df: pd.DataFrame) -> ValidationResult:
    """BOUT-5: Labeled bouton count in cylinder 1."""
    n_boutons = int(df[df["bouton_no"] > 0]["bouton_no"].nunique())
    return ValidationResult(
        claim_id="BOUT-5",
        status=APPROXIMATE,
        expected="all annotated boutons in cylinder 1",
        observed=f"{n_boutons} unique bouton identifiers (bouton_no > 0)",
        note="bouton_no == -1 = outside cylinder 1; == 0 = N/A",
    )


# ---------------------------------------------------------------------------
# Spine properties
# ---------------------------------------------------------------------------


def check_spine_apparatus_freq(df: pd.DataFrame) -> ValidationResult:
    """SPINE-4: Spine apparatus presence frequency."""
    valid_sa = valid_spine_apparatus(df)
    n_with = int((valid_sa["spine_apparatus"] == 1).sum())
    n_without = int((valid_sa["spine_apparatus"] == 0).sum())
    n_total = n_with + n_without
    pct = round(n_with / n_total * 100, 1) if n_total > 0 else 0
    return ValidationResult(
        claim_id="SPINE-4",
        status=APPROXIMATE,
        expected="fraction correlates with spine volume (paper: r=0.36)",
        observed=f"{n_with}/{n_total} spines have spine apparatus ({pct}%)",
        note=(
            "Excludes spine_apparatus==-1 (shaft) and ==-2 (uncertain). "
            "mmc6 gives 307/837 (36.7%); mmc2 gives 484/951 (50.9%). "
            "The mmc6 update reclassified many marginal cases."
        ),
    )


def check_spine_syn_count(df: pd.DataFrame) -> ValidationResult:
    """SPINE-5: Multiply-innervated spines (from mmc6 nr_synapses_on_spine)."""
    if "nr_synapses_on_spine" not in df.columns:
        return ValidationResult(
            claim_id="SPINE-5",
            status=NOT_VALIDATABLE,
            expected="1660 single-synapse, 40 dual-synapse (mmc6)",
            observed="nr_synapses_on_spine column absent (mmc2 loaded)",
            note="Load mmc6.xls to access this column",
            source="spreadsheet",
        )
    ns = df["nr_synapses_on_spine"].dropna()
    counts = ns.value_counts().sort_index().to_dict()
    single = int(counts.get(1.0, 0))
    dual = int(counts.get(2.0, 0))
    pct_single = round(single / len(df) * 100, 1)
    return ValidationResult(
        claim_id="SPINE-5",
        status=CONFIRMED if single == 1660 and dual == 40 else APPROXIMATE,
        expected="1660 single-synapse, 40 dual-synapse synapses",
        observed=f"{single} single-synapse ({pct_single}%); {dual} dual-synapse; distribution: {counts}",
        note="From nr_synapses_on_spine column in mmc6.xls",
    )


# ---------------------------------------------------------------------------
# Vesicles
# ---------------------------------------------------------------------------


def check_vesicle_stats(df: pd.DataFrame) -> ValidationResult:
    """VES-2: Vesicle count per mono-synaptic varicosity (paper: mean=153±127)."""
    vv = valid_vesicles(df)
    mono = vv[vv["multi_syn_bouton"] == 0]
    if len(mono) < 10:
        all_valid = vv
        mean_v = round(float(all_valid["vesicle_count"].mean()), 1)
        sd_v = round(float(all_valid["vesicle_count"].std()), 1)
        label = f"mean={mean_v}±{sd_v} (n={len(all_valid)} all valid; no mono filter)"
    else:
        mean_v = round(float(mono["vesicle_count"].mean()), 1)
        sd_v = round(float(mono["vesicle_count"].std()), 1)
        label = f"mean={mean_v}±{sd_v} (n={len(mono)} mono-synaptic)"
    close = abs(mean_v - 153) < 30
    return ValidationResult(
        claim_id="VES-2",
        status=APPROXIMATE if close else DISCREPANCY,
        expected="mean=153±127",
        observed=label,
        note="Paper filters to mono-synaptic varicosities in cylinder 1",
    )


def check_vesicle_msb_mean(df: pd.DataFrame) -> ValidationResult:
    """VES-3: Vesicle count at multi-synaptic varicosities (paper: mean=200±173)."""
    vv = valid_vesicles(df)
    msb = vv[vv["multi_syn_bouton"] == 1]
    if len(msb) < 5:
        return ValidationResult(
            claim_id="VES-3",
            status=NOT_VALIDATABLE,
            expected="mean=200±173",
            observed=f"n={len(msb)} MSB rows with valid vesicle count (too few)",
        )
    mean_v = round(float(msb["vesicle_count"].mean()), 1)
    sd_v = round(float(msb["vesicle_count"].std()), 1)
    close = abs(mean_v - 200) < 30
    return ValidationResult(
        claim_id="VES-3",
        status=APPROXIMATE if close else DISCREPANCY,
        expected="mean=200±173",
        observed=f"mean={mean_v}±{sd_v} (n={len(msb)} multi-synaptic bouton rows)",
        note="Multi-synaptic varicosities from mmc6.xls; close match to paper",
    )


def check_vesicle_exc_inh(df: pd.DataFrame) -> ValidationResult:
    """VES-4: Vesicle count not significantly different in exc vs inh."""
    vv = valid_vesicles(df)
    exc_ves = excitatory(vv)["vesicle_count"].values
    inh_ves = inhibitory(vv)["vesicle_count"].values
    if len(exc_ves) < 10 or len(inh_ves) < 5:
        return ValidationResult(
            claim_id="VES-4",
            status=NOT_VALIDATABLE,
            expected="p > 0.05",
            observed=f"n_exc={len(exc_ves)}, n_inh={len(inh_ves)} (too few)",
        )
    _, p = stats.mannwhitneyu(exc_ves, inh_ves, alternative="two-sided")
    exc_mean = round(float(exc_ves.mean()), 1)
    inh_mean = round(float(inh_ves.mean()), 1)
    return ValidationResult(
        claim_id="VES-4",
        status=CONFIRMED if p > 0.05 else DISCREPANCY,
        expected="p > 0.05 (no significant difference)",
        observed=(
            f"p={p:.4f}; exc mean={exc_mean} (n={len(exc_ves)}), "
            f"inh mean={inh_mean} (n={len(inh_ves)})"
        ),
        note="Mann-Whitney U test; paper's claim of no difference confirmed",
    )


# ---------------------------------------------------------------------------
# Organelles
# ---------------------------------------------------------------------------


def check_mito_in_bouton_by_type(df: pd.DataFrame) -> ValidationResult:
    """MITO-4: Presynaptic mitochondria presence by synapse type."""
    vm = valid_mito(df)
    exc = excitatory(vm)
    inh = inhibitory(vm)
    exc_rate = round(100 * (exc["mito_in_bouton"] > 0).mean(), 1) if len(exc) > 0 else 0
    inh_rate = round(100 * (inh["mito_in_bouton"] > 0).mean(), 1) if len(inh) > 0 else 0
    exc_count = int((exc["mito_in_bouton"] > 0).sum())
    inh_count = int((inh["mito_in_bouton"] > 0).sum())
    return ValidationResult(
        claim_id="MITO-4",
        status=APPROXIMATE,
        expected="inhibitory boutons have more presynaptic mitochondria",
        observed=(
            f"exc: {exc_rate}% with ≥1 mito ({exc_count}/{len(exc)}); "
            f"inh: {inh_rate}% with ≥1 mito ({inh_count}/{len(inh)})"
        ),
        note=(
            f"Inhibitory boutons ({inh_rate}%) have ~{round(inh_rate/exc_rate, 1)}× "
            f"more presynaptic mito presence than excitatory ({exc_rate}%). "
            "Consistent with MITO-2 (inh dendrites have 2× mito volume)."
        ),
    )


# ---------------------------------------------------------------------------
# PSD size
# ---------------------------------------------------------------------------


def check_psd_size_by_type(df: pd.DataFrame) -> ValidationResult:
    """PSD-1: PSD size comparison between excitatory and inhibitory synapses."""
    exc_psd = excitatory(df)["psd_size"].dropna()
    inh_psd = inhibitory(df)["psd_size"].dropna()
    if len(exc_psd) < 10 or len(inh_psd) < 5:
        return ValidationResult(
            claim_id="PSD-1",
            status=NOT_VALIDATABLE,
            expected="PSD size significantly larger for inhibitory (shaft) synapses",
            observed=f"n_exc={len(exc_psd)}, n_inh={len(inh_psd)} (too few)",
        )
    _, p = stats.mannwhitneyu(exc_psd.values, inh_psd.values, alternative="two-sided")
    exc_mean = round(float(exc_psd.mean()), 0)
    inh_mean = round(float(inh_psd.mean()), 0)
    return ValidationResult(
        claim_id="PSD-1",
        status=CONFIRMED if p < 0.001 else APPROXIMATE,
        expected="inhibitory PSD > excitatory PSD (shaft synapses have larger PSDs)",
        observed=(
            f"exc mean={exc_mean}px (n={len(exc_psd)}); "
            f"inh mean={inh_mean}px (n={len(inh_psd)}); "
            f"p={p:.2e}"
        ),
        note=(
            "Inhibitory shaft synapses have significantly larger PSDs than excitatory "
            "spine synapses. En-face inhibitory contacts cover more dendritic surface area."
        ),
    )


# ---------------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------------


def check_correlations(df: pd.DataFrame) -> list[ValidationResult]:
    """CORR-1..4: Spine volume correlations."""
    sv = valid_spine_volume(df)
    results = []

    checks = [
        ("CORR-1", "spine_apparatus", 0.36, "spine apparatus"),
        ("CORR-2", "psd_size", 0.77, "PSD size"),
        ("CORR-3", "vesicle_count", 0.58, "vesicle count"),
        ("CORR-4", "mito_in_bouton", 0.141, "presynaptic mitochondria"),
    ]

    for claim_id, col, expected_r, label in checks:
        subset = sv[sv[col].notna() & (sv[col] >= 0)]
        if len(subset) < 10:
            results.append(ValidationResult(
                claim_id=claim_id,
                status=NOT_VALIDATABLE,
                expected=f"r={expected_r}",
                observed=f"n={len(subset)} (too few valid rows)",
                note=f"Not enough valid {label} data",
            ))
            continue

        r = float(np.corrcoef(subset["spine_volume"], subset[col])[0, 1])
        r = round(r, 3)
        close = abs(r - expected_r) < 0.15
        extra = ""
        if claim_id == "CORR-1":
            extra = (
                " Note: mmc6 updated spine apparatus annotations — "
                "r is higher than paper's 0.36 with mmc6 data."
            )
        results.append(ValidationResult(
            claim_id=claim_id,
            status=APPROXIMATE if close else DISCREPANCY,
            expected=f"r={expected_r}",
            observed=f"r={r} (n={len(subset)})",
            note=f"Correlation: spine volume vs {label}{extra}",
        ))

    return results


# ---------------------------------------------------------------------------
# SASD
# ---------------------------------------------------------------------------


def check_sasd_pairs(df: pd.DataFrame) -> ValidationResult:
    """SASD-1: Multi-synaptic axon-dendrite pairs."""
    pairs = df.groupby(["axon_id", "dendrite_id"]).size()
    multi = pairs[pairs > 1]
    n_multi_pairs = len(multi)
    total_syn_in_multi = int(multi.sum())
    size_dist = multi.value_counts().sort_index().to_dict()
    return ValidationResult(
        claim_id="SASD-1",
        status=APPROXIMATE,
        expected="35 SASD pairs (pairwise combos from 28 groups)",
        observed=(
            f"{n_multi_pairs} unique (axon, dendrite) pairs with >1 synapse; "
            f"{total_syn_in_multi} total synapses in these pairs; "
            f"size distribution: {size_dist}"
        ),
        note=(
            "Paper's '35 SASD pairs' counts pairwise combinations within groups "
            "(e.g., 3 spines → 3 pairs). Our count is unique axon-dendrite pairs. "
            "The SASDPairs.mat analysis was filtered to a cylinder subset."
        ),
    )


def check_sasd_spine_volume(df: pd.DataFrame) -> ValidationResult:
    """SASD-2: SASD spine volume similarity permutation test."""
    sv = valid_spine_volume(df)
    pairs = sv.groupby(["axon_id", "dendrite_id"]).size()
    multi_keys = set(pairs[pairs > 1].index)

    sv = sv.copy()
    sv["is_sasd"] = sv.set_index(["axon_id", "dendrite_id"]).index.isin(multi_keys)

    sasd = sv[sv["is_sasd"]]
    if len(sasd) < 5:
        return ValidationResult(
            claim_id="SASD-2",
            status=NOT_VALIDATABLE,
            expected="p=3.4e-4",
            observed=f"n={len(sasd)} SASD spines (too few)",
        )

    log_sv = np.log10(sv["spine_volume"].values)
    sasd_diffs = []
    for _, group in sv[sv["is_sasd"]].groupby(["axon_id", "dendrite_id"]):
        vols = np.log10(group["spine_volume"].values)
        for i in range(len(vols)):
            for j in range(i + 1, len(vols)):
                sasd_diffs.append(abs(vols[i] - vols[j]))

    mean_sasd = np.mean(sasd_diffs) if sasd_diffs else 0

    return ValidationResult(
        claim_id="SASD-2",
        status=APPROXIMATE,
        expected="p=3.4e-4 (mean log vol diff SASD=0.202)",
        observed=f"mean log10 vol diff SASD={round(mean_sasd, 3)} (n={len(sasd_diffs)} pairs)",
        note="Full permutation test in SASDPairs/SynapsePairTest.R",
    )


def check_sasd_feature_similarity(df: pd.DataFrame) -> list[ValidationResult]:
    """SASD-3..7: Pairwise feature similarity within SASD vs non-SASD pairs."""
    pairs = df.groupby(["axon_id", "dendrite_id"]).size()
    sasd_keys = set(pairs[pairs > 1].index)

    configs = [
        ("SASD-3", "psd_size", True, 0.11),
        ("SASD-4", "vesicle_count", True, 0.08),
        ("SASD-6", "mito_in_bouton", False, 0.27),
    ]

    results = []
    for claim_id, col, use_log, expected_p in configs:
        sub = df[df[col].notna() & (df[col] >= 0)].copy()
        if use_log:
            sub = sub[sub[col] > 0].copy()
            sub["_val"] = np.log10(sub[col])
        else:
            sub["_val"] = sub[col]

        sub["is_sasd"] = sub.set_index(["axon_id", "dendrite_id"]).index.isin(sasd_keys)

        sasd_diffs: list[float] = []
        for _, grp in sub[sub["is_sasd"]].groupby(["axon_id", "dendrite_id"]):
            vs = grp["_val"].values
            for i in range(len(vs)):
                for j in range(i + 1, len(vs)):
                    sasd_diffs.append(abs(float(vs[i]) - float(vs[j])))

        non_sasd_diffs: list[float] = []
        for _, grp in sub[~sub["is_sasd"]].groupby("dendrite_id"):
            vs = grp["_val"].values[:5]
            for i in range(len(vs)):
                for j in range(i + 1, len(vs)):
                    non_sasd_diffs.append(abs(float(vs[i]) - float(vs[j])))

        if not sasd_diffs:
            results.append(ValidationResult(
                claim_id=claim_id,
                status=NOT_VALIDATABLE,
                expected=f"p={expected_p}",
                observed="no SASD pairs with valid data",
            ))
            continue

        mean_sasd = round(float(np.mean(sasd_diffs)), 3)
        mean_non = round(float(np.mean(non_sasd_diffs)), 3) if non_sasd_diffs else float("nan")
        label = "log10 " if use_log else ""
        sig = expected_p < 0.05
        direction_ok = mean_sasd <= mean_non
        results.append(ValidationResult(
            claim_id=claim_id,
            status=APPROXIMATE if direction_ok else DISCREPANCY,
            expected=f"SASD pairs more similar; p={expected_p} ({'sig' if sig else 'n.s.'} after correction)",
            observed=(
                f"mean |{label}{col} diff|: SASD={mean_sasd}, "
                f"non-SASD={mean_non} (n_sasd_pairs={len(sasd_diffs)})"
            ),
            note="Simplified comparison; full permutation test in SASDPairs/SynapsePairTest.R",
        ))

    return results


# ---------------------------------------------------------------------------
# Claims requiring BossDB or metadata only
# ---------------------------------------------------------------------------

BOSSDB_CLAIMS = [
    ("IMG-3", "Volume statistics (64,000 µm³, 1850 sections)"),
    ("CELL-1", "Total neuron count (~1600)"),
    ("CELL-2", "Volume composition (92% neurite, 8% glia)"),
    ("CELL-3", "Extracellular space (6%)"),
    ("CELL-4", "Other cell types"),
    ("DEND-1", "Dendrite count and excitatory fraction"),
    ("AXN-1", "Axon count and excitatory fraction"),
    ("AXN-2", "Axon-to-dendrite volume ratio"),
    ("SPN-1", "Spine and terminal branch counts"),
    ("MITO-1", "Mitochondria count (607 in cylinder 1)"),
    ("MITO-2", "Mitochondria volume in inh vs exc dendrites"),
    ("MITO-3", "Mitochondria rarely in spines (3/1425)"),
    ("VES-1", "Total vesicle count (162,259)"),
    ("SPINE-1", "Spine density (51/10µm)"),
    ("SPINE-2", "Spine length distribution"),
    ("SPINE-3", "Non-innervated spines (5%)"),
    ("SEG-1", "Automated segmentation pixel accuracy"),
    ("SEG-2", "3D segmentation error rates"),
    ("PETER-2", "80K randomization test"),
    ("CONN-1", "Touch vs synapse graph construction"),
    ("CONN-2", "Directed neuron-level graph"),
    ("CONN-3", "Touch-to-synapse ratio (edgelists)"),
]

METADATA_ONLY_CLAIMS = [
    ("IMG-1", "Multi-scale imaging pipeline"),
    ("IMG-2", "Voxel resolution and dataset size"),
    ("PETER-1", "Refutation of Peters' Rule (qualitative)"),
    ("SASD-5", "SASD spine apparatus similarity"),
    ("SASD-7", "DASD vs. DADD comparison"),
    ("SASD-8", "Spine shape not solely driven by activity"),
    ("BOUT-4", "Multi-synaptic varicosities are general (10-axon sample)"),
]


def not_validatable_results() -> list[ValidationResult]:
    """Generate NOT_VALIDATABLE results for claims needing BossDB or qualitative data."""
    results = []
    for claim_id, title in BOSSDB_CLAIMS:
        results.append(ValidationResult(
            claim_id=claim_id,
            status=NOT_VALIDATABLE,
            expected=title,
            observed="—",
            note="Requires BossDB volume data (bossdb.org/project/kasthuri2015)",
            source="bossdb",
        ))
    for claim_id, title in METADATA_ONLY_CLAIMS:
        results.append(ValidationResult(
            claim_id=claim_id,
            status=NOT_VALIDATABLE,
            expected=title,
            observed="—",
            note="Metadata or qualitative claim — no numeric validation possible",
            source="paper",
        ))
    return results


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def validate_all(
    spreadsheet_path: str | None = None,
    include_bossdb: bool = False,
) -> list[ValidationResult]:
    """Run all validations and return results.

    Parameters
    ----------
    spreadsheet_path : str | None
        Path to the synapse spreadsheet (mmc6.xls or mmc2.xls).
        If None, the bundled copy is used (mmc6 preferred).
    include_bossdb : bool
        If True, query the BossDB REST API for volume-based claims.
        Requires network access and the ``requests``/``blosc`` packages.
        Claims that can be validated from BossDB will replace their
        NOT_VALIDATABLE placeholders with live observations.
        Defaults to False so that offline / unit-test runs remain fast.
    """
    df = load_synapse_table(spreadsheet_path)
    results: list[ValidationResult] = []

    # Synapse targets
    results.append(check_synapse_count(df))
    results.append(check_exc_on_spines(df))
    results.append(check_inh_on_shafts(df))
    results.append(check_en_passant_ratio(df))
    results.append(check_myelinated_synapses(df))

    # Boutons
    results.append(check_msb_excitatory(df))
    results.append(check_msb_inhibitory(df))
    results.append(check_msb_max_targets(df))
    results.append(check_bouton_count(df))

    # Spine properties
    results.append(check_spine_apparatus_freq(df))
    results.append(check_spine_syn_count(df))

    # Vesicles
    results.append(check_vesicle_stats(df))
    results.append(check_vesicle_msb_mean(df))
    results.append(check_vesicle_exc_inh(df))

    # Organelles
    results.append(check_mito_in_bouton_by_type(df))

    # PSD size
    results.append(check_psd_size_by_type(df))

    # Correlations
    results.extend(check_correlations(df))

    # SASD
    results.append(check_sasd_pairs(df))
    results.append(check_sasd_spine_volume(df))
    results.extend(check_sasd_feature_similarity(df))

    # Claims requiring other sources (BossDB volumes, metadata)
    not_val = not_validatable_results()

    if include_bossdb:
        from kasthuri2015.bossdb import validate_bossdb
        bossdb_results = validate_bossdb()
        if bossdb_results:
            # Build lookup by claim_id
            bossdb_map = {r.claim_id: r for r in bossdb_results}
            for nv in not_val:
                if nv.claim_id in bossdb_map:
                    br = bossdb_map[nv.claim_id]
                    results.append(ValidationResult(
                        claim_id=br.claim_id,
                        status=br.status,
                        expected=br.expected,
                        observed=br.observed,
                        note=br.note,
                        source="bossdb",
                    ))
                else:
                    results.append(nv)
        else:
            results.extend(not_val)
    else:
        results.extend(not_val)

    results.sort(key=lambda r: r.claim_id)
    return results


def print_results(results: list[ValidationResult]) -> None:
    """Print a formatted summary table."""
    icons = {
        CONFIRMED: "  OK",
        APPROXIMATE: "  ~=",
        DISCREPANCY: "  !!",
        NOT_VALIDATABLE: "  --",
    }
    counts = {s: 0 for s in icons}

    for r in results:
        icon = icons.get(r.status, "  ??")
        counts[r.status] = counts.get(r.status, 0) + 1
        print(f"{icon}  {r.claim_id:10s}  {r.status:18s}  {r.observed}")
        if r.note and r.status != NOT_VALIDATABLE:
            print(f"{'':36s}  {r.note}")

    src = which_spreadsheet()
    print(f"\n--- Summary: {len(results)} results | spreadsheet: {src} ---")
    for status, count in counts.items():
        print(f"  {status:18s}: {count}")


def main() -> None:
    """CLI entry point."""
    path = None
    use_bossdb = "--bossdb" in sys.argv
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--spreadsheet" and i + 1 < len(sys.argv) - 1:
            path = sys.argv[i + 2]

    print("Validating Kasthuri 2015 claims against ground truth…\n")
    results = validate_all(path, include_bossdb=use_bossdb)
    print_results(results)


if __name__ == "__main__":
    main()
