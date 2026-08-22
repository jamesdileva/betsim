import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CalibrationChart from "../components/CalibrationChart";
import type { CalibrationReport } from "../types/systemPlays";

const REPORT: CalibrationReport = {
  stated_probability: 0.6,
  actual_win_rate: 0.5987,
  calibration_error: 0.0013,
  calibration_status: "well_calibrated",
  confidence_interval_low: 0.58,
  confidence_interval_high: 0.62,
  recommendation: "Your probability estimates are well-calibrated. Keep tracking.",
};

describe("CalibrationChart", () => {
  it("renders stated and actual bars", () => {
    const { container } = render(<CalibrationChart report={REPORT} width={600} height={260} />);
    expect(screen.getByTestId("calibration-chart")).toBeInTheDocument();
    expect(screen.getByText("Stated")).toBeInTheDocument();
    expect(screen.getByText("Actual (simulated)")).toBeInTheDocument();
    const bars = container.querySelectorAll(".recharts-bar-rectangle");
    expect(bars.length).toBeGreaterThanOrEqual(2);
  });
});
