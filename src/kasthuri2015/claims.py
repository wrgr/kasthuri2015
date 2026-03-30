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
CATEGORY_BOUTONS = "boutons"
CATEGORY_ORGANELLES = "organelles"
CATEGORY_SPINE_PROPERTIES = "spine_properties"
CATEGORY_CORRELATIONS = "correlations"
CATEGORY_CONNECTIVITY = "connectivity"
CATEGORY_PETERS_RULE = "peters_rule"
CATEGORY_SASD = "sasd"
CATEGORY_SEGMENTATION = "segmentation"

CATEGORIES = {
    CATEGORY_IMAGING: "Imaging & data acquisition (Figures 1-2)",
    CATEGORY_CELLULAR_INVENTORY: "Cellular inventory & composition (Figure 3)",
    CATEGORY_MORPHOLOGY: "Neuronal morphology — axons, dendrites, spines (Figures 3-4)",
    CATEGORY_SYNAPSES: "Synapse counts, density & targets (Figure 4)",
    CATEGORY_BOUTONS: "Axonal boutons & varicosities (Figure 4)",
    CATEGORY_ORGANELLES: "Sub-cellular organelles — mitochondria & vesicles (Figure 5)",
    CATEGORY_SPINE_PROPERTIES: "Dendritic spine morphology & properties (Figures 4-5)",
    CATEGORY_CORRELATIONS: "Structure-function correlations (Figure 5)",
    CATEGORY_CONNECTIVITY: "Connectivity graph structure (Figures 6-7)",
    CATEGORY_PETERS_RULE: "Refutation of Peters' Rule (Figures 6-7)",
    CATEGORY_SASD: "Same-Axon-Same-Dendrite (SASD) redundancy analysis",
    CATEGORY_SEGMENTATION: "Automated segmentation accuracy (Figure 2)",
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
    id="AXN-3",
    title="Myelinated axon count in reconstructed volume",
    category=CATEGORY_MORPHOLOGY,
    paper_quote=(
        "We also observed eight myelinated axons within the reconstructed volume, "
        "identifiable by their distinct myelin sheath morphology."
    ),
    section="Results — Figure 3",
    reported_values={"myelinated_axons_in_volume": 8},
    reproduced_values={"myelinated_synapses_in_spreadsheet": 2},
    notes=(
        "Paper identifies 8 myelinated axon profiles in the BossDB volume. "
        "Only 2 synapses in mmc6.xls are attributed to myelinated axons (axon_type==2). "
        "Most myelinated axon contacts may fall outside the synapse cylinder subregion."
    ),
    tags=("axons", "myelinated"),
))

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

_r(Claim(
    id="SYN-2",
    title="Excitatory synapses target spines",
    category=CATEGORY_SYNAPSES,
    paper_quote=(
        "Excitatory axons establish synapses mostly on spines "
        "(94%; n = 1,406/1,700)."
    ),
    section="Results — Figure 4",
    reported_values={
        "excitatory_on_spines": 1_406,
        "excitatory_on_spines_pct": 94,
        "total_synapses_denominator": 1_700,
    },
    tags=("synapses", "excitatory", "spines"),
))

_r(Claim(
    id="SYN-3",
    title="Inhibitory synapses target shafts",
    category=CATEGORY_SYNAPSES,
    paper_quote=(
        "Inhibitory axons establish synapses mostly on shafts "
        "(81%, n = 70/86)."
    ),
    section="Results — Figure 4",
    reported_values={
        "inhibitory_on_shafts": 70,
        "inhibitory_total": 86,
        "inhibitory_on_shafts_pct": 81,
    },
    tags=("synapses", "inhibitory", "shafts"),
))

_r(Claim(
    id="SYN-4",
    title="En passant vs. terminal synapses",
    category=CATEGORY_SYNAPSES,
    paper_quote=(
        "Most (71%; n = 1,207/1,700) of the synapses in the volume derive "
        "from varicosities along axons (en passant synapses), and the rest "
        "are at the end of short branches (terminal synapses)."
    ),
    section="Results — Figure 4",
    reported_values={
        "en_passant_synapses": 1_207,
        "en_passant_pct": 71,
        "terminal_synapses": 493,
    },
    tags=("synapses", "en_passant", "terminal"),
))


# ===== BOUTONS & VARICOSITIES ================================================

_r(Claim(
    id="BOUT-1",
    title="Multi-synaptic excitatory varicosities",
    category=CATEGORY_BOUTONS,
    paper_quote=(
        "18% of excitatory axonal varicosities are presynaptic to "
        "multiple partners."
    ),
    section="Results — Figure 4",
    reported_values={"excitatory_multisynaptic_pct": 18},
    tags=("boutons", "multisynaptic", "excitatory"),
))

