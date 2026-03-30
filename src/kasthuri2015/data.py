"""Ground truth data sources for validating Kasthuri 2015 claims.

There are two complementary ground truth sources:

1. **Synapse spreadsheet — mmc6.xls (preferred, updated 2016)**
   - Updated supplemental synapse table from the Lichtman Lab VAST portal
   - Download: https://lichtman.rc.fas.harvard.edu/vast/kasthuri2015_mmc6.xls
   - Local copy: ``ramonify/mmc6.xls``
   - Changes vs. mmc2: revised spine apparatus annotations (307 vs 484 positive),
     new column "nr_synapses_on_spine" (number of synapses per spine)
   - 1700 synapses × 24 columns

2. **Synapse spreadsheet — mmc2.xls (original paper supplement)**
   - Paper's supplemental Table S2, published with Cell 2015 article
   - Local copy: ``ramonify/mmc2.xls``
   - 1700 synapses × 24 columns (last col: single_syn_spine)

3. **BossDB volumes** (bossdb.org/project/kasthuri2015)
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
# File paths and URLs
# ---------------------------------------------------------------------------

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent

# Updated ground truth (preferred) — Lichtman Lab VAST portal
MMC6_PATH = _PACKAGE_ROOT / "ramonify" / "mmc6.xls"
VAST_URL = "https://lichtman.rc.fas.harvard.edu/vast/kasthuri2015_mmc6.xls"

# Original paper supplement (fallback)
MMC2_PATH = _PACKAGE_ROOT / "ramonify" / "mmc2.xls"


# ---------------------------------------------------------------------------
# Column names
# ---------------------------------------------------------------------------

# Shared columns (positions 0-22): same layout in both mmc2 and mmc6
_SHARED_COLUMNS = [
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
    "mito_in_bouton",    # number of mitochondria in bouton; -1=N/A
    "multi_syn_bouton",  # 1=yes, 0=no, -1=unk, -2=unk
    "axon_length_um",    # axon skeleton length in cylinder 1; -1=N/A
    "is_spine",          # 1=spine, 0=shaft
    "dendrite_type",     # 0=Exc/Spiny, 1=Inh/Smooth
    "psd_size",          # PSD area in pixels
    "spine_id",          # spine identifier; 0=shaft, -1=unknown
    "spine_volume",      # voxel count at 24×24×29 nm; -1=shaft, 0=N/A
    "spine_apparatus",   # 0=no, 1=yes, -1=N/A(shaft), -2=uncertain
]

# mmc6 adds "nr_synapses_on_spine" as column 23 (replaces single_syn_spine)
COLUMNS_MMC6 = _SHARED_COLUMNS + ["nr_synapses_on_spine"]

# mmc2 original column 23
COLUMNS_MMC2 = _SHARED_COLUMNS + ["single_syn_spine"]

# Convenience alias — always points to whichever schema is loaded
COLUMNS = COLUMNS_MMC6


# ---------------------------------------------------------------------------
# Voxel size conversion
# ---------------------------------------------------------------------------

# mmc6 spine_volume is in voxels at 24×24×29 nm resolution
VOXEL_NM = (24.0, 24.0, 29.0)
VOXEL_UM3 = (VOXEL_NM[0] * VOXEL_NM[1] * VOXEL_NM[2]) * 1e-9  # nm³ → µm³


def voxels_to_um3(voxels: float | np.ndarray) -> float | np.ndarray:
    """Convert spine_volume voxel count to cubic microns."""
    return voxels * VOXEL_UM3


# ---------------------------------------------------------------------------
# Spreadsheet loaders
# ---------------------------------------------------------------------------


def load_mmc6_table(path: Path | str | None = None) -> pd.DataFrame:
    """Load mmc6.xls (updated Lichtman Lab VAST ground truth).

    mmc6 uses a two-row header (row 0 = column names, row 1 = sub-headers).
    Data begins at row 2.

    Parameters
    ----------
    path : Path or str, optional
        Override path. Defaults to ``ramonify/mmc6.xls``.

    Notes
    -----
    mmc6 changes vs. mmc2
    ~~~~~~~~~~~~~~~~~~~~~~
    - Column 22 (``spine_apparatus``): revised annotations — 307 positive vs 484 in mmc2.
    - Column 23: new column ``nr_synapses_on_spine`` (count) replaces ``single_syn_spine``
      (binary flag). Values: 1 = single, 2 = doubly-innervated, etc.
    - ``spine_volume`` is in voxels (24×24×29 nm each); use :func:`voxels_to_um3` to convert.
    """
    path = Path(path) if path is not None else MMC6_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"mmc6.xls not found: {path}\n"
            f"Download from: {VAST_URL}\n"
            f"Place in the ramonify/ directory."
        )

    raw = pd.read_excel(path, header=None)
    # Skip rows 0 (col headers) and 1 (sub-headers); data starts at row 2
    df = raw.iloc[2:].reset_index(drop=True).copy()
    df.columns = range(len(df.columns))

    n_cols = min(len(COLUMNS_MMC6), len(df.columns))
    df.columns = list(COLUMNS_MMC6[:n_cols]) + [f"col_{i}" for i in range(n_cols, len(df.columns))]

    for col in df.columns:
        if col != "psd_pixel_loc":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_mmc2_table(path: Path | str | None = None) -> pd.DataFrame:
    """Load mmc2.xls (original paper supplement, Cell 2015).

    Parameters
    ----------
    path : Path or str, optional
        Override path. Defaults to ``ramonify/mmc2.xls``.
    """
    path = Path(path) if path is not None else MMC2_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"mmc2.xls not found: {path}\n"
            "Expected the paper's supplemental Table S2 in the ramonify/ directory."
        )

    df = pd.read_excel(path, header=1)
    n_cols = min(len(COLUMNS_MMC2), len(df.columns))
    df.columns = list(COLUMNS_MMC2[:n_cols]) + list(df.columns[n_cols:])

    # Drop fully-empty trailing column if present
    extra = [c for c in df.columns if str(c).startswith("Unnamed") or c == "unused"]
    if extra:
        df = df.drop(columns=extra[:1])  # only drop one extra column

    for col in df.columns:
        if col != "psd_pixel_loc":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_synapse_table(path: Path | str | None = None) -> pd.DataFrame:
    """Load the synapse spreadsheet, preferring mmc6 (updated) over mmc2 (original).

    If ``path`` is provided it is used directly (format is auto-detected by filename).
    Otherwise, mmc6.xls is tried first and mmc2.xls is used as fallback.

    Sentinel values (-1, -2) are preserved so validators can apply their
    own filtering. Use the ``valid_*`` helpers for common subsets.

    Parameters
    ----------
    path : Path or str, optional
        Explicit path to override auto-detection.

    Returns
    -------
    pd.DataFrame
        1700 rows × 24 columns with clean column names.
    """
    if path is not None:
        p = Path(path)
        if "mmc2" in p.name:
            return load_mmc2_table(p)
        return load_mmc6_table(p)

    if MMC6_PATH.exists():
        return load_mmc6_table()
    return load_mmc2_table()


def which_spreadsheet() -> str:
    """Return which spreadsheet will be loaded by :func:`load_synapse_table`."""
    if MMC6_PATH.exists():
        return f"mmc6 (updated, {MMC6_PATH})"
    if MMC2_PATH.exists():
        return f"mmc2 (original, {MMC2_PATH})"
    return "none found"


# ---------------------------------------------------------------------------
# BossDB source
# ---------------------------------------------------------------------------

BOSSDB_PROJECT = "https://bossdb.org/project/kasthuri2015"

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
    """Rows with valid vesicle counts (> 0)."""
    return df[df["vesicle_count"].notna() & (df["vesicle_count"] > 0)]


def valid_terminal(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid terminal/en-passant labels (0 or 1)."""
    return df[df["terminal"].isin([0, 1])]


