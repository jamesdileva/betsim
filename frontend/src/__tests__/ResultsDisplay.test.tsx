import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResultsDisplay from "../components/ResultsDisplay";
import type { MetricSummary } from "../types/simulation";

const BASE_METRICS: MetricSummary = {
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
};

describe("ResultsDisplay", () => {
  it("renders the four key metric cards", () => {
    render(<ResultsDisplay metrics={BASE_METRICS} />);
    expect(screen.getByTestId("metric-win-pct")).toHaveTextContent("62.0%");
    expect(screen.getByTestId("metric-avg-bankroll")).toHaveTextContent("$1,240");
    expect(screen.getByTestId("metric-risk-of-ruin")).toHaveTextContent("18.0%");
    expect(screen.getByTestId("metric-ev-per-bet")).toHaveTextContent("+2.27");
  });

  it("colors risk of ruin green under 10%", () => {
    render(<ResultsDisplay metrics={{ ...BASE_METRICS, risk_of_ruin: 0.05 }} />);
    expect(screen.getByTestId("metric-risk-of-ruin")).toHaveClass("text-success");
  });

  it("flags aggressive strategies over 25% ruin risk", () => {
    render(<ResultsDisplay metrics={{ ...BASE_METRICS, risk_of_ruin: 0.38 }} />);
    expect(screen.getByTestId("metric-risk-of-ruin")).toHaveClass("text-danger");
    expect(screen.getByTestId("ruin-warning")).toBeInTheDocument();
  });

  it("shows negative EV in red", () => {
    render(<ResultsDisplay metrics={{ ...BASE_METRICS, ev_per_bet: -1.5 }} />);
    expect(screen.getByTestId("metric-ev-per-bet")).toHaveClass("text-danger");
    expect(screen.getByTestId("metric-ev-per-bet")).toHaveTextContent("-1.50");
  });
});