_r(Claim(
    id="BOUT-2",
    title="Multi-synaptic inhibitory varicosities",
    category=CATEGORY_BOUTONS,
    paper_quote=(
        "43% of the inhibitory axonal varicosities are presynaptic to "
        "multiple partners."
    ),
    section="Results — Figure 4",
    reported_values={"inhibitory_multisynaptic_pct": 43},
    tags=("boutons", "multisynaptic", "inhibitory"),
))

_r(Claim(
    id="BOUT-3",
    title="Maximum multi-synaptic bouton target count",
    category=CATEGORY_BOUTONS,
    paper_quote=(
        "The most extreme example in this dataset is a large excitatory "
        "en passant bouton innervating five different postsynaptic targets."
    ),
    section="Results — Figure 4",
    reported_values={"max_postsynaptic_targets": 5},
    tags=("boutons", "multisynaptic"),
))

_r(Claim(
    id="BOUT-4",
    title="Multi-synaptic varicosities are general",
    category=CATEGORY_BOUTONS,
    paper_quote=(
        "Tracing ten randomly chosen axons (with 78 varicosities) into the "
        "larger surrounding volume showed all but one axon had at least one "
        "multi-synaptic varicosity."
    ),
    section="Results — Figure 4",
    reported_values={
        "axons_sampled": 10,
        "varicosities_sampled": 78,
        "axons_with_multisynaptic": 9,
    },
    tags=("boutons", "multisynaptic"),
))

_r(Claim(
    id="BOUT-5",
    title="Labeled bouton count in cylinder 1",
    category=CATEGORY_BOUTONS,
    paper_quote=(
        "Excitatory and inhibitory axonal varicosities (boutons) were annotated "
        "throughout cylinder 1 to characterize multi-synaptic bouton prevalence."
    ),
    section="Results — Figure 4",
    reported_values={},
    reproduced_values={
        "unique_boutons_cylinder1": 625,
    },
    notes=(
        "625 unique bouton identifiers (bouton_no > 0) in mmc6.xls. "
        "Rows with bouton_no == -1 are outside cylinder 1; bouton_no == 0 is N/A "
        "(myelinated or not annotated). Multi-synaptic boutons appear multiple times "
        "with the same bouton_no."
    ),
    tags=("boutons", "cylinder1"),
))


# ===== SPINE PROPERTIES ======================================================

_r(Claim(
    id="SPINE-1",
    title="Spine density on red dendrite",
    category=CATEGORY_SPINE_PROPERTIES,
    paper_quote=(
        "Spines appear more densely packed (~51 spines per 10 um dendritic "
        "length for the red dendrite in cylinder 1)."
    ),
    section="Results — Figure 4",
    reported_values={"spines_per_10um": 51},
    tags=("spines", "density"),
))

_r(Claim(
    id="SPINE-2",
    title="Spine length distribution",
    category=CATEGORY_SPINE_PROPERTIES,
    paper_quote=(
        "Spines often of greater length (mean ~1.8 +/- 0.6 um and longest "
        "~3.8 um; n = 77) than expected in mouse cortex."
    ),
    section="Results — Figure 4",
    reported_values={
        "spine_length_mean_um": 1.8,
        "spine_length_sd_um": 0.6,
        "spine_length_max_um": 3.8,
        "n_spines_measured": 77,
    },
    tags=("spines", "morphology"),
))

_r(Claim(
    id="SPINE-3",
    title="Non-innervated spines",
    category=CATEGORY_SPINE_PROPERTIES,
    paper_quote=(
        "Approximately 5% (39/780) of spines belonging to the central "
        "dendrite were not innervated by an axon."
    ),
    section="Results — Figure 4",
    reported_values={
        "non_innervated_spines": 39,
        "total_spines_checked": 780,
        "non_innervated_pct": 5,
    },
    tags=("spines", "innervation"),
))

_r(Claim(
    id="SPINE-4",
    title="Spine apparatus presence frequency",
    category=CATEGORY_SPINE_PROPERTIES,
    paper_quote=(
        "Larger spine volumes were positively correlated with spine "
        "apparati (r = 0.36; p < 0.000001)."
    ),
    section="Results — Figure 5",
    reported_values={"spine_apparatus_r_with_volume": 0.36},
    reproduced_values={
        "spines_with_apparatus_mmc6": 307,
        "spines_without_apparatus_mmc6": 530,
        "pct_with_apparatus_mmc6": 36.7,
        "spines_with_apparatus_mmc2": 484,
        "spines_without_apparatus_mmc2": 467,
        "pct_with_apparatus_mmc2": 50.9,
    },
    notes=(
        "mmc6 (updated) has 307/837 spines with apparatus (36.7%); "
        "mmc2 (original) has 484/951 (50.9%). "
        "The mmc6 revision reclassified many uncertain spine apparatus annotations. "
        "Correlates with spine volume (CORR-1; see also mmc6 vs mmc2 note there)."
    ),
    tags=("spines", "spine_apparatus", "plasticity"),
))

