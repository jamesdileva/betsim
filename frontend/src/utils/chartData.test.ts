import { describe, expect, it } from "vitest";
import type { DistributionData, TrajectoryBands } from "../types/simulation";
import { buildDistributionData, buildTrajectoryData } from "./chartData";

const BANDS: TrajectoryBands = {
  median: [100, 105, 110],
  p10: [100, 95, 90],
  p90: [100, 115, 130],
  min: [100, 85, 70],
  max: [100, 120, 150],
};

describe("buildTrajectoryData", () => {
  it("produces one row per bet index with all bands", () => {
    const rows = buildTrajectoryData(BANDS);
    expect(rows).toHaveLength(3);
    expect(rows[0]).toEqual({
      bet: 0,
      median: 100,
      p10: 100,
      p90: 100,
      min: 100,
      max: 100,
    });
    expect(rows[2].median).toBe(110);
    expect(rows[2].min).toBe(70);
  });

  it("rounds values to two decimals", () => {
    const rows = buildTrajectoryData({
      ...BANDS,
      median: [100.123456, 1, 2],
      p10: BANDS.p10,
      p90: BANDS.p90,
      min: BANDS.min,
      max: BANDS.max,
    });
    expect(rows[0].median).toBe(100.12);
  });

  it("handles a single-point trajectory", () => {
    const rows = buildTrajectoryData({
      median: [500],
      p10: [500],
      p90: [500],
      min: [500],
      max: [500],
    });
    expect(rows).toHaveLength(1);
  });
});

describe("buildDistributionData", () => {
  it("labels bins and preserves counts", () => {
    const distribution: DistributionData = {
      bin_edges: [0, 10, 20, 30],
      counts: [5, 10, 15],
    };
    const bins = buildDistributionData(distribution);
    expect(bins).toHaveLength(3);
    expect(bins[0].label).toBe("$0–$10");
    expect(bins[1].midpoint).toBe(15);
    expect(bins.reduce((sum, b) => sum + b.count, 0)).toBe(30);
  });

  it("handles fractional edges", () => {
    const bins = buildDistributionData({ bin_edges: [99.5, 199.5], counts: [7] });
    expect(bins[0].label).toBe("$100–$200");
    expect(bins[0].midpoint).toBe(149.5);
  });
});
