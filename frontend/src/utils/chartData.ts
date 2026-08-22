import type { DistributionData, TrajectoryBands } from "../types/simulation";

export interface TrajectoryPoint {
  bet: number;
  median: number;
  p10: number;
  p90: number;
  min: number;
  max: number;
}

export interface DistributionBin {
  label: string;
  midpoint: number;
  count: number;
}

/**
 * Reshape API trajectory bands into one row per bet index for Recharts.
 */
export function buildTrajectoryData(bands: TrajectoryBands): TrajectoryPoint[] {
  const n = bands.median.length;
  return Array.from({ length: n }, (_, i) => ({
    bet: i,
    median: round2(bands.median[i]),
    p10: round2(bands.p10[i]),
    p90: round2(bands.p90[i]),
    min: round2(bands.min[i]),
    max: round2(bands.max[i]),
  }));
}

/**
 * Reshape API histogram bins into labeled rows. Counts are preserved exactly:
 * sum(rows.count) === sum(distribution.counts).
 */
export function buildDistributionData(distribution: DistributionData): DistributionBin[] {
  const { bin_edges, counts } = distribution;
  return counts.map((count, i) => {
    const low = bin_edges[i];
    const high = bin_edges[i + 1];
    return {
      label: `$${Math.round(low)}–$${Math.round(high)}`,
      midpoint: (low + high) / 2,
      count,
    };
  });
}

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}
