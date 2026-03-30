"""Ground truth data sources for validating Kasthuri 2015 claims.

There are two complementary ground truth sources:

1. **Synapse spreadsheet** (mmc2.xls / mmc6.xls)
   - Paper's supplemental Table S2: 1700 synapses × 25 columns
   - Local copy: ``ramonify/mmc2.xls``
   - Updated version: https://lichtman.rc.fas.harvard.edu/vast/
   - Validates: synapse counts, targets, boutons, correlations, SASD

2. **BossDB volumes** (bossdb.org/project/kasthuri2015)
   - Actual EM imaging + annotation volumes (neurons, synapses, mito, vesicles)
   - Access via ``intern`` Python SDK (``pip install intern``)
   - Validates: neuron counts, volume fractions, morphology, mitochondria census

Not all claims can be validated from a single source. Some require both,
some require neither (metadata-only claims).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Spreadsheet source (mmc2.xls)
# ---------------------------------------------------------------------------

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
MMC2_PATH = _PACKAGE_ROOT / "ramonify" / "mmc2.xls"

# Clean column names for the 25-column spreadsheet
COLUMNS = [
    "synapse_no",
    "psd_x_um",
    "psd_y_um",
    "psd_z_um",
    "psd_pixel_loc",
    "in_cylinder1",
    "in_cylinder2",
    "in_cylinder3",
    "axon_id",
    "dendrite_id",
    "axon_type",         # 0=Exc, 1=Inh, 2=Myel, -1=Unk
    "bouton_no",         # -1=not in cyl1, 0=N/A
    "terminal",          # 1=terminal, 0=en-passant, -1=not in cyl1/2
    "vesicle_count",     # -1=not in cyl1 or N/A
    "mito_in_bouton",    # -1=N/A
    "multi_syn_bouton",  # 1=yes, 0=no, -1=unk, -2=unk
    "axon_length_um",    # -1=N/A
    "is_spine",          # 1=spine, 0=shaft
    "dendrite_type",     # 0=Exc/Spiny, 1=Inh/Smooth
    "psd_size",          # pixels
    "spine_id",          # 0=shaft, -1=unknown
    "spine_volume",      # cubic microns; -1=shaft, 0=N/A
    "spine_apparatus",   # 0=no, 1=yes, -1=N/A(shaft), -2=uncertain
    "single_syn_spine",  # 1=yes
    "unused",
]


def load_synapse_table(path: Path | str | None = None) -> pd.DataFrame:
    """Load mmc2.xls (or mmc6.xls) and return a cleaned DataFrame.

    Sentinel values (-1, -2) are preserved so validators can apply their
    own filtering. Use the ``valid_*`` helpers for common subsets.

    Parameters
    ----------
    path : Path or str, optional
        Override path to the spreadsheet. Defaults to ``ramonify/mmc2.xls``.
    """
    path = Path(path) if path is not None else MMC2_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Synapse spreadsheet not found: {path}\n"
            "Expected the paper's supplemental Table S2 (mmc2.xls) "
            "in the ramonify/ directory."
        )

    df = pd.read_excel(path, header=1)

    # Assign clean column names
    n_cols = min(len(COLUMNS), len(df.columns))
    df.columns = list(COLUMNS[:n_cols]) + list(df.columns[n_cols:])

    # Drop fully-empty trailing column if present
    if "unused" in df.columns:
        df = df.drop(columns=["unused"])

    # Coerce numeric columns (vesicle_count has ' NaN' strings in some rows)
    for col in df.columns:
        if col not in ("psd_pixel_loc",):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# BossDB source
# ---------------------------------------------------------------------------

BOSSDB_PROJECT = "https://bossdb.org/project/kasthuri2015"

# Known channels (from NeuroData / BossDB documentation)
BOSSDB_CHANNELS = {
    "em": "Raw electron microscopy images",
    "neurons": "Neuron segmentation labels",
    "synapses": "Synapse annotations",
    "mitochondria": "Mitochondria annotations",
    "vesicles": "Vesicle annotations",
}

BOSSDB_RESOLUTION_NM = (3, 3, 30)  # x, y, z voxel size in nanometers


def get_bossdb_info() -> dict:
    """Return BossDB access information (does not require network)."""
    return {
        "project_url": BOSSDB_PROJECT,
        "channels": BOSSDB_CHANNELS,
        "voxel_size_nm": BOSSDB_RESOLUTION_NM,
        "access": {
            "sdk": "intern (pip install intern)",
            "username": "public-access",
            "password": "public",
        },
        "example": (
            'from intern import array\n'
            'em = array("bossdb://kasthuri2015/<experiment>/em")\n'
            'cutout = em[z0:z1, y0:y1, x0:x1]'
        ),
    }


# ---------------------------------------------------------------------------
# Convenience filters for the spreadsheet
# ---------------------------------------------------------------------------


def valid_vesicles(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid vesicle counts (>0, cylinder 1 only)."""
    return df[df["vesicle_count"].notna() & (df["vesicle_count"] > 0)]


def valid_terminal(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid terminal/en-passant labels (0 or 1)."""
    return df[df["terminal"].isin([0, 1])]


def valid_msb(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid multi-synaptic bouton labels (0 or 1)."""
    return df[df["multi_syn_bouton"].isin([0, 1])]


def valid_mito(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid mitochondria counts (>= 0)."""
    return df[df["mito_in_bouton"].notna() & (df["mito_in_bouton"] >= 0)]


def valid_spine_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid spine volumes (> 0)."""
    return df[df["spine_volume"].notna() & (df["spine_volume"] > 0)]


def excitatory(df: pd.DataFrame) -> pd.DataFrame:
    """Excitatory synapses (axon_type == 0)."""
    return df[df["axon_type"] == 0]


def inhibitory(df: pd.DataFrame) -> pd.DataFrame:
    """Inhibitory synapses (axon_type == 1)."""
    return df[df["axon_type"] == 1]


def cylinder1(df: pd.DataFrame) -> pd.DataFrame:
    """Synapses in cylinder 1."""
    return df[df["in_cylinder1"] == 1]
