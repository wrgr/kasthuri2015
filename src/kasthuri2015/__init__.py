"""kasthuri2015 — Reproducible claims from Kasthuri et al. 2015.

Saturated Reconstruction of a Volume of Neocortex.
Cell 162(3), 648-661. doi:10.1016/j.cell.2015.06.054
"""

from kasthuri2015.claims import (
    CATEGORIES,
    CLAIMS,
    Claim,
    claims_by_category,
    get_claim,
    list_categories,
    list_claims,
    summary_table,
)

__all__ = [
    "CATEGORIES",
    "CLAIMS",
    "Claim",
    "claims_by_category",
    "get_claim",
    "list_categories",
    "list_claims",
    "summary_table",
    # BossDB module (requires optional deps: requests, blosc)
    "bossdb",
]
__version__ = "0.1.0"
