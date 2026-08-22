import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ParlaySimulator from "../pages/ParlaySimulator";
import { simulateParlay } from "../services/parlayApi";

vi.mock("../services/parlayApi");

const RESPONSE = {
  combined_probability: 0.121,
  combined_decimal_odds: 9.11,
  ev_per_unit: -0.1,
  break_even_probability: 0.1098,
  run_id: 5,
  metrics: {
    win_pct: 0.15,
    avg_ending_bankroll: 850,
    median_ending_bankroll: 900,
    std_dev: 300,
    min_bankroll: 0,
    max_bankroll: 2000,
    risk_of_ruin: 0.6,
    avg_max_drawdown: -200,
    worst_case_drawdown: -900,
    ev_per_bet: -10,
    ev_total: -10,
  },
  distribution: { bin_edges: [0, 1000, 2000], counts: [4000, 1000] },
};

function renderPage() {
  return render(
    <MemoryRouter>
      <ParlaySimulator />
    </MemoryRouter>,
  );
}

describe("ParlaySimulator page", () => {
  beforeEach(() => {
    vi.mocked(simulateParlay).mockResolvedValue(RESPONSE);
  });

  it("shows a live combined-math preview", () => {
    renderPage();
    const preview = screen.getByTestId("parlay-preview");
    // two default legs: 55% x 55% = 30.25% at 1.909^2 = 3.64x
    expect(preview).toHaveTextContent("30.3%");
    expect(preview).toHaveTextContent("3.64x");
    expect(preview).toHaveTextContent("-"); // EV sign present
  });

  it("submits all legs with converted probabilities", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "Run Parlay Simulation" }));
    await waitFor(() => expect(screen.getByTestId("parlay-results")).toBeInTheDocument());
    expect(vi.mocked(simulateParlay)).toHaveBeenCalledWith(
      expect.objectContaining({
        legs: [
          { odds_american: -110, win_probability: 0.55 },
          { odds_american: -110, win_probability: 0.55 },
        ],
        bankroll: 1000,
        bet_size: 100,
        bet_size_type: "flat",
        seed: 42,
      }),
    );
  });

  it("renders combined stats and ruin warning after the run", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "Run Parlay Simulation" }));
    await waitFor(() =>
      expect(screen.getByTestId("parlay-probability")).toHaveTextContent("12.1%"),
    );
    expect(screen.getByTestId("parlay-payout")).toHaveTextContent("9.11x");
    expect(screen.getByTestId("parlay-ev")).toHaveClass("text-danger");
    expect(screen.getByTestId("parlay-ruin-warning")).toBeInTheDocument();
  });

  it("blocks submit while any leg is invalid", async () => {
    renderPage();
    await userEvent.clear(screen.getByLabelText("Win probability for leg 1"));
    await userEvent.type(screen.getByLabelText("Win probability for leg 1"), "150");
    expect(screen.getByRole("button", { name: "Run Parlay Simulation" })).toBeDisabled();
  });
});
