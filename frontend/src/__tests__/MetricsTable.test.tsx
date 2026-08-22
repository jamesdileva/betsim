import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MetricsTable from "../components/MetricsTable";
import type { MetricSummary } from "../types/simulation";

const METRICS: MetricSummary = {
  win_pct: 0.62,
  avg_ending_bankroll: 1240.5,
  median_ending_bankroll: 1180,
  std_dev: 350.25,
  min_bankroll: 0,
  max_bankroll: 2400,
  risk_of_ruin: 0.18,
  avg_max_drawdown: -320,
  worst_case_drawdown: -450,
  ev_per_bet: 2.27,
  ev_total: 227,
};

describe("MetricsTable", () => {
  it("renders every detailed metric", () => {
    render(<MetricsTable metrics={METRICS} />);
    expect(screen.getByTestId("metrics-table")).toBeInTheDocument();
    expect(screen.getByTestId("table-median")).toHaveTextContent("$1,180");
    expect(screen.getByTestId("table-best-case")).toHaveTextContent("$2,400");
    expect(screen.getByTestId("table-worst-case")).toHaveTextContent("$0");
    expect(screen.getByTestId("table-std-dev")).toHaveTextContent("$350.25");
    expect(screen.getByTestId("table-avg-drawdown")).toHaveTextContent("-$320");
    expect(screen.getByTestId("table-worst-drawdown")).toHaveTextContent("-$450");
    expect(screen.getByTestId("table-ev-total")).toHaveTextContent("+$227");
  });

  it("colors drawdowns and negative EV as danger", () => {
    render(<MetricsTable metrics={{ ...METRICS, ev_total: -100 }} />);
    expect(screen.getByTestId("table-avg-drawdown").className).toContain("text-danger");
    expect(screen.getByTestId("table-worst-drawdown").className).toContain("text-danger");
    expect(screen.getByTestId("table-ev-total").className).toContain("text-danger");
  });
});
