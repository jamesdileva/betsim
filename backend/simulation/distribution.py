"""Distribution helpers: histogram binning and trajectory percentile bands."""

import numpy as np


def histogram(
    final_bankrolls: list[float], num_bins: int = 20
) -> tuple[list[float], list[int]]:
    """Histogram of final bankrolls. Returns (bin_edges, counts).

    len(bin_edges) == num_bins + 1 and sum(counts) == len(final_bankrolls).
    """
    if not final_bankrolls:
        raise ValueError("final_bankrolls must not be empty")
    if num_bins < 1:
        raise ValueError(f"num_bins must be >= 1, got {num_bins}")

    counts, edges = np.histogram(final_bankrolls, bins=num_bins)
    return edges.tolist(), counts.tolist()


def percentile_bands(trajectories: list[list[float]]) -> dict[str, list[float]]:
    """Percentile bands across all trajectories at each bet index.

    Trajectories must be rectangular (same length) — simulate_batch's
    ruin padding guarantees this.
    """
    if not trajectories:
        raise ValueError("trajectories must not be empty")
    lengths = {len(t) for t in trajectories}
    if len(lengths) > 1:
        raise ValueError(f"Trajectories must be rectangular, got lengths {sorted(lengths)}")

    matrix = np.asarray(trajectories, dtype=float)
    return {
        "p10": np.percentile(matrix, 10, axis=0).tolist(),
        "median": np.percentile(matrix, 50, axis=0).tolist(),
        "p90": np.percentile(matrix, 90, axis=0).tolist(),
        "min": np.min(matrix, axis=0).tolist(),
        "max": np.max(matrix, axis=0).tolist(),
    }
