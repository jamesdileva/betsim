import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import SimulationForm from "../components/SimulationForm";

function renderForm(onRun = vi.fn()) {
  render(<SimulationForm onRun={onRun} />);
  return onRun;
}

async function fillAndSubmit(values: Record<string, string>) {
  const replacements: Record<string, string> = {
    odds: "Odds (American)",
    winProbability: "Win probability (%)",
    bankroll: "Bankroll ($)",
    betSize: "Bet size ($ or fraction)",
    numBets: "Bets per simulation",
    numSimulations: "Number of simulations",
  };
  for (const [field, label] of Object.entries(replacements)) {
    if (values[field] !== undefined) {
      const input = screen.getByLabelText(label);
      await userEvent.clear(input);
      await userEvent.type(input, values[field]);
    }
  }
  await userEvent.click(screen.getByRole("button", { name: "Run Simulation" }));
}

describe("SimulationForm", () => {
  it("shows implied probability helper for valid odds", () => {
    renderForm();
    expect(screen.getByTestId("implied-prob")).toHaveTextContent("52.38%");
  });

  it("submits a correct API payload for valid input", async () => {
    const onRun = renderForm();
    await fillAndSubmit({});
    expect(onRun).toHaveBeenCalledWith({
      odds_american: -110,
      win_probability: 0.55,
      bankroll: 1000,
      bet_size: 50,
      bet_size_type: "flat",
      num_bets: 100,
      num_simulations: 5000,
    });
  });

  it.each([
    ["0", "odds"],
    ["-50", "odds"],
    ["abc", "odds"],
  ])("rejects invalid odds %s", async (odds) => {
    const onRun = renderForm();
    await fillAndSubmit({ odds });
    expect(onRun).not.toHaveBeenCalled();
    expect(screen.getByText(/Odds must be a nonzero American value/)).toBeInTheDocument();
  });

  it("rejects win probability outside 0-100%", async () => {
    const onRun = renderForm();
    await fillAndSubmit({ winProbability: "150" });
    expect(onRun).not.toHaveBeenCalled();
    expect(screen.getByText(/between 0% and 100%/)).toBeInTheDocument();
  });

  it("rejects non-positive bankroll", async () => {
    const onRun = renderForm();
    await fillAndSubmit({ bankroll: "-5" });
    expect(onRun).not.toHaveBeenCalled();
    expect(screen.getByText(/Bankroll must be greater than/)).toBeInTheDocument();
  });

  it("accepts zero bet size only for kelly strategies", async () => {
    const onRun = renderForm();
    await userEvent.selectOptions(screen.getByLabelText("Bet strategy"), "kelly");
    await fillAndSubmit({ betSize: "0" });
    expect(onRun).toHaveBeenCalledTimes(1);
  });
});