_r(Claim(
    id="SPINE-5",
    title="Multiply-innervated spines",
    category=CATEGORY_SPINE_PROPERTIES,
    paper_quote=(
        "Dendritic spines are nearly always contacted by a single excitatory axon; "
        "multiply-innervated spines are rare."
    ),
    section="Results — Figure 4",
    reported_values={},
    reproduced_values={
        "single_synapse_spines": 1660,
        "dual_synapse_spines_rows": 40,
        "dual_synapse_unique_spines": 20,
        "total_synapses": 1700,
        "pct_on_single_syn_spine": 97.6,
    },
    notes=(
        "From mmc6.xls column 'nr_synapses_on_spine': 1660 synapses are on spines "
        "with exactly 1 synapse; 40 synapses (on 20 unique spines) share a spine "
        "with one additional synapse. Single-synapse spine prevalence is 97.6%."
    ),
    tags=("spines", "innervation", "multisynaptic"),
))


# ===== CORRELATIONS ===========================================================

_r(Claim(
    id="CORR-1",
    title="Spine volume correlates with spine apparatus",
    category=CATEGORY_CORRELATIONS,
    paper_quote=(
        "Larger spine volumes were positively correlated with spine "
        "apparati (r = 0.36; p < 0.000001)."
    ),
    section="Results — Figure 5",
    reported_values={"r": 0.36, "p_lt": 1e-6},
    reproduced_values={
        "r_mmc6": 0.645,
        "r_mmc2": 0.39,
    },
    notes=(
        "mmc6 (updated spine apparatus annotations) gives r=0.645, "
        "substantially higher than the paper's r=0.36. "
        "mmc2 (original) gives r≈0.39, closer to the paper. "
        "Discrepancy likely reflects revised spine apparatus labeling in mmc6 "
        "which reclassified uncertain cases and reduced false positives."
    ),
    tags=("correlation", "spines", "spine_apparatus"),
))

_r(Claim(
    id="CORR-2",
    title="Spine volume correlates with PSD size",
    category=CATEGORY_CORRELATIONS,
    paper_quote=(
        "Larger spine volumes were positively correlated with larger "
        "postsynaptic densities (r = 0.77; p < 0.000001)."
    ),
    section="Results — Figure 5",
    reported_values={"r": 0.77, "p_lt": 1e-6},
    tags=("correlation", "spines", "psd"),
))

_r(Claim(
    id="CORR-3",
    title="Spine volume correlates with vesicle count",
    category=CATEGORY_CORRELATIONS,
    paper_quote=(
        "Larger spine volumes were positively correlated with larger "
        "numbers of presynaptic vesicles (r = 0.58; p < 0.000001)."
    ),
    section="Results — Figure 5",
    reported_values={"r": 0.58, "p_lt": 1e-6},
    tags=("correlation", "spines", "vesicles"),
))

_r(Claim(
    id="CORR-4",
    title="Spine volume correlates with presynaptic mitochondria",
    category=CATEGORY_CORRELATIONS,
    paper_quote=(
        "Larger spine volumes were positively correlated with presynaptic "
        "mitochondria (r = 0.141; p = 0.007)."
    ),
    section="Results — Figure 5",
    reported_values={"r": 0.141, "p": 0.007},
    tags=("correlation", "spines", "mitochondria"),
))


# ===== ORGANELLES — VESICLE DISTRIBUTION =====================================

_r(Claim(
    id="VES-2",
    title="Vesicle count per mono-synaptic varicosity",
    category=CATEGORY_ORGANELLES,
    paper_quote=(
        "The number of vesicles per synaptic varicosity ranged from 2 to "
        "1,366 for varicosities with one postsynaptic target "
        "(mean = 153 +/- 127)."
    ),
    section="Results — Figure 5",
    reported_values={
        "vesicles_per_varicosity_min": 2,
        "vesicles_per_varicosity_max": 1_366,
        "vesicles_per_varicosity_mean": 153,
        "vesicles_per_varicosity_sd": 127,
    },
    tags=("vesicles", "varicosity"),
))

