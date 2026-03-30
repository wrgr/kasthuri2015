"""Load and validate SASD claims from the sasdpairs.mat file.

Validates claims SASD-1 through SASD-8 by loading the MATLAB data and
running the permutation tests in Python (porting the R analysis).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.io


SASD_MAT = Path(__file__).resolve().parent.parent.parent / "SASDPairs" / "sasdpairs.mat"

# Field names in the .mat struct
FIELDS = [
    "spineid", "axpartid", "dparentid", "aparentid",
    "spinevolume", "psdvol", "spineapp", "nrmitos", "nrvesicles",
    "psd_vast_x", "psd_vast_y", "psd_vast_z",
]


def load_sasd_data() -> list[dict[str, np.ndarray]]:
    """Load SASD pair groups from the .mat file.

    Returns a list of dicts, one per SASD group. Each dict maps field names
    to 1-D numpy arrays (one entry per spine in the group).
    """
    if not SASD_MAT.exists():
        raise FileNotFoundError(f"SASD .mat file not found: {SASD_MAT}")

    mat = scipy.io.loadmat(str(SASD_MAT))
    raw = mat["sasdpairs"]
    n_groups = raw.shape[1]

    groups = []
    for i in range(n_groups):
        group = {}
        for field in FIELDS:
            try:
                arr = raw[0, i][field][0, 0].flatten()
                group[field] = arr.astype(float)
            except (ValueError, IndexError, KeyError):
                pass
        groups.append(group)
    return groups


def groups_to_dataframe(groups: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    """Flatten SASD groups into columnar arrays with pair_id column.

    Returns dict with keys: pair_id, spineid, dparentid, aparentid,
    spinevolume, psdvol, spineapp, nrmitos, nrvesicles.
    """
    columns: dict[str, list] = {f: [] for f in FIELDS[:9]}
    columns["pair_id"] = []

    for i, group in enumerate(groups):
        n = len(group.get("spineid", []))
        columns["pair_id"].extend([i] * n)
        for f in FIELDS[:9]:
            arr = group.get(f, np.full(n, np.nan))
            columns[f].extend(arr.tolist())

    return {k: np.array(v) for k, v in columns.items()}


def compute_all_pairwise_diffs(data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Compute pairwise differences and SASD labels for all spine pairs.

    Returns dict with columns: sasd_label, and one diff column per feature.
    sasd_label values: "SASD", "DASD", "SADD", "DADD".
    """
    n = len(data["spineid"])
    pairs_i = []
    pairs_j = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs_i.append(i)
            pairs_j.append(j)

    pi = np.array(pairs_i)
    pj = np.array(pairs_j)

    same_d = data["dparentid"][pi] == data["dparentid"][pj]
    same_a = data["aparentid"][pi] == data["aparentid"][pj]

    labels = np.where(
        same_a & same_d, "SASD",
        np.where(same_a & ~same_d, "SADD",
                 np.where(~same_a & same_d, "DASD", "DADD"))
    )

    result: dict[str, np.ndarray] = {"sasd_label": labels}

    # Continuous features — use abs diff of log10
    for feat in ["spinevolume", "psdvol", "nrvesicles"]:
        vals = data[feat].astype(float)
        # Avoid log(0)
        vals = np.where(vals > 0, vals, 1.0)
        log_vals = np.log10(vals)
        result[f"log_{feat}"] = np.abs(log_vals[pi] - log_vals[pj])

    # Discrete features — binary same/different
    for feat in ["spineapp", "nrmitos"]:
        result[feat] = (data[feat][pi] != data[feat][pj]).astype(float)

    return result


def permutation_test(
    diffs: np.ndarray,
    labels: np.ndarray,
    group_a: str,
    group_b: str | list[str],
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """Run a permutation test comparing mean diffs between groups.

    Returns dict with mean_a, mean_b, observed_diff, p_value.
    """
    if isinstance(group_b, str):
        group_b = [group_b]

    mask_a = labels == group_a
    mask_b = np.isin(labels, group_b)
    mask = mask_a | mask_b

    diffs_sub = diffs[mask]
    is_a = mask_a[mask]

    mean_a = diffs_sub[is_a].mean()
    mean_b = diffs_sub[~is_a].mean()
    observed = mean_b - mean_a  # positive = group_a more similar

    rng = np.random.default_rng(seed)
    count_ge = 0
    for _ in range(n_permutations):
        perm = rng.permutation(is_a)
        perm_diff = diffs_sub[~perm].mean() - diffs_sub[perm].mean()
        if perm_diff >= observed:
            count_ge += 1

    return {
        "mean_group_a": round(float(mean_a), 4),
        "mean_group_b": round(float(mean_b), 4),
        "observed_diff": round(float(observed), 4),
        "p_value": count_ge / n_permutations,
        "n_permutations": n_permutations,
        "n_group_a": int(is_a.sum()),
        "n_group_b": int((~is_a).sum()),
    }


def validate_sasd(n_permutations: int = 1_000) -> dict:
    """Validate all SASD claims.

    Returns a dict with pair counts, and permutation test results for each
    feature (SASD vs non-SASD comparison).
    """
    groups = load_sasd_data()
    data = groups_to_dataframe(groups)
    pairs = compute_all_pairwise_diffs(data)

    labels = pairs["sasd_label"]
    pair_counts = {
        "SASD": int((labels == "SASD").sum()),
        "DASD": int((labels == "DASD").sum()),
        "SADD": int((labels == "SADD").sum()),
        "DADD": int((labels == "DADD").sum()),
        "total": len(labels),
    }

    features = ["log_spinevolume", "log_psdvol", "log_nrvesicles", "spineapp", "nrmitos"]
    non_sasd = ["DASD", "SADD", "DADD"]

    # SASD vs non-SASD
    sasd_vs_rest = {}
    for feat in features:
        sasd_vs_rest[feat] = permutation_test(
            pairs[feat], labels, "SASD", non_sasd, n_permutations
        )

    # DASD vs DADD (dendrite effect)
    dasd_vs_dadd = {}
    for feat in features:
        dasd_vs_dadd[feat] = permutation_test(
            pairs[feat], labels, "DASD", "DADD", n_permutations
        )

    return {
        "n_groups": len(groups),
        "n_spines": len(data["spineid"]),
        "pair_counts": pair_counts,
        "sasd_vs_rest": sasd_vs_rest,
        "dasd_vs_dadd": dasd_vs_dadd,
    }
