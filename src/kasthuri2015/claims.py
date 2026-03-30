"""Enumeration of reproducible claims from Kasthuri et al. 2015.

Reference
---------
Kasthuri, N., Hayworth, K.J., Berger, D.R., Schalek, R.L., Conchello, J.A.,
Knowles-Barley, S., Lee, D., Vazquez-Reina, A., Kaynig, V., Jones, T.R.,
Roberts, M., Morgan, J.L., Tapia, J.C., Seung, H.S., Roncal, W.G.,
Vogelstein, J.T., Burns, R., Sussman, D.L., Bhatt, P., ... Lichtman, J.W.
(2015). Saturated Reconstruction of a Volume of Neocortex.
Cell, 162(3), 648-661. https://doi.org/10.1016/j.cell.2015.06.054
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class ClaimID(IntEnum):
    """Numeric identifiers for each claim."""

    DATA_ACCESS = 0
    DATA_OVERVIEW = 1
    AXONS_AND_DENDRITES = 2
    SYNAPSES = 3
    MITOCHONDRIA = 4
    SPINES = 5
    VESICLES = 6
    CONNECTIVITY = 7
    STATISTICS = 8
    GRAPH_CONSTRUCTION = 9


@dataclass(frozen=True)
class Claim:
    """A single reproducible claim from the paper.

    Parameters
    ----------
    id : ClaimID
        Numeric identifier matching the original notebook numbering.
    title : str
        Short human-readable title.
    paper_quote : str
        Direct quote or paraphrase of the claim in the paper.
    reported_values : dict[str, Any]
        Key metrics reported in the paper for this claim.
    reproduced_values : dict[str, Any]
        Key metrics reproduced from the data via the original notebooks.
    notebook : str
        Filename of the original Jupyter notebook.
    notes : str
        Additional context or caveats.
    tags : tuple[str, ...]
        Categorical tags for filtering.
    """

    id: ClaimID
    title: str
    paper_quote: str
    reported_values: dict[str, Any] = field(default_factory=dict)
    reproduced_values: dict[str, Any] = field(default_factory=dict)
    notebook: str = ""
    notes: str = ""
    tags: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Claim definitions
# ---------------------------------------------------------------------------

CLAIMS: dict[ClaimID, Claim] = {}


def _register(claim: Claim) -> Claim:
    CLAIMS[claim.id] = claim
    return claim


_register(
    Claim(
        id=ClaimID.DATA_ACCESS,
        title="Data access and setup",
        paper_quote=(
            "Saturated Reconstruction of a Volume of Neocortex — all data "
            "publicly available via NeuroData (formerly Open Connectome Project)."
        ),
        reported_values={
            "token": "kasthuri2015_ramon_v4",
            "resolution": 3,
            "cylinders": 3,
            "bounding_box_xyz": [[694, 1794], [1750, 2460], [1004, 1379]],
        },
        reproduced_values={
            "channels": [
                "neurons",
                "synapses",
                "mitochondria",
                "vesicles",
            ],
        },
        notebook="claim0_get_data.ipynb",
        notes="Foundation notebook; demonstrates data retrieval via ndio.",
        tags=("data", "infrastructure"),
    )
)

_register(
    Claim(
        id=ClaimID.DATA_OVERVIEW,
        title="Volume statistics",
        paper_quote=(
            "The 64,000 um³ box imaged at high resolution had roughly "
            "13.7 million cell profiles in its 1850 sections."
        ),
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
        tags=("volume", "overview"),
    )
)

_register(
    Claim(
        id=ClaimID.AXONS_AND_DENDRITES,
        title="Axons and dendrites",
        paper_quote=(
            "~1600 different neurons within this small region of mammalian brain; "
            "193 dendrites, 92% spiny and purportedly excitatory (177/193); "
            "1407 unmyelinated axons, 93% excitatory (1308/1407). "
            "Neuronal processes occupy 92% of the cellular volume with glial "
            "processes occupying much of the remaining 8%. "
            "The non-cellular (extracellular) space accounts for 6% of total volume. "
            "Axons extend into a 7-fold greater volume than dendrites on average."
        ),
        reported_values={
            "neuron_count": 1_600,
            "dendrites": 193,
            "dendrites_spiny_pct": 92,
            "axons_unmyelinated": 1_407,
            "axons_excitatory_pct": 93,
            "neurite_volume_pct": 92,
            "glia_volume_pct": 8,
            "extracellular_pct": 6,
            "axon_dendrite_volume_ratio": 7,
        },
        reproduced_values={
            "neuron_count": 1_907,
            "segments": 3_945,
            "dendrites": 306,
            "dendrites_excitatory_pct": 95,
            "dendrites_smooth_pct": 5,
            "axons": 1_423,
            "axons_excitatory_pct": 92,
            "axons_inhibitory_pct": 7,
            "myelinated_axons": 8,
            "astrocytes": 10,
            "oligodendrocytes": 333,
            "other": 21,
            "orphans": 25,
            "neurite_volume_pct": 92,
            "glia_volume_pct": 8,
            "extracellular_pct": 0.43,
            "axon_dendrite_neuron_ratio": 4.65,
            "axon_dendrite_voxel_ratio": 0.8,
        },
        notebook="claim2_axons_and_dendrites.ipynb",
        notes=(
            "Some counts differ between paper and reproduced values; "
            "the reproduced analysis uses the full RAMON database while "
            "paper values are from the cylinder subvolume."
        ),
        tags=("morphology", "axons", "dendrites", "glia"),
    )
)

_register(
    Claim(
        id=ClaimID.SYNAPSES,
        title="Synapses",
        paper_quote=(
            "There were 1,700 synapses at a density of one synapse per 1.13 um³."
        ),
        reported_values={
            "synapse_count": 1_700,
            "density_per_um3": 1 / 1.13,
        },
        reproduced_values={
            "synapse_count": 1_700,
            "density_per_um3": 1.0913,
            "psd_volume_fraction_pct": 0.89,
        },
        notebook="claim3_synapses.ipynb",
        tags=("synapses", "density"),
    )
)

_register(
    Claim(
        id=ClaimID.MITOCHONDRIA,
        title="Mitochondria",
        paper_quote=(
            "We identified 607 mitochondria in cylinder 1. "
            "Mitochondria occupy twice as much volume in inhibitory dendrites "
            "than in excitatory dendrites. "
            "Only very rarely (n = 3/1,425) do mitochondria reside in dendritic spines."
        ),
        reported_values={
            "mitochondria_cylinder1": 607,
            "inhibitory_excitatory_volume_ratio": 2,
            "mitochondria_in_spines": 3,
            "total_spines_checked": 1_425,
        },
        reproduced_values={
            "mitochondria_total": 650,
        },
        notebook="claim4_mitochondria.ipynb",
        notes="Volume ratio and spine analysis were started but not fully completed in notebook.",
        tags=("organelles", "mitochondria"),
    )
)

_register(
    Claim(
        id=ClaimID.SPINES,
        title="Dendritic spines",
        paper_quote=(
            "568 spines and 601 terminal axon branches in the 500 um³ cylinder."
        ),
        reported_values={
            "spines_in_cylinder": 568,
            "terminal_axon_branches": 601,
        },
        reproduced_values={
            "spines_red_dendrite": 139,
        },
        notebook="claim5_spines.ipynb",
        notes="Notebook focuses on a single dendrite (segment 10016) as an example.",
        tags=("morphology", "spines"),
    )
)

_register(
    Claim(
        id=ClaimID.VESICLES,
        title="Vesicles",
        paper_quote="n = 162,259 vesicles.",
        reported_values={
            "vesicle_count": 162_259,
        },
        reproduced_values={
            "vesicle_count": 161_368,
        },
        notebook="claim6_vesicles.ipynb",
        tags=("organelles", "vesicles"),
    )
)

_register(
    Claim(
        id=ClaimID.CONNECTIVITY,
        title="Connectivity",
        paper_quote=(
            "Connectivity graphs constructed from spine-axon spatial proximity "
            "(touch graph) and synaptic connections (synapse graph)."
        ),
        reported_values={},
        reproduced_values={
            "graph_types": ["touch", "synapse"],
        },
        notebook="claim7_connectivity.ipynb",
        notes="Builds both undirected touch and directed synapse graphs using networkx.",
        tags=("connectivity", "graphs"),
    )
)

_register(
    Claim(
        id=ClaimID.STATISTICS,
        title="Statistics",
        paper_quote="",
        reported_values={},
        reproduced_values={},
        notebook="claim8_stats.ipynb",
        notes="Placeholder notebook; no analysis implemented.",
        tags=("statistics",),
    )
)

_register(
    Claim(
        id=ClaimID.GRAPH_CONSTRUCTION,
        title="Graph construction",
        paper_quote=(
            "Directed connectivity graph from synaptic data: neurons as nodes, "
            "weighted edges from pre- to post-synaptic partners."
        ),
        reported_values={
            "synapse_count": 1_700,
        },
        reproduced_values={
            "synapse_count": 1_700,
            "export_format": "graphml",
        },
        notebook="claim9_make_graph.ipynb",
        notes=(
            "Graph derived from RAMON metadata; ~2% of connections were "
            "reassigned based on geometries and paint information."
        ),
        tags=("connectivity", "graphs"),
    )
)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def list_claims() -> list[Claim]:
    """Return all claims sorted by ID."""
    return [CLAIMS[k] for k in sorted(CLAIMS)]


def get_claim(claim_id: int | ClaimID) -> Claim:
    """Look up a single claim by numeric ID.

    Parameters
    ----------
    claim_id : int or ClaimID
        The claim number (0-9).

    Returns
    -------
    Claim

    Raises
    ------
    KeyError
        If the claim_id is not recognised.
    """
    return CLAIMS[ClaimID(claim_id)]