_r(Claim(
    id="VES-3",
    title="More vesicles at multi-synaptic varicosities",
    category=CATEGORY_ORGANELLES,
    paper_quote=(
        "Significantly greater numbers of vesicles at multi-synaptic "
        "varicosities (mean = 200 +/- 173)."
    ),
    section="Results — Figure 5",
    reported_values={
        "multisynaptic_vesicles_mean": 200,
        "multisynaptic_vesicles_sd": 173,
    },
    tags=("vesicles", "multisynaptic"),
))

_r(Claim(
    id="VES-4",
    title="Vesicle count similar in excitatory and inhibitory synapses",
    category=CATEGORY_ORGANELLES,
    paper_quote=(
        "The number of vesicles is not significantly different in excitatory "
        "and inhibitory synapses."
    ),
    section="Results — Figure 5",
    reported_values={},
    reproduced_values={
        "exc_mean_vesicles": 178.7,
        "inh_mean_vesicles": 168.4,
        "mannwhitney_p": 0.9845,
        "significant": False,
    },
    notes="Confirmed from mmc6.xls: Mann-Whitney U p=0.98, no significant difference.",
    tags=("vesicles", "excitatory", "inhibitory"),
))

_r(Claim(
    id="PSD-1",
    title="PSD size larger at inhibitory than excitatory synapses",
    category=CATEGORY_SYNAPSES,
    paper_quote=(
        "The size of postsynaptic densities (PSD) was measured for each of the "
        "1,700 synapses; PSD size correlates positively with spine volume (r = 0.77)."
    ),
    section="Results — Figure 5",
    reported_values={"psd_spine_volume_correlation_r": 0.77},
    reproduced_values={
        "mean_psd_all_px": 472,
        "mean_psd_exc_px": 457,
        "mean_psd_inh_px": 755,
        "psd_exc_vs_inh_mannwhitney_p": "< 1e-10",
    },
    notes=(
        "Inhibitory (shaft) synapses have significantly larger PSDs than excitatory "
        "(spine) synapses (755 vs 457 pixels; Mann-Whitney p≈0). "
        "Large en-face inhibitory PSDs covering dendritic shaft surface area exceed "
        "the small spine-head PSDs of excitatory synapses. "
        "Computed from psd_size column in mmc6.xls."
    ),
    tags=("psd", "synapses", "excitatory", "inhibitory"),
))


# ===== SEGMENTATION ==========================================================

_r(Claim(
    id="SEG-1",
    title="Automated segmentation pixel accuracy",
    category=CATEGORY_SEGMENTATION,
    paper_quote=(
        "In single images, 92.6% of the pixels or 87.6% of the profiles "
        "were correctly segmented."
    ),
    section="Results — Figure 2",
    reported_values={
        "pixel_accuracy_pct": 92.6,
        "profile_accuracy_pct": 87.6,
    },
    tags=("segmentation", "accuracy"),
))