def valid_msb(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid multi-synaptic bouton labels (0 or 1)."""
    return df[df["multi_syn_bouton"].isin([0, 1])]


def valid_mito(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid mitochondria counts (≥ 0)."""
    return df[df["mito_in_bouton"].notna() & (df["mito_in_bouton"] >= 0)]


def valid_spine_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with valid spine volumes (> 0; excludes shaft sentinels)."""
    return df[df["spine_volume"].notna() & (df["spine_volume"] > 0)]


def valid_spine_apparatus(df: pd.DataFrame) -> pd.DataFrame:
    """Spine rows with definitive spine apparatus annotation (0 or 1)."""
    return df[(df["is_spine"] == 1) & df["spine_apparatus"].isin([0, 1])]


def excitatory(df: pd.DataFrame) -> pd.DataFrame:
    """Excitatory synapses (axon_type == 0)."""
    return df[df["axon_type"] == 0]


def inhibitory(df: pd.DataFrame) -> pd.DataFrame:
    """Inhibitory synapses (axon_type == 1)."""
    return df[df["axon_type"] == 1]


def myelinated(df: pd.DataFrame) -> pd.DataFrame:
    """Myelinated axon synapses (axon_type == 2)."""
    return df[df["axon_type"] == 2]


def cylinder1(df: pd.DataFrame) -> pd.DataFrame:
    """Synapses in cylinder 1."""
    return df[df["in_cylinder1"] == 1]


def spine_synapses(df: pd.DataFrame) -> pd.DataFrame:
    """Spine synapses (is_spine == 1)."""
    return df[df["is_spine"] == 1]


def shaft_synapses(df: pd.DataFrame) -> pd.DataFrame:
    """Shaft synapses (is_spine == 0)."""
    return df[df["is_spine"] == 0]
