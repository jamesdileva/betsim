import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import StrategyComparison from "../components/StrategyComparison";
import type { SimulationParams } from "../types/simulation";

vi.mock("../services/api", () => ({
  default: { post: vi.fn() },
}));

import api from "../services/api";

const PARAMS: SimulationParams = {
  odds_american: -110,
  win_probability: 0.55,
  bankroll: 1000,
  bet_size: 50,
  bet_size_type: "flat",
  num_bets: 100,
  num_simulations: 500,
};

function mockResponse(medianFinal: number) {
  return {
    data: {
      run_id: 1,
      metrics: {
        win_pct: 0.6,
        avg_ending_bankroll: medianFinal + 50,
        median_ending_bankroll: medianFinal,
        std_dev: 100,
        min_bankroll: 0,
        max_bankroll: 2000,
        risk_of_ruin: 0.2,
        avg_max_drawdown: -100,
        worst_case_drawdown: -300,
        ev_per_bet: 1,
        ev_total: 50,
      },
      distribution: { bin_edges: [0, 1000], counts: [10] },
      trajectory: { median: [], p10: [], p90: [], min: [], max: [] },
    },
  };
}

describe("StrategyComparison", () => {
  it("renders nothing without params", () => {
    const { container } = render(<StrategyComparison params={null} />);
    expect(container.querySelector('[data-testid="strategy-comparison"]')).toBeNull();
  });

  it("calls the API once per strategy and shows all rows", async () => {
    vi.mocked(api.post).mockImplementation((async () =>
      mockResponse(1200)) as never);

    render(<StrategyComparison params={PARAMS} />);
    await waitFor(() =>
      expect(screen.getByTestId("comparison-Flat $")).toBeInTheDocument(),
    );
    expect(vi.mocked(api.post)).toHaveBeenCalledTimes(4);
    for (const name of ["Flat $", "% of bankroll", "Kelly", "Half-Kelly"]) {
      expect(screen.getByTestId(`comparison-${name}`)).toBeInTheDocument();
    }
    // each call overrides the strategy
    const strategies = vi
      .mocked(api.post)
      .mock.calls.map(([, body]) => (body as SimulationParams).bet_size_type);
    expect(new Set(strategies)).toEqual(new Set(["flat", "percentage", "kelly", "half_kelly"]));
  });

  it("warns when a strategy leaves less than half the starting bankroll", async () => {
    vi.mocked(api.post).mockImplementation((async (_url: string, payload?: unknown) => {
      const isKelly =
        (payload as { bet_size_type?: string } | undefined)?.bet_size_type === "kelly";
      return mockResponse(isKelly ? 400 : 1200);
    }) as never);

    render(<StrategyComparison params={PARAMS} />);
    await waitFor(() =>
      expect(screen.getByTestId("comparison-warning")).toBeInTheDocument(),
    );
    // the kelly row's median cell is danger-colored
    expect(screen.getByTestId("comparison-Kelly").innerHTML).toContain("text-danger");
  });
});

