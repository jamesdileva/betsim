import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IntelligenceScore from "../components/IntelligenceScore";
import type { IntelligenceScoreData } from "../types/portfolio";

const DATA: IntelligenceScoreData = {
  score: 84,
  stars: 4,
  risk_level: "Low",
  breakdown: {
    probability: { value: 0.74, points: 18.5, max: 25 },
    simulation: { value: 0.81, points: 20.3, max: 25 },
    ev: { value: 0.083, points: 20.8, max: 25 },
    confidence: { value: 0.88, points: 13.2, max: 15 },
    calibration: { value: "well_calibrated", points: 10, max: 10 },
    bonuses: { value: "bonuses", points: 5, max: 10, applied: "calibration, simulation_agrees" },
  },
};

describe("IntelligenceScore", () => {
  it("renders score, stars, and risk level", () => {
    render(<IntelligenceScore data={DATA} />);
    expect(screen.getByTestId("score-value")).toHaveTextContent("84");
    expect(screen.getByTestId("score-risk")).toHaveTextContent("Low");
    expect(screen.getByText(/★★★★/)).toBeInTheDocument();
  });

  it("renders per-component breakdown bars", () => {
    render(<IntelligenceScore data={DATA} />);
    for (const name of ["probability", "simulation", "ev", "confidence"]) {
      expect(screen.getByTestId(`score-component-${name}`)).toBeInTheDocument();
    }
    expect(screen.getByTestId("score-bonuses")).toHaveTextContent("simulation_agrees");
  });

  it("colors risk level by severity", () => {
    const { rerender } = render(
      <IntelligenceScore data={{ ...DATA, risk_level: "High" }} />,
    );
    expect(screen.getByTestId("score-risk")).toHaveClass("text-danger");
    rerender(<IntelligenceScore data={{ ...DATA, risk_level: "Medium" }} />);
    expect(screen.getByTestId("score-risk")).toHaveClass("text-warning");
  });
});
