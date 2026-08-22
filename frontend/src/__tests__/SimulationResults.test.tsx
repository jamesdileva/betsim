import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SimulationResults from "../components/SimulationResults";
import type { SimulationResult } from "../types/simulation";

const RESULT: SimulationResult = {
  run_id: 1,
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
  trajectory: {
    median: [1000, 1010],
    p10: [1000, 995],
    p90: [1000, 1030],
    min: [1000, 990],
    max: [1000, 1050],
  },
};

describe("SimulationResults", () => {
  it("shows placeholder when there is no result", () => {
    render(<SimulationResults result={null} />);
    expect(screen.getByTestId("results-placeholder")).toBeInTheDocument();
  });

  it("shows loading spinner while running", () => {
    render(<SimulationResults result={null} isRunning />);
    expect(screen.getByTestId("loading-spinner")).toBeInTheDocument();
  });

  it("renders cards, charts, and metrics table together", () => {
    render(<SimulationResults result={RESULT} />);
    expect(screen.getByTestId("metric-win-pct")).toBeInTheDocument();
    expect(screen.getByTestId("bankroll-chart")).toBeInTheDocument();
    expect(screen.getByTestId("distribution-chart")).toBeInTheDocument();
    expect(screen.getByTestId("metrics-table")).toBeInTheDocument();
  });
});
