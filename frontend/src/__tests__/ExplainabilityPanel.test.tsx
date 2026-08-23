import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ExplainabilityPanel from "../components/ExplainabilityPanel";
import type { Factor } from "../types/ml";

const FACTORS: Factor[] = [
  { feature: "model_edge_vs_market", label: "Model edge vs. market", impact: 0.1, direction: "+" },
  { feature: "hours_until_game", label: "Time until kickoff", impact: -0.02, direction: "-" },
];

describe("ExplainabilityPanel", () => {
  it("renders factors with +/- direction indicators", () => {
    render(<ExplainabilityPanel factors={FACTORS} />);
    expect(screen.getByTestId("explainability-panel")).toBeInTheDocument();
    expect(screen.getByText("Model edge vs. market")).toBeInTheDocument();
    expect(screen.getAllByText("+").length).toBeGreaterThan(0);
    expect(screen.getByText("-")).toBeInTheDocument();
  });

  it("formats impacts as signed percentages", () => {
    render(<ExplainabilityPanel factors={FACTORS} />);
    expect(screen.getByText("+10.0%")).toBeInTheDocument();
    expect(screen.getByText("-2.0%")).toBeInTheDocument();
  });

  it("shows model confidence when provided", () => {
    render(<ExplainabilityPanel factors={FACTORS} confidence={0.8} />);
    expect(screen.getByTestId("model-confidence")).toHaveTextContent("80%");
  });

  it("shows an empty message without factors", () => {
    render(<ExplainabilityPanel factors={[]} />);
    expect(screen.getByText(/No factor data available/)).toBeInTheDocument();
  });
});
