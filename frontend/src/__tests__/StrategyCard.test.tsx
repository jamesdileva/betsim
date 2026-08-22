import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import StrategyCard from "../components/StrategyCard";
import type { Strategy } from "../types/strategy";

const STRATEGY: Strategy = {
  id: 7,
  name: "NFL Week 1 -5",
  odds_american: -110,
  win_probability: 0.55,
  bankroll: 1000,
  bet_size: 50,
  bet_size_type: "flat",
  num_bets: 100,
  num_simulations: 5000,
  strategy_type: "single",
  created_at: "2026-08-22T00:00:00Z",
  updated_at: null,
};

describe("StrategyCard", () => {
  it("displays key parameters", () => {
    render(
      <StrategyCard strategy={STRATEGY} onRun={vi.fn()} onEdit={vi.fn()} onDelete={vi.fn()} />,
    );
    expect(screen.getByText("NFL Week 1 -5")).toBeInTheDocument();
    expect(screen.getByTestId("strategy-odds-7")).toHaveTextContent("-110");
    expect(screen.getByText("55.0%")).toBeInTheDocument();
  });

  it("fires the action callbacks", async () => {
    const onRun = vi.fn();
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    render(
      <StrategyCard strategy={STRATEGY} onRun={onRun} onEdit={onEdit} onDelete={onDelete} />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Run" }));
    await userEvent.click(screen.getByRole("button", { name: "Edit" }));
    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    expect(onRun).toHaveBeenCalledWith(STRATEGY);
    expect(onEdit).toHaveBeenCalledWith(STRATEGY);
    expect(onDelete).toHaveBeenCalledWith(STRATEGY);
  });
});
