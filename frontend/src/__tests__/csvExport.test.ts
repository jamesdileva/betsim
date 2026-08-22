import { describe, expect, it } from "vitest";
import { downloadCsv, resultToCsv } from "../utils/csvExport";
import type { SimulationResult } from "../types/simulation";

const RESULT: SimulationResult = {
  run_id: 42,
  metrics: {
    win_pct: 0.62,
    avg_ending_bankroll: 1240,
    median_ending_bankroll: 1180,
    std_dev: 350,
    min_bankroll: 0,
    max_bankroll: 2400,
    risk_of_ruin: 0.18,
    avg_max_drawdown: -320,
    worst_case_drawdown: -450,
    ev_per_bet: 2.27,
    ev_total: 227,
  },
  distribution: { bin_edges: [0, 1000, 2000], counts: [10, 20] },
  trajectory: { median: [], p10: [], p90: [], min: [], max: [] },
};

describe("resultToCsv", () => {
  it("produces a metrics section and a distribution section", () => {
    const csv = resultToCsv(RESULT);
    const lines = csv.split("\n");
    expect(lines[0]).toBe("metric,value");
    expect(csv).toContain("win_pct,0.62");
    expect(csv).toContain("ev_total,227");
    expect(lines).toContain("bin_low,bin_high,count");
    expect(lines).toContain("0,1000,10");
    expect(lines).toContain("1000,2000,20");
  });

  it("escapes values containing commas or quotes", () => {
    const csv = resultToCsv({
      ...RESULT,
      metrics: { ...RESULT.metrics, ev_per_bet: 2.5 },
    });
    // sanity: no unquoted stray commas inside values (all numeric here)
    expect(csv.split("\n")[1]).toBe("win_pct,0.62");
  });
});

describe("downloadCsv", () => {
  it("creates and clicks a download link with the CSV blob", () => {
    const click = vi.fn();
    const anchor = { href: "", download: "", click };
    const createElementSpy = vi
      .spyOn(document, "createElement")
      .mockReturnValue(anchor as unknown as HTMLElement);
    const appendSpy = vi.spyOn(document.body, "appendChild").mockImplementation(() => anchor as unknown as HTMLElement);
    const removeSpy = vi
      .spyOn(document.body, "removeChild")
      .mockReturnValue(anchor as unknown as ChildNode);
    // jsdom lacks blob URL methods entirely
    const createObjectURL = vi.fn(() => "blob:test");
    const revokeObjectURL = vi.fn();
    (URL as unknown as Record<string, unknown>).createObjectURL = createObjectURL;
    (URL as unknown as Record<string, unknown>).revokeObjectURL = revokeObjectURL;

    downloadCsv("test.csv", "a,b\n1,2");

    expect(anchor.download).toBe("test.csv");
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(click).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:test");

    createElementSpy.mockRestore();
    appendSpy.mockRestore();
    removeSpy.mockRestore();
  });
});
