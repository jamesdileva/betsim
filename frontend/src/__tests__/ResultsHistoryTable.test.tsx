import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ResultsHistoryTable from "../components/ResultsHistoryTable";
import type { RunSummary } from "../types/strategy";

const RUNS: RunSummary[] = [
  {
    run_id: 1,
    strategy_id: null,
    odds_american: -110,
    win_probability: 0.55,
    bankroll: 1000,
    bet_size: 50,
    bet_size_type: "flat",
    num_bets: 100,
    num_simulations: 5000,
    created_at: "2026-08-22T10:00:00Z",
    result_count: 5000,
    win_pct: 0.62,
    avg_final_bankroll: 1240,
    risk_of_ruin: 0.18,
  },
  {
    run_id: 2,
    strategy_id: null,
    odds_american: 200,
    win_probability: 0.35,
    bankroll: 500,
    bet_size: 25,
    bet_size_type: "flat",
    num_bets: 50,
    num_simulations: 3000,
    created_at: "2026-08-21T09:00:00Z",
    result_count: 3000,
    win_pct: 0.41,
    avg_final_bankroll: 380,
    risk_of_ruin: 0.44,
  },
];

describe("ResultsHistoryTable", () => {
  it("renders a row per run with key stats", () => {
    render(
      <ResultsHistoryTable runs={RUNS} onRerun={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(screen.getByTestId("history-row-1")).toBeInTheDocument();
    expect(screen.getByTestId("history-row-2")).toBeInTheDocument();
    expect(screen.getByText("62.0%")).toBeInTheDocument();
    expect(screen.getAllByText("-110").length).toBeGreaterThan(0);
  });

  it("highlights high ruin risk in red", () => {
    render(<ResultsHistoryTable runs={RUNS} onRerun={vi.fn()} onDelete={vi.fn()} />);
    const row2 = screen.getByTestId("history-row-2");
    expect(row2.textContent).toContain("44.0%");
    // danger class applied to the ruin cell
    expect(row2.innerHTML).toContain("text-danger");
  });

  it("filters rows by text", async () => {
    render(<ResultsHistoryTable runs={RUNS} onRerun={vi.fn()} onDelete={vi.fn()} />);
    await userEvent.type(screen.getByLabelText("Filter history"), "200");
    expect(screen.queryByTestId("history-row-1")).not.toBeInTheDocument();
    expect(screen.getByTestId("history-row-2")).toBeInTheDocument();
  });

  it("fires re-run with the row's params", async () => {
    const onRerun = vi.fn();
    render(<ResultsHistoryTable runs={RUNS} onRerun={onRerun} onDelete={vi.fn()} />);
    const rerunButtons = screen.getAllByRole("button", { name: "Re-run" });
    await userEvent.click(rerunButtons[0]);
    expect(onRerun).toHaveBeenCalledWith(RUNS[0]);
  });
});