_r(Claim(
    id="SEG-2",
    title="3D segmentation error rates",
    category=CATEGORY_SEGMENTATION,
    paper_quote=(
        "In three dimensions we estimated the need for ~0.9 split "
        "operations and 5.8 merge operations per um³."
    ),
    section="Results — Figure 2",
    reported_values={
        "splits_per_um3": 0.9,
        "merges_per_um3": 5.8,
    },
    tags=("segmentation", "errors"),
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

_r(Claim(
    id="MITO-4",
    title="Presynaptic mitochondria more common at inhibitory boutons",
    category=CATEGORY_ORGANELLES,
    paper_quote=(
        "Larger spine volumes were positively correlated with presynaptic "
        "mitochondria (r = 0.141; p = 0.007)."
    ),
    section="Results — Figure 5",
    reported_values={"r_with_spine_volume": 0.141, "p": 0.007},
    reproduced_values={
        "exc_boutons_with_mito_pct": 31.0,
        "inh_boutons_with_mito_pct": 67.3,
        "exc_boutons_with_mito_n": 232,
        "inh_boutons_with_mito_n": 37,
    },
    notes=(
        "From mito_in_bouton column: inhibitory boutons have ≥1 presynaptic mitochondrion "
        "67% of the time vs. only 31% for excitatory boutons — more than 2× more frequent. "
        "Consistent with MITO-2 (inhibitory dendrites contain 2× the mitochondria volume). "
        "The weak correlation with spine volume (r=0.141) reflects the dominant role of "
        "bouton type, not spine size, in determining presynaptic mitochondria presence."
    ),
    tags=("mitochondria", "boutons", "presynaptic", "excitatory", "inhibitory"),
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

_r(Claim(
    id="CONN-3",
    title="Physical contact vs. synaptic selectivity (touch-to-synapse ratio)",
    category=CATEGORY_CONNECTIVITY,
    paper_quote=(
        "Pyramidal neurons form synapses with only a small subset of available "
        "synaptic partners, despite ample physical opportunity for more connections."
    ),
    section="Results — Figures 6-7",
    reported_values={},
    reproduced_values={
        "synapse_graph_edges": 1_178,
        "touch_graph_edges": 15_680,
        "touch_to_synapse_ratio": 13.3,
    },
    notes=(
        "The touch (physical contact) graph has ~13× more edges than the synapse "
        "(actual connection) graph — demonstrating extreme selectivity in synapse "
        "formation. Computed from .edgelist files in claims/ directory; "
        "edge counts exclude node-declaration lines."
    ),
    tags=("connectivity", "selectivity", "peters_rule"),
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
    title="SASD spine volume similarity (vs. non-SASD)",
    category=CATEGORY_SASD,
    paper_quote=(
        "The similarity in the volumes of axon-coupled pairs of dendritic spines "
        "were statistically significant."
    ),
    section="Results / Supplemental",
    reported_values={
        "feature": "log10_spine_volume",
        "mean_diff_sasd": 0.2017,
        "mean_diff_non_sasd": 0.3269,
        "difference": 0.1252,
        "p_value": 3.4e-4,
        "p_adjusted_by": 0.003,
    },
    reproduced_values={},
    notes=(
        "Permutation test from SASDPairs/SynapsePairTest.R. "
        "Only spine volume was significant after Benjamini-Yekutieli correction."
    ),
    tags=("sasd", "statistics", "spines"),
))

_r(Claim(
    id="SASD-3",
    title="SASD PSD volume similarity (not significant)",
    category=CATEGORY_SASD,
    paper_quote="PSD volume: SASD pairs more similar but not significant after correction.",
    section="Supplemental",
    reported_values={
        "feature": "log10_psd_volume",
        "mean_diff_sasd": 0.2876,
        "mean_diff_non_sasd": 0.3379,
        "difference": 0.05,
        "p_value": 0.11,
        "p_adjusted_by": 0.322,
    },
    tags=("sasd", "statistics", "psd"),
))

_r(Claim(
    id="SASD-4",
    title="SASD vesicle count similarity (not significant)",
    category=CATEGORY_SASD,
    paper_quote="Vesicle count: SASD pairs more similar but not significant after correction.",
    section="Supplemental",
    reported_values={
        "feature": "log10_vesicle_count",
        "mean_diff_sasd": 0.2896,
        "mean_diff_non_sasd": 0.3476,
        "difference": 0.058,
        "p_value": 0.08,
        "p_adjusted_by": 0.322,
    },
    tags=("sasd", "statistics", "vesicles"),
))

_r(Claim(
    id="SASD-5",
    title="SASD spine apparatus similarity (not significant)",
    category=CATEGORY_SASD,
    paper_quote="Spine apparatus: SASD pairs more similar but not significant after correction.",
    section="Supplemental",
    reported_values={
        "feature": "spine_apparatus_pct_diff",
        "mean_diff_sasd_pct": 51,
        "mean_diff_non_sasd_pct": 68,
        "difference_pct": 16,
        "p_value": 0.014,
        "p_adjusted_by": 0.084,
    },
    tags=("sasd", "statistics", "spine_apparatus"),
))

_r(Claim(
    id="SASD-6",
    title="SASD mitochondria count similarity (not significant)",
    category=CATEGORY_SASD,
    paper_quote="Number of mitochondria: SASD pairs slightly more similar, not significant.",
    section="Supplemental",
    reported_values={
        "feature": "n_mitos_pct_diff",
        "mean_diff_sasd_pct": 40,
        "mean_diff_non_sasd_pct": 43,
        "difference_pct": 3.56,
        "p_value": 0.27,
        "p_adjusted_by": 0.636,
    },
    tags=("sasd", "statistics", "mitochondria"),
))

_r(Claim(
    id="SASD-7",
    title="DASD vs. DADD — spine volume on same dendrite",
    category=CATEGORY_SASD,
    paper_quote=(
        "Spine volume is highly significant when comparing DASD to DADD pairs, "
        "and interestingly number of mitochondria also showed a significant effect."
    ),
    section="Supplemental",
    reported_values={
        "spine_volume_p": 1e-4,
        "psd_volume_p": 0.072,
        "vesicle_count_p": 0.147,
        "spine_apparatus_p": 0.1029,
        "n_mitos_p": 0.0064,
    },
    tags=("sasd", "statistics", "dendrite_effect"),
))

_r(Claim(
    id="SASD-8",
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
