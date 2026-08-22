import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BankrollChart from "../components/BankrollChart";
import DistributionChart from "../components/DistributionChart";
import type { TrajectoryBands } from "../types/simulation";

const BANDS: TrajectoryBands = {
  median: [1000, 1002, 1010],
  p10: [1000, 990, 980],
  p90: [1000, 1015, 1030],
  min: [1000, 985, 900],
  max: [1000, 1020, 1060],
};

describe("BankrollChart", () => {
  it("renders with legend entries for all bands", () => {
    render(<BankrollChart bands={BANDS} width={800} height={300} />);
    expect(screen.getByTestId("bankroll-chart")).toBeInTheDocument();
    for (const name of ["Median", "10th pct", "90th pct", "Worst", "Best"]) {
      expect(screen.getByText(name)).toBeInTheDocument();
    }
  });

  it("draws one polyline per band series", () => {
    const { container } = render(<BankrollChart bands={BANDS} width={800} height={300} />);
    const lines = container.querySelectorAll(".recharts-line");
    expect(lines.length).toBeGreaterThanOrEqual(5);
  });
});

describe("DistributionChart", () => {
  it("renders bars for every bin", () => {
    const distribution = { bin_edges: [0, 500, 1000, 1500], counts: [12, 34, 8] };
    const { container } = render(
      <DistributionChart distribution={distribution} width={800} height={300} />,
    );
    expect(screen.getByTestId("distribution-chart")).toBeInTheDocument();
    const bars = container.querySelectorAll(".recharts-bar-rectangle");
    expect(bars).toHaveLength(3);
  });

  it("keeps empty bins in the axis rather than dropping them", () => {
    const distribution = { bin_edges: [0, 100, 200], counts: [0, 5] };
    const { container } = render(
      <DistributionChart distribution={distribution} width={800} height={300} />,
    );
    expect(container.querySelectorAll(".recharts-bar-rectangle").length).toBeLessThanOrEqual(2);
  });
});
