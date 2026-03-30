"""Enumeration of reproducible claims from Kasthuri et al. 2015.

Reference
---------
Kasthuri, N., Hayworth, K.J., Berger, D.R., Schalek, R.L., Conchello, J.A.,
Knowles-Barley, S., Lee, D., Vazquez-Reina, A., Kaynig, V., Jones, T.R.,
Roberts, M., Morgan, J.L., Tapia, J.C., Seung, H.S., Roncal, W.G.,
Vogelstein, J.T., Burns, R., Sussman, D.L., Priebe, C.E., Pfister, H.,
& Lichtman, J.W. (2015). Saturated Reconstruction of a Volume of Neocortex.
Cell, 162(3), 648-661. https://doi.org/10.1016/j.cell.2015.06.054
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Categories — map to paper sections / figures
# ---------------------------------------------------------------------------

CATEGORY_IMAGING = "imaging"
CATEGORY_CELLULAR_INVENTORY = "cellular_inventory"
CATEGORY_MORPHOLOGY = "morphology"
CATEGORY_SYNAPSES = "synapses"
CATEGORY_ORGANELLES = "organelles"
CATEGORY_CONNECTIVITY = "connectivity"
CATEGORY_PETERS_RULE = "peters_rule"
CATEGORY_SASD = "sasd"

CATEGORIES = {
    CATEGORY_IMAGING: "Imaging & data acquisition (Figures 1-2)",
    CATEGORY_CELLULAR_INVENTORY: "Cellular inventory & composition (Figure 3)",
    CATEGORY_MORPHOLOGY: "Neuronal morphology — axons, dendrites, spines (Figures 3-4)",
    CATEGORY_SYNAPSES: "Synapse counts & density (Figure 4)",
    CATEGORY_ORGANELLES: "Sub-cellular organelles — mitochondria & vesicles (Figure 5)",
    CATEGORY_CONNECTIVITY: "Connectivity graph structure (Figures 6-7)",
    CATEGORY_PETERS_RULE: "Refutation of Peters' Rule (Figures 6-7)",
    CATEGORY_SASD: "Same-Axon-Same-Dendrite (SASD) redundancy analysis",
}


# ---------------------------------------------------------------------------
# Claim dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Claim:
    """A single reproducible claim from the paper.

    Parameters
    ----------
    id : str
        Unique short identifier, e.g. ``"IMG-1"`` or ``"SYN-2"``.
    title : str
        Short human-readable title.
    category : str
        One of the ``CATEGORY_*`` constants.
    paper_quote : str
        Direct quote or close paraphrase from the paper.
    section : str
        Paper section or figure where this claim appears.
    reported_values : dict[str, Any]
        Key metrics reported in the paper.
    reproduced_values : dict[str, Any]
        Key metrics reproduced from data (original notebooks or this package).
    notebook : str
        Original notebook filename in ``claims/``, if any.
    notes : str
        Additional context or caveats.
    tags : tuple[str, ...]
        Free-form tags for filtering.
    """

    id: str
    title: str
    category: str
    paper_quote: str
    section: str = ""
    reported_values: dict[str, Any] = field(default_factory=dict)
    reproduced_values: dict[str, Any] = field(default_factory=dict)
    notebook: str = ""
    notes: str = ""
    tags: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

CLAIMS: dict[str, Claim] = {}


def _r(claim: Claim) -> Claim:
    CLAIMS[claim.id] = claim
    return claim


# ===== IMAGING & DATA ACQUISITION ===========================================

_r(Claim(
    id="IMG-1",
    title="Multi-scale imaging pipeline",
    category=CATEGORY_IMAGING,
    paper_quote=(
        "We created a multi-resolution digital volume: first imaging all sections "
        "at low resolution (2 um/pixel), then a sub-volume at 29 nm/pixel, and "
        "finally an ~80,000 um³ box (40 x 40 x 50 um³) at high resolution "
        "(3 nm/pixel)."
    ),
    section="Results — Imaging",
    reported_values={
        "low_res_um_per_pixel": 2,
        "mid_res_nm_per_pixel": 29,
        "high_res_nm_per_pixel": 3,
        "high_res_volume_um3": 80_000,
        "high_res_box_um": [40, 40, 50],
    },
    tags=("imaging", "resolution"),
))

_r(Claim(
    id="IMG-2",
    title="Voxel resolution and dataset size",
    category=CATEGORY_IMAGING,
    paper_quote=(
        "A data set from mouse cortex with a 3 x 3 x 30 cubic nanometer "
        "spatial resolution, yielding 660 GB of images."
    ),
    section="Results — Imaging",
    reported_values={
        "voxel_nm": [3, 3, 30],
        "dataset_gb": 660,
    },
    tags=("imaging", "data"),
))

_r(Claim(
    id="IMG-3",
    title="Imaged volume and sections",
    category=CATEGORY_IMAGING,
    paper_quote=(
        "The 64,000 um³ box imaged at high resolution had roughly "
        "13.7 million cell profiles in its 1,850 sections."
    ),
    section="Results — Imaging",
    reported_values={
        "volume_um3": 64_000,
        "sections": 1_850,
        "cell_profiles": 13_700_000,
    },
    reproduced_values={
        "unique_contours": 569_339,
        "labeled_pixels": 243_813_763,
        "labeled_volume_um3": 42_131,
        "labeled_fraction_pct": 1.47,
    },
    notebook="claim1_data_overview.ipynb",
    tags=("imaging", "volume"),
))


# ===== CELLULAR INVENTORY ====================================================

_r(Claim(
    id="CELL-1",
    title="Total neuron count",
    category=CATEGORY_CELLULAR_INVENTORY,
    paper_quote="~1,600 different neurons within this small region of mammalian brain.",
    section="Results — Figure 3",
    reported_values={"neuron_count": 1_600},
    reproduced_values={"neuron_count": 1_907, "segments": 3_945},
    notebook="claim2_axons_and_dendrites.ipynb",
    notes="Reproduced count is higher; includes full RAMON database vs. cylinder subvolume.",
    tags=("neurons",),
))

_r(Claim(
    id="CELL-2",
    title="Volume composition — neurites vs. glia",
    category=CATEGORY_CELLULAR_INVENTORY,
    paper_quote=(
        "Neuronal processes (axons and dendrites) occupy 92% of the cellular "
        "volume with glial processes occupying much of the remaining 8%."
    ),
    section="Results — Figure 3",
    reported_values={"neurite_volume_pct": 92, "glia_volume_pct": 8},
    reproduced_values={"neurite_volume_pct": 92, "glia_volume_pct": 8},
    notebook="claim2_axons_and_dendrites.ipynb",
    tags=("volume", "composition"),
))

_r(Claim(
    id="CELL-3",
    title="Extracellular space fraction",
    category=CATEGORY_CELLULAR_INVENTORY,
    paper_quote=(
        "The non-cellular (extracellular) space accounts for 6% of the total "
        "volume, less than half the space estimates from living brains."
    ),
    section="Results — Figure 3",
    reported_values={"extracellular_pct": 6},
    reproduced_values={"extracellular_pct": 0.43},
    notebook="claim2_axons_and_dendrites.ipynb",
    notes=(
        "Large discrepancy likely due to tissue fixation shrinkage and "
        "differences in measurement approach."
    ),
    tags=("volume", "extracellular"),
))

_r(Claim(
    id="CELL-4",
    title="Other cell types identified",
    category=CATEGORY_CELLULAR_INVENTORY,
    paper_quote=(
        "We also observed astrocytic processes, myelinated axons, "
        "oligodendrocyte processes and 20 entities we could not easily classify."
    ),
    section="Results — Figure 3",
    reported_values={"unclassified_entities": 20},
    reproduced_values={
        "myelinated_axons": 8,
        "astrocytes": 10,
        "oligodendrocytes": 333,
        "other": 21,
    },
    notebook="claim2_axons_and_dendrites.ipynb",
    tags=("glia", "classification"),
))


# ===== MORPHOLOGY — DENDRITES ================================================

_r(Claim(
    id="DEND-1",
    title="Dendrite count and excitatory fraction",
    category=CATEGORY_MORPHOLOGY,
    paper_quote="193 dendrites, 92% spiny and purportedly excitatory (177/193).",
    section="Results — Figure 3",
    reported_values={
        "dendrites": 193,
        "dendrites_spiny": 177,
        "dendrites_spiny_pct": 92,
    },
    reproduced_values={
        "dendrites": 306,
        "dendrites_excitatory_pct": 95,
        "dendrites_smooth_pct": 5,
    },
    notebook="claim2_axons_and_dendrites.ipynb",
    tags=("dendrites", "excitatory"),
))


# ===== MORPHOLOGY — AXONS ====================================================

_r(Claim(
    id="AXN-1",
    title="Unmyelinated axon count and excitatory fraction",
    category=CATEGORY_MORPHOLOGY,
    paper_quote=(
        "1,407 unmyelinated axons, 93% excitatory (1,308/1,407); "
        "most of remaining are inhibitory."
    ),
    section="Results — Figure 3",
    reported_values={
        "axons_unmyelinated": 1_407,
        "axons_excitatory": 1_308,
        "axons_excitatory_pct": 93,
    },
    reproduced_values={
        "axons": 1_423,
        "axons_excitatory_pct": 92,
        "axons_inhibitory_pct": 7,
    },
    notebook="claim2_axons_and_dendrites.ipynb",
    tags=("axons", "excitatory", "inhibitory"),
))

_r(Claim(
    id="AXN-2",
    title="Axon-to-dendrite volume ratio",
    category=CATEGORY_MORPHOLOGY,
    paper_quote="Axons extend into a 7-fold greater volume than dendrites on average.",
    section="Results — Figure 3",
    reported_values={"axon_dendrite_volume_ratio": 7},
    reproduced_values={
        "axon_dendrite_neuron_ratio": 4.65,
        "axon_dendrite_voxel_ratio": 0.8,
    },
    notebook="claim2_axons_and_dendrites.ipynb",
    notes="Reproduced ratios differ; may reflect different denominator (per-neuron vs. aggregate).",
    tags=("axons", "dendrites", "volume"),
))


# ===== MORPHOLOGY — SPINES ===================================================

_r(Claim(
    id="SPN-1",
    title="Spine and terminal branch counts in cylinder",
    category=CATEGORY_MORPHOLOGY,
    paper_quote=(
        "In the 500 um³ cylinder, no axonal or dendritic orphans, "
        "568 spines and 601 terminal axon branches."
    ),
    section="Results — Figure 3",
    reported_values={
        "spines_in_cylinder": 568,
        "terminal_axon_branches": 601,
        "orphans": 0,
    },
    reproduced_values={
        "spines_red_dendrite": 139,
        "orphans": 25,
    },
    notebook="claim5_spines.ipynb",
    notes="Notebook analyzes a single dendrite (segment 10016) rather than full cylinder.",
    tags=("spines", "morphology"),
))


# ===== SYNAPSES ==============================================================

_r(Claim(
    id="SYN-1",
    title="Total synapse count and density",
    category=CATEGORY_SYNAPSES,
    paper_quote="There were 1,700 synapses at a density of one synapse per 1.13 um³.",
    section="Results — Figure 4",
    reported_values={
        "synapse_count": 1_700,
        "density_per_um3": round(1 / 1.13, 4),
    },
    reproduced_values={
        "synapse_count": 1_700,
        "density_per_um3": 1.0913,
        "psd_volume_fraction_pct": 0.89,
    },
    notebook="claim3_synapses.ipynb",
    tags=("synapses", "density"),
))


# ===== ORGANELLES — MITOCHONDRIA =============================================

_r(Claim(
    id="MITO-1",
    title="Mitochondria count in cylinder 1",
    category=CATEGORY_ORGANELLES,
    paper_quote="We identified 607 mitochondria in cylinder 1.",
    section="Results — Figure 5",
    reported_values={"mitochondria_cylinder1": 607},
    reproduced_values={"mitochondria_total": 650},
    notebook="claim4_mitochondria.ipynb",
    tags=("mitochondria",),
))

_r(Claim(
    id="MITO-2",
    title="Mitochondria volume in inhibitory vs. excitatory dendrites",
    category=CATEGORY_ORGANELLES,
    paper_quote=(
        "Mitochondria occupy twice as much volume in inhibitory dendrites "
        "than in excitatory dendrites."
    ),
    section="Results — Figure 5",
    reported_values={"inhibitory_excitatory_volume_ratio": 2},
    reproduced_values={},
    notebook="claim4_mitochondria.ipynb",
    notes="Not fully reproduced in original notebook.",
    tags=("mitochondria", "inhibitory", "excitatory"),
))

_r(Claim(
    id="MITO-3",
    title="Mitochondria rarely in spines",
    category=CATEGORY_ORGANELLES,
    paper_quote=(
        "Only very rarely (n = 3/1,425) do mitochondria reside in "
        "dendritic spines."
    ),
    section="Results — Figure 5",
    reported_values={
        "mitochondria_in_spines": 3,
        "total_spines_checked": 1_425,
        "fraction_pct": round(3 / 1425 * 100, 2),
    },
    reproduced_values={},
    notebook="claim4_mitochondria.ipynb",
    notes="Spine-level analysis started but not completed in original notebook.",
    tags=("mitochondria", "spines"),
))


# ===== ORGANELLES — VESICLES =================================================

_r(Claim(
    id="VES-1",
    title="Vesicle count",
    category=CATEGORY_ORGANELLES,
    paper_quote="n = 162,259 vesicles.",
    section="Results — Figure 5",
    reported_values={"vesicle_count": 162_259},
    reproduced_values={"vesicle_count": 161_368},
    notebook="claim6_vesicles.ipynb",
    tags=("vesicles",),
))


# ===== CONNECTIVITY ==========================================================

_r(Claim(
    id="CONN-1",
    title="Touch vs. synapse graph construction",
    category=CATEGORY_CONNECTIVITY,
    paper_quote=(
        "We traced the trajectories of all excitatory axons and noted their "
        "juxtapositions, both synaptic and non-synaptic, with every dendritic spine."
    ),
    section="Results — Figures 6-7",
    reported_values={},
    reproduced_values={
        "graph_types": ["touch", "synapse"],
        "synapse_edgelist_edges": 3_896,
        "touch_edgelist_edges": 18_398,
    },
    notebook="claim7_connectivity.ipynb",
    notes="Edgelists available as .edgelist files in claims/ directory.",
    tags=("connectivity", "graphs"),
))

_r(Claim(
    id="CONN-2",
    title="Directed neuron-level graph",
    category=CATEGORY_CONNECTIVITY,
    paper_quote=(
        "Directed connectivity graph from synaptic data: neurons as nodes, "
        "weighted edges from pre- to post-synaptic partners."
    ),
    section="Results — Figures 6-7",
    reported_values={"synapse_count": 1_700},
    reproduced_values={"synapse_count": 1_700, "export_format": "graphml"},
    notebook="claim9_make_graph.ipynb",
    notes=(
        "Graph derived from RAMON metadata; ~2% of connections reassigned "
        "based on geometries and paint information."
    ),
    tags=("connectivity", "graphs", "directed"),
))


# ===== PETERS' RULE ==========================================================

_r(Claim(
    id="PETER-1",
    title="Refutation of Peters' Rule",
    category=CATEGORY_PETERS_RULE,
    paper_quote=(
        "We refute the idea that physical proximity is sufficient to predict "
        "synaptic connectivity (the so-called Peters' rule). Pyramidal neurons "
        "form synapses with only a small subset of available synaptic partners, "
        "despite ample physical opportunity for more connections."
    ),
    section="Results — Figure 7",
    reported_values={},
    reproduced_values={},
    notebook="claim7_connectivity.ipynb",
    notes=(
        "The central finding of the paper. Validated by comparing touch graph "
        "(physical proximity) to synapse graph (actual connections)."
    ),
    tags=("peters_rule", "connectivity"),
))

_r(Claim(
    id="PETER-2",
    title="Randomization test — redundant synapses exceed chance",
    category=CATEGORY_PETERS_RULE,
    paper_quote=(
        "In 80,000 randomization trials — preserving the number of synapses "
        "per axon, per spine, and spatial overlap — none of the randomized "
        "connectivity patterns had as many redundant synapses as the actual data."
    ),
    section="Results — Figure 7",
    reported_values={
        "randomization_trials": 80_000,
        "trials_exceeding_actual": 0,
    },
    reproduced_values={},
    notes="Requires full touch/synapse matrices to reproduce; not yet implemented.",
    tags=("peters_rule", "statistics", "randomization"),
))


# ===== SASD — SAME AXON SAME DENDRITE ========================================

_r(Claim(
    id="SASD-1",
    title="Multi-synaptic contacts between same axon-dendrite pairs",
    category=CATEGORY_SASD,
    paper_quote=(
        "Axons often made two, three, or even more synapses on the same dendrite, "
        "suggesting those multiple-contact axons are communicating more powerfully "
        "with the dendrite."
    ),
    section="Results — Figure 7 / Discussion",
    reported_values={
        "sasd_pairs": 35,
        "dasd_pairs": 166,
        "sadd_pairs": 8,
        "dadd_pairs": 1_502,
    },
    reproduced_values={},
    notes=(
        "SASD pair counts from SASDPairs/SynapsePairTest.R analysis. "
        "Categories: SASD=Same Axon Same Dendrite, DASD=Diff Axon Same Dendrite, "
        "SADD=Same Axon Diff Dendrite, DADD=Diff Axon Diff Dendrite."
    ),
    tags=("sasd", "multisynaptic", "connectivity"),
))

_r(Claim(
    id="SASD-2",
    title="SASD spine volume similarity",
    category=CATEGORY_SASD,
    paper_quote=(
        "The similarity in the volumes of axon-coupled pairs of dendritic spines "
        "were statistically significant."
    ),
    section="Results / Supplemental",
    reported_values={"spine_volume_p_value": 3.4e-4},
    reproduced_values={},
    notes=(
        "Permutation test (10,000 iterations) from SASDPairs/SynapsePairTest.R. "
        "Tested variables: spine volume, PSD volume, vesicle count, mitochondria, "
        "spine apparatus. Only spine volume was significant after BY correction."
    ),
    tags=("sasd", "statistics", "spines"),
))

_r(Claim(
    id="SASD-3",
    title="Spine shape not solely driven by electrical activity",
    category=CATEGORY_SASD,
    paper_quote=(
        "Dendritic spines are not shaped by axons' electrical activity alone, "
        "contrary to wide belief."
    ),
    section="Discussion",
    reported_values={},
    reproduced_values={},
    notes="Qualitative inference from SASD spine volume correlation analysis.",
    tags=("sasd", "spines", "plasticity"),
))


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def list_claims(category: str | None = None) -> list[Claim]:
    """Return claims sorted by ID, optionally filtered by category.

    Parameters
    ----------
    category : str, optional
        If given, only return claims matching this category constant.
    """
    claims = sorted(CLAIMS.values(), key=lambda c: c.id)
    if category is not None:
        claims = [c for c in claims if c.category == category]
    return claims


def get_claim(claim_id: str) -> Claim:
    """Look up a single claim by its string ID (e.g. ``"SYN-1"``).

    Raises
    ------
    KeyError
        If the claim_id is not recognised.
    """
    return CLAIMS[claim_id]


def list_categories() -> dict[str, str]:
    """Return ``{category_key: description}`` mapping."""
    return dict(CATEGORIES)


def claims_by_category() -> dict[str, list[Claim]]:
    """Return claims grouped by category."""
    result: dict[str, list[Claim]] = {}
    for claim in list_claims():
        result.setdefault(claim.category, []).append(claim)
    return result


def summary_table() -> str:
    """Return a human-readable markdown summary table of all claims."""
    lines = ["| ID | Title | Category | Reported | Reproduced |", "|----|-------|----------|----------|------------|"]
    for c in list_claims():
        rep = "yes" if c.reported_values else "-"
        repro = "yes" if c.reproduced_values else "no"
        cat_short = c.category.replace("_", " ")
        lines.append(f"| {c.id} | {c.title} | {cat_short} | {rep} | {repro} |")
    return "\n".join(lines)
